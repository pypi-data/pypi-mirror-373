"""
Training demo for Medical SQL RL Environment with maximum_continual integration.

Demonstrates:
- Full training loop integration
- Curriculum learning progression
- Schema randomization during training
- Performance monitoring and evaluation
- Model update with reward feedback
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from medical_sql_rl.environment.medical_rl_env import MedicalSQLEnvironment
from maximum_continual.client import MaximumContinual
from maximum_continual.types import PredictionResponseWithRewardT
import time
import json
from typing import Dict, Any, List


class MedicalSQLTrainer:
    """Trainer class for medical SQL RL with maximum_continual integration"""
    
    def __init__(self, 
                 vllm_endpoint: str = "http://localhost:8000",
                 base_model: str = "meta-llama/Llama-3.1-8B-Instruct",
                 model_id: str = "medical_sql_agent",
                 num_patients: int = 200):
        """
        Initialize trainer
        
        Args:
            vllm_endpoint: vLLM server endpoint
            base_model: Base model to use
            model_id: Unique model identifier
            num_patients: Number of synthetic patients
        """
        
        print("🚀 Initializing Medical SQL RL Trainer")
        
        # Initialize maximum continual client
        print("   Setting up maximum_continual client...")
        self.client = MaximumContinual(
            vllm_endpoint=vllm_endpoint,
            auto_deploy=True
        )
        
        # Initialize model
        print(f"   Initializing model: {model_id}")
        self.model = self.client.init_model(
            base_model=base_model,
            model_id=model_id
        )
        
        # Initialize RL environment
        print("   Setting up medical SQL environment...")
        self.env = MedicalSQLEnvironment(
            num_patients=num_patients,
            seed=42
        )
        
        # Training state
        self.training_history = []
        self.performance_tracking = {
            "rewards": [],
            "success_rates": [],
            "level_progressions": [],
            "schema_changes": []
        }
        
        print("✅ Trainer initialized successfully!")
    
    def train_episodes(self, num_episodes: int = 100, save_frequency: int = 25) -> Dict[str, Any]:
        """
        Train agent for specified number of episodes
        
        Args:
            num_episodes: Number of training episodes
            save_frequency: Save progress every N episodes
            
        Returns:
            Training results summary
        """
        
        print(f"\n🎯 Starting training for {num_episodes} episodes")
        print("=" * 50)
        
        start_time = time.time()
        
        for episode in range(1, num_episodes + 1):
            episode_start = time.time()
            
            # Reset environment for new episode
            observation = self.env.reset()
            
            # Show progress
            if episode % 10 == 0 or episode <= 5:
                task = observation["task"]
                print(f"\nEpisode {episode}/{num_episodes}")
                print(f"  Task: {task['natural_language'][:60]}...")
                print(f"  Level: {task['level']} | Schema: {observation['schema_variant']}")
            
            # Agent generates prediction using tools
            try:
                prediction = self.model.predict(
                    messages=observation['messages'],
                    tools=observation['tools'],
                    max_iterations=5,
                    temperature=0.7
                )
            except Exception as e:
                print(f"   ❌ Prediction failed: {e}")
                # Create dummy response for error handling
                from maximum_continual.types import MessageT, PredictionResponseT
                prediction = PredictionResponseT(
                    final_response={"error": str(e)},
                    messages=[MessageT(role="assistant", content=f"Error: {e}")],
                    metadata={"error": True}
                )
            
            # Environment evaluates and provides reward  
            next_obs, reward, done, info = self.env.step(prediction)
            
            # Update model with reward feedback
            update_data = PredictionResponseWithRewardT(
                prediction=prediction,
                reward=reward
            )
            
            try:
                update_result = self.model.update(update_data)
            except Exception as e:
                print(f"   ⚠️ Model update failed: {e}")
                update_result = {"error": str(e)}
            
            # Track performance
            episode_info = {
                "episode": episode,
                "reward": reward,
                "success": reward > 0.7,
                "task_level": observation["task"]["level"],
                "schema_variant": observation["schema_variant"],
                "processing_time": time.time() - episode_start,
                "update_result": update_result
            }
            
            self.training_history.append(episode_info)
            self._update_performance_tracking(episode_info, info)
            
            # Show results for some episodes
            if episode % 10 == 0 or episode <= 5:
                success_str = "✅" if reward > 0.7 else "❌"
                print(f"  Reward: {reward:.3f} {success_str} | Time: {episode_info['processing_time']:.1f}s")
                
                # Show recent performance
                recent_rewards = [ep["reward"] for ep in self.training_history[-10:]]
                recent_success = [ep["success"] for ep in self.training_history[-10:]]
                if recent_rewards:
                    avg_reward = sum(recent_rewards) / len(recent_rewards)
                    success_rate = sum(recent_success) / len(recent_success)
                    print(f"  Recent 10 episodes: Avg reward {avg_reward:.3f}, Success rate {success_rate:.1%}")
            
            # Save progress periodically
            if episode % save_frequency == 0:
                self._save_training_progress(f"training_checkpoint_ep{episode}.json")
                print(f"  💾 Progress saved at episode {episode}")
        
        total_time = time.time() - start_time
        
        # Generate final results
        results = self._generate_training_summary(num_episodes, total_time)
        
        # Save final results
        self._save_training_progress("training_final_results.json")
        
        print(f"\n🏆 Training completed in {total_time:.1f} seconds!")
        
        return results
    
    def evaluate_performance(self, num_eval_episodes: int = 20) -> Dict[str, Any]:
        """
        Evaluate trained model performance across different scenarios
        
        Args:
            num_eval_episodes: Number of evaluation episodes
            
        Returns:
            Evaluation results
        """
        
        print(f"\n📊 Evaluating model performance over {num_eval_episodes} episodes")
        
        eval_results = {
            "level_performance": {1: [], 2: [], 3: [], 4: [], 5: []},
            "schema_performance": {},
            "overall_metrics": {}
        }
        
        for episode in range(num_eval_episodes):
            # Reset environment
            observation = self.env.reset()
            task = observation["task"]
            schema = observation["schema_variant"]
            
            # Run prediction
            try:
                prediction = self.model.predict(
                    messages=observation['messages'],
                    tools=observation['tools'],
                    max_iterations=5,
                    temperature=0.1  # Lower temperature for evaluation
                )
                
                # Get reward
                _, reward, _, _ = self.env.step(prediction)
                
                # Track by level
                eval_results["level_performance"][task["level"]].append(reward)
                
                # Track by schema
                if schema not in eval_results["schema_performance"]:
                    eval_results["schema_performance"][schema] = []
                eval_results["schema_performance"][schema].append(reward)
                
            except Exception as e:
                print(f"   Evaluation episode {episode} failed: {e}")
                continue
        
        # Calculate summary statistics
        eval_results["overall_metrics"] = self._calculate_eval_metrics(eval_results)
        
        print("📋 Evaluation Results:")
        for level, rewards in eval_results["level_performance"].items():
            if rewards:
                avg_reward = sum(rewards) / len(rewards)
                success_rate = sum(1 for r in rewards if r > 0.7) / len(rewards)
                print(f"  Level {level}: Avg reward {avg_reward:.3f}, Success rate {success_rate:.1%} ({len(rewards)} episodes)")
        
        return eval_results
    
    def demonstrate_schema_robustness(self) -> Dict[str, Any]:
        """Demonstrate agent robustness across schema variations"""
        
        print("\n🎲 Testing Schema Robustness")
        
        # Test same task type across different schemas
        robustness_results = {}
        
        # Force schema changes for testing
        original_schedule = self.env.schema_randomizer.schedule
        self.env.schema_randomizer.schedule = {1: "complete"}  # Change every episode
        
        test_episodes = 6  # Test across different schemas
        
        for episode in range(test_episodes):
            observation = self.env.reset()
            schema = observation["schema_variant"] 
            task = observation["task"]
            
            print(f"  Testing on schema: {schema}")
            
            try:
                prediction = self.model.predict(
                    messages=observation['messages'],
                    tools=observation['tools'],
                    max_iterations=3,
                    temperature=0.1
                )
                
                _, reward, _, info = self.env.step(prediction)
                
                robustness_results[schema] = {
                    "reward": reward,
                    "success": reward > 0.7,
                    "task_level": task["level"],
                    "adaptation_score": reward  # Simple adaptation metric
                }
                
                print(f"    Reward: {reward:.3f} {'✅' if reward > 0.7 else '❌'}")
                
            except Exception as e:
                print(f"    ❌ Failed: {e}")
                robustness_results[schema] = {"error": str(e)}
        
        # Restore original schedule
        self.env.schema_randomizer.schedule = original_schedule
        
        # Calculate robustness metrics
        valid_results = [r for r in robustness_results.values() if "error" not in r]
        if valid_results:
            avg_adaptation = sum(r["reward"] for r in valid_results) / len(valid_results)
            adaptation_success_rate = sum(1 for r in valid_results if r["success"]) / len(valid_results)
            
            print(f"\n📈 Schema Robustness Summary:")
            print(f"  Schemas tested: {len(robustness_results)}")
            print(f"  Average adaptation score: {avg_adaptation:.3f}")
            print(f"  Cross-schema success rate: {adaptation_success_rate:.1%}")
        
        return robustness_results
    
    def _update_performance_tracking(self, episode_info: Dict, env_info: Dict):
        """Update performance tracking metrics"""
        self.performance_tracking["rewards"].append(episode_info["reward"])
        self.performance_tracking["success_rates"].append(episode_info["success"])
        
        # Track level progressions
        if "curriculum_status" in env_info:
            current_level = env_info["curriculum_status"]["current_level"]
            if (not self.performance_tracking["level_progressions"] or 
                self.performance_tracking["level_progressions"][-1]["level"] != current_level):
                self.performance_tracking["level_progressions"].append({
                    "episode": episode_info["episode"],
                    "level": current_level
                })
        
        # Track schema changes
        if "schema_changes" in env_info and env_info["schema_changes"] > 0:
            self.performance_tracking["schema_changes"].append({
                "episode": episode_info["episode"],
                "schema": episode_info["schema_variant"]
            })
    
    def _generate_training_summary(self, num_episodes: int, total_time: float) -> Dict[str, Any]:
        """Generate comprehensive training summary"""
        
        if not self.training_history:
            return {"error": "No training history available"}
        
        rewards = [ep["reward"] for ep in self.training_history]
        successes = [ep["success"] for ep in self.training_history]
        
        # Calculate performance over time
        window_size = 20
        windowed_performance = []
        
        for i in range(window_size, len(rewards) + 1, window_size):
            window_rewards = rewards[max(0, i - window_size):i]
            window_successes = successes[max(0, i - window_size):i]
            
            windowed_performance.append({
                "episode_range": f"{max(1, i - window_size + 1)}-{i}",
                "avg_reward": sum(window_rewards) / len(window_rewards),
                "success_rate": sum(window_successes) / len(window_successes),
                "episodes": len(window_rewards)
            })
        
        summary = {
            "training_config": {
                "num_episodes": num_episodes,
                "total_time_seconds": total_time,
                "avg_time_per_episode": total_time / num_episodes,
                "num_patients": self.env.num_patients
            },
            "overall_performance": {
                "final_avg_reward": sum(rewards[-20:]) / min(20, len(rewards)) if rewards else 0,
                "final_success_rate": sum(successes[-20:]) / min(20, len(successes)) if successes else 0,
                "total_avg_reward": sum(rewards) / len(rewards),
                "total_success_rate": sum(successes) / len(successes),
                "best_reward": max(rewards) if rewards else 0,
                "improvement": self._calculate_improvement(rewards)
            },
            "curriculum_progression": self.performance_tracking["level_progressions"],
            "schema_adaptations": len(self.performance_tracking["schema_changes"]),
            "windowed_performance": windowed_performance
        }
        
        return summary
    
    def _calculate_improvement(self, rewards: List[float]) -> float:
        """Calculate improvement from beginning to end of training"""
        if len(rewards) < 20:
            return 0.0
        
        early_performance = sum(rewards[:10]) / 10
        late_performance = sum(rewards[-10:]) / 10
        
        return late_performance - early_performance
    
    def _calculate_eval_metrics(self, eval_results: Dict) -> Dict[str, Any]:
        """Calculate evaluation metrics from results"""
        all_rewards = []
        
        # Collect all rewards
        for level_rewards in eval_results["level_performance"].values():
            all_rewards.extend(level_rewards)
        
        if not all_rewards:
            return {"error": "No evaluation data"}
        
        return {
            "overall_avg_reward": sum(all_rewards) / len(all_rewards),
            "overall_success_rate": sum(1 for r in all_rewards if r > 0.7) / len(all_rewards),
            "total_episodes": len(all_rewards),
            "reward_std": (sum((r - sum(all_rewards)/len(all_rewards))**2 for r in all_rewards) / len(all_rewards))**0.5
        }
    
    def _save_training_progress(self, filename: str):
        """Save training progress to file"""
        progress_data = {
            "training_history": self.training_history,
            "performance_tracking": self.performance_tracking,
            "environment_state": {
                "current_episode": self.env.current_episode,
                "curriculum_level": self.env.curriculum_level,
                "schema_variant": self.env.db_manager.current_schema.variant_name
            },
            "timestamp": time.time()
        }
        
        try:
            filepath = os.path.join(os.path.dirname(__file__), filename)
            with open(filepath, 'w') as f:
                json.dump(progress_data, f, indent=2, default=str)
        except Exception as e:
            print(f"   ⚠️ Failed to save progress: {e}")


def main():
    """Main training demonstration"""
    
    print("🏥 Medical SQL RL Training Demonstration")
    print("=" * 60)
    
    try:
        # Initialize trainer
        trainer = MedicalSQLTrainer(
            base_model="meta-llama/Llama-3.1-8B-Instruct",  # Adjust based on your setup
            model_id="medical_sql_demo",
            num_patients=100
        )
        
        # Run training
        training_results = trainer.train_episodes(
            num_episodes=50,  # Reduced for demo
            save_frequency=15
        )
        
        print("\n📊 Training Results Summary:")
        print(f"  Final average reward: {training_results['overall_performance']['final_avg_reward']:.3f}")
        print(f"  Final success rate: {training_results['overall_performance']['final_success_rate']:.1%}")
        print(f"  Total improvement: {training_results['overall_performance']['improvement']:.3f}")
        print(f"  Curriculum progressions: {len(training_results['curriculum_progression'])}")
        print(f"  Schema adaptations: {training_results['schema_adaptations']}")
        
        # Evaluate performance
        print("\n" + "="*40)
        eval_results = trainer.evaluate_performance(num_eval_episodes=15)
        
        # Test schema robustness
        print("\n" + "="*40)
        robustness_results = trainer.demonstrate_schema_robustness()
        
        print("\n🎉 Training demonstration completed successfully!")
        print("\nNext Steps:")
        print("- Adjust num_episodes for longer training")
        print("- Modify base_model to use your preferred model")
        print("- Experiment with different environment parameters")
        print("- Analyze saved training logs for detailed insights")
        
    except Exception as e:
        print(f"\n❌ Training failed: {e}")
        import traceback
        traceback.print_exc()
        
        print("\nTroubleshooting:")
        print("- Ensure vLLM server is running on localhost:8000")
        print("- Check that modal backend is deployed")
        print("- Verify maximum_continual installation")
        print("- Make sure all dependencies are installed")


if __name__ == "__main__":
    main()
