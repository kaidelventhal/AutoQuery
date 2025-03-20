# config.py
from dotenv import load_dotenv

def setup_credentials():
    """
    Set the GOOGLE_APPLICATION_CREDENTIALS environment variable
    to the JSON key stored in the project directory.
    """
    # Get the absolute path to the credentials file
    load_dotenv()

if __name__ == "__main__":
    setup_credentials()
