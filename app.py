
import firebase_admin
from firebase_admin import credentials, db
from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
import pymongo
from datetime import datetime, timezone

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# MongoDB setup (for long-term storage)
mongo_client = pymongo.MongoClient(os.getenv("MONGO_URI"))
db_mongo = mongo_client["gps_tracking"]
collection = db_mongo["locations"]

# Firebase setup
cred = credentials.Certificate('firebase_service.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': os.getenv("FIREBASE_DB_URL")
})

# Function to send data to Firebase Realtime Database
def send_to_firebase(data):
    ref = db.reference('/locations')
    ref.push(data)  # Push the new GPS location to Firebase
    print("Data sent to Firebase!")

@app.route('/')
def index():
    return "Welcome to the Real-Time GPS Tracker API! Created By : Yash and atharv"
# Define a route to accept GPS location data
@app.route('/api/v1/location', methods=['POST'])
def save_location():
    data = request.get_json()
    if data and "latitude" in data and "longitude" in data:
        # Add a timezone-aware UTC timestamp in ISO format
        data["timestamp"] = datetime.now(timezone.utc).isoformat()

        # Store data in MongoDB for long-term storage and retrieve the inserted document's ID
        result = collection.insert_one(data)
        
        # Convert MongoDB ObjectId to a string and add it to the data
        data["_id"] = str(result.inserted_id)
        
        # Send data to Firebase for real-time tracking
        send_to_firebase(data)

        return jsonify({"status": "success", "data": data}), 200
    return jsonify({"error": "Invalid data"}), 400

if __name__ == "__main__":
    app.run(debug=True)
