import json
import os

def load_settings(username):
    filename = f"{username}_settings.json"
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    else:
        # Starting default settings (keys must match your app’s expected keys)
        return {
            "monthly_budget": 2000,
            "categories": ["Food", "Transport", "Rent", "Subscriptions", "Other"]
        }

def save_settings(username, settings):
    filename = f"{username}_settings.json"
    with open(filename, "w") as f:
        json.dump(settings, f)
