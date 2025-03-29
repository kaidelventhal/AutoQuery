# agent_tools.py
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from database import get_db_instance # Import the singleton getter

# Get the database instance (it will be created on first call)
try:
    db_instance = get_db_instance()
except Exception as e:
    # Handle critical failure during initial DB setup (e.g., GCS download failed)
    print(f"FATAL: Failed to initialize Database in agent_tools: {e}")
    db_instance = None

class SQLQueryInput(BaseModel):
    query: str = Field(..., description="The SQL query to execute on the in-memory automotive database (using pandasql syntax).")

@tool(args_schema=SQLQueryInput)
def execute_sql(query: str) -> str:
    """
    Execute the provided SQL query on the in-memory pandas DataFrames
    representing the automotive database using pandasql.
    Returns the results as a CSV formatted string.
    Handles potential database initialization or query errors.
    """
    if db_instance is None:
        # This suggests the initial data loading failed critically
        return "Database Error: DataFrames not available. Check application startup logs."
    try:
        # The run_query method should handle pandasql errors and return a string
        result = db_instance.run_query(query)
        return result
    except Exception as e:
        # Catch any unexpected errors during the query execution itself
        error_msg = f"Unexpected error during pandasql query execution: {str(e)}"
        print(error_msg)
        return error_msg

# List of tools for the agent
tools = [execute_sql]