from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from langchain_core.messages import AIMessage, HumanMessage

import config # Import config first
# --- Configuration & Initialization ---
# Call setup_credentials early to check for ADC/keys
config.setup_credentials()

# Import other modules AFTER basic config/env vars might be needed
from agents import create_sql_agent
# We don't need to explicitly initialize DB here, agent_tools does it via get_db_instance()

# --- Flask App Initialization ---
app = Flask(__name__)
CORS(app)

# --- Agent Initialization ---
# This will trigger the DB initialization via agent_tools -> get_db_instance()
try:
    agent_executor = create_sql_agent()
    print("Flask App: Agent executor initialized (DB loading should have occurred).")
except Exception as e:
    print(f"FATAL: Failed to initialize agent executor (check DB loading?): {e}")
    agent_executor = None

# --- API Routes ---
@app.route('/api/chat', methods=['POST'])
def chat():
    """Handles incoming chat messages and returns the agent's response."""
    if agent_executor is None:
         # More specific error if DB loading likely failed
         return jsonify({"error": "Agent not available. Check backend logs (potential data loading issue)."}), 500

    data = request.json
    user_message = data.get("message")
    history_raw = data.get("history", [])

    if not user_message:
        return jsonify({"error": "No message provided."}), 400

    # Convert frontend history format to LangChain Message objects
    chat_history = []
    for msg in history_raw:
        if msg.get("sender") == "user":
            chat_history.append(HumanMessage(content=msg.get("message", "")))
        elif msg.get("sender") == "agent":
            chat_history.append(AIMessage(content=msg.get("message", "")))

    agent_input = {
        "input": user_message,
        "chat_history": chat_history
    }

    try:
        # Invoke the agent
        response = agent_executor.invoke(agent_input)
        agent_response = response.get("output", "Sorry, I encountered an issue processing your request.")

        return jsonify({
            "response": agent_response,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        print(f"Error during agent invocation: {e}")
        return jsonify({"error": f"An error occurred: {e}"}), 500

@app.route('/health', methods=['GET'])
def health_check():
     """Basic health check endpoint."""
     # Could add a check here to see if db_instance in agent_tools is not None
     status = "ok" if agent_executor is not None else "error: agent not initialized"
     code = 200 if agent_executor is not None else 500
     return jsonify({"status": status}), code

# --- Main Execution ---
if __name__ == '__main__':
    # Use Flask's development server for local testing
    app.run(debug=True, port=5000, host='0.0.0.0')