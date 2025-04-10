# database.py
import os
import pandas as pd
import pandasql as ps
from google.cloud import storage # Added
import io # Added

class Database:
    def __init__(self, bucket_name, folder_path):
        """
        Initializes the Database by loading CSV tables from Google Cloud Storage.

        Args:
            bucket_name (str): The name of the GCS bucket containing the CSV files.
            folder_path (str): The folder path within the bucket where CSVs are located (e.g., 'tables_V2.0'). Can be empty if files are in root.
        """
        if not bucket_name:
            raise ValueError("GCS Bucket name is required.")

        self.bucket_name = bucket_name
        self.folder_path = folder_path.strip('/') # Ensure no leading/trailing slashes for consistency
        self.storage_client = storage.Client()
        self.tables = {} # Dictionary to hold loaded tables
        self.load_tables()

    def _load_single_table(self, table_name_csv):
        """Loads a single table from GCS."""
        try:
            bucket = self.storage_client.bucket(self.bucket_name)
            blob_path = f"{self.folder_path}/{table_name_csv}" if self.folder_path else table_name_csv
            blob = bucket.blob(blob_path)

            if not blob.exists():
                 print(f"Warning: Blob '{blob_path}' not found in bucket '{self.bucket_name}'. Skipping table.")
                 return None

            print(f"Loading {table_name_csv} from gs://{self.bucket_name}/{blob_path}...")
            # Download content as bytes
            content_bytes = blob.download_as_bytes()
            # Read bytes into pandas DataFrame
            # Using io.BytesIO avoids saving to a temporary file
            df = pd.read_csv(io.BytesIO(content_bytes), low_memory=False)
            print(f"{table_name_csv} loaded successfully. Shape: {df.shape}")
            return df
        except Exception as e:
            print(f"Error loading table {table_name_csv} from GCS: {e}")
            # Depending on requirements, you might want to raise the error
            # or allow the app to continue without this table.
            # raise e # Uncomment to make loading failure critical
            return None # Return None if loading fails

    def load_tables(self):
        """Loads all required tables from GCS."""
        print(f"Loading CSV tables from GCS bucket: '{self.bucket_name}', Folder: '{self.folder_path}'")
        table_files = [
            'Ad_table.csv', 'Price_table.csv', 'Sales_table.csv',
            'Basic_table.csv', 'Trim_table.csv', 'Image_table.csv'
        ]
        # Dynamically assign to self.xxx_table attributes
        for csv_file in table_files:
             # Derive attribute name, e.g., 'Ad_table.csv' -> 'ad_table'
             attr_name = csv_file.lower().replace('.csv', '')
             df = self._load_single_table(csv_file)
             setattr(self, attr_name, df) # Set self.ad_table, self.price_table etc.

        # Optional: Check if essential tables were loaded
        if getattr(self, 'ad_table', None) is None:
             print("Critical Error: ad_table failed to load.")
             # Handle critical failure appropriately - maybe raise exception

        print("Finished loading tables.")


    def run_query(self, query):
        """
        Executes a SQL query using pandasql on the loaded DataFrames.
        """
        try:
            # Prepare the environment for pandasql, ensuring only loaded tables are included
            env = {
                'ad_table': getattr(self, 'ad_table', None),
                'price_table': getattr(self, 'price_table', None),
                'sales_table': getattr(self, 'sales_table', None),
                'basic_table': getattr(self, 'basic_table', None),
                'trim_table': getattr(self, 'trim_table', None),
                'img_table': getattr(self, 'img_table', None),
                'pd': pd
            }
            # Filter out any tables that failed to load (are None)
            filtered_env = {k: v for k, v in env.items() if v is not None}

            if not filtered_env:
                 return "Error: No data tables were loaded successfully."

            print(f"Executing SQL query: {query}") # Log the query
            result = ps.sqldf(query, filtered_env)
            print(f"Query returned {len(result)} rows.") # Log result size
            return result.to_csv(index=False)
        except Exception as e:
            # Log the specific error
            print(f"SQL Execution Error for query '{query}': {str(e)}")
            return f"SQL Execution Error: {str(e)}"