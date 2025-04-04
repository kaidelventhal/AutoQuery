# database.py
import os
import pandas as pd
import pandasql as ps
from google.cloud import storage
import io
import config # Import config to get bucket/folder names

class Database:
    def __init__(self):
        """
        Initializes the database by downloading CSVs from GCS
        and loading them into pandas DataFrames.
        """
        self.gcs_client = storage.Client(project=config.GCP_PROJECT)
        self.tables_dir = "/tmp/tables"  # Use App Engine's temporary writable directory
        self.dataframes = {} # Dictionary to hold DataFrames

        if not config.TABLES_BUCKET or not config.TABLES_FOLDER:
            raise ValueError("TABLES_BUCKET and TABLES_FOLDER environment variables must be set.")

        print(f"Attempting to load tables from GCS Bucket: {config.TABLES_BUCKET}, Folder: {config.TABLES_FOLDER}")
        self.download_and_load_tables(config.TABLES_BUCKET, config.TABLES_FOLDER)


    def download_and_load_tables(self, bucket_name, folder_name):
        """Downloads CSV files from GCS and loads them into pandas DataFrames."""
        os.makedirs(self.tables_dir, exist_ok=True)
        bucket = self.gcs_client.bucket(bucket_name)
        blobs = self.gcs_client.list_blobs(bucket, prefix=f"{folder_name}/", delimiter='/')

        loaded_files = []
        required_tables = ['Ad_table.csv', 'Price_table.csv', 'Sales_table.csv', 'Basic_table.csv', 'Trim_table.csv', 'Image_table.csv'] # Add more if needed

        for blob in blobs:
            if blob.name.endswith(".csv"):
                file_name = os.path.basename(blob.name)
                destination_path = os.path.join(self.tables_dir, file_name)
                try:
                    print(f"Downloading {blob.name} to {destination_path}...")
                    blob.download_to_filename(destination_path)
                    print(f"Loading {file_name} into DataFrame...")
                    # Derive table name for pandasql (e.g., 'Ad_table.csv' -> 'ad_table')
                    table_key = file_name.replace('.csv', '').lower()
                    # Load into DataFrame and store in dictionary
                    self.dataframes[table_key] = pd.read_csv(destination_path, low_memory=False)
                    print(f"Loaded {file_name} as '{table_key}'. Shape: {self.dataframes[table_key].shape}")
                    loaded_files.append(file_name)
                except Exception as e:
                    print(f"Error processing {blob.name}: {e}")
                    # Decide if failure to load one table is critical
                    # raise e # Uncomment to make failures critical

        # Verify all required tables were loaded
        missing_tables = [req for req in required_tables if req.replace('.csv', '').lower() not in self.dataframes]
        if missing_tables:
             print(f"WARNING: Missing required table data for: {missing_tables}")
             # raise ValueError(f"Missing required table data for: {missing_tables}") # Uncomment if loading all is mandatory

        print("Finished loading tables from GCS.")


    def run_query(self, query: str) -> str:
        """
        Executes one or more SQL queries on the loaded pandas DataFrames using pandasql.
        Returns results as a combined CSV string.
        """
        print(f"Executing pandasql query:\n{query}")
        # Copy DataFrames into the local environment and add pandas
        local_env = self.dataframes.copy()
        local_env['pd'] = pd

        try:
            # Split the query by semicolon and filter out empty statements.
            queries = [q.strip() for q in query.strip().split(';') if q.strip()]
            csv_results = []
            for q in queries:
                result_df = ps.sqldf(q, local_env)
                output = io.StringIO()
                result_df.to_csv(output, index=False)
                csv_results.append(output.getvalue())
            # Combine all CSV outputs (separated by a blank line)
            combined_csv = "\n\n".join(csv_results)
            print(f"Pandasql query successful, returning results from {len(queries)} query(ies).")
            return combined_csv

        except Exception as e:
            error_message = f"Pandasql Execution Error: {str(e)}"
            print(error_message)
            return f"Error executing query: {str(e)}"


# Optional: Singleton pattern if desired (usually good practice for resources)
_db_instance = None
def get_db_instance():
    global _db_instance
    if _db_instance is None:
        print("Initializing singleton Database instance...")
        _db_instance = Database()
        print("Singleton Database instance initialized.")
    return _db_instance