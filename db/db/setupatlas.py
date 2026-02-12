"""
=============================================================
MongoDB Atlas Setup Script for Kanban Notes App
=============================================================
Run this file to create the database, collections, and
insert default columns and sample notes into MongoDB Atlas.

Usage:
    python setup_atlas.py

Requirements:
    pip install pymongo
=============================================================
"""

from pymongo import MongoClient
from datetime import datetime, timezone
import sys

# ----------------------------------------------------------
# 🔐 UPDATE THIS WITH YOUR ATLAS CONNECTION STRING
# ----------------------------------------------------------
MONGO_URI = "mongodb+srv://fizzy:$Arjuncm0910@cluster1.p95xnmc.mongodb.net/"
DATABASE_NAME = "kanban_notes"


# ----------------------------------------------------------
# Connect to MongoDB Atlas
# ----------------------------------------------------------
def connect_to_mongodb():
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        print("[OK] Connected to MongoDB Atlas.")
        return client[DATABASE_NAME]
    except Exception as e:
        print(f"[ERROR] Could not connect to MongoDB Atlas: {e}")
        sys.exit(1)


# ----------------------------------------------------------
# Create Collections (If Not Exist)
# ----------------------------------------------------------
def create_collections(db):
    existing = db.list_collection_names()

    if "columns" not in existing:
        db.create_collection("columns")
        print("[OK] Created 'columns' collection.")
    else:
        print("[SKIP] 'columns' collection already exists.")

    if "notes" not in existing:
        db.create_collection("notes")
        print("[OK] Created 'notes' collection.")
    else:
        print("[SKIP] 'notes' collection already exists.")


# ----------------------------------------------------------
# Insert Default Columns (Only If Empty)
# ----------------------------------------------------------
def insert_default_columns(db):
    columns_collection = db["columns"]

    if columns_collection.count_documents({}) > 0:
        print("[SKIP] Columns already have data.")
        return columns_collection.find({}).to_list(length=100)

    now = datetime.now(timezone.utc)

    default_columns = [
        {"title": "To Do", "order": 0, "created_at": now},
        {"title": "In Progress", "order": 1, "created_at": now},
        {"title": "Done", "order": 2, "created_at": now},
    ]

    result = columns_collection.insert_many(default_columns)
    print(f"[OK] Inserted {len(result.inserted_ids)} default columns.")

    return columns_collection.find({}).to_list(length=100)


# ----------------------------------------------------------
# Insert Sample Notes (Only If Empty)
# ----------------------------------------------------------
def insert_sample_notes(db, columns):
    notes_collection = db["notes"]

    if notes_collection.count_documents({}) > 0:
        print("[SKIP] Notes already have data.")
        return

    if not columns:
        print("[ERROR] No columns found. Cannot insert notes.")
        return

    # Get column IDs
    todo_column = next((c for c in columns if c["title"] == "To Do"), None)
    in_progress_column = next((c for c in columns if c["title"] == "In Progress"), None)

    if not todo_column:
        print("[ERROR] 'To Do' column not found.")
        return

    now = datetime.now(timezone.utc)

    sample_notes = [
        {
            "title": "Welcome to Kanban Notes",
            "content": "Drag and drop notes between columns to organize your tasks.",
            "column_id": todo_column["_id"],
            "order": 0,
            "color": "#fff9c4",
            "created_at": now,
            "updated_at": now,
        },
        {
            "title": "Add new notes",
            "content": "Click the + button on any column to add a new note.",
            "column_id": todo_column["_id"],
            "order": 1,
            "color": "#c8e6c9",
            "created_at": now,
            "updated_at": now,
        },
        {
            "title": "Edit or delete",
            "content": "Click on a note to edit it or delete it.",
            "column_id": in_progress_column["_id"] if in_progress_column else todo_column["_id"],
            "order": 0,
            "color": "#bbdefb",
            "created_at": now,
            "updated_at": now,
        },
    ]

    result = notes_collection.insert_many(sample_notes)
    print(f"[OK] Inserted {len(result.inserted_ids)} sample notes.")


# ----------------------------------------------------------
# Main Execution
# ----------------------------------------------------------
def main():
    print("=" * 50)
    print("Kanban Notes - MongoDB Atlas Setup")
    print("=" * 50)

    db = connect_to_mongodb()
    create_collections(db)

    columns = insert_default_columns(db)
    insert_sample_notes(db, columns)

    print("=" * 50)
    print("Setup complete! Atlas database is ready.")
    print(f"Database: {DATABASE_NAME}")
    print("Collections: columns, notes")
    print("=" * 50)


if __name__ == "__main__":
    main()
