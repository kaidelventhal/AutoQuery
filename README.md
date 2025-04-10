# AutoQuery AI

**Live Demo:** [Access the AutoQuery AI Assistant](https://autoquery-454320.uc.r.appspot.com/)

## Project Description

AutoQuery AI is an intelligent vehicle recommendation and query assistant deployed on Google Cloud. It helps users find vehicle information by asking questions in natural language. Leveraging Google Vertex AI's language models and LangChain for orchestration, AutoQuery AI translates user requests into SQL queries executed against a vehicle dataset stored in Google Cloud Storage.

## How It Works

1.  **Frontend Interaction:** Users interact with a simple web interface (HTML/CSS/JavaScript) served by Google App Engine.
2.  **API Request:** User messages are sent to a backend API built with Flask and deployed as a separate App Engine service.
3.  **Agent Processing:** The Flask backend uses a LangChain `AgentExecutor`. This agent is powered by a Google Vertex AI LLM (currently configured with Gemini Flash Lite).
4.  **Prompting & Schema:** The agent receives the user query along with a detailed system prompt containing:
    * Instructions on how to behave.
    * The exact database schema (table names, column names, data types).
    * Rules for generating SQL (case-insensitivity, handling specific column names like `Maker` vs `Automaker`, single-statement execution).
    * Guidance on validating user input against known data (e.g., checking model names).
5.  **SQL Generation:** Based on the user query and its prompt, the LLM generates a single `pandasql` (SQLite syntax) query.
6.  **Tool Execution:** The agent invokes a custom LangChain tool (`execute_sql`).
7.  **Data Querying:**
    * The `execute_sql` tool uses the `pandasql` library.
    * `pandasql` runs the generated SQL query against Pandas DataFrames.
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

## Tech Stack

* **Cloud Platform:** Google Cloud
    * **Compute:** App Engine Standard (Python 3.12 Runtime)
    * **Storage:** Cloud Storage (for CSV data)
    * **AI:** Vertex AI (Gemini Flash Lite Model)
* **Backend:**
    * **Language:** Python
    * **Framework:** Flask
    * **Web Server:** Gunicorn (with `gthread` workers)
    * **API Communication:** Flask-CORS
* **AI Orchestration:** LangChain (AgentExecutor, Tools, Prompts)
* **Data Querying:** Pandas, Pandasql
* **Frontend:** HTML, CSS, Vanilla JavaScript

## Key Features

* **Natural Language Interface**: Ask questions in plain English to query vehicle data.
* **Agentic SQL Generation**: Converts natural language to `pandasql` queries using an LLM agent.
* **Cloud-Native Deployment**: Runs efficiently on Google App Engine, utilizing Cloud Storage for data.
* **Error Handling**: Agent attempts to identify and report SQL execution errors.

## Getting Started (for Contributors)

While the primary way to use the app is via the live demo link above, contributors wishing to run or modify the code locally can follow these steps:

### Prerequisites

* Python 3.10+
* Google Cloud SDK (`gcloud`) installed and authenticated (`gcloud auth login`, `gcloud auth application-default login`)
* A Google Cloud Project with Billing enabled.
* APIs Enabled: App Engine Admin, Vertex AI, Cloud Storage, Cloud Build.
* A GCS Bucket containing the required CSV data files (`Ad_table.csv`, `Price_table.csv`, etc.) in a specific folder structure (e.g., `tables_V2.0/`).

### Installation

1.  Clone the repository:
    ```bash
    git clone [https://github.com/yourusername/autoquery-ai.git](https://github.com/yourusername/autoquery-ai.git) # Replace with your repo URL
    cd autoquery-ai
    ```
2.  Set up a Python virtual environment (recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate # Linux/macOS
    # venv\Scripts\activate # Windows
    ```
3.  Install required packages:
    ```bash
    pip install -r backend/requirements.txt
    ```
4.  **Configure Environment Variables (Crucial for Local Backend):**
    Set the following environment variables in your local terminal session *before* running the backend:
    ```bash
    export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
    export TABLES_BUCKET="your-gcs-bucket-name"
    export TABLES_FOLDER="your-folder-in-bucket" # e.g., tables_V2.0 or "" if root
    # Use 'set' instead of 'export' on Windows Command Prompt
    # Use '$env:VAR_NAME = "value"' in PowerShell
    ```
    *(Ensure your local machine is authenticated via `gcloud auth application-default login` for the backend to access GCS and Vertex AI).*

### Local Usage

1.  **Run Backend:**
    ```bash
    # Navigate to the backend directory
    cd backend
    # Run using Flask's development server (for testing, less robust than gunicorn)
    flask run --host=0.0.0.0 --port=5000
    # OR run with gunicorn locally (mimics App Engine better)
    # gunicorn -b 0.0.0.0:5000 -w 1 -k gthread app:app --log-level debug
    ```
2.  **Run Frontend:**
    * Open `frontend/index.html` directly in your browser (will likely fail due to CORS if backend isn't on `localhost:5000`).
    * OR use a simple local web server (like Python's `http.server` or VS Code Live Server) from the `frontend` directory. You may need to adjust the `API_URL` in `script.js` temporarily to `http://localhost:5000/api/chat` for local testing. Remember to change it back before deploying the frontend.

## Deployment

The application is designed for Google App Engine Standard Environment using two services:

1.  **`backend` Service:** Runs the Python/Flask application defined in `backend/app.yaml`. Deployed via `gcloud app deploy backend/app.yaml`.
2.  **`default` Service (or `frontend`):** Serves the static frontend files (HTML/CSS/JS) defined in `frontend/app.yaml`. Deployed via `gcloud app deploy frontend/app.yaml`.

*(Ensure `app.yaml` files have correct project IDs, environment variables, and instance classes before deploying.)*

## Future Enhancements

* **React Frontend:** Migrate the frontend from Vanilla JS to React for a more modern, component-based UI, better state management, and easier development of complex features.
* **Improved Agentic Ability:**
    * **Multi-Step Reasoning:** Implement frameworks like LangGraph to allow the agent to perform multiple sequential `execute_sql` calls for complex requests (e.g., comparing data across years, complex validation steps).
    * **Error Recovery:** Enhance the agent's ability to automatically correct and retry failed SQL queries based on error messages.
    * **Data Visualization:** Add capabilities for the agent to generate simple charts or summaries based on query results.
    * **Image Integration:** Utilize the `img_table` to display relevant vehicle images alongside query results.
* **Enhanced Security:**
    * **Authentication:** Add user login/authentication (e.g., using Google Identity Platform or Firebase Auth) if multi-user support or data protection is needed.
    * **Input Sanitization:** Implement stricter validation and sanitization on user inputs and potentially LLM outputs.
    * **Secrets Management:** Use Google Secret Manager for any API keys or sensitive configuration if needed (currently relies on ADC).
    * **Stricter CORS:** Configure `Flask-CORS` to only allow requests specifically from the deployed frontend origin instead of `*`.
    * **Rate Limiting:** Implement API rate limiting (e.g., using `Flask-Limiter`) to prevent abuse.
* **Data Backend Migration:** For improved performance, scalability, and reduced memory usage (allowing smaller App Engine instances), migrate the data from GCS CSV files + Pandas DataFrames to a dedicated database like Google Cloud SQL (PostgreSQL/MySQL) or potentially BigQuery. This would require replacing `pandasql` with standard SQL querying libraries (like SQLAlchemy or database-specific connectors).

## Conclusion

AutoQuery AI demonstrates the power of combining LLMs (Vertex AI), orchestration frameworks (LangChain), cloud services (GCP App Engine, GCS), and data manipulation libraries (Pandas, Pandasql) to create interactive, data-driven applications. It showcases skills in backend development, API design, cloud deployment, and AI integration.