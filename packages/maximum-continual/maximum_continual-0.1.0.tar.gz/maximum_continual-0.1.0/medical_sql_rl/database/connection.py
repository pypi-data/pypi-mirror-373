"""
DuckDB connection and database management for medical SQL RL environment.

Handles database creation, schema setup, and connection management with
support for multiple schema variants and efficient switching between them.
"""

import duckdb
import os
import tempfile
from typing import Dict, List, Any, Optional
from pathlib import Path

from .schema import DatabaseSchema, get_schema_variant, SCHEMA_VARIANTS


class DatabaseManager:
    """Manages DuckDB connections and database lifecycle"""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize database manager
        
        Args:
            db_path: Path to database file. If None, creates temporary database
        """
        self.db_path = db_path
        self.connection: Optional[duckdb.DuckDBPyConnection] = None
        self.current_schema: Optional[DatabaseSchema] = None
        self.temp_dir = None
        
        if db_path is None:
            self.temp_dir = tempfile.mkdtemp()
            self.db_path = os.path.join(self.temp_dir, "medical_rl.db")
    
    def connect(self) -> duckdb.DuckDBPyConnection:
        """Establish database connection"""
        if self.connection is None:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            self.connection = duckdb.connect(self.db_path)
            
            # Configure DuckDB for optimal performance
            self.connection.execute("PRAGMA enable_progress_bar=false")
            self.connection.execute("PRAGMA threads=4")
            
        return self.connection
    
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def create_schema(self, schema: DatabaseSchema) -> None:
        """Create database schema from schema definition"""
        conn = self.connect()
        
        # Drop existing tables if they exist (in reverse dependency order)
        table_names = [table.name for table in reversed(schema.tables)]
        for table_name in table_names:
            conn.execute(f"DROP TABLE IF EXISTS {table_name}")
        
        # Create tables in dependency order
        for table in schema.tables:
            create_sql = table.get_create_sql()
            try:
                conn.execute(create_sql)
            except Exception as e:
                raise RuntimeError(f"Failed to create table {table.name}: {e}")
        
        self.current_schema = schema
        print(f"✅ Created database schema: {schema.variant_name}")
    
    def switch_schema(self, variant_name: str) -> None:
        """Switch to a different schema variant"""
        schema = get_schema_variant(variant_name)
        self.create_schema(schema)
    
    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """
        Execute SQL query and return results as list of dictionaries
        
        Args:
            query: SQL query to execute
            
        Returns:
            List of dictionaries representing query results
        """
        conn = self.connect()
        
        try:
            result = conn.execute(query)
            
            # Get column names
            columns = [desc[0] for desc in result.description]
            
            # Fetch all results and convert to list of dicts
            rows = result.fetchall()
            return [dict(zip(columns, row)) for row in rows]
            
        except Exception as e:
            raise RuntimeError(f"Query execution failed: {e}")
    
    def execute_statement(self, statement: str) -> None:
        """Execute SQL statement (INSERT, UPDATE, DELETE, etc.)"""
        conn = self.connect()
        
        try:
            conn.execute(statement)
            conn.commit()
        except Exception as e:
            raise RuntimeError(f"Statement execution failed: {e}")
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Get information about a table"""
        conn = self.connect()
        
        try:
            # Get column information
            result = conn.execute(f"PRAGMA table_info('{table_name}')")
            columns = []
            for row in result.fetchall():
                columns.append({
                    "name": row[1],
                    "type": row[2], 
                    "nullable": not row[3],
                    "default": row[4],
                    "primary_key": bool(row[5])
                })
            
            # Get row count
            count_result = conn.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = count_result.fetchone()[0]
            
            return {
                "table_name": table_name,
                "columns": columns,
                "row_count": row_count
            }
            
        except Exception as e:
            raise RuntimeError(f"Failed to get table info for {table_name}: {e}")
    
    def list_tables(self) -> List[str]:
        """List all tables in the database"""
        conn = self.connect()
        
        try:
            result = conn.execute("SHOW TABLES")
            return [row[0] for row in result.fetchall()]
        except Exception as e:
            raise RuntimeError(f"Failed to list tables: {e}")
    
    def get_schema_info(self) -> Dict[str, Any]:
        """Get comprehensive schema information"""
        if not self.current_schema:
            return {"error": "No schema loaded"}
        
        tables_info = {}
        for table_name in self.list_tables():
            tables_info[table_name] = self.get_table_info(table_name)
        
        return {
            "variant_name": self.current_schema.variant_name,
            "description": self.current_schema.description,
            "tables": tables_info
        }
    
    def clear_all_data(self) -> None:
        """Clear all data from all tables (keeping schema)"""
        if not self.current_schema:
            return
            
        conn = self.connect()
        
        # Delete in reverse dependency order to avoid foreign key constraints
        table_names = [table.name for table in reversed(self.current_schema.tables)]
        for table_name in table_names:
            try:
                conn.execute(f"DELETE FROM {table_name}")
            except Exception as e:
                print(f"⚠️  Warning: Could not clear table {table_name}: {e}")
        
        conn.commit()
        print("🗑️  Cleared all data from database")
    
    def get_foreign_key_relationships(self) -> Dict[str, List[Dict[str, str]]]:
        """Get foreign key relationships for all tables"""
        relationships = {}
        
        if not self.current_schema:
            return relationships
            
        for table in self.current_schema.tables:
            table_relationships = []
            for column in table.columns:
                if column.foreign_key:
                    ref_table, ref_column = column.foreign_key.split(".")
                    table_relationships.append({
                        "column": column.name,
                        "references_table": ref_table,
                        "references_column": ref_column
                    })
            relationships[table.name] = table_relationships
        
        return relationships
    
    def validate_schema(self) -> bool:
        """Validate that current database matches expected schema"""
        if not self.current_schema:
            return False
        
        try:
            db_tables = set(self.list_tables())
            schema_tables = set(table.name for table in self.current_schema.tables)
            
            if db_tables != schema_tables:
                print(f"❌ Table mismatch. DB: {db_tables}, Schema: {schema_tables}")
                return False
                
            # Validate each table structure
            for table in self.current_schema.tables:
                table_info = self.get_table_info(table.name)
                db_columns = {col["name"]: col for col in table_info["columns"]}
                
                for column in table.columns:
                    if column.name not in db_columns:
                        print(f"❌ Missing column {column.name} in table {table.name}")
                        return False
                        
            return True
            
        except Exception as e:
            print(f"❌ Schema validation failed: {e}")
            return False
    
    def backup_database(self, backup_path: str) -> None:
        """Create backup of current database"""
        conn = self.connect()
        
        try:
            conn.execute(f"EXPORT DATABASE '{backup_path}'")
            print(f"📦 Database backed up to {backup_path}")
        except Exception as e:
            raise RuntimeError(f"Backup failed: {e}")
    
    def __del__(self):
        """Cleanup on deletion"""
        self.disconnect()
        
        # Clean up temporary directory if created
        if self.temp_dir and os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)


def create_database_manager(schema_variant: str = "medical_clinic_v1", 
                          db_path: Optional[str] = None) -> DatabaseManager:
    """
    Convenience function to create and initialize database manager
    
    Args:
        schema_variant: Name of schema variant to use
        db_path: Optional path to database file
        
    Returns:
        Initialized DatabaseManager instance
    """
    manager = DatabaseManager(db_path)
    schema = get_schema_variant(schema_variant)
    manager.create_schema(schema)
    return manager
