# main.py
import os
import logging
from database import Database # Import the NEW Database class
from agent_tools import set_database_instance
from agents import create_sql_agent
from langchain.schema import AIMessage, HumanMessage

# --- FOR LOCAL TESTING ONLY ---
# Requires setting environment variables for DB connection:
# GOOGLE_CLOUD_PROJECT, INSTANCE_CONNECTION_NAME, DB_USER, DB_PASS, DB_NAME
# Recommend running the Cloud SQL Auth Proxy locally for secure connection.

logging.basicConfig(level=logging.INFO)

def main():
    print("--- Running Local Test Mode (Connecting to Cloud SQL) ---")
    print("Ensure DB environment variables are set and Cloud SQL Auth Proxy is running (recommended).")

    db = None
    agent_executor = None

    # --- Initialize Database Connection ---
    try:
        db = Database() # Reads env vars internally
        set_database_instance(db)
        print("Database connection pool initialized successfully.")
    except Exception as e:
        print(f"FATAL: Failed to initialize database connection: {e}")
        print("Please check environment variables and Cloud SQL proxy/network.")
        return # Exit if DB connection fails

    # --- Initialize Agent ---
    try:
        agent_executor = create_sql_agent()
        print("LangChain Agent created successfully.")
    except Exception as e:
        print(f"FATAL: Failed to create LangChain agent: {e}")
        return # Exit if agent creation fails

    # In-memory chat history (list of LangChain message objects).
    chat_history = []

    print("\nWelcome to the AutoSQL Chat Interface (Local Cloud SQL Test Mode)!")
    print("Enter your natural language queries (type 'exit' to quit).")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "exit":
            break

        if db is None or db.pool is None or agent_executor is None:
            print("Agent: Cannot process query. Database or Agent not ready.")
            continue

        agent_input = {
            "input": user_input,
            "chat_history": chat_history,
        }

        try:
            result = agent_executor.invoke(agent_input)
            agent_output = result.get("output", "No output returned.")

            print("Agent:", agent_output)

            # Update the in-memory chat history.
            chat_history.append(HumanMessage(content=user_input))
            chat_history.append(AIMessage(content=agent_output))

            # Optional: Limit history size locally too
            max_history = 20
            if len(chat_history) > max_history:
                chat_history = chat_history[-max_history:]

        except Exception as e:
            print(f"\nError during local agent invocation: {e}")
            logging.error("Local agent invocation error:", exc_info=True) # Log stack trace


    # Cleanup connections on exit
    if db:
        db.close_connection()
    print("Exiting local test mode.")

if __name__ == "__main__":
    main()