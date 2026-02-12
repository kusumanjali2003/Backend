"""
=============================================================
FastAPI Backend for Kanban Notes App
=============================================================
This file contains all the API endpoints for managing
columns and notes on the Kanban board.

Endpoints:
    GET    /api/columns         - Get all columns
    POST   /api/columns         - Create a new column
    PUT    /api/columns/{id}    - Update a column
    DELETE /api/columns/{id}    - Delete a column and its notes

    GET    /api/notes           - Get all notes
    POST   /api/notes           - Create a new note
    PUT    /api/notes/{id}      - Update a note
    DELETE /api/notes/{id}      - Delete a note
    PUT    /api/notes/{id}/move - Move a note to another column
=============================================================
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pymongo import MongoClient
from bson import ObjectId
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
import os

# ----------------------------------------------------------
# App Initialization
# ----------------------------------------------------------
app = FastAPI(title="Kanban Notes API")

# ----------------------------------------------------------
# CORS Middleware (allow React frontend to talk to backend)
# ----------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------------
# MongoDB Connection
# ----------------------------------------------------------
MONGO_URI = "mongodb+srv://fizzy:$Arjuncm0910@cluster1.p95xnmc.mongodb.net/"
DATABASE_NAME = "kanban_notes"

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]

# Collection references
columns_collection = db["columns"]
notes_collection = db["notes"]


# ----------------------------------------------------------
# Pydantic Models (request body validation)
# ----------------------------------------------------------
class ColumnCreate(BaseModel):
    """Schema for creating a new column."""
    title: str


class ColumnUpdate(BaseModel):
    """Schema for updating a column."""
    title: Optional[str] = None
    order: Optional[int] = None


class NoteCreate(BaseModel):
    """Schema for creating a new note."""
    title: str
    content: str = ""
    column_id: str
    color: str = "#fff9c4"


class NoteUpdate(BaseModel):
    """Schema for updating a note."""
    title: Optional[str] = None
    content: Optional[str] = None
    color: Optional[str] = None


class NoteMove(BaseModel):
    """Schema for moving a note to a different column."""
    column_id: str
    order: int


# ----------------------------------------------------------
# Helper: Convert MongoDB document to JSON-friendly dict
# ----------------------------------------------------------
def doc_to_dict(doc):
    if doc is None:
        return None

    for key, value in doc.items():
        if isinstance(value, ObjectId):
            doc[key] = str(value)

    return doc


# ==========================================================
# COLUMN ENDPOINTS
# ==========================================================

@app.get("/api/columns")
def get_all_columns():
    """
    Get all columns, sorted by their order.
    Returns a list of column objects.
    """
    # Find all columns and sort by the 'order' field
    columns = columns_collection.find().sort("order", 1)
    # Convert each document to a dict
    result = [doc_to_dict(col) for col in columns]
    return result


@app.post("/api/columns")
def create_column(column: ColumnCreate):
    """
    Create a new column at the end of the board.
    Auto-assigns the next order number.
    """
    # Count existing columns to determine the order
    count = columns_collection.count_documents({})

    # Build the column document
    new_column = {
        "title": column.title,
        "order": count,
        "created_at": datetime.now(timezone.utc),
    }

    # Insert into MongoDB
    result = columns_collection.insert_one(new_column)

    # Return the created column with its new _id
    new_column["_id"] = str(result.inserted_id)
    return new_column


@app.put("/api/columns/{column_id}")
def update_column(column_id: str, column: ColumnUpdate):
    """
    Update a column's title or order.
    Only updates fields that are provided (not None).
    """
    # Build update dict with only non-None fields
    update_data = {}
    if column.title is not None:
        update_data["title"] = column.title
    if column.order is not None:
        update_data["order"] = column.order

    # Nothing to update
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update.")

    # Update the column in MongoDB
    result = columns_collection.update_one(
        {"_id": ObjectId(column_id)},
        {"$set": update_data}
    )

    # Check if the column was found
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Column not found.")

    # Return the updated column
    updated = columns_collection.find_one({"_id": ObjectId(column_id)})
    return doc_to_dict(updated)


@app.delete("/api/columns/{column_id}")
def delete_column(column_id: str):
    """
    Delete a column and all notes inside it.
    """
    # First, delete all notes that belong to this column
    notes_collection.delete_many({"column_id": column_id})

    # Then delete the column itself
    result = columns_collection.delete_one({"_id": ObjectId(column_id)})

    # Check if the column existed
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Column not found.")

    return {"message": "Column and its notes deleted."}


# ==========================================================
# NOTE ENDPOINTS
# ==========================================================

@app.get("/api/notes")
def get_all_notes():
    """
    Get all notes, sorted by their order within each column.
    Returns a list of note objects.
    """
    # Find all notes and sort by order
    notes = notes_collection.find().sort("order", 1)
    result = [doc_to_dict(note) for note in notes]
    return result


@app.post("/api/notes")
def create_note(note: NoteCreate):
    """
    Create a new note in a specified column.
    Auto-assigns the next order number within that column.
    """
    # Verify the target column exists
    column = columns_collection.find_one({"_id": ObjectId(note.column_id)})
    if not column:
        raise HTTPException(status_code=404, detail="Column not found.")

    # Count existing notes in this column for ordering
    count = notes_collection.count_documents({"column_id": note.column_id})
    now = datetime.now(timezone.utc)

    # Build the note document
    new_note = {
        "title": note.title,
        "content": note.content,
        "column_id": note.column_id,
        "order": count,
        "color": note.color,
        "created_at": now,
        "updated_at": now,
    }

    # Insert into MongoDB
    result = notes_collection.insert_one(new_note)

    # Return the created note with its new _id
    new_note["_id"] = str(result.inserted_id)
    return new_note


@app.put("/api/notes/{note_id}")
def update_note(note_id: str, note: NoteUpdate):
    """
    Update a note's title, content, or color.
    Only updates fields that are provided (not None).
    """
    # Build update dict with only non-None fields
    update_data = {}
    if note.title is not None:
        update_data["title"] = note.title
    if note.content is not None:
        update_data["content"] = note.content
    if note.color is not None:
        update_data["color"] = note.color

    # Nothing to update
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update.")

    # Always update the timestamp
    update_data["updated_at"] = datetime.now(timezone.utc)

    # Update the note in MongoDB
    result = notes_collection.update_one(
        {"_id": ObjectId(note_id)},
        {"$set": update_data}
    )

    # Check if the note was found
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Note not found.")

    # Return the updated note
    updated = notes_collection.find_one({"_id": ObjectId(note_id)})
    return doc_to_dict(updated)


@app.delete("/api/notes/{note_id}")
def delete_note(note_id: str):
    """
    Delete a single note by its ID.
    """
    result = notes_collection.delete_one({"_id": ObjectId(note_id)})

    # Check if the note existed
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Note not found.")

    return {"message": "Note deleted."}


@app.put("/api/notes/{note_id}/move")
def move_note(note_id: str, move: NoteMove):
    """
    Move a note to a different column and/or change its order.
    Used for drag-and-drop functionality.
    """
    # Verify the target column exists
    column = columns_collection.find_one({"_id": ObjectId(move.column_id)})
    if not column:
        raise HTTPException(status_code=404, detail="Target column not found.")

    # Update the note's column and order
    result = notes_collection.update_one(
        {"_id": ObjectId(note_id)},
        {"$set": {
            "column_id": move.column_id,
            "order": move.order,
            "updated_at": datetime.now(timezone.utc),
        }}
    )

    # Check if the note was found
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Note not found.")

    # Return the updated note
    updated = notes_collection.find_one({"_id": ObjectId(note_id)})
    return doc_to_dict(updated)


# ----------------------------------------------------------
# Serve React Frontend (static files)
# ----------------------------------------------------------
# Check if the frontend build folder exists
frontend_build_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "build")

if os.path.exists(frontend_build_path):
    # Serve static files (JS, CSS, images) from the build folder
    app.mount("/static", StaticFiles(directory=os.path.join(frontend_build_path, "static")), name="static")

    @app.get("/{full_path:path}")
    def serve_react(full_path: str):
        """
        Catch-all route: serves the React app's index.html
        for any path not matched by API routes above.
        """
        return FileResponse(os.path.join(frontend_build_path, "index.html"))


# ----------------------------------------------------------
# Run the server
# ----------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    import sys
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except OSError as e:
        print(f"Failed to start server: {e}")
        print("Port may be in use. Try changing the port or stopping the other process.")
        sys.exit(1)
