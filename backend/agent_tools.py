# agent_tools.py
from pydantic import BaseModel, Field
from langchain.agents import tool
from database import Database # Import the NEW Database class
import logging # Add logging

# This global variable will hold the database instance set by app.py
db_instance: Database | None = None

def set_database_instance(db: Database):
    """Sets the shared database instance."""
    global db_instance
    logging.info(f"Setting database instance in agent_tools: {type(db)}")
    db_instance = db

class SQLQueryInput(BaseModel):
    query: str = Field(..., description="The SQL query to execute on the automotive database.")

@tool
def execute_sql(query: str) -> str:
    """
    Execute the provided SQL query on the automotive database (SQLite) and return the results as CSV.
    Use this tool to run SELECT queries against the available tables.
    Provide the complete standard SQL query as the input string.
    If an error occurs during execution, this tool will return a string starting with 'SQL Execution Error:'.
    """
    logging.info(f"Executing SQL via tool. DB instance type: {type(db_instance)}")
    if db_instance is None:
        logging.error("Error: execute_sql called but database instance is None.")
        return "Error: Database not initialized in the application."
    try:
        # run_query now expected to return CSV string on success, or error string starting with "Error:"
        result_or_error = db_instance.run_query(query)

        if isinstance(result_or_error, str) and result_or_error.startswith("Error:"):
             # Pass DB errors back to the agent clearly, including the failed query
             logging.warning(f"SQL execution failed. Error passed back to agent: {result_or_error}")
             # Reformat slightly to make it very clear for the LLM prompt
             return f"SQL Execution Error: {result_or_error.replace('Error: ', '')}. Failed Query: {query}"

        elif isinstance(result_or_error, str):
            # Successful query execution, result is CSV string
            # Limit result size to prevent excessively large responses
            max_length = 5000 # Adjust as needed
            if len(result_or_error) > max_length:
                truncated_msg = "\n... (results truncated)"
                header_end = result_or_error.find('\n')
                if header_end != -1:
                    header = result_or_error[:header_end+1]
                    return header + result_or_error[header_end+1:max_length - len(truncated_msg) - len(header)] + truncated_msg
                else:
                    return result_or_error[:max_length - len(truncated_msg)] + truncated_msg
            return result_or_error # Return CSV string
        else:
             # Should not happen if run_query behaves as expected
             logging.error(f"run_query returned unexpected type: {type(result_or_error)}")
             return f"SQL Execution Error: Unexpected return type from database query execution. Failed Query: {query}"

    except Exception as e:
        # Catch unexpected errors in the tool logic itself
        logging.error(f"Unexpected error within execute_sql tool: {e}", exc_info=True)
        return f"SQL Execution Error: Unexpected tool error: {str(e)}. Failed Query: {query}"