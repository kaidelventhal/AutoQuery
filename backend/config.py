# config.py
import os
import io
from dotenv import load_dotenv
from google.cloud import secretmanager

load_dotenv() # Load environment variables from .env file for local development

# --- GCP Config ---
GCP_PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT")
GCP_REGION = os.environ.get("GCP_REGION", "us-central1") # Example region

# --- GCS Config (for loading data) ---
# These are typically set in app.yaml for deployment
# Or in your local .env for local development
TABLES_BUCKET = os.environ.get("TABLES_BUCKET")
TABLES_FOLDER = os.environ.get("TABLES_FOLDER")

# --- Secret Manager Config ---
# Used IF you need to fetch an API key explicitly.
# Often, Vertex AI uses Application Default Credentials (ADC) automatically on GCP.
API_KEY_SECRET_NAME = os.environ.get("API_KEY_SECRET_NAME") # e.g., "VERTEX_AI_API_KEY" or similar
secret_client = None

def get_secret_client():
    """Initializes and returns the Secret Manager client."""
    global secret_client
    if secret_client is None:
        secret_client = secretmanager.SecretManagerServiceClient()
    return secret_client

def get_secret(secret_name, project_id=GCP_PROJECT, version="latest"):
    """Fetches a secret value from Google Secret Manager."""
    if not project_id or not secret_name:
        print(f"Warning: GCP_PROJECT or Secret Name ({secret_name}) not configured. Cannot fetch secret.")
        return None
    try:
        client = get_secret_client()
        name = f"projects/{project_id}/secrets/{secret_name}/versions/{version}"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        print(f"Error accessing secret {secret_name}: {e}")
        return None

# --- Vertex AI Setup (ADC is usually sufficient) ---
def setup_credentials():
    """
    Sets up credentials. For Vertex AI on App Engine, Application Default Credentials (ADC)
    are typically sufficient. Ensure the App Engine service account has 'Vertex AI User' role.
    This function mainly serves to print a confirmation or handle explicit key file paths if set.
    """
    # Explicitly setting GOOGLE_APPLICATION_CREDENTIALS might be needed
    # if ADC isn't working or for specific auth scenarios.
    # You could potentially fetch a key from Secret Manager and write it to a temp file
    # if the library requires a file path, but try ADC first.
    key_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if key_path and os.path.exists(key_path):
         print(f"Using explicit credentials file: {key_path}")
    elif API_KEY_SECRET_NAME:
         print(f"Attempting to use ADC. Also configured to potentially fetch secret: {API_KEY_SECRET_NAME}")
         # Fetching logic could be added here if needed, e.g., saving to /tmp
    else:
         print("Using Application Default Credentials (ADC) for Vertex AI.")

    if not GCP_PROJECT:
         print("Warning: GOOGLE_CLOUD_PROJECT environment variable is not set.")


if __name__ == "__main__":
    # Example usage for testing config
    setup_credentials()
    print(f"Project ID: {GCP_PROJECT}")
    print(f"Tables Bucket: {TABLES_BUCKET}")
    print(f"Tables Folder: {TABLES_FOLDER}")
    # Example API key fetch
    # if API_KEY_SECRET_NAME:
    #    api_key = get_secret(API_KEY_SECRET_NAME)
    #    print(f"API Key Secret fetched: {'Yes' if api_key else 'No'}")