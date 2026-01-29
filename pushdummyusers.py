import json
from pymongo import MongoClient
from datetime import datetime

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["notesDB"]
collection = db["users"]

# Load users JSON
with open("users.json", "r") as file:
    users = json.load(file)

# Convert ISO date strings to datetime objects
for user in users:
    user["createdAt"] = datetime.fromisoformat(
        user["createdAt"].replace("Z", "")
    )
    user["updatedAt"] = datetime.fromisoformat(
        user["updatedAt"].replace("Z", "")
    )

# Insert users
result = collection.insert_many(users)

print(f"Inserted {len(result.inserted_ids)} users successfully ✅")
