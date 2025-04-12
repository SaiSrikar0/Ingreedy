from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client.ingreedy

# Collections
recipes = db.recipes
ingredients = db.ingredients

def init_db():
    """Initialize database with indexes"""
    try:
        # Create indexes
        recipes.create_index([("title", "text")])
        recipes.create_index([("ingredients", "text")])
        recipes.create_index([("tags", "text")])
        
        # Create unique index for ingredients
        ingredients.create_index("name", unique=True)
        
        print("✅ Database indexes created successfully")
    except Exception as e:
        print(f"⚠️ Warning: Could not create all indexes: {e}")
        print("Continuing with basic functionality...")

def save_recipe(recipe_data):
    """Save a recipe to the database"""
    recipe_data["created_at"] = datetime.utcnow()
    recipe_data["updated_at"] = datetime.utcnow()
    return recipes.insert_one(recipe_data)

def save_ingredients(ingredient_list):
    """Save ingredients to the database"""
    for ingredient in ingredient_list:
        ingredients.update_one(
            {"name": ingredient.lower()},
            {"$set": {"name": ingredient.lower(), "updated_at": datetime.utcnow()}},
            upsert=True
        )

def get_all_ingredients():
    """Get all unique ingredients"""
    return [doc["name"] for doc in ingredients.find({}, {"name": 1})]

def search_recipes_by_ingredients(ingredient_list, max_results=5):
    """Search recipes by ingredients"""
    # Convert ingredients to lowercase for case-insensitive matching
    ingredient_list = [ing.lower() for ing in ingredient_list]
    
    # Find recipes that contain any of the ingredients
    pipeline = [
        {
            "$match": {
                "ingredients_simple": {
                    "$in": ingredient_list
                }
            }
        },
        {
            "$addFields": {
                "match_count": {
                    "$size": {
                        "$setIntersection": ["$ingredients_simple", ingredient_list]
                    }
                }
            }
        },
        {
            "$sort": {"match_count": -1}
        },
        {
            "$limit": max_results
        }
    ]
    
    return list(recipes.aggregate(pipeline))

def get_recipe_by_id(recipe_id):
    """Get a recipe by its ID"""
    return recipes.find_one({"_id": recipe_id})

def update_recipe(recipe_id, recipe_data):
    """Update a recipe"""
    recipe_data["updated_at"] = datetime.utcnow()
    return recipes.update_one(
        {"_id": recipe_id},
        {"$set": recipe_data}
    )

def delete_recipe(recipe_id):
    """Delete a recipe"""
    return recipes.delete_one({"_id": recipe_id}) 