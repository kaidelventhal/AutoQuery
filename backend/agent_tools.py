from pydantic import BaseModel, Field
from langchain.agents import tool
from database import Database 
import logging

logging.basicConfig(level=logging.INFO) 

db_instance: Database | None = None

VALID_TABLES = ["ad_table", "price_table", "sales_table", "basic_table", "trim_table", "img_table"]

def set_database_instance(db: Database):
    """Sets the shared database instance."""
    global db_instance
    logging.info(f"Setting database instance in agent_tools: {type(db)}")
    db_instance = db

class SQLQueryInput(BaseModel):
    query: str = Field(..., description="The SQL query to execute on the automotive database.")

@tool
def execute_sql(query: str) -> str:

    if db_instance is None:
        return "Error: Database not initialized"
    try:
        # Force SELECT queries only for safety? Add basic check:
        if not query.strip().upper().startswith("SELECT") and not query.strip().upper().startswith("PRAGMA"):
             logging.warning(f"Rejected non-SELECT/PRAGMA query: {query[:100]}")
             return f"SQL Execution Error: Only SELECT or PRAGMA queries are allowed. Failed Query: {query}"

        result_or_error = db_instance.run_query(query)

        if isinstance(result_or_error, str) and result_or_error.startswith("Error:"):
             logging.warning(f"SQL execution failed. Error passed back to agent: {result_or_error}")
             return f"SQL Execution Error: {result_or_error.replace('Error: ', '')}. Failed Query: {query}"

        elif isinstance(result_or_error, str):
            max_length = 5000 
            if len(result_or_error) > max_length:
                truncated_msg = "\n... (results truncated)"
                header_end = result_or_error.find('\n')
                if header_end != -1:
                    header = result_or_error[:header_end+1]
                    return header + result_or_error[header_end+1:max_length - len(truncated_msg) - len(header)] + truncated_msg
                else:
                    return result_or_error[:max_length - len(truncated_msg)] + truncated_msg
            return result_or_error 
        else:
             logging.error(f"run_query returned unexpected type: {type(result_or_error)}")
             return f"SQL Execution Error: Unexpected return type from database query execution. Failed Query: {query}"

    except Exception as e:
        logging.error(f"Unexpected error within execute_sql tool: {e}", exc_info=True)
        return f"SQL Execution Error: Unexpected tool error: {str(e)}. Failed Query: {query}"

@tool
def get_table_schema(table_name: str) -> str:
    """
    Returns the schema (column names and data types) for the specified table.
    Use this tool ONLY if you are unsure about the exact columns or data types available in a specific table.
    Input must be one of the valid table names: ad_table, price_table, sales_table, basic_table, trim_table, img_table.
    """
    logging.info(f"Executing get_table_schema tool for table: {table_name}")
    if db_instance is None:
        logging.error("Error: get_table_schema called but database instance is None.")
        return "Error: Database not initialized."

    if table_name not in VALID_TABLES:
         logging.warning(f"Invalid table name requested for schema: {table_name}")
         return f"Error: Invalid table name '{table_name}'. Valid tables are: {', '.join(VALID_TABLES)}"

    try:
        query = f"PRAGMA table_info('{table_name}');" 
        logging.info(f"Executing schema query: {query}")
        schema_info = db_instance.run_query(query)

        if isinstance(schema_info, str) and schema_info.startswith("Error:"):
             logging.warning(f"Schema query failed for {table_name}: {schema_info}")
             return f"Schema Fetch Error: {schema_info.replace('Error: ', '')}. Failed Query: {query}"
        elif isinstance(schema_info, str):
             return f"Schema for table '{table_name}':\n{schema_info}"
        else:
            logging.error(f"Schema query for {table_name} returned unexpected type: {type(schema_info)}")
            return f"Schema Fetch Error: Unexpected return type. Failed Query: {query}"

    except Exception as e:
        logging.error(f"Error in get_table_schema tool for {table_name}: {e}", exc_info=True)
        return f"Schema Fetch Error: Unexpected tool error: {str(e)}"

# --- NEW TOOL: Get Distinct Values ---
@tool
def get_distinct_values(table_name: str, column_name: str) -> str:
    if db_instance is None:
        logging.error("Error: get_distinct_values called but database instance is None.")
        return "Error: Database not initialized."

    if table_name not in VALID_TABLES:
         logging.warning(f"Invalid table name requested for distinct values: {table_name}")
         return f"Error: Invalid table name '{table_name}'. Valid tables are: {', '.join(VALID_TABLES)}"


    if not column_name.isalnum() and '_' not in column_name:
         logging.warning(f"Potentially unsafe column name requested for distinct values: {column_name}")
         # Allow quoted names like "2015"
         if not (column_name.startswith('"') and column_name.endswith('"')):
              return f"Error: Invalid characters in column name '{column_name}'."


    try:
        query = f'SELECT DISTINCT "{column_name}" FROM "{table_name}" WHERE "{column_name}" IS NOT NULL AND "{column_name}" != "" LIMIT 10;'
        logging.info(f"Executing distinct values query: {query}")
        distinct_values = db_instance.run_query(query)

        if isinstance(distinct_values, str) and distinct_values.startswith("Error:"):
             logging.warning(f"Distinct values query failed for {table_name}.{column_name}: {distinct_values}")
             return f"Distinct Values Error: {distinct_values.replace('Error: ', '')}. Failed Query: {query}"
        elif isinstance(distinct_values, str):
             if distinct_values.strip() == column_name or distinct_values.strip() == f'"{column_name}"':
                  return f"Distinct values sample for '{column_name}' in '{table_name}':\n(No non-empty values found)"
             return f"Distinct values sample for '{column_name}' in '{table_name}':\n{distinct_values}"
        else:
             logging.error(f"Distinct values query for {table_name}.{column_name} returned unexpected type: {type(distinct_values)}")
             return f"Distinct Values Error: Unexpected return type. Failed Query: {query}"

    except Exception as e:
        logging.error(f"Error in get_distinct_values tool for {table_name}.{column_name}: {e}", exc_info=True)
        return f"Distinct Values Error: Unexpected tool error: {str(e)}"