from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import os

app = Flask(__name__)
CORS(app)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/login_db")

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
    db = client.get_database()
    users_collection = db.users
except Exception as e:
    print(f"Failed to connect to MongoDB: {e}")
    users_collection = None

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
         return jsonify({"error": "Missing username or password"}), 400

    if users_collection is not None:
        user = users_collection.find_one({"username": username, "password": password})
        if user:
            return jsonify({"message": "Login successful"}), 200
        else:
            return jsonify({"error": "Invalid credentials"}), 401
    else:
        # Mock login for testing if DB is not available
        if username == "admin" and password == "admin":
             return jsonify({"message": "Login successful"}), 200
        return jsonify({"error": "Invalid credentials"}), 401
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
