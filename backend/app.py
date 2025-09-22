from flask import Flask, request, jsonify
from flask_cors import CORS
from agents import create_sql_agent
from agent_tools import set_database_instance
from database import Database
from langchain.schema import AIMessage, HumanMessage
import os

db = Database()
set_database_instance(db)
agent_executor = create_sql_agent()

chat_history = []
app = Flask(__name__)
CORS(app)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "Message cannot be empty."}), 400

    result = agent_executor.invoke({"input": user_message, "chat_history": chat_history})
    final_response = result.get("output", "Sorry, I encountered an issue.")

    agent_steps = ""
    if "intermediate_steps" in result:
        for action, observation in result["intermediate_steps"]:
            agent_steps += f"Tool Used: {action.tool}\n"
            tool_input_str = str(action.tool_input).replace('\n', ' ')
            agent_steps += f"Tool Input: {tool_input_str}\n\n"

    if not agent_steps:
        agent_steps = "No tools were used for this response."

    response_payload = {
        "agent_steps": agent_steps.strip(),
        "final_response": final_response
    }

    chat_history.append(HumanMessage(content=user_message))
    chat_history.append(AIMessage(content=final_response))

    return jsonify(response_payload)

if __name__ == '__main__':
    app.run(port=int(os.environ.get('PORT', 8080)), host='0.0.0.0')