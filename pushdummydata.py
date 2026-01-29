import json
from pymongo import MongoClient
from datetime import datetime

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["notesDB"]
collection = db["tiles"]

# Load JSON file
with open("tiles.json", "r") as file:
    data = json.load(file)

# Convert ISO date strings to datetime objects
for user in data:
    for tile in user["tiles"]:
        tile["createdAt"] = datetime.fromisoformat(
            tile["createdAt"].replace("Z", "")
        )
        tile["updatedAt"] = datetime.fromisoformat(
            tile["updatedAt"].replace("Z", "")
        )

# Insert into MongoDB
result = collection.insert_many(data)

print(f"Inserted {len(result.inserted_ids)} documents successfully ✅")
