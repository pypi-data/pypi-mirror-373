# Medical SQL RL Environment

A comprehensive reinforcement learning environment for training agents to query medical databases using SQL. Features schema randomization and ground-truth based evaluation for robust learning across different database designs.

## 🏥 Overview

This system trains agents to accurately fetch medical data by:
- **Generating synthetic medical databases** with realistic patient, condition, medication, and activity data
- **Randomizing database schemas** every X examples to ensure robustness across different designs
- **Evaluating results against ground truth** rather than expected SQL queries
- **Providing curriculum learning** across 5 difficulty levels
- **Integrating with maximum_continual** for continual learning with LoRA updates

## 🎯 Key Features

### Schema Robustness Training
- **3 schema variants**: Medical clinic, hospital system, healthcare network
- **Automatic randomization**: Minor changes (every 25 episodes), major changes (every 100), complete redesign (every 250)
- **Cross-schema generalization**: Agent learns to adapt to different table/column names and relationships

### Ground Truth Evaluation
- **No expected SQL**: Focuses on correct results, not specific query patterns
- **Multiple evaluation strategies**: Exact match, numerical tolerance, set matching, partial matching
- **Medical context awareness**: Appropriate tolerance for clinical data

### Progressive Difficulty
1. **Level 1**: Basic retrieval (single table SELECT)
2. **Level 2**: Aggregations (COUNT, AVG, GROUP BY)
3. **Level 3**: Joins (multi-table relationships)
4. **Level 4**: Complex analytics (window functions, CTEs)
5. **Level 5**: Natural language interpretation

### Comprehensive Tooling
- **SQL Query Tool**: Execute queries with safety checks and performance monitoring
- **Schema Interface**: Explore database structure and relationships
- **Query Validation**: Syntax checking and optimization suggestions

## 📦 Installation

```bash
# Install dependencies
pip install -r medical_sql_rl/requirements.txt

# Install maximum_continual (if not already installed)
pip install maximum_continual
```

## 🚀 Quick Start

### Basic Usage

```python
from medical_sql_rl.environment.medical_rl_env import MedicalSQLEnvironment

# Initialize environment
env = MedicalSQLEnvironment(num_patients=100, seed=42)

# Reset for new episode
observation = env.reset()

# Get task and tools
task = observation["task"]
tools = observation["tools"]

print(f"Task: {task['natural_language']}")
print(f"Level: {task['level']}")
print(f"Expected columns: {task['expected_columns']}")

# Agent would use tools to explore schema and execute SQL
# See examples/basic_usage.py for complete demo
```

### Training Integration

```python
from medical_sql_rl.environment.medical_rl_env import MedicalSQLEnvironment
from maximum_continual.client import MaximumContinual
from maximum_continual.types import PredictionResponseWithRewardT

# Initialize components
client = MaximumContinual()
model = client.init_model(
    base_model="meta-llama/Llama-3.1-8B-Instruct",
    model_id="medical_sql_agent"
)
env = MedicalSQLEnvironment(num_patients=200)

# Training loop
for episode in range(1000):
    # Reset environment
    observation = env.reset()
    
    # Agent generates prediction using tools
    prediction = model.predict(
        messages=observation['messages'],
        tools=observation['tools']
    )
    
    # Environment evaluates and provides reward
    _, reward, done, info = env.step(prediction)
    
    # Update model with reward feedback
    update_data = PredictionResponseWithRewardT(
        prediction=prediction,
        reward=reward
    )
    model.update(update_data)
```

## 📊 Database Schema

### Core Tables

The system generates realistic medical data across 7 core tables:

- **patients**: Demographics and contact information
- **conditions**: Medical diagnoses with ICD-10 codes
- **medications**: Prescriptions with dosage and status
- **vitals**: Blood pressure, heart rate, temperature measurements
- **appointments**: Visit scheduling and outcomes
- **activity_data**: Daily steps, sleep, calories from wearables
- **lab_results**: Laboratory test results with reference ranges

### Schema Variations

**Medical Clinic (medical_clinic_v1)**:
```sql
CREATE TABLE patients (
    patient_id INTEGER PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    date_of_birth DATE,
    gender VARCHAR(10)
);
```

**Hospital System (hospital_system_v1)**:
```sql
CREATE TABLE patient_records (
    id INTEGER PRIMARY KEY,
    fname VARCHAR(50),
    lname VARCHAR(50),
    birth_date DATE,
    sex VARCHAR(1)
);
```

**Healthcare Network (healthcare_network_v1)**:
```sql
CREATE TABLE individuals (
    person_id INTEGER PRIMARY KEY,
    given_name VARCHAR(50),
    family_name VARCHAR(50),
    date_of_birth DATE,
    gender_code VARCHAR(10)
);
```

## 🎲 Schema Randomization

The system automatically varies schemas to ensure robustness:

### Minor Variations (Every 25 episodes)
- Column name changes: `first_name` → `fname` → `given_name`
- Data type adjustments: `DATE` → `TIMESTAMP`, `FLOAT` → `DECIMAL`
- 20-40% of columns affected

### Major Variations (Every 100 episodes)  
- Table relationship modifications
- Addition/removal of optional columns
- Foreign key structure changes

### Complete Redesign (Every 250 episodes)
- Switch to entirely different schema variant
- Different medical domain focus
- New table and column naming conventions

## 🏆 Evaluation System

### Multi-Dimensional Rewards

**Result Accuracy (50%)**:
- Exact match for categorical data
- Numerical tolerance for aggregations
- Set matching for unordered results

**Query Execution (20%)**:
- SQL syntax correctness
- Runtime performance
- Error handling

**Process Quality (20%)**:
- Schema exploration usage
- Logical reasoning steps
- Tool utilization

**Data Completeness (10%)**:
- Expected columns present
- Appropriate result counts
- Edge case handling

### Evaluation Strategies

```python
# Exact matching for simple queries
{"evaluation_type": "exact_match"}

# Numerical tolerance for aggregations
{"evaluation_type": "numerical_tolerance", "tolerance": 0.01}

# Order-independent comparison
{"evaluation_type": "set_match"}

# Precision/recall for complex queries
{"evaluation_type": "partial_match"}
```

## 📚 Examples

### Run Basic Demo
```bash
cd medical_sql_rl/examples
python basic_usage.py
```

### Full Training Demo
```bash
cd medical_sql_rl/examples  
python training_demo.py
```

## 📈 Performance Metrics

The system tracks comprehensive metrics:

### Training Progress
- **Success Rate**: Percentage of tasks completed successfully
- **Average Reward**: Multi-dimensional reward score
- **Curriculum Progression**: Advancement through difficulty levels
- **Schema Adaptation**: Performance after schema changes

### Robustness Measures
- **Cross-Schema Transfer**: Performance on first exposure to new schemas
- **Adaptation Speed**: Recovery time after schema changes
- **Generalization**: Held-out test performance

### Quality Indicators
- **Query Efficiency**: Execution time and resource usage
- **Tool Usage**: Appropriate use of schema exploration
- **Error Recovery**: Handling of invalid queries and edge cases

## 🔧 Configuration

### Environment Settings
```python
env = MedicalSQLEnvironment(
    num_patients=100,                    # Database size
    randomization_schedule={             # Schema change frequency
        25: "minor",
        100: "major", 
        250: "complete"
    },
    seed=42                             # Reproducibility
)
```

### Training Parameters
```python
trainer.train_episodes(
    num_episodes=1000,                  # Training length
    save_frequency=25,                  # Checkpoint frequency
    curriculum_threshold=0.8            # Level advancement threshold
)
```

## 🎯 Success Criteria

### Performance Targets
- **Level 1 (Basic)**: 95% accuracy within 100 episodes
- **Level 2 (Aggregation)**: 90% accuracy within 200 episodes
- **Level 3 (Joins)**: 85% accuracy within 300 episodes
- **Level 4 (Complex)**: 80% accuracy within 500 episodes
- **Level 5 (Natural Language)**: 75% accuracy within 1000 episodes

### Robustness Criteria
- **Minor Schema Changes**: <5% accuracy drop
- **Major Schema Changes**: <20% accuracy drop
- **Complete Redesign**: <40% initial drop, recovery within 50 episodes
- **Cross-Schema Transfer**: >60% accuracy on first exposure

## 🚀 Advanced Usage

### Custom Query Tasks
```python
from medical_sql_rl.evaluation.query_tasks import QueryTask

custom_task = QueryTask(
    task_id="custom_001",
    level=3,
    category="medication_analysis",
    description="Find patients with drug interactions",
    natural_language="Show patients taking multiple medications that might interact",
    ground_truth_result=[...],
    evaluation_config={"evaluation_type": "set_match"}
)
```

### Custom Schema Variants
```python
from medical_sql_rl.database.schema import DatabaseSchema, Table, Column, DataType

custom_schema = DatabaseSchema(
    variant_name="custom_clinic_v1",
    description="Custom medical clinic schema",
    tables=[
        Table(
            name="patients",
            columns=[
                Column("id", DataType.INTEGER, primary_key=True),
                # ... additional columns
            ]
        )
    ]
)
```

## 📝 Project Structure

```
medical_sql_rl/
├── README.md                    # This file
├── requirements.txt             # Dependencies
├── database/
│   ├── schema.py               # Schema definitions
│   ├── connection.py           # DuckDB management
│   ├── synthetic_generator.py  # Data generation
│   └── schema_randomizer.py    # Schema variations
├── tools/
│   └── sql_tools.py           # Agent tools
├── environment/
│   └── medical_rl_env.py      # Main RL environment
├── evaluation/
│   ├── result_evaluator.py    # Result comparison
│   └── query_tasks.py         # Task definitions
└── examples/
    ├── basic_usage.py         # Basic demo
    └── training_demo.py       # Full training
```

## 🤝 Contributing

This medical SQL RL environment provides a robust foundation for training agents on diverse database schemas. Key areas for extension:

- **Additional medical domains** (cardiology, oncology, etc.)
- **Real anonymized datasets** for validation
- **Multi-database support** (PostgreSQL, MySQL)
- **Advanced evaluation metrics** for clinical relevance
- **Privacy-preserving techniques** for sensitive data

## 📄 License

This project integrates with the maximum_continual framework and follows its licensing terms.

---

🏥 **Ready to train robust medical SQL agents!** Start with `examples/basic_usage.py` and progress to full training with `examples/training_demo.py`.
