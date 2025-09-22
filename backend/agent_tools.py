from pydantic import BaseModel, Field
from langchain.agents import tool
from database import Database

db_instance: Database | None = None
VALID_TABLES = ["vehicle_ads", "price_table", "sales_table", "basic_table", "trim_table"]

def set_database_instance(db: Database):
    global db_instance
    db_instance = db

@tool
def execute_sql(query: str) -> str:
    """Executes a SQL query and returns the result as CSV."""
    if db_instance is None:
        return "Error: Database not initialized"
    
    if not query.strip().upper().startswith("SELECT"):
        return f"Error: Only SELECT queries are allowed."

    try:
        result = db_instance.run_query(query)
        return result
    except Exception as e:
        return f"SQL Execution Error: {str(e)}"

@tool
def get_table_schema(table_name: str) -> str:
    """Returns the schema for a given table."""
    if db_instance is None:
        return "Error: Database not initialized."
    if table_name not in VALID_TABLES:
        return f"Error: Invalid table name '{table_name}'."
    query = f"PRAGMA table_info('{table_name}');"
    return db_instance.run_query(query)

@tool
def get_distinct_values(table_name: str, column_name: str) -> str:
    """Returns distinct values from a table's column."""
    if db_instance is None:
        return "Error: Database not initialized."
    if table_name not in VALID_TABLES:
        return f"Error: Invalid table name '{table_name}'."
    query = f'SELECT DISTINCT "{column_name}" FROM "{table_name}" WHERE "{column_name}" IS NOT NULL LIMIT 10;'
    return db_instance.run_query(query)