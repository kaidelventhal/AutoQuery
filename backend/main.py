# main.py
import os
import pandas as pd
from config import setup_credentials
from agent_tools import set_database_instance
from agents import create_sql_agent
from langchain.schema import AIMessage, HumanMessage

def load_local_db_from_csv(table_dir):
    """
    Loads required CSV tables from a local directory and returns a dictionary
    mapping table names (lowercase without .csv) to DataFrames.
    """
    dataframes = {}
    required_files = [
        'Ad_table.csv', 'Price_table.csv', 'Sales_table.csv',
        'Basic_table.csv', 'Trim_table.csv', 'Image_table.csv'
    ]
    for file in required_files:
        path = os.path.join(table_dir, file)
        if os.path.exists(path):
            key = file.replace('.csv', '').lower()
            print(f"Loading {file} from local cache...")
            dataframes[key] = pd.read_csv(path, low_memory=False)
        else:
            print(f"File not found in {table_dir}: {file}")
    return dataframes

# A simple local database class that mimics your Database class
class LocalDatabase:
    def __init__(self, dataframes):
        self.dataframes = dataframes

    def run_query(self, query: str) -> str:
        import io
        import pandasql as ps
        # Create a local environment for pandasql (make DataFrames and pandas available)
        local_env = self.dataframes.copy()
        local_env['pd'] = pd
        try:
            result_df = ps.sqldf(query, local_env)
            output = io.StringIO()
            result_df.to_csv(output, index=False)
            return output.getvalue()
        except Exception as e:
            return f"Error executing query: {str(e)}"

# A cached version of your Database class that downloads from GCS only if needed.
# (This is a simplified version that replaces the original Database.__init__)
class CachedDatabase:
    def __init__(self):
        from google.cloud import storage
        import config

        # Use a persistent directory for caching (can be set via env variable)
        self.tables_dir = os.environ.get("TABLES_CACHE_DIR", "./tables_cache")
        os.makedirs(self.tables_dir, exist_ok=True)
        self.dataframes = {}
        required_files = [
            'Ad_table.csv', 'Price_table.csv', 'Sales_table.csv',
            'Basic_table.csv', 'Trim_table.csv', 'Image_table.csv'
        ]
        # Check if all required files exist in the cache
        cached_files = os.listdir(self.tables_dir)
        if set(required_files).issubset(set(cached_files)):
            print("Loading tables from cache directory:", self.tables_dir)
            for file in required_files:
                path = os.path.join(self.tables_dir, file)
                key = file.replace('.csv', '').lower()
                self.dataframes[key] = pd.read_csv(path, low_memory=False)
        else:
            print("Cache incomplete. Downloading tables from GCS...")
            # Initialize the GCS client
            client = storage.Client(project=config.GCP_PROJECT)
            bucket = client.bucket(config.TABLES_BUCKET)
            blobs = client.list_blobs(bucket, prefix=f"{config.TABLES_FOLDER}/", delimiter='/')
            for blob in blobs:
                if blob.name.endswith(".csv"):
                    file_name = os.path.basename(blob.name)
                    destination_path = os.path.join(self.tables_dir, file_name)
                    print(f"Downloading {blob.name} to {destination_path}...")
                    blob.download_to_filename(destination_path)
                    key = file_name.replace('.csv', '').lower()
                    self.dataframes[key] = pd.read_csv(destination_path, low_memory=False)
            print("Finished downloading and caching tables.")

    def run_query(self, query: str) -> str:
        import io
        import pandasql as ps
        local_env = self.dataframes.copy()
        local_env['pd'] = pd
        try:
            result_df = ps.sqldf(query, local_env)
            output = io.StringIO()
            result_df.to_csv(output, index=False)
            return output.getvalue()
        except Exception as e:
            return f"Error executing query: {str(e)}"

def main():
    setup_credentials()
    
    # Decide mode based on environment variable
    use_local = os.environ.get("USE_LOCAL_TABLES", "false").lower() == "true"
    
    if use_local:
        local_dir = os.environ.get("LOCAL_TABLE_DIR")
        if not local_dir:
            raise Exception("LOCAL_TABLE_DIR environment variable not set.")
        print("Using local CSV files from:", local_dir)
        dataframes = load_local_db_from_csv(local_dir)
        db = LocalDatabase(dataframes)
    else:
        print("Using cached GCS tables...")
        db = CachedDatabase()
    
    # Set the database instance for your agent tools
    set_database_instance(db)
    
    # Initialize the agent executor and chat history
    agent_executor = create_sql_agent()
    chat_history = []
    
    print("Welcome to the AutoSQL Chat Interface (Terminal)!")
    print("Enter your natural language queries (type 'exit' to quit).")
    
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "exit":
            break
        
        agent_input = {
            "input": user_input,
            "chat_history": chat_history,
            "agent_scratchpad": []
        }
        
        result = agent_executor.invoke(agent_input)
        agent_output = result.get("output", "No output returned.")
        print("Agent:", agent_output)
        
        # Update in-memory chat history
        chat_history.append(HumanMessage(content=user_input))
        chat_history.append(AIMessage(content=agent_output))
        
if __name__ == "__main__":
    main()
