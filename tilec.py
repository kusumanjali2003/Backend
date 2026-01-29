from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["notesDB"]
collection = db["tiles"]

# Update each document
for doc in collection.find():
    tile_count = len(doc.get("tiles", []))

    collection.update_one(
        {"_id": doc["_id"]},
        {"$set": {"tilec": tile_count}}
    )

print("tilec field added successfully ✅")
