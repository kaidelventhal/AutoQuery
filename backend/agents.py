from langchain_google_vertexai import ChatVertexAI
from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from prompts import get_sql_generation_prompt
from langchain.schema import AIMessage, HumanMessage
from agent_tools import execute_sql, get_table_schema, get_distinct_values

tools = [execute_sql, get_table_schema, get_distinct_values]

def create_sql_agent():
    llm = ChatVertexAI(
        model="gemini-2.5-flash",
        temperature=0,
        convert_system_message_to_human=True,
        project="autoquery-472902"
    )
    llm_with_tools = llm.bind_tools(tools)

    prompt = get_sql_generation_prompt()

    def input_extractor(x):
        return x.get("input", x.get("question", ""))

    def scratchpad_formatter(x):
        return format_to_openai_tool_messages(x.get("intermediate_steps", []))

    agent_components = {
        "input": input_extractor,
        "agent_scratchpad": scratchpad_formatter,
        "chat_history": lambda x: x.get("chat_history", [])
    }

    agent = agent_components | prompt | llm_with_tools | OpenAIToolsAgentOutputParser()

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        return_intermediate_steps=True
    )
    return agent_executor