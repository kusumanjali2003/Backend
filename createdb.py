from pymongo import MongoClient  
# This imports the tool that lets Python talk to MongoDB

client = MongoClient("mongodb://localhost:27017/")  
# This connects to MongoDB running on your computer

db = client["notesDB"]  
# This names your database (it will be created automatically)

collection = db["users"]  
# This creates a collection inside the database

collection.insert_one({"status": "database created"})  
# This inserts one record, which forces MongoDB to create the DB

print("Database created successfully")  
# This confirms everything worked
