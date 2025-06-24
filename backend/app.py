# backend/app.py

from flask import Flask, request, jsonify
from flask_cors import CORS
from agents import create_sql_agent
from agent_tools import set_database_instance
from database import Database
from langchain.schema import AIMessage, HumanMessage
import os
import logging
import signal
import sys

logging.basicConfig(level=logging.INFO)

db = None
try:
    db = Database()
    set_database_instance(db)
    logging.info("Database object initialized for SQLite file.")
except Exception as e:
    logging.error(f"FATAL: Failed to initialize Database object: {e}", exc_info=True)
    db = None
    set_database_instance(None)

agent_executor = None
if db: 
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
CORS(app, resources={r"/api/*": {"origins": "*"}})



@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        headers = response.headers
        headers['Access-Control-Allow-Origin'] = '*'
        headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    data = request.get_json()
    user_message = data.get("message", "").strip()

    if not user_message:
        logging.warning("Received empty chat request.")
        return jsonify({"error": "Message cannot be empty."}), 400

    result = agent_executor.invoke({"input": user_message, "chat_history": chat_history})

    final_response = result.get("output", "Agent did not return an output.")

    status_report = ""
    if "intermediate_steps" in result:
        for action, observation in result["intermediate_steps"]:
            status_report += f"Tool Used: {action.tool}\n"
            tool_input_str = str(action.tool_input).replace('\n', ' ')
            status_report += f"Tool Input: {tool_input_str}\n\n"

    response_payload = {
        "status": status_report,
        "final_response": final_response
    }

    chat_history.append(HumanMessage(content=user_message))
    chat_history.append(AIMessage(content=final_response))

    return jsonify(response_payload)

@app.route('/_ah/warmup')
def warmup():
    logging.info("Warmup request received.")
    if db is None:
         logging.warning("Warmup: Database object not initialized.")

    return '', 200, {}

@app.route('/healthz')
def healthz():
     if db: 
         try:
              conn = db._get_connection()
              conn.close()
              return "OK", 200
         except Exception as e:
              logging.error(f"Health check DB connection failed: {e}")
              return "Service Unavailable (DB connection failed)", 503
     else:
          return "Service Unavailable (DB init failed)", 503

def cleanup(signum, frame):
    logging.info("Received shutdown signal. Cleaning up...")
    logging.info("Cleanup complete (no persistent DB pool to close). Exiting.")
    sys.exit(0)

signal.signal(signal.SIGTERM, cleanup)
signal.signal(signal.SIGINT, cleanup)

if __name__ == '__main__':
    logging.warning("Running Flask development server (for local testing only).")
    if db:
         logging.info(f"Local testing with DB path: {db.db_path}")
    else:
         logging.error("DB object not created for local testing.")
    app.run(debug=False, port=int(os.environ.get('PORT', 8080)), host='0.0.0.0')