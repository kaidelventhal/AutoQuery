# database.py
import os
import pandas as pd
import pandasql as ps

class Database:
    def __init__(self, tables_dir):
        self.tables_dir = tables_dir
        self.load_tables()
    
    def load_tables(self):
        print("Loading CSV tables from:", self.tables_dir)
        self.ad_table = pd.read_csv(os.path.join(self.tables_dir, 'Ad_table.csv'), low_memory=False)
        self.price_table = pd.read_csv(os.path.join(self.tables_dir, 'Price_table.csv'), low_memory=False)
        self.sales_table = pd.read_csv(os.path.join(self.tables_dir, 'Sales_table.csv'), low_memory=False)
        self.basic_table = pd.read_csv(os.path.join(self.tables_dir, 'Basic_table.csv'), low_memory=False)
        self.trim_table = pd.read_csv(os.path.join(self.tables_dir, 'Trim_table.csv'), low_memory=False)
        self.img_table = pd.read_csv(os.path.join(self.tables_dir, 'Image_table.csv'), low_memory=False)
        print("Tables loaded successfully.")
    
    def run_query(self, query):
        try:
            env = {
                'ad_table': self.ad_table,
                'price_table': self.price_table,
                'sales_table': self.sales_table,
                'basic_table': self.basic_table,
                'trim_table': self.trim_table,
                'img_table': self.img_table,
                'pd': pd
            }
            result = ps.sqldf(query, env)
            return result.to_csv(index=False)
        except Exception as e:
            return f"SQL Execution Error: {str(e)}"
