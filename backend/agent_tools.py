# agent_tools.py
from pydantic import BaseModel, Field
from langchain.agents import tool
from database import Database

db_instance = None

def set_database_instance(db):
    global db_instance
    db_instance = db

class SQLQueryInput(BaseModel):
    query: str = Field(..., description="The SQL query to execute on the automotive database.")

@tool
def execute_sql(query: str) -> str:
    """
    Execute the provided SQL query on the automotive database and return the results.
    """
    if db_instance is None:
        return "Database not initialized."
    result = db_instance.run_query(query)
    return result
