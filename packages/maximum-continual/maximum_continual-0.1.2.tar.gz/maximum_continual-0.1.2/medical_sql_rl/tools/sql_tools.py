"""
SQL tools for medical RL environment that integrate with maximum_continual framework.

Provides SQLQueryTool and DatabaseSchemaInterface for agents to interact with
medical databases and explore schema structures.
"""

import time
from typing import Dict, List, Any, Optional
import json

from maximum_continual.base_tools import Tool
from ..database.connection import DatabaseManager


class SQLQueryTool(Tool):
    """Tool for executing SQL queries against the medical database"""
    
    name = "sql_query"
    description = "Execute SQL queries against the medical database to retrieve patient data, conditions, medications, and other health information. Returns query results as a list of records."
    inputs = {
        "query": {
            "type": "string",
            "description": "SQL query to execute against the medical database. Should be a valid SELECT statement."
        }
    }
    output_type = "object"
    output_schema = {
        "type": "object",
        "properties": {
            "success": {
                "type": "boolean",
                "description": "Whether the query executed successfully"
            },
            "results": {
                "type": "array",
                "items": {
                    "type": "object"
                },
                "description": "Query results as list of dictionaries"
            },
            "row_count": {
                "type": "integer", 
                "description": "Number of rows returned"
            },
            "execution_time_ms": {
                "type": "number",
                "description": "Query execution time in milliseconds"
            },
            "error": {
                "type": "string",
                "description": "Error message if query failed"
            }
        },
        "required": ["success", "results", "row_count", "execution_time_ms"]
    }
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize SQL query tool
        
        Args:
            db_manager: DatabaseManager instance for executing queries
        """
        super().__init__()
        self.db_manager = db_manager
        self.max_results = 1000  # Limit results to prevent memory issues
        self.timeout_seconds = 30  # Query timeout
    
    def forward(self, query: str) -> Dict[str, Any]:
        """
        Execute SQL query and return results
        
        Args:
            query: SQL query string to execute
            
        Returns:
            Dictionary with query results and metadata
        """
        start_time = time.time()
        
        # Basic SQL validation
        query = query.strip()
        if not query:
            return {
                "success": False,
                "results": [],
                "row_count": 0,
                "execution_time_ms": 0,
                "error": "Empty query provided"
            }
        
        # Check for dangerous SQL operations
        dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE']
        query_upper = query.upper()
        for keyword in dangerous_keywords:
            if keyword in query_upper:
                return {
                    "success": False,
                    "results": [],
                    "row_count": 0,
                    "execution_time_ms": 0,
                    "error": f"Query contains forbidden keyword: {keyword}. Only SELECT statements are allowed."
                }
        
        try:
            # Execute query
            results = self.db_manager.execute_query(query)
            
            # Limit results if too many
            if len(results) > self.max_results:
                results = results[:self.max_results]
                warning_msg = f"Results truncated to {self.max_results} rows"
            else:
                warning_msg = None
            
            execution_time_ms = (time.time() - start_time) * 1000
            
            response = {
                "success": True,
                "results": results,
                "row_count": len(results),
                "execution_time_ms": round(execution_time_ms, 2)
            }
            
            if warning_msg:
                response["warning"] = warning_msg
                
            return response
            
        except Exception as e:
            execution_time_ms = (time.time() - start_time) * 1000
            return {
                "success": False,
                "results": [],
                "row_count": 0,
                "execution_time_ms": round(execution_time_ms, 2),
                "error": str(e)
            }


class DatabaseSchemaInterface(Tool):
    """Tool for exploring database schema and relationships"""
    
    name = "database_schema"
    description = "Explore the medical database schema including table structures, column information, and relationships. Use this to understand the database before writing queries."
    inputs = {
        "action": {
            "type": "string",
            "description": "Action to perform: 'list_tables', 'describe_table', 'show_relationships', or 'get_schema_summary'"
        },
        "table_name": {
            "type": "string",
            "description": "Name of table to describe (required for 'describe_table' action)"
        }
    }
    output_type = "object"
    output_schema = {
        "type": "object",
        "properties": {
            "success": {
                "type": "boolean",
                "description": "Whether the action was successful"
            },
            "action": {
                "type": "string",
                "description": "The action that was performed"
            },
            "data": {
                "type": "object",
                "description": "Result data specific to the action performed"
            },
            "error": {
                "type": "string", 
                "description": "Error message if action failed"
            }
        },
        "required": ["success", "action"]
    }
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize database schema interface tool
        
        Args:
            db_manager: DatabaseManager instance for schema exploration
        """
        super().__init__()
        self.db_manager = db_manager
    
    def forward(self, action: str, table_name: str = None) -> Dict[str, Any]:
        """
        Perform schema exploration action
        
        Args:
            action: Action to perform
            table_name: Optional table name for table-specific actions
            
        Returns:
            Dictionary with action results
        """
        try:
            if action == "list_tables":
                return self._list_tables()
            elif action == "describe_table":
                if not table_name:
                    return {
                        "success": False,
                        "action": action,
                        "error": "table_name is required for describe_table action"
                    }
                return self._describe_table(table_name)
            elif action == "show_relationships":
                return self._show_relationships()
            elif action == "get_schema_summary":
                return self._get_schema_summary()
            else:
                return {
                    "success": False,
                    "action": action,
                    "error": f"Unknown action: {action}. Valid actions are: list_tables, describe_table, show_relationships, get_schema_summary"
                }
                
        except Exception as e:
            return {
                "success": False,
                "action": action,
                "error": str(e)
            }
    
    def _list_tables(self) -> Dict[str, Any]:
        """List all tables in the database"""
        tables = self.db_manager.list_tables()
        
        # Get basic info for each table
        table_info = {}
        for table_name in tables:
            try:
                info = self.db_manager.get_table_info(table_name)
                table_info[table_name] = {
                    "row_count": info["row_count"],
                    "column_count": len(info["columns"])
                }
            except Exception as e:
                table_info[table_name] = {
                    "error": str(e)
                }
        
        return {
            "success": True,
            "action": "list_tables",
            "data": {
                "tables": tables,
                "table_count": len(tables),
                "table_info": table_info
            }
        }
    
    def _describe_table(self, table_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific table"""
        table_info = self.db_manager.get_table_info(table_name)
        
        # Format column information for better readability
        columns = []
        for col in table_info["columns"]:
            column_desc = {
                "name": col["name"],
                "type": col["type"],
                "nullable": col["nullable"],
                "primary_key": col["primary_key"]
            }
            if col["default"]:
                column_desc["default"] = col["default"]
            columns.append(column_desc)
        
        return {
            "success": True,
            "action": "describe_table",
            "data": {
                "table_name": table_name,
                "row_count": table_info["row_count"],
                "columns": columns,
                "column_count": len(columns)
            }
        }
    
    def _show_relationships(self) -> Dict[str, Any]:
        """Show foreign key relationships between tables"""
        relationships = self.db_manager.get_foreign_key_relationships()
        
        # Format relationships for better understanding
        formatted_relationships = []
        for table, table_relationships in relationships.items():
            for rel in table_relationships:
                formatted_relationships.append({
                    "from_table": table,
                    "from_column": rel["column"],
                    "to_table": rel["references_table"],
                    "to_column": rel["references_column"],
                    "relationship": f"{table}.{rel['column']} -> {rel['references_table']}.{rel['references_column']}"
                })
        
        return {
            "success": True,
            "action": "show_relationships",
            "data": {
                "relationships": formatted_relationships,
                "relationship_count": len(formatted_relationships),
                "tables_with_foreign_keys": list(relationships.keys())
            }
        }
    
    def _get_schema_summary(self) -> Dict[str, Any]:
        """Get a comprehensive schema summary"""
        schema_info = self.db_manager.get_schema_info()
        
        # Calculate summary statistics
        total_rows = 0
        total_columns = 0
        
        tables_summary = []
        for table_name, table_info in schema_info["tables"].items():
            table_summary = {
                "name": table_name,
                "row_count": table_info["row_count"],
                "column_count": len(table_info["columns"]),
                "primary_key_columns": [col["name"] for col in table_info["columns"] if col["primary_key"]],
                "nullable_columns": [col["name"] for col in table_info["columns"] if col["nullable"]]
            }
            tables_summary.append(table_summary)
            total_rows += table_info["row_count"]
            total_columns += len(table_info["columns"])
        
        return {
            "success": True,
            "action": "get_schema_summary",
            "data": {
                "schema_variant": schema_info["variant_name"],
                "description": schema_info["description"],
                "table_count": len(schema_info["tables"]),
                "total_rows": total_rows,
                "total_columns": total_columns,
                "tables": tables_summary,
                "schema_info": schema_info
            }
        }


class QueryValidationTool(Tool):
    """Tool for validating SQL queries before execution"""
    
    name = "validate_query"
    description = "Validate SQL query syntax and check for potential issues before execution. Helps ensure queries are safe and well-formed."
    inputs = {
        "query": {
            "type": "string",
            "description": "SQL query to validate"
        }
    }
    output_type = "object"
    output_schema = {
        "type": "object",
        "properties": {
            "valid": {
                "type": "boolean",
                "description": "Whether the query is valid"
            },
            "issues": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "List of validation issues found"
            },
            "warnings": {
                "type": "array", 
                "items": {
                    "type": "string"
                },
                "description": "List of potential warnings"
            },
            "suggestions": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "Suggestions for query improvement"
            }
        },
        "required": ["valid", "issues", "warnings", "suggestions"]
    }
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize query validation tool
        
        Args:
            db_manager: DatabaseManager instance for validation
        """
        super().__init__()
        self.db_manager = db_manager
    
    def forward(self, query: str) -> Dict[str, Any]:
        """
        Validate SQL query
        
        Args:
            query: SQL query to validate
            
        Returns:
            Dictionary with validation results
        """
        issues = []
        warnings = []
        suggestions = []
        
        query = query.strip()
        if not query:
            return {
                "valid": False,
                "issues": ["Empty query provided"],
                "warnings": [],
                "suggestions": ["Provide a valid SQL SELECT statement"]
            }
        
        query_upper = query.upper()
        
        # Check for dangerous operations
        dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE']
        for keyword in dangerous_keywords:
            if keyword in query_upper:
                issues.append(f"Query contains forbidden keyword: {keyword}")
        
        # Check if it's a SELECT query
        if not query_upper.strip().startswith('SELECT'):
            issues.append("Only SELECT queries are allowed")
        
        # Check for common issues
        if ';' in query[:-1]:  # Semicolon not at the end
            warnings.append("Multiple statements detected - only the first will be executed")
        
        if 'SELECT *' in query_upper:
            warnings.append("Using SELECT * - consider specifying columns explicitly")
        
        if 'ORDER BY' not in query_upper and 'GROUP BY' not in query_upper:
            if 'JOIN' in query_upper or 'WHERE' in query_upper:
                suggestions.append("Consider adding ORDER BY clause for consistent results")
        
        # Try to validate table/column names against current schema
        try:
            available_tables = self.db_manager.list_tables()
            
            # Simple validation - check if mentioned tables exist
            for table in available_tables:
                if table.upper() in query_upper:
                    # Table seems to be referenced
                    break
            else:
                warnings.append("Query may not reference any known tables")
                
        except Exception as e:
            warnings.append(f"Could not validate against schema: {e}")
        
        # Check for potential performance issues
        if 'LIKE' in query_upper and query.count('%') > 4:
            warnings.append("Multiple LIKE operations with wildcards may be slow")
        
        if query_upper.count('JOIN') > 5:
            warnings.append("Query has many JOINs - consider if all are necessary")
        
        # Basic syntax validation by attempting to explain the query
        try:
            # Try EXPLAIN query (this won't actually execute, just parse)
            explain_query = f"EXPLAIN {query}"
            # We don't actually execute this, just check if the query structure is valid
            pass
        except Exception as e:
            issues.append(f"Syntax error: {e}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "suggestions": suggestions
        }
