from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from config import setup_credentials
from database import Database
from agent_tools import set_database_instance
from agents import create_sql_agent
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize agent and database
setup_credentials()
db = Database(os.environ.get("TABLES_DIR"))
set_database_instance(db)
agent_executor = create_sql_agent()

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    agent_input = {
        "input": data["message"],
        "chat_history": data["history"],
        "agent_scratchpad": []
    }
    
    response = agent_executor.invoke(agent_input)
    return jsonify({
        "response": response["output"],
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/history', methods=['GET'])
def get_history():
    # Implement history retrieval from your history.py
    from history import load_history
    return jsonify(load_history())

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)