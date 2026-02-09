"""
=============================================================
MongoDB Setup Script for Kanban Notes App
=============================================================
Run this file to create the database, collections, and
insert default columns and sample notes into MongoDB.

Usage:
    python db/setup_db.py

Requirements:
    - MongoDB server must be running on localhost:27017
    - pymongo must be installed (pip install pymongo)
=============================================================
"""

from pymongo import MongoClient
from datetime import datetime, timezone


# ----------------------------------------------------------
# Database Connection Settings
# ----------------------------------------------------------
MONGO_URI = "mongodb://localhost:27017"
DATABASE_NAME = "kanban_notes"


def connect_to_mongodb():
    """
    Connect to the MongoDB server.
    Returns the database object if successful, exits if not.
    """
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        # Test the connection by pinging the server
        client.admin.command("ping")
        print("[OK] Connected to MongoDB server.")
        return client[DATABASE_NAME]
    except Exception as e:
        print(f"[ERROR] Could not connect to MongoDB: {e}")
        exit(1)


def create_collections(db):
    """
    Create the 'columns' and 'notes' collections.
    If they already exist, MongoDB will skip creation silently.
    """
    # Get existing collection names
    existing = db.list_collection_names()

    # Create 'columns' collection if it doesn't exist
    if "columns" not in existing:
        db.create_collection("columns")
        print("[OK] Created 'columns' collection.")
    else:
        print("[SKIP] 'columns' collection already exists.")

    # Create 'notes' collection if it doesn't exist
    if "notes" not in existing:
        db.create_collection("notes")
        print("[OK] Created 'notes' collection.")
    else:
        print("[SKIP] 'notes' collection already exists.")


def insert_default_columns(db):
    """
    Insert three default Kanban columns: To Do, In Progress, Done.
    Only inserts if the columns collection is empty.
    """
    columns_collection = db["columns"]

    # Skip if columns already have data
    if columns_collection.count_documents({}) > 0:
        print("[SKIP] Columns already have data. Skipping defaults.")
        return []

    # Default columns for the Kanban board
    default_columns = [
        {
            "title": "To Do",
            "order": 0,
            "created_at": datetime.now(timezone.utc),
        },
        {
            "title": "In Progress",
            "order": 1,
            "created_at": datetime.now(timezone.utc),
        },
        {
            "title": "Done",
            "order": 2,
            "created_at": datetime.now(timezone.utc),
        },
    ]

    # Insert all default columns at once
    result = columns_collection.insert_many(default_columns)
    print(f"[OK] Inserted {len(result.inserted_ids)} default columns.")
    return result.inserted_ids


def insert_sample_notes(db, column_ids):
    """
    Insert a few sample notes into the first column (To Do).
    Only inserts if the notes collection is empty.
    """
    notes_collection = db["notes"]

    # Skip if notes already have data
    if notes_collection.count_documents({}) > 0:
        print("[SKIP] Notes already have data. Skipping samples.")
        return

    # We need at least one column_id to attach notes to
    if not column_ids:
        print("[SKIP] No column IDs provided. Skipping sample notes.")
        return

    # Sample notes for the 'To Do' column
    now = datetime.now(timezone.utc)
    sample_notes = [
        {
            "title": "Welcome to Kanban Notes",
            "content": "Drag and drop notes between columns to organize your tasks.",
            "column_id": str(column_ids[0]),
            "order": 0,
            "color": "#fff9c4",
            "created_at": now,
            "updated_at": now,
        },
        {
            "title": "Add new notes",
            "content": "Click the + button on any column to add a new note.",
            "column_id": str(column_ids[0]),
            "order": 1,
            "color": "#c8e6c9",
            "created_at": now,
            "updated_at": now,
        },
        {
            "title": "Edit or delete",
            "content": "Click on a note to edit it, or use the delete button to remove it.",
            "column_id": str(column_ids[1]),
            "order": 0,
            "color": "#bbdefb",
            "created_at": now,
            "updated_at": now,
        },
    ]

    # Insert all sample notes at once
    result = notes_collection.insert_many(sample_notes)
    print(f"[OK] Inserted {len(result.inserted_ids)} sample notes.")


def main():
    """
    Main function: connects to MongoDB, sets up collections,
    and inserts default data.
    """
    print("=" * 50)
    print("Kanban Notes - MongoDB Setup")
    print("=" * 50)

    # Step 1: Connect to MongoDB
    db = connect_to_mongodb()

    # Step 2: Create collections
    create_collections(db)

    # Step 3: Insert default columns
    column_ids = insert_default_columns(db)

    # Step 4: Insert sample notes
    insert_sample_notes(db, column_ids)

    print("=" * 50)
    print("Setup complete! Database is ready.")
    print(f"Database: {DATABASE_NAME}")
    print(f"Collections: columns, notes")
    print("=" * 50)


# ----------------------------------------------------------
# Run the script
# ----------------------------------------------------------
if __name__ == "__main__":
    main()
