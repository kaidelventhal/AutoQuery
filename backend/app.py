# backend/app.py

from flask import Flask, request, jsonify
from flask_cors import CORS
from agents import create_sql_agent
from agent_tools import set_database_instance
from database import Database # Import the SQLite Database class
from langchain.schema import AIMessage, HumanMessage
import os
import logging
import signal
import sys

logging.basicConfig(level=logging.INFO)

# --- Initialize Database ---
db = None
try:
    # Instantiate the SQLite Database class
    db = Database()
    set_database_instance(db)
    # Optional: Add a check here to see if the DB file actually exists
    # This relies on the logic within Database.__init__ and run_query
    logging.info("Database object initialized for SQLite file.")
except Exception as e:
    logging.error(f"FATAL: Failed to initialize Database object: {e}", exc_info=True)
    db = None
    set_database_instance(None)

# --- Initialize Agent ---
agent_executor = None
if db: # Check if db object was created (doesn't guarantee file exists yet)
    try:
        agent_executor = create_sql_agent()
        logging.info("LangChain Agent created successfully.")
    except Exception as e:
        logging.error(f"FATAL: Failed to create LangChain agent: {e}", exc_info=True)
        agent_executor = None
else:
    logging.warning("Database object initialization failed, skipping agent creation.")

chat_history = []
app = Flask(__name__)
# This CORS config SHOULD work once the 500 error is fixed
CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
    # If it is an OPTIONS request, return an empty successful response
    if request.method == 'OPTIONS':
        # Return an empty 200 response with the required headers
        response = app.make_default_options_response()
        # Optionally, you can add additional CORS headers here if needed:
        headers = response.headers
        headers['Access-Control-Allow-Origin'] = '*'
        headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    # For POST, continue with processing
    data = request.get_json()
    if not data or "message" not in data:
        logging.warning("Received invalid chat request: Missing 'message'")
        return jsonify({"error": "Missing 'message' in request body"}), 400

    # ... rest of your POST processing
    result = agent_executor.invoke({"input": data.get("message"), "chat_history": chat_history})
    response_content = result.get("output", "Agent did not return an output.")
    chat_history.append(HumanMessage(content=data.get("message")))
    chat_history.append(AIMessage(content=response_content))
    return jsonify({"response": response_content})

@app.route('/_ah/warmup')
def warmup():
    logging.info("Warmup request received.")
    # --- CORRECTED CHECK ---
    if db is None:
         logging.warning("Warmup: Database object not initialized.")
    # You could try calling db._get_connection() here to test connectivity early
    # try:
    #      conn = db._get_connection()
    #      conn.close()
    #      logging.info("Warmup: DB connection test successful.")
    # except Exception as e:
    #      logging.error(f"Warmup: DB connection test failed: {e}")
    # --- End Corrected Check ---
    return '', 200, {}

@app.route('/healthz')
def healthz():
    # --- CORRECTED CHECK ---
     if db: # Basic check: is the Database object instantiated?
         # More robust: try a quick connection/query
         try:
              conn = db._get_connection()
              # Optional: Run a super simple query like "SELECT 1"
              # cursor = conn.cursor()
              # cursor.execute("SELECT 1")
              # cursor.fetchone()
              conn.close()
              return "OK", 200
         except Exception as e:
              logging.error(f"Health check DB connection failed: {e}")
              return "Service Unavailable (DB connection failed)", 503
     else:
          return "Service Unavailable (DB init failed)", 503
    # --- End Corrected Check ---

# --- Graceful Shutdown Handling ---
# Remove db.close_connection() call as SQLite connections are short-lived
def cleanup(signum, frame):
    logging.info("Received shutdown signal. Cleaning up...")
    # No persistent DB connection pool to close for SQLite used this way
    logging.info("Cleanup complete (no persistent DB pool to close). Exiting.")
    sys.exit(0)

signal.signal(signal.SIGTERM, cleanup)
signal.signal(signal.SIGINT, cleanup)

# --- Main Execution ---
if __name__ == '__main__':
    logging.warning("Running Flask development server (for local testing only).")
    # Ensure DB file exists locally for testing
    if db:
         logging.info(f"Local testing with DB path: {db.db_path}")
    else:
         logging.error("DB object not created for local testing.")
    app.run(debug=False, port=int(os.environ.get('PORT', 8080)), host='0.0.0.0')