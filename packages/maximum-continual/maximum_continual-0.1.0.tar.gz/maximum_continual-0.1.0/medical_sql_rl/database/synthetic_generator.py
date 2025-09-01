"""
Synthetic medical data generator for SQL RL environment.

Generates realistic medical data across different schema variants with proper
relationships, medical accuracy, and statistical distributions.
"""

import random
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional
from faker import Faker
import numpy as np

from .schema import DatabaseSchema, SCHEMA_VARIANTS
from .connection import DatabaseManager


class MedicalDataGenerator:
    """Generates synthetic medical data with realistic relationships"""
    
    def __init__(self, seed: int = 42):
        """
        Initialize data generator
        
        Args:
            seed: Random seed for reproducible data generation
        """
        self.fake = Faker()
        self.fake.seed_instance(seed)
        random.seed(seed)
        np.random.seed(seed)
        
        # Medical data constants
        self.common_conditions = [
            ("Hypertension", "I10", ["mild", "moderate", "severe"]),
            ("Type 2 Diabetes", "E11.9", ["controlled", "moderate", "severe"]),
            ("Obesity", "E66.9", ["mild", "moderate", "severe"]),
            ("Hyperlipidemia", "E78.5", ["mild", "moderate"]),
            ("Asthma", "J45.9", ["mild", "moderate", "severe"]),
            ("Depression", "F32.9", ["mild", "moderate", "severe"]),
            ("Anxiety", "F41.9", ["mild", "moderate"]),
            ("Osteoarthritis", "M19.9", ["mild", "moderate", "severe"]),
            ("COPD", "J44.1", ["mild", "moderate", "severe"]),
            ("Atrial Fibrillation", "I48.91", ["controlled", "uncontrolled"]),
        ]
        
        self.medications = [
            ("Lisinopril", "ACE Inhibitor", ["5mg", "10mg", "20mg"]),
            ("Metformin", "Biguanide", ["500mg", "850mg", "1000mg"]),
            ("Atorvastatin", "Statin", ["10mg", "20mg", "40mg", "80mg"]),
            ("Albuterol", "Bronchodilator", ["90mcg", "108mcg"]),
            ("Sertraline", "SSRI", ["25mg", "50mg", "100mg"]),
            ("Omeprazole", "PPI", ["20mg", "40mg"]),
            ("Amlodipine", "CCB", ["2.5mg", "5mg", "10mg"]),
            ("Levothyroxine", "Thyroid Hormone", ["25mcg", "50mcg", "75mcg", "100mcg"]),
            ("Gabapentin", "Anticonvulsant", ["100mg", "300mg", "400mg"]),
            ("Ibuprofen", "NSAID", ["200mg", "400mg", "600mg", "800mg"]),
        ]
        
        self.lab_tests = [
            ("Complete Blood Count", "CBC", "cells/μL", (4000, 11000)),
            ("Basic Metabolic Panel", "BMP", "mg/dL", (70, 100)),
            ("Lipid Panel", "LIPID", "mg/dL", (100, 200)),
            ("Hemoglobin A1c", "HBA1C", "%", (4.0, 6.0)),
            ("Thyroid Stimulating Hormone", "TSH", "mIU/L", (0.4, 4.0)),
            ("Vitamin D", "VIT_D", "ng/mL", (30, 100)),
            ("Creatinine", "CREAT", "mg/dL", (0.6, 1.2)),
            ("Liver Function Panel", "LFT", "U/L", (10, 40)),
        ]
        
    def generate_patients(self, count: int, schema: DatabaseSchema) -> List[Dict[str, Any]]:
        """Generate patient records"""
        patients = []
        patient_table = schema.get_table_by_name(self._get_patient_table_name(schema))
        
        for i in range(1, count + 1):
            # Generate basic demographics
            gender = random.choice(["Male", "Female", "Other"])
            birth_date = self.fake.date_of_birth(minimum_age=18, maximum_age=95)
            
            patient_data = {}
            
            # Map fields based on schema variant
            for column in patient_table.columns:
                if column.primary_key:
                    patient_data[column.name] = i
                elif column.name in ["first_name", "fname", "given_name"]:
                    patient_data[column.name] = self.fake.first_name()
                elif column.name in ["last_name", "lname", "family_name"]:
                    patient_data[column.name] = self.fake.last_name()
                elif column.name in ["date_of_birth", "birth_date", "dob"]:
                    patient_data[column.name] = birth_date
                elif column.name in ["gender", "sex", "gender_code"]:
                    if "sex" in column.name and column.max_length == 1:
                        patient_data[column.name] = gender[0]  # M/F/O
                    else:
                        patient_data[column.name] = gender
                elif column.name in ["phone", "contact_phone", "telephone"]:
                    patient_data[column.name] = self.fake.phone_number()
                elif column.name in ["email", "contact_email"]:
                    patient_data[column.name] = self.fake.email()
                elif column.name in ["address", "home_address", "residential_address"]:
                    patient_data[column.name] = self.fake.address()
                elif column.name in ["insurance_id", "insurance_number", "coverage_id"]:
                    patient_data[column.name] = f"INS{random.randint(100000, 999999)}"
                elif column.name in ["created_at", "admission_timestamp", "registration_date"]:
                    patient_data[column.name] = datetime.now() - timedelta(days=random.randint(1, 365))
            
            patients.append(patient_data)
        
        return patients
    
    def generate_conditions(self, patients: List[Dict], schema: DatabaseSchema) -> List[Dict[str, Any]]:
        """Generate medical conditions for patients"""
        conditions = []
        condition_id = 1
        
        condition_table = schema.get_table_by_name(self._get_condition_table_name(schema))
        patient_id_field = self._get_patient_id_field(schema)
        
        for patient in patients:
            # Each patient has 0-4 conditions
            num_conditions = np.random.poisson(1.5)
            if num_conditions > 4:
                num_conditions = 4
                
            selected_conditions = random.sample(self.common_conditions, min(num_conditions, len(self.common_conditions)))
            
            for condition_name, icd_code, severities in selected_conditions:
                condition_data = {}
                
                for column in condition_table.columns:
                    if column.primary_key:
                        condition_data[column.name] = condition_id
                    elif column.foreign_key and patient_id_field in column.foreign_key:
                        condition_data[column.name] = patient[self._get_patient_id_field_name(schema)]
                    elif column.name in ["condition_name", "diagnosis", "issue_description"]:
                        condition_data[column.name] = condition_name
                    elif column.name in ["icd_10_code", "diagnostic_code", "classification_code"]:
                        condition_data[column.name] = icd_code
                    elif column.name in ["diagnosis_date", "date_diagnosed", "diagnosis_timestamp", "identified_on"]:
                        days_ago = random.randint(30, 1095)  # 1 month to 3 years ago
                        if "timestamp" in column.name:
                            condition_data[column.name] = datetime.now() - timedelta(days=days_ago)
                        else:
                            condition_data[column.name] = date.today() - timedelta(days=days_ago)
                    elif column.name in ["severity", "severity_level", "severity_rating"]:
                        condition_data[column.name] = random.choice(severities)
                    elif column.name in ["status", "current_status", "management_status"]:
                        condition_data[column.name] = random.choice(["active", "chronic", "resolved"])
                    elif column.name in ["diagnosed_by", "attending_physician", "care_provider"]:
                        condition_data[column.name] = random.randint(1, 20)  # Doctor IDs
                    elif column.name in ["notes", "clinical_notes", "clinical_observations"]:
                        condition_data[column.name] = f"Patient presents with {condition_name.lower()}"
                
                conditions.append(condition_data)
                condition_id += 1
        
        return conditions
    
    def generate_medications(self, patients: List[Dict], conditions: List[Dict], schema: DatabaseSchema) -> List[Dict[str, Any]]:
        """Generate medication records"""
        medications = []
        medication_id = 1
        
        medication_table = schema.get_table_by_name(self._get_medication_table_name(schema))
        patient_id_field_name = self._get_patient_id_field_name(schema)
        
        for patient in patients:
            # Each patient has 0-3 medications
            num_medications = np.random.poisson(1.0)
            if num_medications > 3:
                num_medications = 3
                
            selected_medications = random.sample(self.medications, min(num_medications, len(self.medications)))
            
            for med_name, generic, dosages in selected_medications:
                medication_data = {}
                
                for column in medication_table.columns:
                    if column.primary_key:
                        medication_data[column.name] = medication_id
                    elif column.foreign_key:
                        medication_data[column.name] = patient[patient_id_field_name]
                    elif column.name in ["medication_name", "drug_name", "medication", "agent_name"]:
                        medication_data[column.name] = med_name
                    elif column.name in ["generic_name", "generic_equivalent", "alternative_name"]:
                        medication_data[column.name] = generic
                    elif column.name in ["dosage", "dose", "therapeutic_dose"]:
                        medication_data[column.name] = random.choice(dosages)
                    elif column.name in ["frequency", "administration_schedule", "dosing_regimen"]:
                        medication_data[column.name] = random.choice(["Once daily", "Twice daily", "Three times daily", "As needed"])
                    elif column.name in ["prescribed_date", "prescription_date", "therapy_initiated"]:
                        days_ago = random.randint(1, 365)
                        medication_data[column.name] = date.today() - timedelta(days=days_ago)
                    elif column.name in ["start_date", "treatment_start", "therapy_start"]:
                        days_ago = random.randint(1, 365)
                        medication_data[column.name] = date.today() - timedelta(days=days_ago)
                    elif column.name in ["end_date", "treatment_end", "therapy_conclusion"]:
                        if random.random() < 0.3:  # 30% have end dates
                            days_future = random.randint(1, 180)
                            medication_data[column.name] = date.today() + timedelta(days=days_future)
                    elif column.name in ["prescribed_by", "prescribing_physician", "prescriber"]:
                        medication_data[column.name] = random.randint(1, 20)
                    elif column.name in ["status", "prescription_status", "therapy_status"]:
                        medication_data[column.name] = random.choice(["active", "discontinued", "completed"])
                
                medications.append(medication_data)
                medication_id += 1
        
        return medications
    
    def generate_vitals(self, patients: List[Dict], schema: DatabaseSchema) -> List[Dict[str, Any]]:
        """Generate vital signs data"""
        vitals = []
        vital_id = 1
        
        vital_table = schema.get_table_by_name(self._get_vital_table_name(schema))
        patient_id_field_name = self._get_patient_id_field_name(schema)
        
        for patient in patients:
            # Each patient has 3-8 vital measurements
            num_vitals = random.randint(3, 8)
            
            for _ in range(num_vitals):
                vital_data = {}
                
                # Generate realistic vital signs
                height_cm = np.random.normal(170, 15)  # Mean height 170cm, std 15cm
                weight_kg = np.random.normal(75, 20)   # Mean weight 75kg, std 20kg
                systolic_bp = np.random.normal(120, 20) 
                diastolic_bp = np.random.normal(80, 15)
                heart_rate = np.random.normal(75, 15)
                temperature = np.random.normal(36.8, 0.5)
                
                for column in vital_table.columns:
                    if column.primary_key:
                        vital_data[column.name] = vital_id
                    elif column.foreign_key:
                        vital_data[column.name] = patient[patient_id_field_name]
                    elif column.name in ["measurement_date", "recorded_at", "assessment_time"]:
                        days_ago = random.randint(1, 180)
                        if "timestamp" in column.name or "recorded_at" in column.name or "assessment_time" in column.name:
                            vital_data[column.name] = datetime.now() - timedelta(days=days_ago, hours=random.randint(0, 23))
                        else:
                            vital_data[column.name] = date.today() - timedelta(days=days_ago)
                    elif column.name in ["height_cm", "height_centimeters", "stature_cm"]:
                        vital_data[column.name] = max(150, min(200, round(height_cm, 1)))
                    elif column.name in ["weight_kg", "weight_kilograms", "mass_kg"]:
                        vital_data[column.name] = max(40, min(150, round(weight_kg, 1)))
                    elif column.name in ["blood_pressure_systolic", "systolic_bp", "arterial_pressure_high"]:
                        vital_data[column.name] = max(80, min(200, int(systolic_bp)))
                    elif column.name in ["blood_pressure_diastolic", "diastolic_bp", "arterial_pressure_low"]:
                        vital_data[column.name] = max(50, min(120, int(diastolic_bp)))
                    elif column.name in ["heart_rate", "pulse_rate", "cardiac_frequency"]:
                        vital_data[column.name] = max(50, min(120, int(heart_rate)))
                    elif column.name in ["temperature_celsius", "body_temperature", "core_temperature"]:
                        vital_data[column.name] = max(35.0, min(40.0, round(temperature, 1)))
                    elif column.name in ["recorded_by", "measured_by_staff", "assessor"]:
                        vital_data[column.name] = random.randint(1, 50)  # Staff IDs
                
                vitals.append(vital_data)
                vital_id += 1
        
        return vitals
    
    def generate_appointments(self, patients: List[Dict], schema: DatabaseSchema) -> List[Dict[str, Any]]:
        """Generate appointment/visit data"""
        appointments = []
        appointment_id = 1
        
        appointment_table = schema.get_table_by_name(self._get_appointment_table_name(schema))
        patient_id_field_name = self._get_patient_id_field_name(schema)
        
        for patient in patients:
            # Each patient has 2-6 appointments
            num_appointments = random.randint(2, 6)
            
            for _ in range(num_appointments):
                appointment_data = {}
                
                for column in appointment_table.columns:
                    if column.primary_key:
                        appointment_data[column.name] = appointment_id
                    elif column.foreign_key:
                        appointment_data[column.name] = patient[patient_id_field_name]
                    elif column.name in ["doctor_id", "physician_id", "healthcare_provider"]:
                        appointment_data[column.name] = random.randint(1, 20)
                    elif column.name in ["appointment_date", "visit_datetime", "encounter_timestamp"]:
                        days_ago = random.randint(1, 365)
                        appointment_data[column.name] = datetime.now() - timedelta(days=days_ago, hours=random.randint(8, 17))
                    elif column.name in ["appointment_type", "visit_category", "service_type"]:
                        appointment_data[column.name] = random.choice(["Annual Physical", "Follow-up", "Urgent Care", "Specialist Consult", "Lab Review"])
                    elif column.name in ["duration_minutes", "session_duration", "contact_duration"]:
                        appointment_data[column.name] = random.choice([15, 30, 45, 60])
                    elif column.name in ["status", "visit_outcome", "encounter_disposition"]:
                        appointment_data[column.name] = random.choice(["completed", "scheduled", "cancelled", "no-show"])
                    elif column.name in ["notes", "visit_summary", "encounter_documentation"]:
                        appointment_data[column.name] = "Routine visit completed without complications"
                
                appointments.append(appointment_data)
                appointment_id += 1
        
        return appointments
    
    def generate_activity_data(self, patients: List[Dict], schema: DatabaseSchema) -> List[Dict[str, Any]]:
        """Generate daily activity/fitness tracking data"""
        activities = []
        activity_id = 1
        
        activity_table = schema.get_table_by_name(self._get_activity_table_name(schema))
        patient_id_field_name = self._get_patient_id_field_name(schema)
        
        for patient in patients:
            # Generate 30-90 days of activity data per patient
            num_days = random.randint(30, 90)
            
            for day in range(num_days):
                activity_data = {}
                
                # Generate realistic activity patterns
                base_steps = np.random.normal(7500, 2500)  # Average daily steps
                sleep_hours = np.random.normal(7.5, 1.0)   # Sleep duration
                calories = base_steps * 0.04 + np.random.normal(0, 100)  # Rough calorie estimate
                
                for column in activity_table.columns:
                    if column.primary_key:
                        activity_data[column.name] = activity_id
                    elif column.foreign_key:
                        activity_data[column.name] = patient[patient_id_field_name]
                    elif column.name in ["date", "tracking_date", "measurement_date"]:
                        activity_data[column.name] = date.today() - timedelta(days=day)
                    elif column.name in ["step_count", "daily_steps", "ambulation_count"]:
                        activity_data[column.name] = max(0, int(base_steps))
                    elif column.name in ["sleep_hours", "sleep_duration", "rest_period_hours"]:
                        activity_data[column.name] = max(0, min(12, round(sleep_hours, 1)))
                    elif column.name in ["calories_burned", "energy_expenditure", "metabolic_expenditure"]:
                        activity_data[column.name] = max(0, int(calories))
                    elif column.name in ["active_minutes", "exercise_minutes", "physical_activity_duration"]:
                        activity_data[column.name] = random.randint(0, 120)
                    elif column.name in ["heart_rate_avg", "average_heart_rate", "cardiac_rhythm_mean"]:
                        activity_data[column.name] = random.randint(60, 100)
                
                activities.append(activity_data)
                activity_id += 1
        
        return activities
    
    def generate_lab_results(self, patients: List[Dict], schema: DatabaseSchema) -> List[Dict[str, Any]]:
        """Generate laboratory test results"""
        lab_results = []
        result_id = 1
        
        lab_table = schema.get_table_by_name(self._get_lab_table_name(schema))
        patient_id_field_name = self._get_patient_id_field_name(schema)
        
        for patient in patients:
            # Each patient has 3-8 lab results
            num_results = random.randint(3, 8)
            selected_tests = random.sample(self.lab_tests, min(num_results, len(self.lab_tests)))
            
            for test_name, test_code, unit, normal_range in selected_tests:
                result_data = {}
                
                # Generate result value within or outside normal range
                min_val, max_val = normal_range
                if random.random() < 0.8:  # 80% normal results
                    result_value = np.random.uniform(min_val, max_val)
                    status = "normal"
                else:  # 20% abnormal results
                    if random.random() < 0.5:
                        result_value = np.random.uniform(min_val * 0.5, min_val)  # Below normal
                    else:
                        result_value = np.random.uniform(max_val, max_val * 1.5)  # Above normal
                    status = "abnormal"
                
                for column in lab_table.columns:
                    if column.primary_key:
                        result_data[column.name] = result_id
                    elif column.foreign_key:
                        result_data[column.name] = patient[patient_id_field_name]
                    elif column.name in ["test_name", "test_description", "examination_name"]:
                        result_data[column.name] = test_name
                    elif column.name in ["test_code", "lab_code", "procedure_code"]:
                        result_data[column.name] = test_code
                    elif column.name in ["result_value", "numeric_result", "quantitative_outcome"]:
                        result_data[column.name] = round(result_value, 2)
                    elif column.name in ["result_unit", "measurement_unit", "unit_of_measure"]:
                        result_data[column.name] = unit
                    elif column.name in ["reference_range", "normal_range", "reference_interval"]:
                        result_data[column.name] = f"{min_val}-{max_val}"
                    elif column.name in ["status", "result_classification", "clinical_significance"]:
                        result_data[column.name] = status
                    elif column.name in ["test_date", "sample_collection_time", "specimen_collection"]:
                        days_ago = random.randint(1, 180)
                        result_data[column.name] = datetime.now() - timedelta(days=days_ago)
                    elif column.name in ["ordered_by", "requesting_physician", "ordering_provider"]:
                        result_data[column.name] = random.randint(1, 20)
                
                lab_results.append(result_data)
                result_id += 1
        
        return lab_results
    
    def populate_database(self, db_manager: DatabaseManager, num_patients: int = 100) -> Dict[str, int]:
        """
        Populate database with synthetic data
        
        Args:
            db_manager: DatabaseManager instance
            num_patients: Number of patients to generate
            
        Returns:
            Dictionary with counts of generated records
        """
        if not db_manager.current_schema:
            raise ValueError("Database manager must have a schema loaded")
        
        schema = db_manager.current_schema
        print(f"🏥 Generating synthetic medical data for {num_patients} patients...")
        
        # Generate data in dependency order
        patients = self.generate_patients(num_patients, schema)
        print(f"👥 Generated {len(patients)} patients")
        
        conditions = self.generate_conditions(patients, schema)
        print(f"🩺 Generated {len(conditions)} conditions")
        
        medications = self.generate_medications(patients, conditions, schema)
        print(f"💊 Generated {len(medications)} medications")
        
        vitals = self.generate_vitals(patients, schema)
        print(f"📊 Generated {len(vitals)} vital measurements")
        
        appointments = self.generate_appointments(patients, schema)
        print(f"📅 Generated {len(appointments)} appointments")
        
        activities = self.generate_activity_data(patients, schema)
        print(f"🏃 Generated {len(activities)} activity records")
        
        lab_results = self.generate_lab_results(patients, schema)
        print(f"🔬 Generated {len(lab_results)} lab results")
        
        # Insert data into database
        datasets = [
            (patients, self._get_patient_table_name(schema)),
            (conditions, self._get_condition_table_name(schema)),
            (medications, self._get_medication_table_name(schema)),
            (vitals, self._get_vital_table_name(schema)),
            (appointments, self._get_appointment_table_name(schema)),
            (activities, self._get_activity_table_name(schema)),
            (lab_results, self._get_lab_table_name(schema)),
        ]
        
        for data, table_name in datasets:
            self._insert_data(db_manager, table_name, data)
        
        counts = {
            "patients": len(patients),
            "conditions": len(conditions),
            "medications": len(medications),
            "vitals": len(vitals),
            "appointments": len(appointments),
            "activities": len(activities),
            "lab_results": len(lab_results),
        }
        
        print("✅ Database populated successfully!")
        return counts
    
    def _insert_data(self, db_manager: DatabaseManager, table_name: str, data: List[Dict]):
        """Insert data into database table"""
        if not data:
            return
            
        # Build INSERT statement
        columns = list(data[0].keys())
        placeholders = ", ".join(["?" for _ in columns])
        insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
        
        # Convert data to tuples for bulk insert
        values = []
        for record in data:
            value_tuple = tuple(record[col] for col in columns)
            values.append(value_tuple)
        
        conn = db_manager.connect()
        try:
            conn.executemany(insert_sql, values)
            conn.commit()
        except Exception as e:
            raise RuntimeError(f"Failed to insert data into {table_name}: {e}")
    
    # Helper methods to map table names across schema variants
    def _get_patient_table_name(self, schema: DatabaseSchema) -> str:
        """Get patient table name for given schema"""
        for table in schema.tables:
            if any(keyword in table.name.lower() for keyword in ["patient", "individual"]):
                return table.name
        raise ValueError(f"No patient table found in schema {schema.variant_name}")
    
    def _get_condition_table_name(self, schema: DatabaseSchema) -> str:
        """Get condition table name for given schema"""
        for table in schema.tables:
            if any(keyword in table.name.lower() for keyword in ["condition", "health", "issue"]):
                return table.name
        raise ValueError(f"No condition table found in schema {schema.variant_name}")
    
    def _get_medication_table_name(self, schema: DatabaseSchema) -> str:
        """Get medication table name for given schema"""
        for table in schema.tables:
            if any(keyword in table.name.lower() for keyword in ["medication", "prescription", "therapeutic", "agent"]):
                return table.name
        raise ValueError(f"No medication table found in schema {schema.variant_name}")
    
    def _get_vital_table_name(self, schema: DatabaseSchema) -> str:
        """Get vitals table name for given schema"""
        for table in schema.tables:
            if any(keyword in table.name.lower() for keyword in ["vital", "biometric"]):
                return table.name
        raise ValueError(f"No vital table found in schema {schema.variant_name}")
    
    def _get_appointment_table_name(self, schema: DatabaseSchema) -> str:
        """Get appointment table name for given schema"""
        for table in schema.tables:
            if any(keyword in table.name.lower() for keyword in ["appointment", "visit", "encounter"]):
                return table.name
        raise ValueError(f"No appointment table found in schema {schema.variant_name}")
    
    def _get_activity_table_name(self, schema: DatabaseSchema) -> str:
        """Get activity table name for given schema"""
        for table in schema.tables:
            if any(keyword in table.name.lower() for keyword in ["activity", "fitness", "wellness", "tracking"]):
                return table.name
        raise ValueError(f"No activity table found in schema {schema.variant_name}")
    
    def _get_lab_table_name(self, schema: DatabaseSchema) -> str:
        """Get lab results table name for given schema"""
        for table in schema.tables:
            if any(keyword in table.name.lower() for keyword in ["lab", "diagnostic", "test"]):
                return table.name
        raise ValueError(f"No lab table found in schema {schema.variant_name}")
    
    def _get_patient_id_field(self, schema: DatabaseSchema) -> str:
        """Get patient ID foreign key field reference"""
        patient_table = self._get_patient_table_name(schema)
        for table in schema.tables:
            if table.name == patient_table:
                for column in table.columns:
                    if column.primary_key:
                        return f"{patient_table}.{column.name}"
        raise ValueError(f"No patient ID field found in {patient_table}")
    
    def _get_patient_id_field_name(self, schema: DatabaseSchema) -> str:
        """Get patient ID field name"""
        patient_table = self._get_patient_table_name(schema)
        for table in schema.tables:
            if table.name == patient_table:
                for column in table.columns:
                    if column.primary_key:
                        return column.name
        raise ValueError(f"No patient ID field found in {patient_table}")
