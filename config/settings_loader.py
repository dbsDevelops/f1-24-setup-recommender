import json

SETTINGS_FILE = "config/settings.txt"

def load_settings():
    """Loads settings from the configuration file."""
    with open(SETTINGS_FILE, "r") as file:
        return json.load(file)