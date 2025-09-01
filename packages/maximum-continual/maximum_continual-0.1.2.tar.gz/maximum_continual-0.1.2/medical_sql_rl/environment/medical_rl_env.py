"""
Medical SQL RL Environment - Main reinforcement learning environment for training agents.

Orchestrates the complete training process including:
- Schema randomization for robustness
- Task generation and management  
- Agent interaction and evaluation
- Reward calculation and feedback
- Progress tracking and metrics
"""

import random
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import asdict
import json

from maximum_continual.types import MessageT, PredictionResponseT
from ..database.connection import DatabaseManager
from ..database.synthetic_generator import MedicalDataGenerator
from ..database.schema_randomizer import SchemaRandomizer, GroundTruthGenerator
from ..tools.sql_tools import SQLQueryTool, DatabaseSchemaInterface, QueryValidationTool
from ..evaluation.result_evaluator import ResultEvaluator
from ..evaluation.query_tasks import QueryTaskGenerator, QueryTask


class MedicalSQLEnvironment:
    """
    Main RL environment for medical SQL query learning
    
    Manages the complete training process including schema variations,
    task generation, agent interaction, and reward calculation.
    """
    
    def __init__(self,
                 db_path: Optional[str] = None,
                 num_patients: int = 100,
                 randomization_schedule: Optional[Dict[int, str]] = None,
                 seed: int = 42):
        """
        Initialize the medical SQL RL environment
        
        Args:
            db_path: Path to database file (None for temporary)
            num_patients: Number of synthetic patients to generate
            randomization_schedule: When to randomize schema (episode -> change_type)
            seed: Random seed for reproducibility
        """
        self.db_manager = DatabaseManager(db_path)
        self.data_generator = MedicalDataGenerator(seed)
        self.schema_randomizer = SchemaRandomizer(
            randomization_schedule=randomization_schedule or {25: "minor", 100: "major", 250: "complete"},
            seed=seed
        )
        self.ground_truth_generator = GroundTruthGenerator(self.schema_randomizer)
        self.task_generator = QueryTaskGenerator()
        self.result_evaluator = ResultEvaluator()
        
        # Environment state
        self.current_episode = 0
        self.current_task: Optional[QueryTask] = None
        self.episode_history: List[Dict[str, Any]] = []
        self.performance_metrics: Dict[str, List[float]] = {
            "success_rate": [],
            "avg_reward": [],
            "schema_adaptation_time": []
        }
        
        # Training configuration
        self.num_patients = num_patients
        self.max_query_time_seconds = 30
        self.curriculum_level = 1  # Start with basic tasks
        self.tasks_per_level = 20
        self.level_up_threshold = 0.8  # Success rate to advance to next level
        
        # Performance tracking
        self.recent_performance = []  # Last 10 episodes
        self.schema_change_episodes = []
        self.level_progression = []
        
        # Initialize with first schema
        self._initialize_environment()
        
        random.seed(seed)
    
    def _initialize_environment(self):
        """Initialize the environment with default schema and data"""
        # Start with medical_clinic_v1 schema
        self.db_manager.switch_schema("medical_clinic_v1")
        
        # Generate initial synthetic data
        self.data_generator.populate_database(self.db_manager, self.num_patients)
        
        # Set current schema in randomizer
        self.schema_randomizer.current_schema = self.db_manager.current_schema
        
        print("🎯 Medical SQL RL Environment initialized")
        print(f"   Database: {self.db_manager.current_schema.variant_name}")
        print(f"   Patients: {self.num_patients}")
        print(f"   Curriculum Level: {self.curriculum_level}")
    
    def reset(self) -> Dict[str, Any]:
        """
        Reset environment for new episode
        
        Returns:
            Initial observation with task and available tools
        """
        self.current_episode += 1
        
        # Check if schema should be randomized
        if self.schema_randomizer.should_randomize(self.current_episode):
            self._randomize_schema()
        
        # Generate new task based on current curriculum level
        self.current_task = self.task_generator.generate_task(level=self.curriculum_level)
        
        # Create tools for current schema
        tools = self._create_tools()
        
        # Create initial message for agent
        initial_messages = self._create_task_messages()
        
        observation = {
            "episode": self.current_episode,
            "task": asdict(self.current_task),
            "messages": initial_messages,
            "tools": tools,
            "schema_info": self.db_manager.get_schema_info(),
            "curriculum_level": self.curriculum_level,
            "schema_variant": self.db_manager.current_schema.variant_name
        }
        
        return observation
    
    def step(self, agent_response: PredictionResponseT) -> Tuple[Dict[str, Any], float, bool, Dict[str, Any]]:
        """
        Process agent action and return (observation, reward, done, info)
        
        Args:
            agent_response: Agent's prediction response with SQL query execution
            
        Returns:
            Tuple of (next_observation, reward, episode_done, info_dict)
        """
        start_time = time.time()
        
        # Extract SQL results from agent response
        agent_result, execution_metadata = self._extract_agent_result(agent_response)
        
        # Generate ground truth for current task and schema
        ground_truth = self.ground_truth_generator.generate_ground_truth(
            asdict(self.current_task),
            self.db_manager.current_schema
        )
        
        # Evaluate agent result against ground truth
        evaluation_result = self.result_evaluator.evaluate_result(
            agent_result,
            ground_truth,
            self.current_task.evaluation_config
        )
        
        # Calculate comprehensive reward
        reward = self._calculate_reward(evaluation_result, execution_metadata, agent_response)
        
        # Update performance tracking
        self._update_performance_metrics(reward, evaluation_result)
        
        # Check if episode is done (always single-task episodes)
        done = True
        
        # Record episode results
        episode_record = {
            "episode": self.current_episode,
            "task_id": self.current_task.task_id,
            "task_level": self.current_task.level,
            "schema_variant": self.db_manager.current_schema.variant_name,
            "reward": reward,
            "evaluation_result": evaluation_result,
            "execution_metadata": execution_metadata,
            "processing_time_ms": (time.time() - start_time) * 1000,
            "curriculum_level": self.curriculum_level
        }
        
        self.episode_history.append(episode_record)
        
        # Check curriculum progression
        self._check_curriculum_progression()
        
        # Prepare next observation (empty since episode is done)
        next_observation = {}
        
        # Info dictionary with detailed feedback
        info = {
            "episode_record": episode_record,
            "performance_summary": self._get_performance_summary(),
            "curriculum_status": self._get_curriculum_status(),
            "schema_changes": len(self.schema_change_episodes),
            "ground_truth": ground_truth,
            "agent_result": agent_result
        }
        
        return next_observation, reward, done, info
    
    def _randomize_schema(self):
        """Randomize database schema and regenerate data"""
        print(f"🔄 Randomizing schema at episode {self.current_episode}")
        
        # Generate new schema variant
        new_schema = self.schema_randomizer.generate_schema_variant(
            self.current_episode
        )
        
        # Apply new schema to database
        self.db_manager.create_schema(new_schema)
        
        # Regenerate data for new schema
        self.data_generator.populate_database(self.db_manager, self.num_patients)
        
        # Record schema change
        self.schema_change_episodes.append({
            "episode": self.current_episode,
            "old_schema": self.schema_randomizer.current_schema.variant_name if self.schema_randomizer.current_schema else "none",
            "new_schema": new_schema.variant_name,
            "change_type": self.schema_randomizer.get_randomization_type(self.current_episode)
        })
        
        print(f"   New schema: {new_schema.variant_name}")
    
    def _create_tools(self) -> List[Any]:
        """Create tools for current database schema"""
        return [
            SQLQueryTool(self.db_manager),
            DatabaseSchemaInterface(self.db_manager),
            QueryValidationTool(self.db_manager)
        ]
    
    def _create_task_messages(self) -> List[MessageT]:
        """Create initial messages presenting the task to the agent"""
        system_message = MessageT(
            role="system",
            content=f"""You are a medical data analyst working with a healthcare database. 
Your task is to write and execute SQL queries to answer medical questions.

Current Database Schema: {self.db_manager.current_schema.variant_name}
Description: {self.db_manager.current_schema.description}

Available Tools:
1. sql_query - Execute SQL queries against the database
2. database_schema - Explore table structures and relationships  
3. validate_query - Validate query syntax before execution

Important Guidelines:
- Always explore the database schema first to understand table structures
- Write clean, efficient SQL queries
- Only use SELECT statements (no INSERT, UPDATE, DELETE, DROP)
- Consider medical context and clinical significance in your queries
- Provide accurate results based on the data available

Your goal is to answer the medical question accurately and efficiently."""
        )
        
        user_message = MessageT(
            role="user",
            content=f"""Medical Query Task (Level {self.current_task.level}):

Question: {self.current_task.natural_language}

Category: {self.current_task.category}
Description: {self.current_task.description}

Expected columns in result: {', '.join(self.current_task.expected_columns)}

{f'Hints: {", ".join(self.current_task.hints)}' if self.current_task.hints else ''}

Please start by exploring the database schema to understand the available tables and their relationships, then write and execute an appropriate SQL query to answer this medical question."""
        )
        
        return [system_message, user_message]
    
    def _extract_agent_result(self, agent_response: PredictionResponseT) -> Tuple[List[Dict], Dict]:
        """Extract SQL query results from agent response"""
        execution_metadata = {
            "sql_executed_successfully": False,
            "execution_time_seconds": 0,
            "query_count": 0,
            "schema_exploration_used": False,
            "validation_used": False,
            "errors": [],
            "tool_usage": []
        }
        
        agent_result = []
        
        # Analyze agent's messages and tool usage
        if not agent_response.messages:
            execution_metadata["errors"].append("No messages in agent response")
            return agent_result, execution_metadata
        
        for message in agent_response.messages:
            if message.role == "tool":
                # Parse tool response to extract SQL results
                try:
                    tool_content = json.loads(message.content) if isinstance(message.content, str) else message.content
                    
                    # Track tool usage
                    if "sql_query" in message.content:
                        execution_metadata["query_count"] += 1
                        execution_metadata["tool_usage"].append("sql_query")
                        
                        if isinstance(tool_content, dict) and "results" in tool_content:
                            if tool_content.get("success", False):
                                execution_metadata["sql_executed_successfully"] = True
                                execution_metadata["execution_time_seconds"] = tool_content.get("execution_time_ms", 0) / 1000
                                agent_result = tool_content["results"]
                            else:
                                execution_metadata["errors"].append(tool_content.get("error", "SQL execution failed"))
                    
                    elif "database_schema" in message.content:
                        execution_metadata["schema_exploration_used"] = True
                        execution_metadata["tool_usage"].append("database_schema")
                    
                    elif "validate_query" in message.content:
                        execution_metadata["validation_used"] = True
                        execution_metadata["tool_usage"].append("validate_query")
                        
                except (json.JSONDecodeError, AttributeError):
                    # Content might not be JSON
                    if "sql_query" in message.content.lower():
                        execution_metadata["tool_usage"].append("sql_query")
        
        return agent_result, execution_metadata
    
    def _calculate_reward(self, 
                         evaluation_result: Dict[str, Any], 
                         execution_metadata: Dict[str, Any], 
                         agent_response: PredictionResponseT) -> float:
        """Calculate comprehensive reward based on multiple factors"""
        
        # 1. Result Accuracy (50% weight)
        result_score = evaluation_result.get("score", 0.0)
        result_weight = 0.5
        
        # 2. Query Execution Success (20% weight)
        execution_score = 1.0 if execution_metadata["sql_executed_successfully"] else 0.0
        
        # Apply time penalty for slow queries
        exec_time = execution_metadata["execution_time_seconds"]
        if exec_time > 10:  # Penalty for queries taking more than 10 seconds
            time_penalty = max(0, min(1, (20 - exec_time) / 10))
            execution_score *= time_penalty
            
        execution_weight = 0.2
        
        # 3. Process Quality (20% weight)
        process_score = self._calculate_process_score(execution_metadata, agent_response)
        process_weight = 0.2
        
        # 4. Data Completeness (10% weight)  
        completeness_score = self._calculate_completeness_score(
            evaluation_result, self.current_task
        )
        completeness_weight = 0.1
        
        # Calculate weighted final reward
        final_reward = (
            result_score * result_weight +
            execution_score * execution_weight +
            process_score * process_weight + 
            completeness_score * completeness_weight
        )
        
        # Bonus for curriculum level (higher levels get bonus for completion)
        level_bonus = 0.1 * (self.current_task.level - 1) if result_score > 0.8 else 0
        final_reward += level_bonus
        
        # Schema adaptation bonus (bonus for maintaining performance after schema change)
        if self.current_episode in [ep["episode"] for ep in self.schema_change_episodes]:
            if result_score > 0.7:  # Good performance despite schema change
                final_reward += 0.2
        
        return min(1.0, max(0.0, final_reward))  # Clamp between 0 and 1
    
    def _calculate_process_score(self, execution_metadata: Dict, agent_response: PredictionResponseT) -> float:
        """Calculate score for agent's reasoning process quality"""
        score = 0.0
        
        # Bonus for using schema exploration
        if execution_metadata["schema_exploration_used"]:
            score += 0.4
        
        # Bonus for query validation  
        if execution_metadata["validation_used"]:
            score += 0.2
        
        # Check reasoning quality in messages
        reasoning_score = 0.0
        if agent_response.messages:
            for message in agent_response.messages:
                if message.role == "assistant":
                    content = message.content.lower()
                    
                    # Look for good practices in reasoning
                    if any(word in content for word in ["because", "since", "therefore", "analysis", "examine"]):
                        reasoning_score += 0.1
                    
                    if any(word in content for word in ["join", "relationship", "foreign key"]):
                        reasoning_score += 0.1  # Shows understanding of relationships
                        
                    if any(word in content for word in ["where", "filter", "condition"]):
                        reasoning_score += 0.05  # Shows understanding of filtering
        
        score += min(0.4, reasoning_score)  # Cap reasoning bonus at 0.4
        
        # Penalty for errors
        if execution_metadata["errors"]:
            score -= 0.2 * len(execution_metadata["errors"])
        
        return max(0.0, min(1.0, score))
    
    def _calculate_completeness_score(self, evaluation_result: Dict, task: QueryTask) -> float:
        """Calculate score for data completeness and column matching"""
        score = 0.0
        
        # Check if expected columns are present
        agent_count = evaluation_result.get("agent_result_count", 0)
        expected_count = evaluation_result.get("ground_truth_count", 0)
        
        if agent_count > 0 and expected_count > 0:
            # Bonus for having results
            score += 0.5
            
            # Bonus for reasonable result count
            count_ratio = min(agent_count, expected_count) / max(agent_count, expected_count)
            score += 0.3 * count_ratio
            
            # Check evaluation details for column completeness
            details = evaluation_result.get("details", {})
            if "field_scores" in details:
                field_scores = details["field_scores"]
                if field_scores:
                    avg_field_score = sum(fs.get("matches", 0) / max(fs.get("total", 1), 1) 
                                        for fs in field_scores.values()) / len(field_scores)
                    score += 0.2 * avg_field_score
        
        return min(1.0, max(0.0, score))
    
    def _update_performance_metrics(self, reward: float, evaluation_result: Dict):
        """Update performance tracking metrics"""
        # Add to recent performance (sliding window)
        self.recent_performance.append({
            "reward": reward,
            "success": evaluation_result.get("score", 0) > 0.7,  # Success threshold
            "episode": self.current_episode
        })
        
        # Keep only last 20 episodes for recent performance
        if len(self.recent_performance) > 20:
            self.recent_performance.pop(0)
        
        # Update aggregate metrics
        if len(self.performance_metrics["avg_reward"]) < 100:  # Keep last 100 episodes
            self.performance_metrics["avg_reward"].append(reward)
            self.performance_metrics["success_rate"].append(
                1.0 if evaluation_result.get("score", 0) > 0.7 else 0.0
            )
        else:
            # Sliding window
            self.performance_metrics["avg_reward"].pop(0)
            self.performance_metrics["success_rate"].pop(0)
            self.performance_metrics["avg_reward"].append(reward)
            self.performance_metrics["success_rate"].append(
                1.0 if evaluation_result.get("score", 0) > 0.7 else 0.0
            )
    
    def _check_curriculum_progression(self):
        """Check if agent should advance to next curriculum level"""
        if len(self.recent_performance) < 10:  # Need at least 10 episodes
            return
        
        # Calculate recent success rate at current level
        recent_successes = [p["success"] for p in self.recent_performance[-10:]]
        success_rate = sum(recent_successes) / len(recent_successes)
        
        # Check if ready to advance
        if success_rate >= self.level_up_threshold and self.curriculum_level < 5:
            self.curriculum_level += 1
            self.level_progression.append({
                "episode": self.current_episode,
                "new_level": self.curriculum_level,
                "success_rate": success_rate
            })
            print(f"🎓 Curriculum advanced to Level {self.curriculum_level} (Success rate: {success_rate:.2%})")
        
        # Check if need to step back a level (struggling)
        elif success_rate < 0.3 and self.curriculum_level > 1:
            self.curriculum_level -= 1
            print(f"📉 Curriculum reduced to Level {self.curriculum_level} (Success rate: {success_rate:.2%})")
    
    def _get_performance_summary(self) -> Dict[str, Any]:
        """Get current performance summary"""
        if not self.recent_performance:
            return {"message": "No performance data available"}
        
        recent_rewards = [p["reward"] for p in self.recent_performance]
        recent_successes = [p["success"] for p in self.recent_performance]
        
        return {
            "recent_avg_reward": sum(recent_rewards) / len(recent_rewards),
            "recent_success_rate": sum(recent_successes) / len(recent_successes),
            "total_episodes": self.current_episode,
            "episodes_at_current_level": len([p for p in self.recent_performance 
                                            if p.get("level", self.curriculum_level) == self.curriculum_level])
        }
    
    def _get_curriculum_status(self) -> Dict[str, Any]:
        """Get current curriculum status"""
        return {
            "current_level": self.curriculum_level,
            "level_description": self.task_generator.get_level_description(self.curriculum_level),
            "level_progressions": len(self.level_progression),
            "next_level_threshold": self.level_up_threshold
        }
    
    def get_recent_success_rate(self, window_size: int = 10) -> float:
        """Get success rate over recent episodes"""
        if len(self.recent_performance) < window_size:
            window_size = len(self.recent_performance)
        
        if window_size == 0:
            return 0.0
        
        recent_successes = [p["success"] for p in self.recent_performance[-window_size:]]
        return sum(recent_successes) / len(recent_successes)
    
    def get_schema_adaptation_metrics(self) -> Dict[str, Any]:
        """Get metrics on how well agent adapts to schema changes"""
        if not self.schema_change_episodes:
            return {"message": "No schema changes yet"}
        
        adaptation_scores = []
        
        for schema_change in self.schema_change_episodes:
            change_episode = schema_change["episode"]
            
            # Look at performance in episodes after schema change
            post_change_episodes = [
                ep for ep in self.episode_history 
                if ep["episode"] > change_episode and ep["episode"] <= change_episode + 10
            ]
            
            if post_change_episodes:
                avg_reward = sum(ep["reward"] for ep in post_change_episodes) / len(post_change_episodes)
                adaptation_scores.append(avg_reward)
        
        if adaptation_scores:
            return {
                "schema_changes": len(self.schema_change_episodes),
                "avg_adaptation_score": sum(adaptation_scores) / len(adaptation_scores),
                "adaptation_scores": adaptation_scores
            }
        else:
            return {"message": "Not enough post-change data for analysis"}
    
    def save_episode_history(self, filepath: str):
        """Save complete episode history to file"""
        history_data = {
            "episodes": self.episode_history,
            "schema_changes": self.schema_change_episodes,
            "level_progressions": self.level_progression,
            "performance_summary": self._get_performance_summary(),
            "curriculum_status": self._get_curriculum_status()
        }
        
        with open(filepath, 'w') as f:
            json.dump(history_data, f, indent=2, default=str)
        
        print(f"📊 Episode history saved to {filepath}")
    
    def load_episode_history(self, filepath: str):
        """Load episode history from file"""
        with open(filepath, 'r') as f:
            history_data = json.load(f)
        
        self.episode_history = history_data.get("episodes", [])
        self.schema_change_episodes = history_data.get("schema_changes", [])
        self.level_progressions = history_data.get("level_progressions", [])
        
        # Restore episode counter
        if self.episode_history:
            self.current_episode = max(ep["episode"] for ep in self.episode_history)
        
        print(f"📁 Episode history loaded from {filepath}")
        print(f"   Restored {len(self.episode_history)} episodes")
