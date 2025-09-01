"""
Database schema definitions for medical SQL RL environment.

Defines multiple schema variants with different table structures, column names,
and relationships to ensure agent robustness across database designs.
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum


class DataType(Enum):
    """Supported data types across schema variations"""
    INTEGER = "INTEGER"
    VARCHAR = "VARCHAR"
    TEXT = "TEXT"
    DATE = "DATE"
    TIMESTAMP = "TIMESTAMP"
    FLOAT = "FLOAT"
    DECIMAL = "DECIMAL"
    BOOLEAN = "BOOLEAN"


@dataclass
class Column:
    """Column definition with name, type, and constraints"""
    name: str
    data_type: DataType
    max_length: int = None
    nullable: bool = True
    primary_key: bool = False
    foreign_key: str = None  # Format: "table.column"
    unique: bool = False


@dataclass
class Table:
    """Table definition with columns and constraints"""
    name: str
    columns: List[Column]
    
    def get_create_sql(self) -> str:
        """Generate CREATE TABLE SQL statement"""
        columns_sql = []
        
        for col in self.columns:
            col_def = f"{col.name} {col.data_type.value}"
            
            if col.data_type == DataType.VARCHAR and col.max_length:
                col_def += f"({col.max_length})"
            
            if col.primary_key:
                col_def += " PRIMARY KEY"
            elif not col.nullable:
                col_def += " NOT NULL"
                
            if col.unique:
                col_def += " UNIQUE"
                
            columns_sql.append(col_def)
        
        # Add foreign key constraints
        for col in self.columns:
            if col.foreign_key:
                fk_table, fk_column = col.foreign_key.split(".")
                columns_sql.append(
                    f"FOREIGN KEY ({col.name}) REFERENCES {fk_table}({fk_column})"
                )
        
        return f"CREATE TABLE {self.name} (\n    {',\\n    '.join(columns_sql)}\n);"


@dataclass 
class DatabaseSchema:
    """Complete database schema with multiple tables"""
    variant_name: str
    tables: List[Table]
    description: str
    
    def get_all_create_statements(self) -> List[str]:
        """Get CREATE statements for all tables in dependency order"""
        return [table.get_create_sql() for table in self.tables]
    
    def get_table_by_name(self, name: str) -> Table:
        """Get table by name"""
        for table in self.tables:
            if table.name == name:
                return table
        raise ValueError(f"Table {name} not found in schema {self.variant_name}")


# Schema Variant 1: Medical Clinic
MEDICAL_CLINIC_V1 = DatabaseSchema(
    variant_name="medical_clinic_v1",
    description="Standard medical clinic database schema",
    tables=[
        Table(
            name="patients",
            columns=[
                Column("patient_id", DataType.INTEGER, primary_key=True),
                Column("first_name", DataType.VARCHAR, max_length=50, nullable=False),
                Column("last_name", DataType.VARCHAR, max_length=50, nullable=False),
                Column("date_of_birth", DataType.DATE, nullable=False),
                Column("gender", DataType.VARCHAR, max_length=10),
                Column("phone", DataType.VARCHAR, max_length=15),
                Column("email", DataType.VARCHAR, max_length=100),
                Column("address", DataType.TEXT),
                Column("insurance_id", DataType.VARCHAR, max_length=50),
                Column("created_at", DataType.TIMESTAMP),
            ]
        ),
        Table(
            name="conditions",
            columns=[
                Column("condition_id", DataType.INTEGER, primary_key=True),
                Column("patient_id", DataType.INTEGER, foreign_key="patients.patient_id", nullable=False),
                Column("condition_name", DataType.VARCHAR, max_length=100, nullable=False),
                Column("icd_10_code", DataType.VARCHAR, max_length=10),
                Column("diagnosis_date", DataType.DATE, nullable=False),
                Column("severity", DataType.VARCHAR, max_length=20),
                Column("status", DataType.VARCHAR, max_length=20),  # active, resolved, chronic
                Column("diagnosed_by", DataType.INTEGER),  # doctor_id
                Column("notes", DataType.TEXT),
            ]
        ),
        Table(
            name="medications",
            columns=[
                Column("medication_id", DataType.INTEGER, primary_key=True),
                Column("patient_id", DataType.INTEGER, foreign_key="patients.patient_id", nullable=False),
                Column("medication_name", DataType.VARCHAR, max_length=100, nullable=False),
                Column("generic_name", DataType.VARCHAR, max_length=100),
                Column("dosage", DataType.VARCHAR, max_length=50),
                Column("frequency", DataType.VARCHAR, max_length=50),
                Column("prescribed_date", DataType.DATE),
                Column("start_date", DataType.DATE),
                Column("end_date", DataType.DATE),
                Column("prescribed_by", DataType.INTEGER),  # doctor_id
                Column("status", DataType.VARCHAR, max_length=20),  # active, discontinued, completed
            ]
        ),
        Table(
            name="vitals",
            columns=[
                Column("vital_id", DataType.INTEGER, primary_key=True),
                Column("patient_id", DataType.INTEGER, foreign_key="patients.patient_id", nullable=False),
                Column("measurement_date", DataType.TIMESTAMP, nullable=False),
                Column("height_cm", DataType.FLOAT),
                Column("weight_kg", DataType.FLOAT),
                Column("blood_pressure_systolic", DataType.INTEGER),
                Column("blood_pressure_diastolic", DataType.INTEGER),
                Column("heart_rate", DataType.INTEGER),
                Column("temperature_celsius", DataType.FLOAT),
                Column("recorded_by", DataType.INTEGER),  # staff_id
            ]
        ),
        Table(
            name="appointments",
            columns=[
                Column("appointment_id", DataType.INTEGER, primary_key=True),
                Column("patient_id", DataType.INTEGER, foreign_key="patients.patient_id", nullable=False),
                Column("doctor_id", DataType.INTEGER),
                Column("appointment_date", DataType.TIMESTAMP, nullable=False),
                Column("appointment_type", DataType.VARCHAR, max_length=50),
                Column("duration_minutes", DataType.INTEGER),
                Column("status", DataType.VARCHAR, max_length=20),  # scheduled, completed, cancelled, no-show
                Column("notes", DataType.TEXT),
            ]
        ),
        Table(
            name="activity_data",
            columns=[
                Column("activity_id", DataType.INTEGER, primary_key=True),
                Column("patient_id", DataType.INTEGER, foreign_key="patients.patient_id", nullable=False),
                Column("date", DataType.DATE, nullable=False),
                Column("step_count", DataType.INTEGER),
                Column("sleep_hours", DataType.FLOAT),
                Column("calories_burned", DataType.INTEGER),
                Column("active_minutes", DataType.INTEGER),
                Column("heart_rate_avg", DataType.INTEGER),
            ]
        ),
        Table(
            name="lab_results",
            columns=[
                Column("lab_result_id", DataType.INTEGER, primary_key=True),
                Column("patient_id", DataType.INTEGER, foreign_key="patients.patient_id", nullable=False),
                Column("test_name", DataType.VARCHAR, max_length=100, nullable=False),
                Column("test_code", DataType.VARCHAR, max_length=20),
                Column("result_value", DataType.FLOAT),
                Column("result_unit", DataType.VARCHAR, max_length=20),
                Column("reference_range", DataType.VARCHAR, max_length=50),
                Column("status", DataType.VARCHAR, max_length=20),  # normal, abnormal, critical
                Column("test_date", DataType.TIMESTAMP, nullable=False),
                Column("ordered_by", DataType.INTEGER),  # doctor_id
            ]
        )
    ]
)

# Schema Variant 2: Hospital System (different naming conventions)
HOSPITAL_SYSTEM_V1 = DatabaseSchema(
    variant_name="hospital_system_v1", 
    description="Hospital system with different column names and structure",
    tables=[
        Table(
            name="patient_records",
            columns=[
                Column("id", DataType.INTEGER, primary_key=True),
                Column("fname", DataType.VARCHAR, max_length=50, nullable=False),
                Column("lname", DataType.VARCHAR, max_length=50, nullable=False),
                Column("birth_date", DataType.DATE, nullable=False),
                Column("sex", DataType.VARCHAR, max_length=1),  # M/F/O
                Column("contact_phone", DataType.VARCHAR, max_length=15),
                Column("contact_email", DataType.VARCHAR, max_length=100),
                Column("home_address", DataType.TEXT),
                Column("insurance_number", DataType.VARCHAR, max_length=50),
                Column("admission_timestamp", DataType.TIMESTAMP),
            ]
        ),
        Table(
            name="medical_conditions",
            columns=[
                Column("record_id", DataType.INTEGER, primary_key=True),
                Column("patient_record_id", DataType.INTEGER, foreign_key="patient_records.id", nullable=False),
                Column("condition_name", DataType.VARCHAR, max_length=100, nullable=False),
                Column("diagnostic_code", DataType.VARCHAR, max_length=10),
                Column("diagnosis_timestamp", DataType.TIMESTAMP, nullable=False),
                Column("severity_level", DataType.VARCHAR, max_length=20),
                Column("current_status", DataType.VARCHAR, max_length=20),
                Column("attending_physician", DataType.INTEGER),
                Column("clinical_notes", DataType.TEXT),
            ]
        ),
        Table(
            name="prescriptions",
            columns=[
                Column("prescription_id", DataType.INTEGER, primary_key=True),
                Column("patient_record_id", DataType.INTEGER, foreign_key="patient_records.id", nullable=False),
                Column("medication", DataType.VARCHAR, max_length=100, nullable=False),
                Column("generic_equivalent", DataType.VARCHAR, max_length=100),
                Column("dose", DataType.VARCHAR, max_length=50),
                Column("administration_schedule", DataType.VARCHAR, max_length=50),
                Column("prescription_date", DataType.DATE),
                Column("treatment_start", DataType.DATE),
                Column("treatment_end", DataType.DATE),
                Column("prescribing_physician", DataType.INTEGER),
                Column("prescription_status", DataType.VARCHAR, max_length=20),
            ]
        ),
        Table(
            name="vital_signs",
            columns=[
                Column("measurement_id", DataType.INTEGER, primary_key=True),
                Column("patient_record_id", DataType.INTEGER, foreign_key="patient_records.id", nullable=False),
                Column("recorded_at", DataType.TIMESTAMP, nullable=False),
                Column("height_centimeters", DataType.DECIMAL),
                Column("weight_kilograms", DataType.DECIMAL),
                Column("systolic_bp", DataType.INTEGER),
                Column("diastolic_bp", DataType.INTEGER),
                Column("pulse_rate", DataType.INTEGER),
                Column("body_temperature", DataType.DECIMAL),
                Column("measured_by_staff", DataType.INTEGER),
            ]
        ),
        Table(
            name="patient_visits",
            columns=[
                Column("visit_id", DataType.INTEGER, primary_key=True),
                Column("patient_record_id", DataType.INTEGER, foreign_key="patient_records.id", nullable=False),
                Column("physician_id", DataType.INTEGER),
                Column("visit_datetime", DataType.TIMESTAMP, nullable=False),
                Column("visit_category", DataType.VARCHAR, max_length=50),
                Column("session_duration", DataType.INTEGER),
                Column("visit_outcome", DataType.VARCHAR, max_length=20),
                Column("visit_summary", DataType.TEXT),
            ]
        ),
        Table(
            name="fitness_tracking",
            columns=[
                Column("tracking_id", DataType.INTEGER, primary_key=True),
                Column("patient_record_id", DataType.INTEGER, foreign_key="patient_records.id", nullable=False),
                Column("tracking_date", DataType.DATE, nullable=False),
                Column("daily_steps", DataType.INTEGER),
                Column("sleep_duration", DataType.DECIMAL),
                Column("energy_expenditure", DataType.INTEGER),
                Column("exercise_minutes", DataType.INTEGER),
                Column("average_heart_rate", DataType.INTEGER),
            ]
        ),
        Table(
            name="laboratory_tests",
            columns=[
                Column("test_id", DataType.INTEGER, primary_key=True),
                Column("patient_record_id", DataType.INTEGER, foreign_key="patient_records.id", nullable=False),
                Column("test_description", DataType.VARCHAR, max_length=100, nullable=False),
                Column("lab_code", DataType.VARCHAR, max_length=20),
                Column("numeric_result", DataType.DECIMAL),
                Column("measurement_unit", DataType.VARCHAR, max_length=20),
                Column("normal_range", DataType.VARCHAR, max_length=50),
                Column("result_classification", DataType.VARCHAR, max_length=20),
                Column("sample_collection_time", DataType.TIMESTAMP, nullable=False),
                Column("requesting_physician", DataType.INTEGER),
            ]
        )
    ]
)

# Schema Variant 3: Healthcare Network (more normalized, different relationships)
HEALTHCARE_NETWORK_V1 = DatabaseSchema(
    variant_name="healthcare_network_v1",
    description="Healthcare network with normalized design and different field names",
    tables=[
        Table(
            name="individuals",
            columns=[
                Column("person_id", DataType.INTEGER, primary_key=True),
                Column("given_name", DataType.VARCHAR, max_length=50, nullable=False),
                Column("family_name", DataType.VARCHAR, max_length=50, nullable=False),
                Column("date_of_birth", DataType.DATE, nullable=False),
                Column("gender_code", DataType.VARCHAR, max_length=10),
                Column("telephone", DataType.VARCHAR, max_length=15),
                Column("email", DataType.VARCHAR, max_length=100),
                Column("residential_address", DataType.TEXT),
                Column("coverage_id", DataType.VARCHAR, max_length=50),
                Column("registration_date", DataType.TIMESTAMP),
            ]
        ),
        Table(
            name="health_issues",
            columns=[
                Column("issue_id", DataType.INTEGER, primary_key=True),
                Column("individual_id", DataType.INTEGER, foreign_key="individuals.person_id", nullable=False),
                Column("issue_description", DataType.VARCHAR, max_length=100, nullable=False),
                Column("classification_code", DataType.VARCHAR, max_length=10),
                Column("identified_on", DataType.DATE, nullable=False),
                Column("severity_rating", DataType.VARCHAR, max_length=20),
                Column("management_status", DataType.VARCHAR, max_length=20),
                Column("care_provider", DataType.INTEGER),
                Column("clinical_observations", DataType.TEXT),
            ]
        ),
        Table(
            name="therapeutic_agents",
            columns=[
                Column("agent_id", DataType.INTEGER, primary_key=True),
                Column("individual_id", DataType.INTEGER, foreign_key="individuals.person_id", nullable=False),
                Column("agent_name", DataType.VARCHAR, max_length=100, nullable=False),
                Column("alternative_name", DataType.VARCHAR, max_length=100),
                Column("therapeutic_dose", DataType.VARCHAR, max_length=50),
                Column("dosing_regimen", DataType.VARCHAR, max_length=50),
                Column("therapy_initiated", DataType.DATE),
                Column("therapy_start", DataType.DATE),
                Column("therapy_conclusion", DataType.DATE),
                Column("prescriber", DataType.INTEGER),
                Column("therapy_status", DataType.VARCHAR, max_length=20),
            ]
        ),
        Table(
            name="biometric_data",
            columns=[
                Column("biometric_id", DataType.INTEGER, primary_key=True),
                Column("individual_id", DataType.INTEGER, foreign_key="individuals.person_id", nullable=False),
                Column("assessment_time", DataType.TIMESTAMP, nullable=False),
                Column("stature_cm", DataType.FLOAT),
                Column("mass_kg", DataType.FLOAT),
                Column("arterial_pressure_high", DataType.INTEGER),
                Column("arterial_pressure_low", DataType.INTEGER),
                Column("cardiac_frequency", DataType.INTEGER),
                Column("core_temperature", DataType.FLOAT),
                Column("assessor", DataType.INTEGER),
            ]
        ),
        Table(
            name="care_encounters",
            columns=[
                Column("encounter_id", DataType.INTEGER, primary_key=True),
                Column("individual_id", DataType.INTEGER, foreign_key="individuals.person_id", nullable=False),
                Column("healthcare_provider", DataType.INTEGER),
                Column("encounter_timestamp", DataType.TIMESTAMP, nullable=False),
                Column("service_type", DataType.VARCHAR, max_length=50),
                Column("contact_duration", DataType.INTEGER),
                Column("encounter_disposition", DataType.VARCHAR, max_length=20),
                Column("encounter_documentation", DataType.TEXT),
            ]
        ),
        Table(
            name="wellness_metrics",
            columns=[
                Column("metric_id", DataType.INTEGER, primary_key=True),
                Column("individual_id", DataType.INTEGER, foreign_key="individuals.person_id", nullable=False),
                Column("measurement_date", DataType.DATE, nullable=False),
                Column("ambulation_count", DataType.INTEGER),
                Column("rest_period_hours", DataType.FLOAT),
                Column("metabolic_expenditure", DataType.INTEGER),
                Column("physical_activity_duration", DataType.INTEGER),
                Column("cardiac_rhythm_mean", DataType.INTEGER),
            ]
        ),
        Table(
            name="diagnostic_results",
            columns=[
                Column("result_id", DataType.INTEGER, primary_key=True),
                Column("individual_id", DataType.INTEGER, foreign_key="individuals.person_id", nullable=False),
                Column("examination_name", DataType.VARCHAR, max_length=100, nullable=False),
                Column("procedure_code", DataType.VARCHAR, max_length=20),
                Column("quantitative_outcome", DataType.FLOAT),
                Column("unit_of_measure", DataType.VARCHAR, max_length=20),
                Column("reference_interval", DataType.VARCHAR, max_length=50),
                Column("clinical_significance", DataType.VARCHAR, max_length=20),
                Column("specimen_collection", DataType.TIMESTAMP, nullable=False),
                Column("ordering_provider", DataType.INTEGER),
            ]
        )
    ]
)

# Registry of all schema variants
SCHEMA_VARIANTS = {
    "medical_clinic_v1": MEDICAL_CLINIC_V1,
    "hospital_system_v1": HOSPITAL_SYSTEM_V1,
    "healthcare_network_v1": HEALTHCARE_NETWORK_V1,
}


def get_schema_variant(variant_name: str) -> DatabaseSchema:
    """Get schema variant by name"""
    if variant_name not in SCHEMA_VARIANTS:
        raise ValueError(f"Unknown schema variant: {variant_name}")
    return SCHEMA_VARIANTS[variant_name]


def list_schema_variants() -> List[str]:
    """List all available schema variants"""
    return list(SCHEMA_VARIANTS.keys())
