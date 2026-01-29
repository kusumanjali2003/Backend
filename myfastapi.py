from fastapi import FastAPI, HTTPException
from pymongo import MongoClient

app = FastAPI()

client = MongoClient("mongodb://localhost:27017/")
db = client["notesDB"]
collection = db["tiles"]

@app.get("/tiles/{uid}")
def get_tiles_by_uid(uid: str):
    doc = collection.find_one(
        {"uid": uid},
        {"_id": 0}
    )

    if not doc:
        raise HTTPException(status_code=404, detail="Tiles not found")

    return doc
