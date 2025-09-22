import pandas as pd
import sqlite3
import os
import logging

DATA_DIR = os.path.join(os.path.dirname(__file__), 'tables_V2.0')
DB_PATH = os.path.join(os.path.dirname(__file__), 'autoquery_data.db')

TABLE_MAPPING = {
    os.path.join(DATA_DIR, "Basic_table.csv"): "basic_table",
    os.path.join(DATA_DIR, "Price_table.csv"): "price_table",
    os.path.join(DATA_DIR, "Sales_table.csv"): "sales_table",
    os.path.join(DATA_DIR, "Trim_table.csv"): "trim_table",
    os.path.join(DATA_DIR, "vehicle_ads.csv"): "vehicle_ads"
}

def create_db_and_get_schema():
    if os.path.exists(DB_PATH):
        logging.info(f"Database file '{DB_PATH}' already exists. Deleting it to rebuild.")
        os.remove(DB_PATH)

    all_tables_created = []

    try:
        conn = sqlite3.connect(DB_PATH)
        logging.info(f"Successfully created SQLite database at '{DB_PATH}'")

        for csv_path, table_name in TABLE_MAPPING.items():
            if os.path.exists(csv_path):
                logging.info(f"Reading '{os.path.basename(csv_path)}'...")
                df = pd.read_csv(csv_path)
                df.columns = df.columns.str.strip()

                if table_name == "sales_table":
                    for col in df.columns:
                        if col.isdigit():
                            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

                df.to_sql(table_name, conn, if_exists='replace', index=False)
                all_tables_created.append(table_name)
                logging.info(f"Successfully created table '{table_name}'.")
            else:
                logging.warning(f"CSV file not found, skipping: '{csv_path}'")

        print("\n" + "="*50)
        print("DATABASE SCHEMA FOR PROMPTS.PY")
        print("="*50 + "\n")

        for table_name in sorted(all_tables_created):
            print(f"        `{table_name}`: Description of the table.")
            df = pd.read_sql_query(f"SELECT * FROM {table_name} LIMIT 1", conn)
            schema = pd.io.sql.get_schema(df, table_name)
            columns = [line.strip().split(" ") for line in schema.split('\n') if "CREATE TABLE" not in line and ")" not in line and line.strip() != ""]
            for col_info in columns:
                col_name = col_info[0].replace('"', '')
                col_type = col_info[1]
                print(f"            `{col_name}` ({col_type})")
            print("")

        conn.close()
        logging.info("Database creation complete and connection closed.")

    except Exception as e:
        logging.error(f"An error occurred during database creation: {e}", exc_info=True)

if __name__ == "__main__":
    create_db_and_get_schema()