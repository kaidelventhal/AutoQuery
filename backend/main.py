# main.py
import os
from config import setup_credentials
from database import Database
from agent_tools import set_database_instance
from agents import create_sql_agent
from langchain.schema import AIMessage, HumanMessage

def main():
    setup_credentials()
    
    # Use the TABLES_DIR environment variable set in config.py.
    tables_dir = os.environ.get("TABLES_DIR")
    if not tables_dir:
        raise Exception("TABLES_DIR environment variable not set.")
    
    db = Database(tables_dir)
    set_database_instance(db)
    
    # In-memory chat history (list of LangChain message objects).
    chat_history = []
    
    agent_executor = create_sql_agent()
    
    print("Welcome to the AutoSQL Chat Interface!")
    print("Enter your natural language queries (type 'exit' to quit).")
    
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "exit":
            break
        
        agent_input = {
            "input": user_input,
            "chat_history": chat_history,
            "agent_scratchpad": []
        }
        
        result = agent_executor.invoke(agent_input)
        agent_output = result.get("output", "No output returned.")
        
        print("Agent:", agent_output)
        
        # Update the in-memory chat history.
        chat_history.append(HumanMessage(content=user_input))
        chat_history.append(AIMessage(content=agent_output))
    
if __name__ == "__main__":
    main()
