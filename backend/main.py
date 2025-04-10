# main.py
import os
# from config import setup_credentials # Removed call
from database import Database
from agent_tools import set_database_instance
from agents import create_sql_agent
from langchain.schema import AIMessage, HumanMessage

# --- FOR LOCAL TESTING ONLY ---
# This script is primarily for running the chat interface locally in the terminal.
# It does NOT use GCS by default unless you manually set environment variables.
# The `app.py` file is the entry point for App Engine deployment using Gunicorn.

def main():
    # setup_credentials() # Removed call

    # --- Attempt to load local config if available for testing ---
    # For local testing, you might temporarily set environment variables
    # or modify this section to load from a local path again.
    # Example using local path for testing:
    tables_dir_local = "C:/Users/kdelv/Documents/tables_V2.0" # <<< Or your local path
    print(f"--- Running Local Test Mode ---")
    print(f"Attempting to load tables from LOCAL directory: {tables_dir_local}")
    print("NOTE: Deployment uses GCS via environment variables in app.yaml.")

    try:
        # Temporarily simulate Database class structure for local files if needed
        # OR adjust Database class temporarily for local testing path.
        # This example assumes you might manually point Database to local path
        # IF you modify Database class or pass a local path handler.
        # For simplicity, we'll rely on the GCS path if env vars are set,
        # otherwise it might fail if not running in GAE context.

        # If you want robust local testing mirroring GAE:
        # 1. Set TABLES_BUCKET/TABLES_FOLDER env vars locally.
        # 2. Ensure your local machine is authenticated (`gcloud auth application-default login`).
        # 3. Run this script. It should then use the GCS version of Database.

        # Simplified local path loading for basic testing (requires modifying Database or using dummy data)
        # This part is tricky because Database is now GCS-focused.
        # Easiest local test: Set env vars and use ADC as described above.
        # If you *must* use local files without ADC/GCS for testing:
        # You would need to conditionally change the Database init or loading logic.

        # Assuming env vars are set locally and ADC login is done for local GCS test:
        gcs_bucket = os.environ.get("TABLES_BUCKET")
        gcs_folder = os.environ.get("TABLES_FOLDER")
        if not gcs_bucket:
             print("WARNING: TABLES_BUCKET env var not set for local test. Database init might fail.")
             # raise Exception("Set TABLES_BUCKET and TABLES_FOLDER env vars for local GCS test.")
             # Or fallback to a dummy/local path version of Database if implemented
             return # Exit if no bucket is defined for local test

        db = Database(bucket_name=gcs_bucket, folder_path=gcs_folder)
        set_database_instance(db)

    except Exception as e:
         print(f"Error setting up database for local test: {e}")
         print("Ensure GCS environment variables are set and you are authenticated via 'gcloud auth application-default login'.")
         return # Exit if setup fails

    # In-memory chat history (list of LangChain message objects).
    chat_history = []

    agent_executor = create_sql_agent()

    print("\nWelcome to the AutoSQL Chat Interface (Local Test Mode)!")
    print("Enter your natural language queries (type 'exit' to quit).")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "exit":
            break

        if db is None:
             print("Agent: Database is not initialized. Cannot process query.")
             continue

        agent_input = {
            "input": user_input,
            "chat_history": chat_history,
            # "agent_scratchpad": [] # Handled by AgentExecutor
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
            print(f"Error during local agent invocation: {e}")


if __name__ == "__main__":
    main()