from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
print(f"Connecting to MongoDB at: {MONGO_URI}")

try:
    # Connect to MongoDB
    client = MongoClient(MONGO_URI)
    
    # Test connection
    db = client.ingreedy
    db.command('ping')
    
    print("✅ Successfully connected to MongoDB!")
    
    # Create a test collection
    test_collection = db.test_collection
    
    # Insert a test document
    test_document = {"name": "test", "message": "Hello MongoDB!"}
    result = test_collection.insert_one(test_document)
    print(f"✅ Inserted document with ID: {result.inserted_id}")
    
    # Find the document
    found_document = test_collection.find_one({"name": "test"})
    print(f"✅ Found document: {found_document}")
    
    # Delete the test document
    test_collection.delete_one({"name": "test"})
    print("✅ Deleted test document")
    
    # Close the connection
    client.close()
    print("✅ Connection closed")
    
except Exception as e:
    print(f"❌ Error connecting to MongoDB: {e}") 