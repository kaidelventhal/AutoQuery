import os
import pandas as pd
import pandasql as ps

# === SETUP: Define your table directory and load CSV files ===

# Update this path to the location of your downloaded DVM-CAR tables
TABLE_DIR = r'C:\Users\kdelv\Documents\tables_V2.0'

# Load the CSV tables into pandas DataFrames
ad_table = pd.read_csv(os.path.join(TABLE_DIR, 'Ad_table.csv'))
price_table = pd.read_csv(os.path.join(TABLE_DIR, 'Price_table.csv'))
sales_table = pd.read_csv(os.path.join(TABLE_DIR, 'Sales_table.csv'))
basic_table = pd.read_csv(os.path.join(TABLE_DIR, 'Basic_table.csv'))
trim_table = pd.read_csv(os.path.join(TABLE_DIR, 'Trim_table.csv'))
img_table = pd.read_csv(os.path.join(TABLE_DIR, 'Image_table.csv'))

# === FUNCTION: Run SQL queries on the DataFrames using pandasql ===

def run_query(query, env):
    """
    Executes an SQL query on pandas DataFrames using pandasql.
    
    :param query: SQL query string.
    :param env: Dictionary containing the environment variables (e.g., DataFrames).
    :return: A DataFrame with the query results.
    """
    return ps.sqldf(query, env)

# === FUNCTION: Dummy natural language to SQL converter ===

def simulate_nl_to_sql(nl_query):
    """
    Dummy function to simulate the conversion of a natural language query to an SQL query.
    In a production version, replace this function with one that uses an LLM (via LangChain or similar)
    to generate SQL queries.
    
    :param nl_query: A natural language query string.
    :return: An SQL query string.
    """
    nl_query_lower = nl_query.lower()
    if "2018" in nl_query_lower and "saloon" in nl_query_lower:
        sql_query = """
        SELECT * FROM ad_table
        WHERE Reg_year = 2018 AND Bodytype = 'Saloon'
        """
    elif "price" in nl_query_lower:
        sql_query = """
        SELECT a.Genmodel_ID, a.Maker, a.Genmodel, p.Year, p.Price
        FROM ad_table AS a
        JOIN price_table AS p ON a.Genmodel_ID = p.Genmodel_ID
        WHERE p.Year = 2018
        """
    else:
        sql_query = "SELECT * FROM ad_table LIMIT 5"
    
    return sql_query

# === MAIN FUNCTION: Interactive Query Agent ===

def main():
    print("Welcome to AutoSensei Query Interface!")
    print("Enter your natural language query to retrieve data from the automotive database.")
    print("Type 'exit' to quit.\n")
    
    while True:
        nl_query = input("Your query: ").strip()
        if nl_query.lower() == 'exit':
            print("Exiting. Thank you!")
            break
        
        # Convert the natural language query to an SQL query.
        # (Later, integrate with an LLM-powered conversion using LangChain)
        sql_query = simulate_nl_to_sql(nl_query)
        print("\n[DEBUG] Generated SQL Query:")
        print(sql_query)
        
        # Run the SQL query using pandasql.
        # Passing globals() gives pandasql access to your DataFrames.
        try:
            result_df = run_query(sql_query, globals())
            print("\nQuery Results:")
            print(result_df.head(), "\n")
        except Exception as e:
            print("Error executing query:", e)

if __name__ == "__main__":
    main()
