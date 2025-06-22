# backend/agents.py
from langchain_google_vertexai import ChatVertexAI
from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from prompts import get_sql_generation_prompt
from langchain.schema import AIMessage, HumanMessage
# Import the new tools along with the existing one
from agent_tools import execute_sql, get_table_schema, get_distinct_values

# --- UPDATED: Define the list of ALL tools available to the agent ---
tools = [execute_sql, get_table_schema, get_distinct_values]

def create_sql_agent():
    """
    Create and return an agent executor that uses the Gemini model with tool support,
    including SQL execution and schema/value exploration tools.
    """
    llm = ChatVertexAI(
        model="gemini-2.0-flash-lite", # Consider specifying or using the latest stable flash
        temperature=0,
        convert_system_message_to_human=True, # Often needed for Gemini via Langchain
        project="autoquery-454320" # Ensure this is your correct GCP project ID
    )
    # Bind all available tools to the LLM
    llm_with_tools = llm.bind_tools(tools)

    prompt = get_sql_generation_prompt() # Get the updated prompt

    # Standard Langchain setup for OpenAI Tools agents
    def input_extractor(x):
        # Handles potential variations in input dictionary keys
        return x.get("input", x.get("question", ""))

    def scratchpad_formatter(x):
        return format_to_openai_tool_messages(x.get("intermediate_steps", []))

    agent_components = {
        "input": input_extractor,
        "agent_scratchpad": scratchpad_formatter,
        "chat_history": lambda x: x.get("chat_history", []) # Handle optional chat history
    }

    # Define the agent chain
    agent = agent_components | prompt | llm_with_tools | OpenAIToolsAgentOutputParser()

    # Create the executor, ensuring all tools are passed
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools, # Pass the complete list of tools here
        verbose=True, # Keep verbose=True for debugging
        handle_parsing_errors=True # Add robustness
        )
    return agent_executor