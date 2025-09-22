import os
import logging
from database import Database 
from agent_tools import set_database_instance
from agents import create_sql_agent
from langchain.schema import AIMessage, HumanMessage


logging.basicConfig(level=logging.INFO)

def main():
    print("--- Running Local Test Mode (Connecting to Cloud SQL) ---")
    print("Ensure DB environment variables are set and Cloud SQL Auth Proxy is running (recommended).")

    db = None
    agent_executor = None

    try:
        db = Database() 
        set_database_instance(db)
        print("Database connection pool initialized successfully.")
    except Exception as e:
        print(f"FATAL: Failed to initialize database connection: {e}")
        print("Please check environment variables and Cloud SQL proxy/network.")
        return

    try:
        agent_executor = create_sql_agent()
        print("LangChain Agent created successfully.")
    except Exception as e:
        print(f"FATAL: Failed to create LangChain agent: {e}")
        return

    chat_history = []

    print("\nWelcome to the AutoSQL Chat Interface (Local Cloud SQL Test Mode)!")
    print("Enter your natural language queries (type 'exit' to quit).")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "exit":
            break


        agent_input = {
            "input": user_input,
            "chat_history": chat_history,
        }

        try:
            result = agent_executor.invoke(agent_input)
            agent_output = result.get("output", "No output returned.")

            print("Agent:", agent_output)

            chat_history.append(HumanMessage(content=user_input))
            chat_history.append(AIMessage(content=agent_output))

            max_history = 20
            if len(chat_history) > max_history:
                chat_history = chat_history[-max_history:]

        except Exception as e:
            print(f"\nError during local agent invocation: {e}")
            logging.error("Local agent invocation error:", exc_info=True) 


    if db:
        db.close_connection()
    print("Exiting local test mode.")

if __name__ == "__main__":
    main()