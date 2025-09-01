"""
Query tasks definition for medical SQL RL environment.

Defines 5 levels of query difficulty with ground truth results for curriculum learning:
1. Basic Retrieval - Simple SELECT statements
2. Aggregation - COUNT, SUM, AVG operations
3. Joins - Multi-table queries with relationships
4. Complex Analytics - Window functions, CTEs, complex correlations
5. Natural Language - Ambiguous queries requiring interpretation
"""

from typing import Dict, List, Any, Optional
import random
from dataclasses import dataclass
from datetime import date, datetime, timedelta


@dataclass
class QueryTask:
    """Represents a single SQL query task with ground truth"""
    task_id: str
    level: int
    category: str
    description: str
    natural_language: str
    ground_truth_result: List[Dict[str, Any]]
    evaluation_config: Dict[str, Any]
    difficulty_factors: List[str]
    expected_columns: List[str]
    hints: Optional[List[str]] = None


class QueryTaskGenerator:
    """Generates query tasks with ground truth results for different difficulty levels"""
    
    def __init__(self):
        self.task_templates = self._initialize_task_templates()
        self.task_counter = 0
    
    def generate_task(self, level: int, category: str = None) -> QueryTask:
        """
        Generate a query task for specified level and category
        
        Args:
            level: Difficulty level (1-5)
            category: Optional specific category to generate
            
        Returns:
            QueryTask instance
        """
        if level not in self.task_templates:
            raise ValueError(f"Invalid level: {level}. Must be 1-5.")
        
        level_templates = self.task_templates[level]
        
        if category:
            if category not in level_templates:
                available = list(level_templates.keys())
                raise ValueError(f"Category {category} not available for level {level}. Available: {available}")
            templates = [level_templates[category]]
        else:
            templates = list(level_templates.values())
        
        # Select random template
        template = random.choice(templates)
        
        # Generate task from template
        self.task_counter += 1
        task = self._instantiate_template(template, level, self.task_counter)
        
        return task
    
    def generate_curriculum(self, tasks_per_level: int = 20) -> List[QueryTask]:
        """Generate a complete curriculum of tasks across all levels"""
        curriculum = []
        
        for level in range(1, 6):
            for _ in range(tasks_per_level):
                task = self.generate_task(level)
                curriculum.append(task)
        
        return curriculum
    
    def get_level_description(self, level: int) -> str:
        """Get description of what each level covers"""
        descriptions = {
            1: "Basic Retrieval: Simple SELECT statements with WHERE clauses on single tables",
            2: "Aggregation: COUNT, SUM, AVG, GROUP BY operations with basic filtering",
            3: "Joins: Multi-table queries with INNER/LEFT JOIN operations",
            4: "Complex Analytics: Window functions, CTEs, subqueries, and statistical operations",
            5: "Natural Language: Ambiguous queries requiring contextual interpretation"
        }
        return descriptions.get(level, "Unknown level")
    
    def _initialize_task_templates(self) -> Dict[int, Dict[str, Dict]]:
        """Initialize task templates for all difficulty levels"""
        return {
            1: self._get_level1_templates(),
            2: self._get_level2_templates(),
            3: self._get_level3_templates(),
            4: self._get_level4_templates(),
            5: self._get_level5_templates()
        }
    
    def _get_level1_templates(self) -> Dict[str, Dict]:
        """Level 1: Basic Retrieval Tasks"""
        return {
            "patient_lookup": {
                "description": "Find basic patient information",
                "natural_language_templates": [
                    "Show me all patients named {first_name}",
                    "Get patient information for someone with the last name {last_name}",
                    "Find all patients born in {birth_year}",
                    "List patients who are {age} years old"
                ],
                "ground_truth_generator": self._generate_patient_lookup_truth,
                "evaluation_config": {"evaluation_type": "exact_match"},
                "expected_columns": ["patient_id", "first_name", "last_name", "date_of_birth"],
                "difficulty_factors": ["single_table", "simple_where_clause"],
                "hints": ["Use the patients table", "Filter with WHERE clause"]
            },
            
            "condition_lookup": {
                "description": "Find medical conditions for specific criteria",
                "natural_language_templates": [
                    "What conditions does patient ID {patient_id} have?",
                    "Show me all patients with {condition_name}",
                    "Find all {severity} severity conditions",
                    "List conditions diagnosed in {year}"
                ],
                "ground_truth_generator": self._generate_condition_lookup_truth,
                "evaluation_config": {"evaluation_type": "set_match"},
                "expected_columns": ["condition_name", "diagnosis_date", "severity", "patient_id"],
                "difficulty_factors": ["single_table", "condition_filtering"],
                "hints": ["Check the conditions/medical_conditions/health_issues table", "Use appropriate date filtering"]
            },
            
            "medication_lookup": {
                "description": "Find medication information",
                "natural_language_templates": [
                    "What medications is patient {patient_id} taking?",
                    "Show all prescriptions for {medication_name}",
                    "Find active medications prescribed in {month} {year}",
                    "List all {dosage} medications"
                ],
                "ground_truth_generator": self._generate_medication_lookup_truth,
                "evaluation_config": {"evaluation_type": "set_match"},
                "expected_columns": ["medication_name", "dosage", "status", "patient_id"],
                "difficulty_factors": ["single_table", "status_filtering"],
                "hints": ["Use medications/prescriptions/therapeutic_agents table", "Check medication status"]
            },
            
            "appointment_lookup": {
                "description": "Find appointment information",
                "natural_language_templates": [
                    "Show appointments for patient {patient_id}",
                    "Find all {appointment_type} appointments",
                    "List appointments on {date}",
                    "Show {status} appointments"
                ],
                "ground_truth_generator": self._generate_appointment_lookup_truth,
                "evaluation_config": {"evaluation_type": "temporal_tolerance", "time_tolerance_days": 1},
                "expected_columns": ["appointment_id", "patient_id", "appointment_date", "appointment_type", "status"],
                "difficulty_factors": ["single_table", "date_filtering"],
                "hints": ["Use appointments/visits/encounters table", "Be careful with date formats"]
            }
        }
    
    def _get_level2_templates(self) -> Dict[str, Dict]:
        """Level 2: Aggregation Tasks"""
        return {
            "patient_counts": {
                "description": "Count patients by various criteria",
                "natural_language_templates": [
                    "How many patients do we have?",
                    "Count patients by gender",
                    "How many patients were born in each decade?",
                    "Count patients by insurance type"
                ],
                "ground_truth_generator": self._generate_patient_count_truth,
                "evaluation_config": {"evaluation_type": "exact_match"},
                "expected_columns": ["count", "group_by_field"],
                "difficulty_factors": ["aggregation", "group_by"],
                "hints": ["Use COUNT() function", "GROUP BY for categories"]
            },
            
            "condition_statistics": {
                "description": "Statistical analysis of medical conditions",
                "natural_language_templates": [
                    "What's the average number of conditions per patient?",
                    "Count conditions by severity level",
                    "How many active vs resolved conditions are there?",
                    "Which condition is most common?"
                ],
                "ground_truth_generator": self._generate_condition_stats_truth,
                "evaluation_config": {"evaluation_type": "numerical_tolerance", "tolerance": 0.01},
                "expected_columns": ["condition_name", "count", "severity", "avg_per_patient"],
                "difficulty_factors": ["aggregation", "medical_logic"],
                "hints": ["Use COUNT(), AVG() functions", "GROUP BY condition attributes"]
            },
            
            "medication_analytics": {
                "description": "Analyze medication patterns",
                "natural_language_templates": [
                    "What's the average number of medications per patient?",
                    "Count prescriptions by month",
                    "Which medications are prescribed most frequently?",
                    "How many active vs discontinued medications?"
                ],
                "ground_truth_generator": self._generate_medication_stats_truth,
                "evaluation_config": {"evaluation_type": "numerical_tolerance", "tolerance": 0.02},
                "expected_columns": ["medication_name", "prescription_count", "avg_per_patient", "status_count"],
                "difficulty_factors": ["aggregation", "temporal_grouping"],
                "hints": ["COUNT(), AVG() with GROUP BY", "Consider medication status"]
            },
            
            "vital_statistics": {
                "description": "Analyze vital signs data",
                "natural_language_templates": [
                    "What's the average blood pressure across all patients?",
                    "Calculate BMI statistics",
                    "Find the highest and lowest recorded temperatures",
                    "Average heart rate by age group"
                ],
                "ground_truth_generator": self._generate_vital_stats_truth,
                "evaluation_config": {"evaluation_type": "numerical_tolerance", "tolerance": 0.05},
                "expected_columns": ["avg_systolic", "avg_diastolic", "avg_heart_rate", "avg_temperature"],
                "difficulty_factors": ["numerical_aggregation", "calculated_fields"],
                "hints": ["Use AVG(), MIN(), MAX() functions", "Calculate BMI from height/weight"]
            }
        }
    
    def _get_level3_templates(self) -> Dict[str, Dict]:
        """Level 3: Join Tasks"""
        return {
            "patient_condition_join": {
                "description": "Join patients with their conditions",
                "natural_language_templates": [
                    "Show patient names with their medical conditions",
                    "List all patients with diabetes and their contact information", 
                    "Find patients with multiple chronic conditions",
                    "Show patient demographics for those with heart conditions"
                ],
                "ground_truth_generator": self._generate_patient_condition_join_truth,
                "evaluation_config": {"evaluation_type": "set_match"},
                "expected_columns": ["patient_name", "condition_name", "diagnosis_date", "severity"],
                "difficulty_factors": ["inner_join", "multi_table"],
                "hints": ["JOIN patients with conditions table", "Use patient_id as foreign key"]
            },
            
            "medication_prescriber_join": {
                "description": "Connect medications with prescribing information",
                "natural_language_templates": [
                    "Show patients and their current medications",
                    "List medication adherence by patient",
                    "Find patients taking multiple medications",
                    "Show medication history for each patient"
                ],
                "ground_truth_generator": self._generate_medication_join_truth,
                "evaluation_config": {"evaluation_type": "partial_match"},
                "expected_columns": ["patient_name", "medication_name", "dosage", "prescribed_date"],
                "difficulty_factors": ["left_join", "medication_status"],
                "hints": ["LEFT JOIN to include all patients", "Filter by medication status"]
            },
            
            "appointment_outcome_join": {
                "description": "Analyze appointments with patient outcomes",
                "natural_language_templates": [
                    "Show appointment history with patient information",
                    "Find patients with frequent medical visits",
                    "Correlate appointment types with patient conditions",
                    "List no-show appointments by patient demographics"
                ],
                "ground_truth_generator": self._generate_appointment_join_truth,
                "evaluation_config": {"evaluation_type": "set_match"},
                "expected_columns": ["patient_name", "appointment_date", "appointment_type", "status"],
                "difficulty_factors": ["temporal_join", "appointment_status"],
                "hints": ["JOIN appointments with patients", "Consider appointment status"]
            },
            
            "comprehensive_health_view": {
                "description": "Multi-table health overview",
                "natural_language_templates": [
                    "Show complete health profile for each patient",
                    "List patients with conditions, medications, and recent vitals",
                    "Find correlation between conditions and prescribed medications",
                    "Show patient health timeline with appointments and diagnoses"
                ],
                "ground_truth_generator": self._generate_comprehensive_join_truth,
                "evaluation_config": {"evaluation_type": "partial_match"},
                "expected_columns": ["patient_name", "condition_count", "medication_count", "last_appointment"],
                "difficulty_factors": ["multiple_joins", "comprehensive_view"],
                "hints": ["JOIN multiple tables", "Use LEFT JOIN to preserve all patients"]
            }
        }
    
    def _get_level4_templates(self) -> Dict[str, Dict]:
        """Level 4: Complex Analytics Tasks"""
        return {
            "health_trends": {
                "description": "Analyze health trends over time",
                "natural_language_templates": [
                    "Show monthly trends in new diagnoses",
                    "Calculate rolling average of patient vitals",
                    "Find seasonal patterns in appointment scheduling", 
                    "Analyze medication adherence trends"
                ],
                "ground_truth_generator": self._generate_health_trends_truth,
                "evaluation_config": {"evaluation_type": "numerical_tolerance", "tolerance": 0.05},
                "expected_columns": ["time_period", "metric_value", "trend_direction", "moving_average"],
                "difficulty_factors": ["window_functions", "time_series", "trend_analysis"],
                "hints": ["Use window functions like ROW_NUMBER(), LAG()", "GROUP BY time periods"]
            },
            
            "risk_stratification": {
                "description": "Patient risk analysis and stratification",
                "natural_language_templates": [
                    "Identify high-risk patients based on multiple conditions",
                    "Calculate cardiovascular risk scores",
                    "Find patients with medication interaction risks",
                    "Stratify patients by diabetes management quality"
                ],
                "ground_truth_generator": self._generate_risk_stratification_truth,
                "evaluation_config": {"evaluation_type": "partial_match"},
                "expected_columns": ["patient_id", "risk_score", "risk_category", "risk_factors"],
                "difficulty_factors": ["complex_scoring", "case_statements", "multi_factor_analysis"],
                "hints": ["Use CASE statements for scoring", "Consider multiple health factors"]
            },
            
            "outcome_correlation": {
                "description": "Correlate treatments with outcomes",
                "natural_language_templates": [
                    "Show correlation between doctor visits and step count",
                    "Analyze medication effectiveness on vital signs",
                    "Find relationship between appointment frequency and health outcomes",
                    "Compare treatment adherence across patient demographics"
                ],
                "ground_truth_generator": self._generate_correlation_truth,
                "evaluation_config": {"evaluation_type": "numerical_tolerance", "tolerance": 0.1},
                "expected_columns": ["correlation_metric", "statistical_significance", "sample_size"],
                "difficulty_factors": ["statistical_analysis", "correlation_calculation"],
                "hints": ["Use CTEs for complex calculations", "Calculate statistical measures"]
            },
            
            "predictive_analytics": {
                "description": "Predictive health analytics queries",
                "natural_language_templates": [
                    "Predict patients likely to miss appointments based on history",
                    "Identify patients at risk for medication non-adherence",
                    "Find early indicators of chronic disease development",
                    "Predict resource utilization based on patient complexity"
                ],
                "ground_truth_generator": self._generate_predictive_truth,
                "evaluation_config": {"evaluation_type": "partial_match"},
                "expected_columns": ["patient_id", "prediction_score", "confidence_level", "key_indicators"],
                "difficulty_factors": ["predictive_modeling", "complex_joins", "scoring_algorithms"],
                "hints": ["Use historical data for patterns", "Build composite scores"]
            }
        }
    
    def _get_level5_templates(self) -> Dict[str, Dict]:
        """Level 5: Natural Language Tasks"""
        return {
            "ambiguous_health_queries": {
                "description": "Interpret ambiguous health-related questions",
                "natural_language_templates": [
                    "Which patients are not doing well?",
                    "Show me the sickest patients",
                    "Find patients who need attention",
                    "Who should we prioritize for follow-up?"
                ],
                "ground_truth_generator": self._generate_ambiguous_health_truth,
                "evaluation_config": {"evaluation_type": "semantic_match", "semantic_tolerance": 0.7},
                "expected_columns": ["patient_id", "health_score", "priority_level", "reasons"],
                "difficulty_factors": ["interpretation", "multi_factor_scoring", "clinical_judgment"],
                "hints": ["Consider multiple health indicators", "Define 'not doing well' quantitatively"]
            },
            
            "contextual_medical_queries": {
                "description": "Queries requiring medical context understanding",
                "natural_language_templates": [
                    "Show patients with concerning vital signs",
                    "Find medication regimens that might interact",
                    "Which patients have uncontrolled conditions?",
                    "Identify care gaps in chronic disease management"
                ],
                "ground_truth_generator": self._generate_contextual_medical_truth,
                "evaluation_config": {"evaluation_type": "semantic_match", "semantic_tolerance": 0.8},
                "expected_columns": ["patient_id", "concern_type", "severity_level", "recommendations"],
                "difficulty_factors": ["medical_knowledge", "threshold_determination", "clinical_interpretation"],
                "hints": ["Define medical thresholds", "Consider clinical significance"]
            },
            
            "population_health_insights": {
                "description": "Population-level health insights from natural language",
                "natural_language_templates": [
                    "How is our patient population doing overall?",
                    "What are the biggest health concerns we should address?",
                    "Where are we succeeding and failing in patient care?",
                    "What trends should worry us?"
                ],
                "ground_truth_generator": self._generate_population_insights_truth,
                "evaluation_config": {"evaluation_type": "semantic_match", "semantic_tolerance": 0.6},
                "expected_columns": ["metric_name", "current_value", "trend", "assessment"],
                "difficulty_factors": ["population_analysis", "trend_identification", "health_assessment"],
                "hints": ["Aggregate across patient population", "Calculate population health metrics"]
            },
            
            "complex_clinical_scenarios": {
                "description": "Complex clinical reasoning scenarios",
                "natural_language_templates": [
                    "Find patients similar to John Doe (patient 12345) for comparative analysis",
                    "Show me patterns that might explain why some patients improve faster",
                    "Which factors seem to predict successful treatment outcomes?",
                    "Help me understand why certain patients are high utilizers"
                ],
                "ground_truth_generator": self._generate_clinical_scenario_truth,
                "evaluation_config": {"evaluation_type": "partial_match"},
                "expected_columns": ["analysis_type", "findings", "patterns", "recommendations"],
                "difficulty_factors": ["pattern_recognition", "similarity_analysis", "clinical_reasoning"],
                "hints": ["Use comparative analysis techniques", "Look for statistical patterns"]
            }
        }
    
    def _instantiate_template(self, template: Dict, level: int, task_id: int) -> QueryTask:
        """Convert template to actual QueryTask instance"""
        category = template.get("description", f"level_{level}_task")
        
        # Select random natural language template
        nl_templates = template["natural_language_templates"]
        nl_template = random.choice(nl_templates)
        
        # Generate parameters for the template
        parameters = self._generate_task_parameters()
        
        try:
            natural_language = nl_template.format(**parameters)
        except KeyError:
            # If template has placeholders we don't have, use as-is
            natural_language = nl_template
        
        # Generate ground truth using the specified generator
        ground_truth_generator = template["ground_truth_generator"]
        ground_truth = ground_truth_generator(parameters, level)
        
        return QueryTask(
            task_id=f"task_{level}_{task_id:03d}",
            level=level,
            category=category,
            description=template["description"],
            natural_language=natural_language,
            ground_truth_result=ground_truth,
            evaluation_config=template["evaluation_config"],
            difficulty_factors=template["difficulty_factors"],
            expected_columns=template["expected_columns"],
            hints=template.get("hints")
        )
    
    def _generate_task_parameters(self) -> Dict[str, Any]:
        """Generate random parameters for task templates"""
        current_year = datetime.now().year
        return {
            "patient_id": random.randint(1, 100),
            "first_name": random.choice(["John", "Jane", "Michael", "Sarah", "David", "Emily"]),
            "last_name": random.choice(["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia"]),
            "birth_year": random.randint(1940, 2000),
            "age": random.randint(20, 80),
            "condition_name": random.choice(["Diabetes", "Hypertension", "Asthma", "Depression", "Obesity"]),
            "medication_name": random.choice(["Metformin", "Lisinopril", "Albuterol", "Sertraline", "Atorvastatin"]),
            "severity": random.choice(["mild", "moderate", "severe"]),
            "dosage": random.choice(["10mg", "20mg", "50mg", "100mg"]),
            "appointment_type": random.choice(["Annual Physical", "Follow-up", "Urgent Care"]),
            "status": random.choice(["completed", "scheduled", "cancelled"]),
            "year": random.randint(2020, current_year),
            "month": random.choice(["January", "February", "March", "April", "May", "June",
                                   "July", "August", "September", "October", "November", "December"]),
            "date": f"{current_year}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
        }
    
    # Ground truth generators (these would generate realistic mock data)
    # In a real implementation, these would query the actual database
    
    def _generate_patient_lookup_truth(self, params: Dict, level: int) -> List[Dict]:
        """Generate ground truth for patient lookup queries"""
        return [
            {
                "patient_id": params.get("patient_id", 1),
                "first_name": params.get("first_name", "John"),
                "last_name": params.get("last_name", "Doe"),
                "date_of_birth": "1980-05-15",
                "gender": "Male"
            }
        ]
    
    def _generate_condition_lookup_truth(self, params: Dict, level: int) -> List[Dict]:
        return [
            {
                "condition_name": "Type 2 Diabetes",
                "diagnosis_date": "2020-03-15",
                "severity": "moderate",
                "patient_id": params.get("patient_id", 1)
            },
            {
                "condition_name": "Hypertension", 
                "diagnosis_date": "2019-08-22",
                "severity": "mild",
                "patient_id": params.get("patient_id", 1)
            }
        ]
    
    def _generate_medication_lookup_truth(self, params: Dict, level: int) -> List[Dict]:
        return [
            {
                "medication_name": "Metformin",
                "dosage": "500mg",
                "status": "active",
                "patient_id": params.get("patient_id", 1)
            }
        ]
    
    def _generate_appointment_lookup_truth(self, params: Dict, level: int) -> List[Dict]:
        return [
            {
                "appointment_id": 1,
                "patient_id": params.get("patient_id", 1),
                "appointment_date": "2024-01-15",
                "appointment_type": "Annual Physical",
                "status": "completed"
            }
        ]
    
    def _generate_patient_count_truth(self, params: Dict, level: int) -> List[Dict]:
        return [{"count": 150}]
    
    def _generate_condition_stats_truth(self, params: Dict, level: int) -> List[Dict]:
        return [
            {"condition_name": "Diabetes", "count": 25, "avg_per_patient": 1.2},
            {"condition_name": "Hypertension", "count": 32, "avg_per_patient": 1.1}
        ]
    
    def _generate_medication_stats_truth(self, params: Dict, level: int) -> List[Dict]:
        return [
            {"medication_name": "Metformin", "prescription_count": 18, "avg_per_patient": 0.8}
        ]
    
    def _generate_vital_stats_truth(self, params: Dict, level: int) -> List[Dict]:
        return [
            {"avg_systolic": 125.3, "avg_diastolic": 82.1, "avg_heart_rate": 72.5, "avg_temperature": 98.6}
        ]
    
    def _generate_patient_condition_join_truth(self, params: Dict, level: int) -> List[Dict]:
        return [
            {
                "patient_name": "John Doe",
                "condition_name": "Type 2 Diabetes",
                "diagnosis_date": "2020-03-15",
                "severity": "moderate"
            }
        ]
    
    def _generate_medication_join_truth(self, params: Dict, level: int) -> List[Dict]:
        return [
            {
                "patient_name": "John Doe",
                "medication_name": "Metformin",
                "dosage": "500mg",
                "prescribed_date": "2020-03-20"
            }
        ]
    
    def _generate_appointment_join_truth(self, params: Dict, level: int) -> List[Dict]:
        return [
            {
                "patient_name": "John Doe",
                "appointment_date": "2024-01-15",
                "appointment_type": "Follow-up",
                "status": "completed"
            }
        ]
    
    def _generate_comprehensive_join_truth(self, params: Dict, level: int) -> List[Dict]:
        return [
            {
                "patient_name": "John Doe",
                "condition_count": 2,
                "medication_count": 1,
                "last_appointment": "2024-01-15"
            }
        ]
    
    def _generate_health_trends_truth(self, params: Dict, level: int) -> List[Dict]:
        return [
            {"time_period": "2024-01", "metric_value": 125.3, "trend_direction": "increasing", "moving_average": 123.8}
        ]
    
    def _generate_risk_stratification_truth(self, params: Dict, level: int) -> List[Dict]:
        return [
            {
                "patient_id": 1,
                "risk_score": 7.5,
                "risk_category": "high",
                "risk_factors": "diabetes, hypertension, age>65"
            }
        ]
    
    def _generate_correlation_truth(self, params: Dict, level: int) -> List[Dict]:
        return [
            {
                "correlation_metric": "visit_vs_steps",
                "correlation_value": -0.15,
                "statistical_significance": 0.02,
                "sample_size": 150
            }
        ]
    
    def _generate_predictive_truth(self, params: Dict, level: int) -> List[Dict]:
        return [
            {
                "patient_id": 1,
                "prediction_score": 0.72,
                "confidence_level": 0.85,
                "key_indicators": "missed appointments, medication gaps"
            }
        ]
    
    def _generate_ambiguous_health_truth(self, params: Dict, level: int) -> List[Dict]:
        return [
            {
                "patient_id": 1,
                "health_score": 3.2,
                "priority_level": "high",
                "reasons": "multiple chronic conditions, poor vital trends"
            }
        ]
    
    def _generate_contextual_medical_truth(self, params: Dict, level: int) -> List[Dict]:
        return [
            {
                "patient_id": 1,
                "concern_type": "blood_pressure_control",
                "severity_level": "moderate",
                "recommendations": "medication adjustment, lifestyle counseling"
            }
        ]
    
    def _generate_population_insights_truth(self, params: Dict, level: int) -> List[Dict]:
        return [
            {
                "metric_name": "diabetes_control_rate",
                "current_value": 0.68,
                "trend": "improving",
                "assessment": "good progress but room for improvement"
            }
        ]
    
    def _generate_clinical_scenario_truth(self, params: Dict, level: int) -> List[Dict]:
        return [
            {
                "analysis_type": "patient_similarity",
                "findings": "5 similar patients identified",
                "patterns": "all respond well to combination therapy",
                "recommendations": "consider similar treatment approach"
            }
        ]
