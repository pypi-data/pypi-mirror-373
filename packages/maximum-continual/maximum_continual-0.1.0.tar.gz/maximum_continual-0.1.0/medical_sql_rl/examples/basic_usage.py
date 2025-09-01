"""
Basic usage example for the Medical SQL RL Environment.

Demonstrates:
- Environment setup and initialization
- Single episode execution
- Schema exploration
- Task generation and evaluation
- Basic metrics and reporting
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from medical_sql_rl.environment.medical_rl_env import MedicalSQLEnvironment
from medical_sql_rl.evaluation.query_tasks import QueryTaskGenerator
from maximum_continual.types import MessageT, PredictionResponseT, ToolCallT, ToolCallFunctionT
import json


def create_mock_agent_response(sql_query: str, use_schema_tool: bool = True) -> PredictionResponseT:
    """
    Create a mock agent response for testing purposes
    In a real scenario, this would come from the maximum_continual agent
    """
    messages = []
    
    # Add assistant message with reasoning
    reasoning_message = MessageT(
        role="assistant",
        content=f"""I need to answer this medical question by querying the database. Let me start by exploring the database schema to understand the available tables and relationships.

My approach:
1. First, I'll explore the database schema to understand table structures
2. Then I'll write an appropriate SQL query to answer the question
3. Finally, I'll execute the query and analyze the results

Let me start by examining the database schema."""
    )
    messages.append(reasoning_message)
    
    if use_schema_tool:
        # Add schema exploration
        schema_tool_call = ToolCallT(
            id="call_1",
            function=ToolCallFunctionT(
                name="database_schema",
                arguments='{"action": "get_schema_summary"}'
            )
        )
        
        schema_message = MessageT(
            role="assistant", 
            content="Let me explore the database schema first.",
            tool_calls=[schema_tool_call]
        )
        messages.append(schema_message)
        
        # Mock schema response
        schema_response = MessageT(
            role="tool",
            content='{"success": true, "action": "get_schema_summary", "data": {"schema_variant": "medical_clinic_v1", "table_count": 7, "total_rows": 500}}',
            tool_call_id="call_1"
        )
        messages.append(schema_response)
    
    # Add SQL query execution
    sql_tool_call = ToolCallT(
        id="call_2",
        function=ToolCallFunctionT(
            name="sql_query",
            arguments=json.dumps({"query": sql_query})
        )
    )
    
    sql_message = MessageT(
        role="assistant",
        content=f"Now I'll execute the SQL query: {sql_query}",
        tool_calls=[sql_tool_call]
    )
    messages.append(sql_message)
    
    # Mock SQL response (this would normally come from actual execution)
    sql_response = MessageT(
        role="tool",
        content=json.dumps({
            "success": True,
            "results": [
                {"patient_id": 1, "first_name": "John", "last_name": "Doe", "date_of_birth": "1980-05-15"},
                {"patient_id": 2, "first_name": "Jane", "last_name": "Smith", "date_of_birth": "1975-03-22"}
            ],
            "row_count": 2,
            "execution_time_ms": 45.2
        }),
        tool_call_id="call_2"
    )
    messages.append(sql_response)
    
    return PredictionResponseT(
        final_response={"content": "Query executed successfully, found 2 patients."},
        messages=messages,
        metadata={"model_id": "mock_agent", "iterations": 1}
    )


def demonstrate_basic_usage():
    """Demonstrate basic usage of the Medical SQL RL Environment"""
    
    print("🏥 Medical SQL RL Environment - Basic Usage Demo")
    print("=" * 60)
    
    # Initialize the environment
    print("\n1. Initializing Environment...")
    env = MedicalSQLEnvironment(
        num_patients=50,  # Smaller dataset for demo
        seed=42
    )
    
    print("✅ Environment initialized successfully!")
    print(f"   Schema: {env.db_manager.current_schema.variant_name}")
    print(f"   Tables: {len(env.db_manager.list_tables())}")
    
    # Reset environment to get first task
    print("\n2. Generating Task...")
    observation = env.reset()
    
    current_task = observation["task"]
    print("📋 Generated Task:")
    print(f"   ID: {current_task['task_id']}")
    print(f"   Level: {current_task['level']}")
    print(f"   Category: {current_task['category']}")
    print(f"   Question: {current_task['natural_language']}")
    print(f"   Expected columns: {', '.join(current_task['expected_columns'])}")
    
    # Show available tools
    print("\n3. Available Tools:")
    for i, tool in enumerate(observation["tools"], 1):
        print(f"   {i}. {tool.name}: {tool.description[:60]}...")
    
    # Demonstrate schema exploration
    print("\n4. Exploring Database Schema...")
    schema_tool = observation["tools"][1]  # DatabaseSchemaInterface
    
    # List tables
    table_info = schema_tool.forward("list_tables")
    print(f"   Tables found: {table_info['data']['tables']}")
    
    # Describe a table
    if table_info["success"] and table_info["data"]["tables"]:
        first_table = table_info["data"]["tables"][0]
        table_details = schema_tool.forward("describe_table", first_table)
        print(f"   {first_table} table:")
        if table_details["success"]:
            for col in table_details["data"]["columns"][:3]:  # Show first 3 columns
                print(f"     - {col['name']} ({col['type']}) {'[PK]' if col['primary_key'] else ''}")
    
    # Create mock agent response
    print("\n5. Simulating Agent Response...")
    
    # Create a simple SQL query based on the task level
    if current_task["level"] == 1:
        # Basic patient lookup
        mock_query = "SELECT patient_id, first_name, last_name, date_of_birth FROM patients LIMIT 5"
    elif current_task["level"] == 2:
        # Aggregation
        mock_query = "SELECT COUNT(*) as patient_count FROM patients"
    else:
        # Default query
        mock_query = "SELECT * FROM patients LIMIT 3"
    
    agent_response = create_mock_agent_response(mock_query, use_schema_tool=True)
    print(f"   Generated mock SQL query: {mock_query}")
    print(f"   Agent used {len(agent_response.messages)} messages")
    
    # Process agent response through environment
    print("\n6. Processing Agent Response...")
    next_obs, reward, done, info = env.step(agent_response)
    
    print(f"✅ Episode completed!")
    print(f"   Reward: {reward:.3f}")
    print(f"   Success: {'Yes' if reward > 0.7 else 'No'}")
    print(f"   Episode done: {done}")
    
    # Show detailed results
    print("\n7. Detailed Results:")
    episode_record = info["episode_record"]
    evaluation_result = episode_record["evaluation_result"]
    
    print(f"   Evaluation type: {evaluation_result['evaluation_type']}")
    print(f"   Score: {evaluation_result['score']:.3f}")
    print(f"   Agent result count: {evaluation_result.get('agent_result_count', 0)}")
    print(f"   Expected result count: {evaluation_result.get('ground_truth_count', 0)}")
    print(f"   Processing time: {episode_record['processing_time_ms']:.1f}ms")
    
    # Show execution metadata
    exec_metadata = episode_record["execution_metadata"]
    print(f"   SQL executed: {'Yes' if exec_metadata['sql_executed_successfully'] else 'No'}")
    print(f"   Schema exploration used: {'Yes' if exec_metadata['schema_exploration_used'] else 'No'}")
    print(f"   Tools used: {', '.join(exec_metadata['tool_usage'])}")
    
    # Performance summary
    print("\n8. Performance Summary:")
    perf_summary = info["performance_summary"]
    print(f"   Total episodes: {perf_summary['total_episodes']}")
    print(f"   Recent average reward: {perf_summary['recent_avg_reward']:.3f}")
    print(f"   Recent success rate: {perf_summary['recent_success_rate']:.1%}")
    
    # Curriculum status
    print("\n9. Curriculum Status:")
    curriculum = info["curriculum_status"]
    print(f"   Current level: {curriculum['current_level']}")
    print(f"   Level description: {curriculum['level_description']}")
    
    return env


def demonstrate_multiple_episodes():
    """Demonstrate running multiple episodes with different task types"""
    
    print("\n\n🔄 Multiple Episodes Demo")
    print("=" * 40)
    
    env = MedicalSQLEnvironment(num_patients=30, seed=123)
    
    # Run 5 episodes with different queries
    queries = [
        "SELECT COUNT(*) as total_patients FROM patients",
        "SELECT condition_name, COUNT(*) as count FROM conditions GROUP BY condition_name",
        "SELECT patient_id, first_name, last_name FROM patients WHERE gender = 'Male'",
        "SELECT medication_name, dosage FROM medications WHERE status = 'active'",
        "SELECT appointment_type, COUNT(*) as count FROM appointments GROUP BY appointment_type"
    ]
    
    episode_results = []
    
    for i, query in enumerate(queries, 1):
        print(f"\n--- Episode {i} ---")
        
        # Reset for new episode
        obs = env.reset()
        task = obs["task"]
        print(f"Task: {task['natural_language'][:50]}...")
        
        # Create agent response
        agent_response = create_mock_agent_response(query, use_schema_tool=(i % 2 == 1))
        
        # Process episode
        _, reward, _, info = env.step(agent_response)
        
        episode_results.append({
            "episode": i,
            "query": query,
            "reward": reward,
            "success": reward > 0.7,
            "task_level": task["level"]
        })
        
        print(f"Reward: {reward:.3f} | Success: {'Yes' if reward > 0.7 else 'No'}")
    
    # Summary
    print(f"\n📊 Summary of {len(episode_results)} episodes:")
    avg_reward = sum(r["reward"] for r in episode_results) / len(episode_results)
    success_rate = sum(r["success"] for r in episode_results) / len(episode_results)
    
    print(f"   Average reward: {avg_reward:.3f}")
    print(f"   Success rate: {success_rate:.1%}")
    print(f"   Performance by level:")
    
    # Group by level
    level_performance = {}
    for result in episode_results:
        level = result["task_level"]
        if level not in level_performance:
            level_performance[level] = []
        level_performance[level].append(result["reward"])
    
    for level, rewards in level_performance.items():
        avg_level_reward = sum(rewards) / len(rewards)
        print(f"     Level {level}: {avg_level_reward:.3f} ({len(rewards)} episodes)")


def demonstrate_schema_variation():
    """Demonstrate schema randomization functionality"""
    
    print("\n\n🎲 Schema Variation Demo")
    print("=" * 35)
    
    # Create environment with frequent schema changes for demo
    env = MedicalSQLEnvironment(
        num_patients=20,
        randomization_schedule={2: "minor", 4: "major", 6: "complete"},  # Change every 2 episodes
        seed=456
    )
    
    print("Schema randomization schedule: every 2 episodes")
    
    # Run several episodes to trigger schema changes
    for episode in range(1, 8):
        obs = env.reset()
        
        current_schema = obs["schema_variant"]
        task = obs["task"]
        
        print(f"\nEpisode {episode}:")
        print(f"  Schema: {current_schema}")
        print(f"  Task Level: {task['level']}")
        
        # Simple query for each episode
        agent_response = create_mock_agent_response(
            "SELECT COUNT(*) as count FROM patients", 
            use_schema_tool=False
        )
        
        _, reward, _, info = env.step(agent_response)
        print(f"  Reward: {reward:.3f}")
        
        # Check if schema changed
        if episode > 1:
            prev_schema = getattr(demonstrate_schema_variation, 'prev_schema', None)
            if prev_schema and prev_schema != current_schema:
                print(f"  🔄 Schema changed from {prev_schema} to {current_schema}")
        
        demonstrate_schema_variation.prev_schema = current_schema
    
    # Show schema adaptation metrics
    adaptation_metrics = env.get_schema_adaptation_metrics()
    if "schema_changes" in adaptation_metrics:
        print(f"\n📈 Schema Adaptation Metrics:")
        print(f"   Total schema changes: {adaptation_metrics['schema_changes']}")
        print(f"   Average adaptation score: {adaptation_metrics['avg_adaptation_score']:.3f}")


if __name__ == "__main__":
    try:
        # Run basic demo
        env = demonstrate_basic_usage()
        
        # Run multiple episodes demo
        demonstrate_multiple_episodes()
        
        # Run schema variation demo
        demonstrate_schema_variation()
        
        print("\n\n🎉 All demos completed successfully!")
        print("\nNext steps:")
        print("- See training_demo.py for full training loop integration")
        print("- Modify queries in create_mock_agent_response() to test different scenarios")
        print("- Adjust environment parameters to experiment with different settings")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        print("\nTroubleshooting:")
        print("- Ensure all dependencies are installed (pip install -r requirements.txt)")
        print("- Check that DuckDB is available")
        print("- Verify all module imports are correct")
