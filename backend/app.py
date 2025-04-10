from flask import Flask, request, jsonify
from flask_cors import CORS
# from config import setup_credentials # Removed - No longer needed
from agents import create_sql_agent
from agent_tools import set_database_instance
from database import Database # Keep this
from langchain.schema import AIMessage, HumanMessage
import os
import logging # Optional: Improve logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize credentials and the agent
# setup_credentials() # Removed - ADC handles this

# --- Get GCS configuration from App Engine Environment Variables ---
gcs_bucket_name = os.environ.get("TABLES_BUCKET")
gcs_folder_path = os.environ.get("TABLES_FOLDER") # Can be empty string if files are in bucket root

if not gcs_bucket_name:
    logging.error("FATAL: TABLES_BUCKET environment variable not set.")
    # Decide how to handle this - exit or try to run degraded?
    # For now, we'll let the Database class raise an error later.
    pass

agent_executor = create_sql_agent()

# --- Initialize Database with GCS config ---
try:
    db = Database(bucket_name=gcs_bucket_name, folder_path=gcs_folder_path)
    set_database_instance(db)
    logging.info("Database initialized successfully from GCS.")
except Exception as e:
    logging.error(f"FATAL: Failed to initialize database from GCS: {e}")
    # Handle inability to start - maybe return errors on API calls
    db = None # Ensure db is None if initialization fails
    set_database_instance(None)

# --- In-memory chat history (Simple approach) ---
# Note: This history is lost if the instance restarts or scales down/up.
# For persistent history across requests/instances, you'd need an external store
# (like Firestore, Memorystore, or a database).
chat_history = [] # Global variable

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
    global chat_history # <<< ADD THIS LINE

    # Handle OPTIONS (though CORS should intercept)
    if request.method == 'OPTIONS':
         logging.info("Received OPTIONS request for /api/chat - Flask-CORS should have handled this.")
         resp = app.make_default_options_response()
         # Add headers Flask-CORS would have added
         h = resp.headers
         h['Access-Control-Allow-Origin'] = '*'
         h['Access-Control-Allow-Methods'] = resp.headers.get('Allow', 'POST, OPTIONS')
         h['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
         h['Access-Control-Max-Age'] = '86400'
         return resp

    # --- Handle POST request ---
    if db is None or getattr(db, 'ad_table', None) is None:
         logging.error("Chat request (POST) received but database is not ready.")
         return jsonify({"error": "Server error: Database not available or not loaded correctly."}), 503

    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Missing 'message' in request body"}), 400

    user_input = data.get("message")
    logging.info(f"Received chat message (POST): {user_input}")

    # Now it correctly reads the global chat_history
    agent_input = {
        "input": user_input,
        "chat_history": chat_history,
    }

    try:
        if agent_executor is None:
             logging.error("Agent executor not initialized.")
             return jsonify({"error": "Server error: Agent not available."}), 503

        result = agent_executor.invoke(agent_input)
        response_content = result.get("output", "Agent did not return an output.")

        # Now it correctly modifies the global chat_history
        chat_history.append(HumanMessage(content=user_input))
        chat_history.append(AIMessage(content=response_content))
        max_history = 20
        if len(chat_history) > max_history:
            chat_history = chat_history[-max_history:] # Assignment is fine now

        logging.info(f"Agent response: {response_content}")
        return jsonify({"response": response_content})

    except Exception as e:
        logging.error(f"Error during agent invocation: {e}", exc_info=True)
        return jsonify({"error": f"An internal error occurred during agent processing: {e}"}), 500
    # --- End POST request handling ---

# ... (health_check function and __main__ block remain the same) ...

if __name__ == '__main__':
    app.run(debug=False, port=int(os.environ.get('PORT', 8080)), host='0.0.0.0')
