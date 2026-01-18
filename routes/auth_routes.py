from flask import Blueprint, request, jsonify

auth = Blueprint('auth', __name__)

@auth.route("/register", methods=["POST"])
def register():
    # Refresh users list from file to be safe
    from database.db import users, save_user, load_users
    users = load_users()
    
    data = request.json
    # Basic check if user exists
    for user in users:
        if user["email"] == data["email"]:
             return jsonify({"error": "User already exists"}), 400
             
    # Append to memory list (global reference in db.py updates)
    # But better to just use save_user which handles load-append-save
    save_user(data)
    
    return jsonify({"message": "User registered"}), 201

@auth.route("/login", methods=["POST"])
def login():
    from database.db import load_users
    users = load_users() # Always get fresh data
    
    data = request.json
    for user in users:
        if user["email"] == data["email"] and user["password"] == data["password"]:
            # In a real app, return a JWT token here
            return jsonify({"message": "Login success", "user": {"email": user["email"], "username": user.get("username", "User")}})
    return jsonify({"error": "Invalid credentials"}), 401
