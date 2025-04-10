# config.py
import os

# No hardcoded paths needed here anymore.
# App Engine uses Application Default Credentials (ADC) automatically
# for Google Cloud client libraries (like Vertex AI and Cloud Storage).
# GCS Bucket/Folder configuration is now handled via environment variables
# set in app.yaml and read directly in app.py/database.py.

# You can keep this file empty or remove it if nothing else needs configuration here.
# If keeping it, ensure setup_credentials() is NOT called from app.py or main.py.

# Let's leave it empty for now. You could add other non-sensitive config later.
pass