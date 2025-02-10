# history.py
import json
import os

HISTORY_FILE = "chat_history.json"

def load_history():
    """
    Load chat history from a JSON file.
    Returns a list of history items.
    """
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_history(history):
    """
    Save chat history (a list of dictionaries) to a JSON file.
    """
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)
