import json
import os

DB_FILE = 'database/users.json'

def load_users():
    if not os.path.exists(DB_FILE):
        return []
    try:
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_user(user):
    users = load_users()
    users.append(user)
    try:
        with open(DB_FILE, 'w') as f:
            json.dump(users, f, indent=4)
    except Exception as e:
        print(f"Error saving user: {e}")

# Initial load
users = load_users()

# We can keep progress_data in memory or add similar persistence if needed later
progress_data = []
