# agents.py
from langchain_google_vertexai import ChatVertexAI
from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from prompts import get_sql_generation_prompt
from langchain.schema import AIMessage, HumanMessage
from agent_tools import execute_sql

# Define the list of tools available to the agent.
tools = [execute_sql]

def create_sql_agent():
    """
    Create and return an agent executor that uses the Gemini model with tool support.
    """
    llm = ChatVertexAI(
        model="gemini-2.0-flash-lite-preview-02-05",
        temperature=0,
        convert_system_message_to_human=True,
        project = "autoquery-454320"
    )
    llm_with_tools = llm.bind_tools(tools)
    
    prompt = get_sql_generation_prompt()
    
    def input_extractor(x):
        return x["input"]
    
    def scratchpad_formatter(x):
        return format_to_openai_tool_messages(x["intermediate_steps"])
    
    agent_components = {
        "input": input_extractor,
        "agent_scratchpad": scratchpad_formatter,
        "chat_history": lambda x: x["chat_history"]
    }
    
    agent = agent_components | prompt | llm_with_tools | OpenAIToolsAgentOutputParser()
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    return agent_executor
