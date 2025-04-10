# agent_tools.py
from pydantic import BaseModel, Field
from langchain.agents import tool
# Remove the incorrect import: from database import get_db_instance
from database import Database # Ensure Database class is imported if needed for type hinting, but not essential here

# This global variable will hold the database instance set by app.py
db_instance = None

def set_database_instance(db: Database):
    """Sets the shared database instance."""
    global db_instance
    print(f"Setting database instance in agent_tools: {type(db)}") # Add print for debugging
    db_instance = db

class SQLQueryInput(BaseModel):
    query: str = Field(..., description="The SQL query to execute on the automotive database.")

@tool #removed(args_schema=SQLQueryInput) because args schema is not defined in the tool call in the agents.py file
def execute_sql(query: str) -> str:
    """
    Execute the provided SQL query on the automotive database and return the results as CSV.
    Use this tool to run SELECT queries against the available tables (ad_table, price_table, sales_table, etc.).
    Provide the complete SQL query as the input string.
    """
    print(f"Executing SQL via tool. DB instance type: {type(db_instance)}") # Add print for debugging
    if db_instance is None:
        print("Error: execute_sql called but database instance is None.") # Add print for debugging
        return "Error: Database not initialized in the application."
    try:
        # Assuming db_instance is an instance of your Database class
        result_csv = db_instance.run_query(query)
        # Ensure the result is a string. run_query already returns CSV string or error string.
        if isinstance(result_csv, str):
             # Limit result size to prevent excessively large responses if necessary
             max_length = 5000 # Example limit, adjust as needed
             if len(result_csv) > max_length:
                  return result_csv[:max_length] + "\n... (results truncated)"
             return result_csv
        else:
             # Should not happen if run_query works as expected, but handle just in case
             return "Error: Query execution returned an unexpected data type."
    except Exception as e:
        print(f"Error during execute_sql: {e}") # Log exception
        # Return a user-friendly error message
        return f"Error executing SQL query: {str(e)}"