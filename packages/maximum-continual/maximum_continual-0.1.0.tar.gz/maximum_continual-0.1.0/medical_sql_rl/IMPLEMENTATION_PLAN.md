# Medical SQL RL Environment - Implementation Plan

## Overview

This document outlines the comprehensive plan for creating a Reinforcement Learning environment that trains the maximum_continual agent to accurately fetch medical data using SQL queries on synthetic databases.

## Goals

The primary objective is to train an agent to correctly interpret and execute medical data queries such as:
- "All the conditions someone has"
- "All the medications someone has" 
- "A daily average of step count correlated with doctor visits"
- More complex analytical queries involving joins, aggregations, and correlations

## Architecture Overview

### 1. System Components

```
medical_sql_rl/
├── IMPLEMENTATION_PLAN.md          # This document
├── environment/                    # RL Environment
│   ├── __init__.py
│   ├── medical_rl_env.py          # Main RL environment class
│   └── reward_calculator.py       # Reward computation logic
├── database/                       # Database components  
│   ├── __init__.py
│   ├── synthetic_generator.py     # Generate synthetic medical data
│   ├── schema.py                  # Database schema definitions
│   └── queries.py                 # Ground truth queries and expected results
├── tools/                         # Custom tools for agent
│   ├── __init__.py
│   └── sql_query_tool.py         # SQL querying tool for DuckDB
├── evaluation/                    # Evaluation and metrics
│   ├── __init__.py
│   ├── metrics.py                # Evaluation metrics
│   └── test_cases.py             # Test case definitions
├── examples/                      # Usage examples and demos
│   ├── __init__.py
│   ├── basic_training.py         # Basic training example
│   └── evaluation_demo.py        # Evaluation demonstration
└── requirements.txt              # Additional dependencies
```

### 2. Core Design Principles

1. **Realistic Medical Data**: Synthetic databases mirror real medical database structures
2. **Progressive Complexity**: Start simple, gradually introduce more complex scenarios
3. **Robust Evaluation**: Multiple metrics to assess query accuracy and reasoning
4. **Integration**: Seamless integration with existing maximum_continual framework
5. **Extensibility**: Easy to add new medical domains and query types

## Database Design

### 3. Synthetic Medical Database Schema

We'll create multiple interconnected tables representing a realistic medical system:

#### Core Tables:

1. **patients** - Patient demographics and basic information
```sql
CREATE TABLE patients (
    patient_id INTEGER PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    date_of_birth DATE,
    gender VARCHAR(10),
    phone VARCHAR(15),
    email VARCHAR(100),
    address VARCHAR(200),
    insurance_id VARCHAR(50),
    created_at TIMESTAMP
);
```

2. **conditions** - Medical conditions/diagnoses
```sql
CREATE TABLE conditions (
    condition_id INTEGER PRIMARY KEY,
    patient_id INTEGER,
    condition_name VARCHAR(100),
    icd_10_code VARCHAR(10),
    diagnosis_date DATE,
    severity VARCHAR(20),
    status VARCHAR(20), -- active, resolved, chronic
    diagnosed_by INTEGER, -- doctor_id
    notes TEXT,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
);
```

3. **medications** - Prescription and medication data
```sql
CREATE TABLE medications (
    medication_id INTEGER PRIMARY KEY,
    patient_id INTEGER,
    medication_name VARCHAR(100),
    generic_name VARCHAR(100),
    dosage VARCHAR(50),
    frequency VARCHAR(50),
    prescribed_date DATE,
    start_date DATE,
    end_date DATE,
    prescribed_by INTEGER, -- doctor_id
    status VARCHAR(20), -- active, discontinued, completed
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
);
```

4. **vitals** - Vital signs and measurements
```sql
CREATE TABLE vitals (
    vital_id INTEGER PRIMARY KEY,
    patient_id INTEGER,
    measurement_date TIMESTAMP,
    height_cm FLOAT,
    weight_kg FLOAT,
    blood_pressure_systolic INTEGER,
    blood_pressure_diastolic INTEGER,
    heart_rate INTEGER,
    temperature_celsius FLOAT,
    recorded_by INTEGER,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
);
```

5. **appointments** - Doctor visits and appointments
```sql
CREATE TABLE appointments (
    appointment_id INTEGER PRIMARY KEY,
    patient_id INTEGER,
    doctor_id INTEGER,
    appointment_date TIMESTAMP,
    appointment_type VARCHAR(50),
    duration_minutes INTEGER,
    status VARCHAR(20), -- scheduled, completed, cancelled, no-show
    notes TEXT,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
);
```

6. **activity_data** - Daily activity tracking (steps, sleep, etc.)
```sql
CREATE TABLE activity_data (
    activity_id INTEGER PRIMARY KEY,
    patient_id INTEGER,
    date DATE,
    step_count INTEGER,
    sleep_hours FLOAT,
    calories_burned INTEGER,
    active_minutes INTEGER,
    heart_rate_avg INTEGER,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
);
```

7. **lab_results** - Laboratory test results
```sql
CREATE TABLE lab_results (
    lab_result_id INTEGER PRIMARY KEY,
    patient_id INTEGER,
    test_name VARCHAR(100),
    test_code VARCHAR(20),
    result_value FLOAT,
    result_unit VARCHAR(20),
    reference_range VARCHAR(50),
    status VARCHAR(20), -- normal, abnormal, critical
    test_date TIMESTAMP,
    ordered_by INTEGER,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
);
```

#### Supporting Tables:

8. **doctors** - Healthcare provider information
9. **hospitals** - Hospital/clinic information  
10. **insurance** - Insurance provider data
11. **medical_history** - Historical medical events

### 4. Data Generation Strategy

The synthetic data generator will:
- Create realistic patient populations with diverse demographics
- Generate plausible medical conditions with proper ICD-10 codes
- Create medication regimens that make clinical sense
- Generate correlated activity and health data
- Ensure referential integrity across all tables
- Include edge cases and outliers for robust testing

### 4.1. Database Schema Randomization Strategy

To ensure agent robustness across different database designs, the system will randomize schema every X examples:

#### Schema Variation Types:

1. **Column Name Variations**:
   ```sql
   -- Variant A
   CREATE TABLE patients (patient_id, first_name, last_name, dob, gender, phone_number, email_address)
   
   -- Variant B  
   CREATE TABLE patient_records (id, fname, lname, birth_date, sex, contact_phone, contact_email)
   
   -- Variant C
   CREATE TABLE individuals (person_id, given_name, family_name, date_of_birth, gender_code, telephone, email)
   ```

2. **Table Structure Variations**:
   - Normalized vs denormalized designs
   - Different foreign key relationships
   - Composite vs single-column primary keys
   - Optional vs required fields

3. **Data Type Variations**:
   - DATE vs TIMESTAMP vs VARCHAR for dates
   - INTEGER vs VARCHAR for IDs
   - FLOAT vs DECIMAL for measurements
   - JSON vs separate columns for complex data

4. **Relationship Variations**:
   - Direct foreign keys vs junction tables
   - One-to-many vs many-to-many relationships
   - Self-referencing relationships (e.g., patient referrals)

#### Randomization Schedule:
- **Every 25 examples**: Minor variations (column names, data types)
- **Every 100 examples**: Major structural changes (table relationships)
- **Every 250 examples**: Complete schema redesign with different medical domain focus

#### Schema Variant Examples:

```python
SCHEMA_VARIANTS = {
    "medical_clinic_v1": {
        "patients": ["patient_id", "first_name", "last_name", "dob", "gender"],
        "conditions": ["condition_id", "patient_id", "diagnosis", "date_diagnosed"],
        "medications": ["med_id", "patient_id", "drug_name", "prescribed_date"]
    },
    "hospital_system_v1": {
        "patient_records": ["id", "fname", "lname", "birth_date", "sex"],
        "medical_conditions": ["record_id", "patient_record_id", "condition_name", "diagnosis_timestamp"],
        "prescriptions": ["prescription_id", "patient_record_id", "medication", "prescription_date"]
    },
    "healthcare_network_v1": {
        "individuals": ["person_id", "given_name", "family_name", "date_of_birth", "gender_code"],
        "health_issues": ["issue_id", "individual_id", "issue_description", "identified_on"],
        "therapeutic_agents": ["agent_id", "individual_id", "agent_name", "therapy_start"]
    }
}
```

## RL Environment Design

### 5. MedicalSQLEnvironment Class

The core RL environment will implement:

```python
class MedicalSQLEnvironment:
    def __init__(self, db_path: str, query_set: List[QueryTask]):
        self.db = duckdb.connect(db_path)
        self.query_tasks = query_set
        self.current_task = None
        self.agent = None
        
    def reset(self) -> Dict[str, Any]:
        """Reset environment and return initial observation"""
        
    def step(self, agent_response: PredictionResponseT) -> Tuple[Dict, float, bool, Dict]:
        """Process agent action and return (observation, reward, done, info)"""
        
    def evaluate_response(self, agent_result: List[Dict], ground_truth_result: List[Dict]) -> float:
        """Calculate reward based on result accuracy against ground truth"""
        
    def randomize_schema(self, episode_number: int) -> None:
        """Randomize database schema based on episode number and variation schedule"""
```

### 6. Query Task Types

#### Level 1: Basic Retrieval
- Single table queries
- Simple WHERE clauses
- Basic SELECT statements

#### Level 2: Aggregation and Grouping  
- COUNT, SUM, AVG operations
- GROUP BY clauses
- HAVING conditions

#### Level 3: Joins and Relationships
- INNER/LEFT JOIN operations
- Multi-table queries
- Foreign key relationships

#### Level 4: Complex Analytics
- Window functions
- CTEs (Common Table Expressions)
- Complex correlations and statistical analysis

#### Level 5: Natural Language to SQL
- Ambiguous natural language queries
- Contextual understanding
- Multi-step reasoning

### 7. Example Query Tasks

```python
QUERY_TASKS = [
    {
        "id": 1,
        "level": 1,
        "description": "Find all conditions for patient ID 12345",
        "natural_language": "What medical conditions does patient 12345 have?",
        "ground_truth_result": [
            {"condition_name": "Type 2 Diabetes", "diagnosis_date": "2020-03-15", "severity": "moderate"},
            {"condition_name": "Hypertension", "diagnosis_date": "2019-08-22", "severity": "mild"},
            {"condition_name": "Obesity", "diagnosis_date": "2021-01-10", "severity": "moderate"}
        ],
        "evaluation_type": "exact_match",
        "result_columns": ["condition_name", "diagnosis_date", "severity"]
    },
    {
        "id": 2, 
        "level": 2,
        "description": "Average daily steps for patients with diabetes",
        "natural_language": "What's the average daily step count for patients diagnosed with diabetes?",
        "ground_truth_result": [
            {"avg_steps": 6847.23}
        ],
        "evaluation_type": "numerical_tolerance",
        "tolerance": 0.01,  # 1% tolerance
        "result_columns": ["avg_steps"]
    },
    {
        "id": 3,
        "level": 4,
        "description": "Correlation between doctor visits and step count",
        "natural_language": "Show me the daily average step count correlated with doctor visits",
        "ground_truth_result": [
            {"visit_status": "visit_day", "avg_steps": 5234.12},
            {"visit_status": "no_visit", "avg_steps": 7891.45}
        ],
        "evaluation_type": "set_match",  # Order doesn't matter
        "tolerance": 0.02,
        "result_columns": ["visit_status", "avg_steps"]
    }
]
```

## Tool Integration

### 8. SQL Query Tool

A custom tool that integrates with the maximum_continual framework:

```python
class SQLQueryTool(Tool):
    """Tool for executing SQL queries against the medical database"""
    
    def __init__(self, db_connection):
        self.name = "sql_query"
        self.description = "Execute SQL queries against the medical database"
        self.db = db_connection
        
    def execute(self, query: str) -> Dict[str, Any]:
        """Execute SQL query and return results with metadata"""
```

### 9. Database Schema Tool

A tool that provides schema information to help the agent understand table structures:

```python
class DatabaseSchemaInterface(Tool):
    """Tool for exploring database schema and relationships"""
    
    def execute(self, action: str, table_name: str = None) -> Dict[str, Any]:
        """Actions: 'list_tables', 'describe_table', 'show_relationships'"""
```

## Reward System

### 10. Multi-dimensional Reward Function

The reward system evaluates multiple aspects based purely on results and process:

1. **Result Accuracy (50%)**:
   - Exact match for categorical data
   - Numerical tolerance for aggregations (configurable per task)
   - Set matching for unordered results
   - Precision and recall for partial matches

2. **Query Execution Success (20%)**:
   - SQL syntax correctness
   - No runtime errors
   - Reasonable execution time (<10 seconds)

3. **Process Quality (20%)**:
   - Proper use of schema exploration tools
   - Logical reasoning steps in code execution
   - Graceful error handling and recovery

4. **Data Completeness (10%)**:
   - All expected columns present
   - Appropriate data types in results
   - Handling of edge cases and null values

### 11. Result Matching Strategies

```python
class ResultEvaluator:
    def evaluate_result(self, agent_result: List[Dict], 
                       ground_truth: List[Dict],
                       evaluation_config: Dict) -> float:
        
        eval_type = evaluation_config.get("evaluation_type", "exact_match")
        
        if eval_type == "exact_match":
            return self._exact_match_score(agent_result, ground_truth)
        elif eval_type == "numerical_tolerance":
            tolerance = evaluation_config.get("tolerance", 0.01)
            return self._numerical_tolerance_score(agent_result, ground_truth, tolerance)
        elif eval_type == "set_match":
            return self._set_match_score(agent_result, ground_truth)
        elif eval_type == "partial_match":
            return self._partial_match_score(agent_result, ground_truth)
    
    def _exact_match_score(self, agent_result, ground_truth):
        """Perfect match required"""
        return 1.0 if agent_result == ground_truth else 0.0
    
    def _numerical_tolerance_score(self, agent_result, ground_truth, tolerance):
        """Allow numerical differences within tolerance"""
        # Implementation for numerical comparison with tolerance
    
    def _set_match_score(self, agent_result, ground_truth):  
        """Order doesn't matter, but all items must match"""
        # Implementation for unordered set comparison
    
    def _partial_match_score(self, agent_result, ground_truth):
        """Calculate precision/recall for partial matches"""
        # Implementation for partial matching with precision/recall

def calculate_reward(agent_result: List[Dict], 
                    ground_truth_result: List[Dict],
                    evaluation_config: Dict,
                    execution_metadata: Dict) -> float:
    
    # Primary score: result accuracy
    result_evaluator = ResultEvaluator()
    accuracy_score = result_evaluator.evaluate_result(
        agent_result, ground_truth_result, evaluation_config
    )
    
    # Execution success bonus/penalty
    execution_score = 1.0 if execution_metadata.get("sql_executed_successfully") else 0.0
    execution_time = execution_metadata.get("execution_time_seconds", 0)
    time_penalty = max(0, min(1, (10 - execution_time) / 10))  # Penalty if >10 seconds
    execution_score *= time_penalty
    
    # Process quality score
    process_score = evaluate_reasoning_process(execution_metadata)
    
    # Data completeness score  
    completeness_score = evaluate_data_completeness(agent_result, evaluation_config)
    
    return (0.5 * accuracy_score + 
            0.2 * execution_score + 
            0.2 * process_score + 
            0.1 * completeness_score)
```

## Evaluation Framework

### 12. Metrics and Benchmarks

1. **Task Success Rate**: Percentage of queries returning correct results
2. **Progressive Learning**: Improvement across difficulty levels
3. **Generalization**: Performance on unseen query types
4. **Robustness**: Handling of edge cases and malformed queries
5. **Efficiency**: Query execution time and resource usage

### 13. Evaluation Pipeline

```python
class MedicalSQLEvaluator:
    def __init__(self, test_cases: List[QueryTask]):
        self.test_cases = test_cases
        
    def evaluate_model(self, model: MaximumContinualModel) -> Dict[str, float]:
        """Comprehensive evaluation across all test cases"""
        
    def generate_report(self, results: Dict) -> str:
        """Generate detailed evaluation report"""
```

## Training Strategy

### 14. Curriculum Learning

1. **Phase 1**: Basic single-table queries (Tasks 1-20)
2. **Phase 2**: Aggregations and grouping (Tasks 21-50)  
3. **Phase 3**: Multi-table joins (Tasks 51-80)
4. **Phase 4**: Complex analytics (Tasks 81-120)
5. **Phase 5**: Mixed difficulty with real-world scenarios

### 15. Schema Randomization System

```python
class SchemaRandomizer:
    """Handles database schema variations for robust training"""
    
    def __init__(self, base_schema_variants: Dict, randomization_schedule: Dict):
        self.variants = base_schema_variants
        self.schedule = randomization_schedule
        self.current_schema = None
        
    def should_randomize(self, episode_number: int) -> bool:
        """Determine if schema should be randomized this episode"""
        for interval, change_type in self.schedule.items():
            if episode_number % interval == 0:
                return True
        return False
    
    def generate_schema_variant(self, episode_number: int) -> Dict:
        """Generate new schema variant based on episode"""
        # Minor changes every 25 episodes
        if episode_number % 25 == 0 and episode_number % 100 != 0:
            return self._apply_minor_variations()
        # Major changes every 100 episodes  
        elif episode_number % 100 == 0 and episode_number % 250 != 0:
            return self._apply_major_variations()
        # Complete redesign every 250 episodes
        elif episode_number % 250 == 0:
            return self._complete_schema_redesign()
        
        return self.current_schema
    
    def _apply_minor_variations(self) -> Dict:
        """Apply minor variations like column name changes"""
        # Randomly rename 20-30% of columns
        # Change some data types (keeping semantic meaning)
        pass
    
    def _apply_major_variations(self) -> Dict:
        """Apply major structural changes"""
        # Change table relationships
        # Modify foreign key structures
        # Add/remove optional columns
        pass
    
    def _complete_schema_redesign(self) -> Dict:
        """Complete schema redesign with different medical focus"""
        # Switch between clinic, hospital, research database designs
        # Different medical specialties (cardiology, oncology, etc.)
        pass

class GroundTruthGenerator:
    """Generates ground truth results for any schema variant"""
    
    def __init__(self, schema_randomizer: SchemaRandomizer):
        self.schema_randomizer = schema_randomizer
        
    def generate_ground_truth(self, task: Dict, current_schema: Dict) -> List[Dict]:
        """Generate ground truth results for current schema variant"""
        # Execute canonical query against current database
        # Return results that should be matched regardless of SQL approach
        pass
```

### 16. Training Loop Integration

```python
def train_medical_sql_agent(model: MaximumContinualModel,
                          env: MedicalSQLEnvironment,
                          num_episodes: int = 1000):
    """Main training loop with schema randomization"""
    
    schema_randomizer = SchemaRandomizer(
        base_schema_variants=SCHEMA_VARIANTS,
        randomization_schedule={25: "minor", 100: "major", 250: "complete"}
    )
    
    for episode in range(num_episodes):
        # Check if schema should be randomized
        if schema_randomizer.should_randomize(episode):
            new_schema = schema_randomizer.generate_schema_variant(episode)
            env.update_schema(new_schema)
            print(f"Episode {episode}: Schema updated to variant {new_schema['variant_name']}")
        
        # Reset environment and get task with current schema
        task = env.reset()
        
        # Generate fresh ground truth for current schema
        ground_truth = env.generate_ground_truth_for_current_schema(task)
        
        # Agent generates prediction using tools
        prediction = model.predict(
            messages=task['messages'],
            tools=task['tools']  # Tools reflect current schema
        )
        
        # Extract agent's query result from prediction
        agent_result = extract_sql_result_from_prediction(prediction)
        
        # Environment evaluates result against ground truth
        reward = env.evaluate_response(agent_result, ground_truth)
        
        # Update model with reward feedback
        update_data = PredictionResponseWithRewardT(
            prediction=prediction,
            reward=reward
        )
        model.update(update_data)
        
        # Log progress
        if episode % 50 == 0:
            success_rate = env.get_recent_success_rate()
            print(f"Episode {episode}: Success rate = {success_rate:.2%}, "
                  f"Current schema = {env.current_schema['variant_name']}")
```

## Implementation Timeline

### 17. Development Phases

#### Week 1-2: Foundation
- [ ] Create database schema and synthetic data generator
- [ ] Implement basic SQL query tool
- [ ] Set up DuckDB integration
- [ ] Design schema variation system

#### Week 3-4: Core Environment  
- [ ] Implement MedicalSQLEnvironment class
- [ ] Create result-based reward calculation system
- [ ] Develop basic query tasks with ground truth results (Levels 1-2)
- [ ] Implement SchemaRandomizer class

#### Week 5-6: Tool Integration
- [ ] Integrate with maximum_continual framework
- [ ] Create database schema exploration tools
- [ ] Implement training loop with schema randomization
- [ ] Build GroundTruthGenerator for dynamic schema variants

#### Week 7-8: Advanced Features
- [ ] Add complex query tasks (Levels 3-5)
- [ ] Implement comprehensive result evaluation framework
- [ ] Create curriculum learning system with schema progression
- [ ] Build robustness testing across schema variants

#### Week 9-10: Testing and Refinement
- [ ] Extensive testing across all schema variants
- [ ] Performance optimization and schema generation efficiency
- [ ] Documentation and examples with multiple schema types
- [ ] Validation of cross-schema generalization

## Success Criteria

### 18. Performance Targets

1. **Basic Queries (Level 1)**: 95% accuracy within 100 episodes
2. **Aggregations (Level 2)**: 90% accuracy within 200 episodes  
3. **Joins (Level 3)**: 85% accuracy within 300 episodes
4. **Complex Analytics (Level 4)**: 80% accuracy within 500 episodes
5. **Natural Language (Level 5)**: 75% accuracy within 1000 episodes

### 19. Quality Metrics

- **Result-Based Generalization**: >70% accuracy on held-out test cases
- **Schema Robustness**: <15% performance drop when switching schemas
- **Cross-Schema Transfer**: >60% accuracy on first exposure to new schema variant
- **Efficiency**: Average query execution time <2 seconds
- **Learning Speed**: 20% improvement in success rate every 100 episodes
- **Schema Adaptation**: Return to baseline performance within 25 episodes of schema change

### 20. Schema Robustness Criteria

- **Minor Variations (Column Names)**: <5% accuracy drop
- **Major Variations (Table Structure)**: <20% accuracy drop  
- **Complete Redesign**: <40% accuracy drop initially, recovery within 50 episodes
- **Cross-Domain Transfer**: >50% accuracy when switching medical specialties
- **Schema Discovery**: Agent should successfully use schema exploration tools 95% of the time

## Risk Mitigation

### 21. Potential Challenges and Solutions

1. **SQL Complexity**: Start simple, gradually increase complexity
2. **Data Realism**: Collaborate with medical professionals for validation  
3. **Schema Randomization Complexity**: Careful balance between variation and learnable patterns
4. **Training Instability from Schema Changes**: Gradual schema transitions and adaptation periods
5. **Ground Truth Generation**: Ensuring consistent results across schema variants
6. **Computational Cost**: Efficient database regeneration and schema switching
7. **Result Evaluation Ambiguity**: Robust comparison methods for different result formats

## Future Extensions  

### 22. Potential Enhancements

1. **Multi-database Support**: PostgreSQL, MySQL, SQLite
2. **Real Data Integration**: Anonymized real medical datasets
3. **Multi-modal Queries**: Combining SQL with text analysis
4. **Federated Queries**: Across multiple medical systems
5. **Privacy-Preserving Learning**: Differential privacy techniques

---

This implementation plan provides a comprehensive roadmap for creating a robust medical SQL RL environment. The modular design allows for incremental development and testing, while the integration with maximum_continual ensures seamless adoption of the continual learning paradigm.
