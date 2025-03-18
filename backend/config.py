# config.py
import os

def setup_credentials():
    """
    Set the GOOGLE_APPLICATION_CREDENTIALS environment variable
    to the JSON key stored in the project directory.
    """
    # Get the absolute path to the credentials file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    credentials_path = os.path.abspath(os.path.join(current_dir, "..", "autoquery-450504-07c8eb3d217b.json"))
    
    # Verify the file exists
    if not os.path.exists(credentials_path):
        raise FileNotFoundError(f"Credentials file not found at: {credentials_path}")
        
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
    os.environ["TABLES_DIR"] = "C:/Users/kdelv/Documents/tables_V2.0"

if __name__ == "__main__":
    setup_credentials()
