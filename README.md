# AutoQuery AI

**Live Demo:** [Access the AutoQuery AI Assistant](https://autoquery-472902.ue.r.appspot.com/)

App can take a second to load due to non persistent server. (First request will take longer to load the database into memory and initialize container)

Try asking the assistant questions about the dataset to see what it can do.

## Project Description

AutoQuery AI is an intelligent vehicle recommendation and query assistant deployed on Google Cloud. It helps users find vehicle information by asking questions in natural language. Leveraging Google Vertex AI's language models and LangChain for orchestration, AutoQuery AI translates user requests Agenticaly into SQL queries executed against a vehicle dataset stored in sqlite3 database

## How It Works

1.  **Frontend Interaction:** Users interact with a simple web interface (HTML/CSS/JavaScript) served by Google App Engine.
2.  **API Request:** User messages are sent to a backend API built with Flask and deployed as a separate App Engine service.
3.  **Agent Processing:** The Flask backend uses a LangChain AgentExecutor. This agent is powered by a Google Vertex AI LLM (currently configured with Gemini Flash Lite).
4.  **Prompting & Schema:** The agent receives the user query along with a detailed system prompt containing:
    * Instructions on how to behave.
    * The exact database schema (table names, column names, data types).
    * Guidance on validating user input against known data (e.g., checking model names).
5.  **SQL Generation:** Based on the user query and its prompt, the LLM generates a single query.
6.  **Tool Execution:** The agent invokes a custom LangChain tool (`execute_sql`).
7.  **Data Querying:**
    * The execute_sql tool uses the sqlite library.
    * sqlite runs the generated SQL query against sqlite3 DataFrames.
    * These DataFrames are loaded into memory by the backend application *on startup* from CSV files stored in a Google Cloud Storage (GCS) bucket.
8.  **Result Formatting:** The tool returns the query results as a CSV-formatted string (or an error message) back to the agent.
9.  **Response Generation:** The agent analyzes the tool's output (the CSV data or error) and formulates a final, user-friendly natural language response.
10. **API Response:** The Flask backend sends the agent's response back to the frontend, which displays it to the user.

## Example Prompts to Try

Here are a few example questions you can ask to test the agent's capabilities:

* **Simple Lookup & Sorting:**
    * `What was the top selling car in 2015?`
    * `What car had the largest engine size?`
    * `Which car has the highest top speed?`
* **Filtering:**
    * `Show me red Ford Fiesta cars registered after 2018` (Tests case-insensitivity)
    * `List BMW cars registered in 2020 with less than 10000 miles`
    * `Find cars with an automatic gearbox and more than 200 engine power`
* **Joins / Combining Info (Implicit):**
    * `What was the entry price for a Ford Focus in 2019?` (Uses `price_table`)
    * `Show sales data for the Ford F150 in 2016` (Tests model name handling "F150")
* **Testing Limitations:**
    * `List the top selling cars for 2018 and 2019` (Agent should state it can only do one year at a time)
    * `What data do you have for the 'CyberTruck' model?` (Agent should report no data found if it's not in the tables)

Feel free to experiment with different combinations of makes, models, years, colors, features, etc.!
