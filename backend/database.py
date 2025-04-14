# backend/database.py
import os
import sqlite3
import pandas as pd
import io
import logging

logging.basicConfig(level=logging.INFO)

# --- Configuration ---
# Determine the absolute path to the directory containing this script
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Construct the path to the database file relative to this script's location
DB_FILENAME = "autoquery_data.db"
DB_FILE_PATH = os.path.join(_BASE_DIR, DB_FILENAME)
# --- End Configuration ---

class Database:
    def __init__(self):
        self.db_path = DB_FILE_PATH
        logging.info(f"Database object initialized for SQLite file: {self.db_path}")
        if not os.path.exists(self.db_path):
             # This might happen during local testing if the DB isn't generated yet,
             # but should not happen in App Engine if deployment included the file.
             logging.warning(f"Database file not found at {self.db_path} during init.")

    def _get_connection(self):
        """Establishes a read-only connection to the SQLite database."""
        try:
            if not os.path.exists(self.db_path):
                 raise FileNotFoundError(f"SQLite DB file not found: {self.db_path}")
            # Connect using file path and READ-ONLY mode
            # uri=True allows using mode=ro parameter
            conn = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True, timeout=10)
            logging.info(f"Connected to SQLite DB (read-only): {self.db_path}")
            return conn
        except sqlite3.Error as e:
            # Check if error is because file doesn't exist or isn't a DB
            logging.error(f"Error connecting to SQLite database {self.db_path}: {e}", exc_info=True)
            raise

    def run_query(self, query: str) -> str:
        """Executes a SQL query against the read-only SQLite database."""
        logging.info(f"Attempting to execute SQLite query (RO mode): {query[:500]}...")
        conn = None
        try:
            conn = self._get_connection()
            # Using pandas read_sql_query still works fine with the connection object
            result_df = pd.read_sql_query(query, conn)
            logging.info(f"Query returned {len(result_df)} rows.")

            if result_df.empty:
                # Return headers only for empty results
                return ",".join(result_df.columns) + "\n" if result_df.columns.tolist() else ""
            else:
                csv_buffer = io.StringIO()
                result_df.to_csv(csv_buffer, index=False)
                csv_output = csv_buffer.getvalue()
                return csv_output

        except FileNotFoundError as e:
             logging.error(f"Query failed because DB file was not found: {e}")
             return f"Error: Database file missing at {self.db_path}."
        except sqlite3.OperationalError as db_err:
             # Specific check for write attempts on read-only DB
             if "attempt to write a readonly database" in str(db_err):
                 logging.error(f"Write rejected on read-only DB. Query: '{query[:200]}...'", exc_info=False)
                 return f"Error: Database is read-only ({db_err})"
             else:
                 logging.error(f"SQLite Operational Error: {db_err}. Query: '{query[:200]}...'", exc_info=True)
                 return f"SQL Execution Error: {str(db_err)}"
        except sqlite3.Error as db_err:
            logging.error(f"General SQLite Error: {db_err}. Query: '{query[:200]}...'", exc_info=True)
            return f"SQL Execution Error: {str(db_err)}"
        except Exception as e:
            logging.error(f"Unexpected error during query execution: {e}", exc_info=True)
            return f"Unexpected Error: {str(e)}"
        finally:
            if conn:
                conn.close()
                logging.info("SQLite connection closed.")