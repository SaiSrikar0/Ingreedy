import os
import json
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB setup
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "ingreedy")
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
recipes_collection = db["recipes"]

def main():
    """Check and fix the recipes collection"""
    # Get count of recipes
    count = recipes_collection.count_documents({})
    print(f"Found {count} recipes in the database")
    
    # Get a sample recipe
    recipe = recipes_collection.find_one()
    if not recipe:
        print("No recipes found!")
        return
    
    # Print recipe structure
    print("\nSample recipe structure:")
    print(f"Recipe ID: {recipe.get('_id')}")
    print(f"Recipe keys: {list(recipe.keys())}")
    print(f"Recipe title: {recipe.get('title')}")
    
    # Check if ingredients field exists and has the right structure
    if 'ingredients' not in recipe:
        print("\nWARNING: 'ingredients' field missing from recipes!")
    else:
        print(f"\nIngredients type: {type(recipe.get('ingredients'))}")
        print(f"Sample ingredients: {recipe.get('ingredients')[:3] if isinstance(recipe.get('ingredients'), list) else recipe.get('ingredients')}")
    
    # Create sample recipe data for fixing
    sample_recipes = [
        {
            "title": "Simple Pasta",
            "url": "http://example.com/simple-pasta",
            "ingredients": ["1 pound pasta", "2 tablespoons olive oil", "3 cloves garlic, minced", 
                          "1/4 teaspoon red pepper flakes", "1/2 cup grated Parmesan cheese"],
            "instructions": ["Cook pasta according to package directions.", 
                           "Heat oil in a large skillet over medium heat.", 
                           "Add garlic and red pepper flakes, cook for 1 minute.",
                           "Drain pasta and add to skillet, toss to coat.",
                           "Sprinkle with cheese before serving."],
            "image_url": "https://example.com/pasta.jpg",
            "prep_time": "5 minutes",
            "cook_time": "15 minutes",
            "servings": "4 servings",
            "tags": ["pasta", "quick meals", "italian"],
            "ingredients_simple": ["pasta", "olive oil", "garlic", "red pepper flakes", "parmesan cheese"]
        },
        {
            "title": "Quick Scrambled Eggs",
            "url": "http://example.com/scrambled-eggs",
            "ingredients": ["4 large eggs", "2 tablespoons milk", "1/8 teaspoon salt", 
                          "1/8 teaspoon black pepper", "1 tablespoon butter"],
            "instructions": ["Whisk eggs, milk, salt and pepper in a bowl.",
                           "Melt butter in a skillet over medium heat.",
                           "Pour egg mixture into skillet.",
                           "Cook, stirring occasionally, until eggs are set but still moist.",
                           "Serve immediately."],
            "image_url": "https://example.com/eggs.jpg",
            "prep_time": "2 minutes",
            "cook_time": "5 minutes",
            "servings": "2 servings",
            "tags": ["breakfast", "quick", "eggs"],
            "ingredients_simple": ["eggs", "milk", "salt", "black pepper", "butter"]
        }
    ]
    
    # Ask user if they want to fix the data
    answer = input("\nDo you want to add sample recipes to fix the data? (y/n): ")
    if answer.lower() == 'y':
        # Clear the collection
        recipes_collection.delete_many({})
        
        # Insert sample recipes
        recipes_collection.insert_many(sample_recipes)
        print(f"Inserted {len(sample_recipes)} sample recipes")
        
        # Verify
        count = recipes_collection.count_documents({})
        print(f"Collection now has {count} recipes")
    else:
        print("No changes made to the database")

if __name__ == "__main__":
    main() 