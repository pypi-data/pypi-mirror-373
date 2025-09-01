"""
Schema randomization system for medical SQL RL environment.

Handles systematic variation of database schemas to ensure agent robustness
across different database designs, column names, and structural patterns.
"""

import random
import copy
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import replace

from .schema import DatabaseSchema, Table, Column, DataType, SCHEMA_VARIANTS
from .synthetic_generator import MedicalDataGenerator
from .connection import DatabaseManager


class SchemaRandomizer:
    """Handles database schema variations for robust training"""
    
    def __init__(self, 
                 base_schema_variants: Dict[str, DatabaseSchema] = None,
                 randomization_schedule: Dict[int, str] = None,
                 seed: int = 42):
        """
        Initialize schema randomizer
        
        Args:
            base_schema_variants: Dictionary of base schema variants
            randomization_schedule: When to apply different types of variations
            seed: Random seed for reproducible variations
        """
        self.variants = base_schema_variants or SCHEMA_VARIANTS
        self.schedule = randomization_schedule or {25: "minor", 100: "major", 250: "complete"}
        self.current_schema: Optional[DatabaseSchema] = None
        self.variation_history: List[Dict[str, Any]] = []
        
        random.seed(seed)
        
        # Column name variations for minor changes
        self.column_name_variants = {
            # Patient table variations
            "patient_id": ["patient_id", "id", "person_id", "individual_id"],
            "first_name": ["first_name", "fname", "given_name", "forename"],
            "last_name": ["last_name", "lname", "family_name", "surname"],
            "date_of_birth": ["date_of_birth", "birth_date", "dob", "birthdate"],
            "gender": ["gender", "sex", "gender_code", "gender_identity"],
            "phone": ["phone", "contact_phone", "telephone", "phone_number"],
            "email": ["email", "contact_email", "email_address", "email_addr"],
            "address": ["address", "home_address", "residential_address", "street_address"],
            "insurance_id": ["insurance_id", "insurance_number", "coverage_id", "policy_number"],
            "created_at": ["created_at", "admission_timestamp", "registration_date", "enrollment_date"],
            
            # Condition table variations
            "condition_id": ["condition_id", "record_id", "issue_id", "diagnosis_id"],
            "condition_name": ["condition_name", "diagnosis", "issue_description", "medical_condition"],
            "icd_10_code": ["icd_10_code", "diagnostic_code", "classification_code", "condition_code"],
            "diagnosis_date": ["diagnosis_date", "date_diagnosed", "diagnosis_timestamp", "identified_on"],
            "severity": ["severity", "severity_level", "severity_rating", "condition_severity"],
            "status": ["status", "current_status", "management_status", "condition_status"],
            "diagnosed_by": ["diagnosed_by", "attending_physician", "care_provider", "doctor_id"],
            "notes": ["notes", "clinical_notes", "clinical_observations", "documentation"],
            
            # Medication variations
            "medication_id": ["medication_id", "prescription_id", "agent_id", "drug_id"],
            "medication_name": ["medication_name", "drug_name", "medication", "agent_name"],
            "generic_name": ["generic_name", "generic_equivalent", "alternative_name", "generic_drug"],
            "dosage": ["dosage", "dose", "therapeutic_dose", "medication_dose"],
            "frequency": ["frequency", "administration_schedule", "dosing_regimen", "schedule"],
            "prescribed_date": ["prescribed_date", "prescription_date", "therapy_initiated", "order_date"],
            "start_date": ["start_date", "treatment_start", "therapy_start", "begin_date"],
            "end_date": ["end_date", "treatment_end", "therapy_conclusion", "stop_date"],
            "prescribed_by": ["prescribed_by", "prescribing_physician", "prescriber", "ordering_doctor"],
            
            # Vital signs variations
            "vital_id": ["vital_id", "measurement_id", "biometric_id", "reading_id"],
            "measurement_date": ["measurement_date", "recorded_at", "assessment_time", "vital_timestamp"],
            "height_cm": ["height_cm", "height_centimeters", "stature_cm", "body_height"],
            "weight_kg": ["weight_kg", "weight_kilograms", "mass_kg", "body_weight"],
            "blood_pressure_systolic": ["blood_pressure_systolic", "systolic_bp", "arterial_pressure_high", "sys_bp"],
            "blood_pressure_diastolic": ["blood_pressure_diastolic", "diastolic_bp", "arterial_pressure_low", "dia_bp"],
            "heart_rate": ["heart_rate", "pulse_rate", "cardiac_frequency", "pulse"],
            "temperature_celsius": ["temperature_celsius", "body_temperature", "core_temperature", "temp_c"],
            "recorded_by": ["recorded_by", "measured_by_staff", "assessor", "technician_id"],
            
            # Appointment variations
            "appointment_id": ["appointment_id", "visit_id", "encounter_id", "session_id"],
            "doctor_id": ["doctor_id", "physician_id", "healthcare_provider", "provider_id"],
            "appointment_date": ["appointment_date", "visit_datetime", "encounter_timestamp", "session_time"],
            "appointment_type": ["appointment_type", "visit_category", "service_type", "encounter_type"],
            "duration_minutes": ["duration_minutes", "session_duration", "contact_duration", "visit_length"],
            
            # Activity variations
            "activity_id": ["activity_id", "tracking_id", "metric_id", "fitness_id"],
            "date": ["date", "tracking_date", "measurement_date", "activity_date"],
            "step_count": ["step_count", "daily_steps", "ambulation_count", "steps"],
            "sleep_hours": ["sleep_hours", "sleep_duration", "rest_period_hours", "sleep_time"],
            "calories_burned": ["calories_burned", "energy_expenditure", "metabolic_expenditure", "calories"],
            "active_minutes": ["active_minutes", "exercise_minutes", "physical_activity_duration", "workout_time"],
            "heart_rate_avg": ["heart_rate_avg", "average_heart_rate", "cardiac_rhythm_mean", "avg_pulse"],
            
            # Lab results variations
            "lab_result_id": ["lab_result_id", "test_id", "result_id", "lab_id"],
            "test_name": ["test_name", "test_description", "examination_name", "lab_test"],
            "test_code": ["test_code", "lab_code", "procedure_code", "test_identifier"],
            "result_value": ["result_value", "numeric_result", "quantitative_outcome", "test_result"],
            "result_unit": ["result_unit", "measurement_unit", "unit_of_measure", "units"],
            "reference_range": ["reference_range", "normal_range", "reference_interval", "normal_values"],
            "test_date": ["test_date", "sample_collection_time", "specimen_collection", "collection_date"],
            "ordered_by": ["ordered_by", "requesting_physician", "ordering_provider", "doctor_id"],
        }
        
        # Data type variations
        self.data_type_variants = {
            DataType.INTEGER: [DataType.INTEGER],  # Keep integers as integers for IDs
            DataType.VARCHAR: [DataType.VARCHAR, DataType.TEXT],
            DataType.TEXT: [DataType.TEXT, DataType.VARCHAR],
            DataType.DATE: [DataType.DATE, DataType.TIMESTAMP],
            DataType.TIMESTAMP: [DataType.TIMESTAMP, DataType.DATE],
            DataType.FLOAT: [DataType.FLOAT, DataType.DECIMAL],
            DataType.DECIMAL: [DataType.DECIMAL, DataType.FLOAT],
        }
    
    def should_randomize(self, episode_number: int) -> bool:
        """Determine if schema should be randomized this episode"""
        for interval, change_type in self.schedule.items():
            if episode_number > 0 and episode_number % interval == 0:
                return True
        return False
    
    def get_randomization_type(self, episode_number: int) -> str:
        """Get the type of randomization to apply"""
        # Check from largest to smallest interval
        for interval in sorted(self.schedule.keys(), reverse=True):
            if episode_number % interval == 0:
                return self.schedule[interval]
        return "none"
    
    def generate_schema_variant(self, episode_number: int, base_variant: str = None) -> DatabaseSchema:
        """
        Generate new schema variant based on episode
        
        Args:
            episode_number: Current episode number
            base_variant: Base schema to vary from (if None, picks randomly)
            
        Returns:
            New schema variant
        """
        randomization_type = self.get_randomization_type(episode_number)
        
        if randomization_type == "minor":
            return self._apply_minor_variations(base_variant)
        elif randomization_type == "major":
            return self._apply_major_variations(base_variant)
        elif randomization_type == "complete":
            return self._complete_schema_redesign()
        else:
            # No randomization needed
            if self.current_schema:
                return self.current_schema
            else:
                return list(self.variants.values())[0]
    
    def _apply_minor_variations(self, base_variant: str = None) -> DatabaseSchema:
        """Apply minor variations like column name changes and data type adjustments"""
        base_schema = self._get_base_schema(base_variant)
        new_schema = copy.deepcopy(base_schema)
        
        # Change 20-40% of column names
        total_columns = sum(len(table.columns) for table in new_schema.tables)
        num_changes = random.randint(int(total_columns * 0.2), int(total_columns * 0.4))
        
        changes_made = 0
        attempts = 0
        max_attempts = total_columns * 2
        
        while changes_made < num_changes and attempts < max_attempts:
            attempts += 1
            
            # Pick random table and column
            table = random.choice(new_schema.tables)
            column = random.choice(table.columns)
            
            # Skip primary keys and already changed columns
            if column.primary_key or hasattr(column, '_changed'):
                continue
            
            # Try to find a variant for this column name
            original_name = self._get_original_column_name(column.name)
            if original_name in self.column_name_variants:
                variants = self.column_name_variants[original_name]
                new_name = random.choice([v for v in variants if v != column.name])
                column.name = new_name
                column._changed = True
                changes_made += 1
                
                # Also update foreign key references
                self._update_foreign_key_references(new_schema, table.name, original_name, new_name)
        
        # Apply some data type variations (5-10% of columns)
        type_changes = random.randint(int(total_columns * 0.05), int(total_columns * 0.1))
        type_changes_made = 0
        
        for table in new_schema.tables:
            for column in table.columns:
                if type_changes_made >= type_changes:
                    break
                    
                if column.primary_key or column.foreign_key:
                    continue
                    
                if column.data_type in self.data_type_variants:
                    variants = self.data_type_variants[column.data_type]
                    if len(variants) > 1:
                        new_type = random.choice([t for t in variants if t != column.data_type])
                        column.data_type = new_type
                        type_changes_made += 1
        
        # Update schema metadata
        new_schema.variant_name = f"{base_schema.variant_name}_minor_v{len(self.variation_history) + 1}"
        new_schema.description = f"Minor variation of {base_schema.description}"
        
        self._record_variation("minor", new_schema, base_schema)
        return new_schema
    
    def _apply_major_variations(self, base_variant: str = None) -> DatabaseSchema:
        """Apply major structural changes like table relationships and optional columns"""
        base_schema = self._get_base_schema(base_variant)
        new_schema = copy.deepcopy(base_schema)
        
        # First apply minor variations
        minor_schema = self._apply_minor_variations(base_variant)
        new_schema = copy.deepcopy(minor_schema)
        
        # Add/remove optional columns (10-20% of tables)
        num_table_changes = random.randint(1, max(1, len(new_schema.tables) // 3))
        
        for _ in range(num_table_changes):
            table = random.choice(new_schema.tables)
            
            if random.random() < 0.6:  # 60% chance to add column
                self._add_optional_column(table)
            else:  # 40% chance to remove optional column
                self._remove_optional_column(table)
        
        # Modify some table relationships (change foreign key structures)
        self._modify_table_relationships(new_schema)
        
        # Update schema metadata
        new_schema.variant_name = f"{base_schema.variant_name}_major_v{len(self.variation_history) + 1}"
        new_schema.description = f"Major variation of {base_schema.description}"
        
        self._record_variation("major", new_schema, base_schema)
        return new_schema
    
    def _complete_schema_redesign(self) -> DatabaseSchema:
        """Complete schema redesign with different medical focus"""
        # Pick a different base variant than current
        available_variants = list(self.variants.keys())
        if self.current_schema and self.current_schema.variant_name in available_variants:
            available_variants.remove(self.current_schema.variant_name)
        
        new_base = random.choice(available_variants)
        new_schema = copy.deepcopy(self.variants[new_base])
        
        # Apply some randomization to the new base
        randomized_schema = self._apply_minor_variations(new_base)
        
        # Update metadata
        randomized_schema.variant_name = f"{new_base}_complete_v{len(self.variation_history) + 1}"
        randomized_schema.description = f"Complete redesign based on {new_base}"
        
        self._record_variation("complete", randomized_schema, new_schema)
        return randomized_schema
    
    def _get_base_schema(self, base_variant: str = None) -> DatabaseSchema:
        """Get base schema for variations"""
        if base_variant and base_variant in self.variants:
            return self.variants[base_variant]
        elif self.current_schema:
            # Find the original base variant for current schema
            for variant_name, schema in self.variants.items():
                if self.current_schema.variant_name.startswith(variant_name):
                    return schema
        
        # Default to first available variant
        return list(self.variants.values())[0]
    
    def _get_original_column_name(self, current_name: str) -> str:
        """Map current column name back to original for finding variants"""
        for original, variants in self.column_name_variants.items():
            if current_name in variants:
                return original
        return current_name
    
    def _update_foreign_key_references(self, schema: DatabaseSchema, table_name: str, 
                                     old_column: str, new_column: str):
        """Update foreign key references when column names change"""
        old_fk = f"{table_name}.{old_column}"
        new_fk = f"{table_name}.{new_column}"
        
        for table in schema.tables:
            for column in table.columns:
                if column.foreign_key == old_fk:
                    column.foreign_key = new_fk
    
    def _add_optional_column(self, table: Table):
        """Add an optional column to a table"""
        # Define some optional columns that could be added
        optional_columns_by_table_type = {
            "patient": [
                Column("middle_name", DataType.VARCHAR, max_length=50),
                Column("emergency_contact", DataType.VARCHAR, max_length=100),
                Column("preferred_language", DataType.VARCHAR, max_length=20),
                Column("marital_status", DataType.VARCHAR, max_length=20),
            ],
            "condition": [
                Column("onset_date", DataType.DATE),
                Column("resolved_date", DataType.DATE),
                Column("treatment_plan", DataType.TEXT),
                Column("follow_up_required", DataType.BOOLEAN),
            ],
            "medication": [
                Column("pharmacy_name", DataType.VARCHAR, max_length=100),
                Column("refills_remaining", DataType.INTEGER),
                Column("side_effects_noted", DataType.TEXT),
            ],
            "vital": [
                Column("bmi", DataType.FLOAT),
                Column("oxygen_saturation", DataType.INTEGER),
                Column("respiratory_rate", DataType.INTEGER),
            ],
            "appointment": [
                Column("copay_amount", DataType.DECIMAL),
                Column("insurance_verified", DataType.BOOLEAN),
                Column("followup_needed", DataType.BOOLEAN),
            ],
            "activity": [
                Column("device_type", DataType.VARCHAR, max_length=50),
                Column("sync_timestamp", DataType.TIMESTAMP),
                Column("data_quality_score", DataType.FLOAT),
            ],
            "lab": [
                Column("lab_facility", DataType.VARCHAR, max_length=100),
                Column("rush_order", DataType.BOOLEAN),
                Column("technician_notes", DataType.TEXT),
            ]
        }
        
        # Determine table type
        table_type = None
        table_lower = table.name.lower()
        for key in optional_columns_by_table_type.keys():
            if key in table_lower:
                table_type = key
                break
        
        if table_type and optional_columns_by_table_type[table_type]:
            # Add a random optional column
            new_column = copy.deepcopy(random.choice(optional_columns_by_table_type[table_type]))
            
            # Make sure column name doesn't already exist
            existing_names = [col.name for col in table.columns]
            if new_column.name not in existing_names:
                table.columns.append(new_column)
    
    def _remove_optional_column(self, table: Table):
        """Remove an optional column from a table"""
        # Find non-essential columns that can be removed
        removable_columns = []
        
        for column in table.columns:
            if (not column.primary_key and 
                not column.foreign_key and 
                column.nullable and 
                not any(keyword in column.name.lower() for keyword in ["name", "id", "date"])):
                removable_columns.append(column)
        
        if removable_columns:
            column_to_remove = random.choice(removable_columns)
            table.columns.remove(column_to_remove)
    
    def _modify_table_relationships(self, schema: DatabaseSchema):
        """Modify foreign key relationships between tables"""
        # This is a complex operation, so we'll do simple modifications
        # In a full implementation, you might completely restructure relationships
        
        # For now, we'll just modify some foreign key column names
        for table in schema.tables:
            for column in table.columns:
                if column.foreign_key and random.random() < 0.3:  # 30% chance to modify
                    # Change the foreign key column name slightly
                    if "_id" in column.name:
                        base_name = column.name.replace("_id", "")
                        new_variants = [f"{base_name}_ref", f"{base_name}_key", f"ref_{base_name}"]
                        column.name = random.choice(new_variants)
    
    def _record_variation(self, variation_type: str, new_schema: DatabaseSchema, base_schema: DatabaseSchema):
        """Record schema variation for tracking"""
        variation_record = {
            "type": variation_type,
            "episode": len(self.variation_history) + 1,
            "base_variant": base_schema.variant_name,
            "new_variant": new_schema.variant_name,
            "timestamp": random.randint(1000000, 9999999),  # Simplified timestamp
            "changes": self._compare_schemas(base_schema, new_schema)
        }
        
        self.variation_history.append(variation_record)
        self.current_schema = new_schema
    
    def _compare_schemas(self, old_schema: DatabaseSchema, new_schema: DatabaseSchema) -> Dict[str, Any]:
        """Compare two schemas and return differences"""
        changes = {
            "column_name_changes": [],
            "data_type_changes": [],
            "columns_added": [],
            "columns_removed": [],
            "table_changes": []
        }
        
        # Compare tables by matching similar names
        old_tables = {table.name: table for table in old_schema.tables}
        new_tables = {table.name: table for table in new_schema.tables}
        
        # For simplicity, assume table mapping based on position
        for i, (old_table, new_table) in enumerate(zip(old_schema.tables, new_schema.tables)):
            # Compare columns
            old_cols = {col.name: col for col in old_table.columns}
            new_cols = {col.name: col for col in new_table.columns}
            
            for old_name, old_col in old_cols.items():
                if old_name not in new_cols:
                    # Column was renamed or removed
                    # Try to find by position
                    if len(old_table.columns) == len(new_table.columns):
                        old_pos = [c.name for c in old_table.columns].index(old_name)
                        new_name = new_table.columns[old_pos].name
                        if old_name != new_name:
                            changes["column_name_changes"].append({
                                "table": old_table.name,
                                "old_name": old_name,
                                "new_name": new_name
                            })
                    else:
                        changes["columns_removed"].append({
                            "table": old_table.name,
                            "column": old_name
                        })
            
            # Check for added columns
            if len(new_table.columns) > len(old_table.columns):
                for new_col in new_table.columns:
                    if new_col.name not in old_cols:
                        changes["columns_added"].append({
                            "table": new_table.name,
                            "column": new_col.name,
                            "type": new_col.data_type.value
                        })
        
        return changes
    
    def get_variation_history(self) -> List[Dict[str, Any]]:
        """Get history of schema variations"""
        return self.variation_history
    
    def reset_history(self):
        """Reset variation history"""
        self.variation_history = []
        self.current_schema = None


class GroundTruthGenerator:
    """Generates ground truth results for any schema variant"""
    
    def __init__(self, schema_randomizer: SchemaRandomizer):
        self.schema_randomizer = schema_randomizer
        self.data_generator = MedicalDataGenerator()
    
    def generate_ground_truth(self, task: Dict[str, Any], current_schema: DatabaseSchema) -> List[Dict[str, Any]]:
        """
        Generate ground truth results for current schema variant
        
        Args:
            task: Query task definition
            current_schema: Current database schema
            
        Returns:
            Ground truth results that should match regardless of SQL approach
        """
        # This would execute a canonical query against the current database
        # For now, return mock results based on task type
        
        task_type = task.get("level", 1)
        
        if task_type == 1:  # Basic retrieval
            return self._generate_basic_retrieval_truth(task, current_schema)
        elif task_type == 2:  # Aggregations
            return self._generate_aggregation_truth(task, current_schema)
        elif task_type == 3:  # Joins
            return self._generate_join_truth(task, current_schema)
        elif task_type == 4:  # Complex analytics
            return self._generate_complex_truth(task, current_schema)
        else:  # Natural language
            return self._generate_nl_truth(task, current_schema)
    
    def _generate_basic_retrieval_truth(self, task: Dict, schema: DatabaseSchema) -> List[Dict]:
        """Generate ground truth for basic retrieval queries"""
        # This would execute the actual query against the database
        # For now, return mock realistic results
        return [
            {"condition_name": "Type 2 Diabetes", "diagnosis_date": "2020-03-15", "severity": "moderate"},
            {"condition_name": "Hypertension", "diagnosis_date": "2019-08-22", "severity": "mild"}
        ]
    
    def _generate_aggregation_truth(self, task: Dict, schema: DatabaseSchema) -> List[Dict]:
        """Generate ground truth for aggregation queries"""
        return [{"avg_steps": 6847.23}]
    
    def _generate_join_truth(self, task: Dict, schema: DatabaseSchema) -> List[Dict]:
        """Generate ground truth for join queries"""
        return [
            {"patient_name": "John Doe", "condition_count": 3},
            {"patient_name": "Jane Smith", "condition_count": 1}
        ]
    
    def _generate_complex_truth(self, task: Dict, schema: DatabaseSchema) -> List[Dict]:
        """Generate ground truth for complex analytics"""
        return [
            {"visit_status": "visit_day", "avg_steps": 5234.12},
            {"visit_status": "no_visit", "avg_steps": 7891.45}
        ]
    
    def _generate_nl_truth(self, task: Dict, schema: DatabaseSchema) -> List[Dict]:
        """Generate ground truth for natural language queries"""
        return [{"result": "Complex NL query result"}]
