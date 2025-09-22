import os
import sqlite3
import pandas as pd
import io
import logging

logging.basicConfig(level=logging.INFO)


_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILENAME = "autoquery_data.db"
DB_FILE_PATH = os.path.join(_BASE_DIR, DB_FILENAME)

class Database:
    def __init__(self):
        self.db_path = DB_FILE_PATH
        logging.info(f"Database object initialized for SQLite file: {self.db_path}")
        if not os.path.exists(self.db_path):
             
             logging.warning(f"Database file not found at {self.db_path} during init.")

    def _get_connection(self):
        """Establishes a read-only connection to the SQLite database."""
        try:
            if not os.path.exists(self.db_path):
                 raise FileNotFoundError(f"SQLite DB file not found: {self.db_path}")
           
            conn = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True, timeout=10)
            logging.info(f"Connected to SQLite DB (read-only): {self.db_path}")
            return conn
        except sqlite3.Error as e:
            logging.error(f"Error connecting to SQLite database {self.db_path}: {e}", exc_info=True)
            raise

    def run_query(self, query: str) -> str:
        """Executes a SQL query against the read-only SQLite database."""
        logging.info(f"Attempting to execute SQLite query (RO mode): {query[:500]}...")
        conn = None
        try:
            conn = self._get_connection()
            result_df = pd.read_sql_query(query, conn)
            logging.info(f"Query returned {len(result_df)} rows.")

            if result_df.empty:
                return ",".join(result_df.columns) + "\n" if result_df.columns.tolist() else ""
            else:
                csv_buffer = io.StringIO()
                result_df.to_csv(csv_buffer, index=False)
                csv_output = csv_buffer.getvalue()
                return csv_output
        finally:
            if conn:
                conn.close()
                logging.info("SQLite connection closed.")