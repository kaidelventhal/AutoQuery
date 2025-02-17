# config.py
import os

def setup_credentials():
    """
    Set the GOOGLE_APPLICATION_CREDENTIALS environment variable
    to the JSON key stored in the project directory.
    """
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "../autoquery-450504-07c8eb3d217b.json"
    os.environ["TABLES_DIR"] = "C:/Users/kdelv/Documents/tables_V2.0"
if __name__ == "__main__":
    setup_credentials()
