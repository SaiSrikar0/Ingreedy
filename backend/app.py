import os
import sys
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the RecipeProcessor
from data.processor import RecipeProcessor

# Load environment variables
load_dotenv()

# MongoDB setup
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "ingreedy")
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
recipes_collection = db["recipes"]
processed_collection = db["processed_recipes"]

# Create and configure app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Create a global RecipeProcessor instance
recipe_processor = RecipeProcessor()

@app.route('/')
def index():
    """Home endpoint"""
    return jsonify({
        "message": "Welcome to the Ingreedy API",
        "endpoints": {
            "GET /": "This help message",
            "GET /recipes": "Get all recipes",
            "GET /recipes/<id>": "Get recipe by ID",
            "GET /recipes/search?ingredients=ing1,ing2,...": "Search recipes by ingredients",
            "GET /recipes/random": "Get a random recipe",
            "GET /ingredients": "Get list of all unique ingredients"
        }
    })

@app.route('/recipes')
def get_all_recipes():
    """Get all recipes with pagination"""
    # Get pagination parameters
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    skip = (page - 1) * limit
    
    # Get recipes
    recipes = list(recipes_collection.find({}, {'_id': 0}).skip(skip).limit(limit))
    total = recipes_collection.count_documents({})
    
    return jsonify({
        "page": page,
        "limit": limit,
        "total": total,
        "recipes": recipes
    })

@app.route('/recipes/<recipe_id>')
def get_recipe_by_id(recipe_id):
    """Get recipe by ID"""
    recipe = recipes_collection.find_one({"_id": recipe_id}, {'_id': 0})
    
    if recipe:
        return jsonify(recipe)
    else:
        return jsonify({"error": "Recipe not found"}), 404

@app.route('/recipes/random')
def get_random_recipe():
    """Get a random recipe"""
    # Get a random recipe
    recipe = recipes_collection.aggregate([
        {"$sample": {"size": 1}}
    ]).next()
    
    # Convert ObjectId to string
    recipe['_id'] = str(recipe['_id'])
    
    return jsonify(recipe)

@app.route('/recipes/search')
def search_recipes_by_ingredients():
    """Search recipes by ingredients"""
    # Get ingredients from query parameters
    ingredients_param = request.args.get('ingredients', '')
    if not ingredients_param:
        return jsonify({"error": "No ingredients provided"}), 400
    
    # Split ingredients into a list
    ingredients = [ing.strip() for ing in ingredients_param.split(',')]
    
    # Initialize the recipe processor if needed
    global recipe_processor
    
    # Check if the processor is initialized with data
    if recipe_processor.recipes_df is None:
        # Try to load data
        if not recipe_processor.load_data_from_mongodb():
            if not recipe_processor.load_data_from_json():
                return jsonify({"error": "No recipe data available"}), 500
        
        # Process data
        recipe_processor.preprocess_ingredients()
        recipe_processor.vectorize_ingredients()
        recipe_processor.apply_kmeans_clustering()
        recipe_processor.apply_hierarchical_clustering()
    
    # Find recipes with the given ingredients
    matching_recipes = recipe_processor.find_recipes_by_ingredients(ingredients)
    
    # Return results
    return jsonify({
        "ingredients": ingredients,
        "recipes": matching_recipes,
        "count": len(matching_recipes)
    })

@app.route('/ingredients')
def get_all_ingredients():
    """Get a list of all unique ingredients"""
    # Get all recipes
    recipes = list(recipes_collection.find({}, {'ingredients': 1, '_id': 0}))
    
    # Flatten the list of ingredients
    all_ingredients = []
    for recipe in recipes:
        if 'ingredients' in recipe and isinstance(recipe['ingredients'], list):
            for ingredient in recipe['ingredients']:
                # Extract just the ingredient name (remove quantities, etc.)
                ingredient_name = ingredient.split(',')[0].strip().lower()
                all_ingredients.append(ingredient_name)
    
    # Get unique ingredients
    unique_ingredients = sorted(list(set(all_ingredients)))
    
    return jsonify({
        "ingredients": unique_ingredients,
        "count": len(unique_ingredients)
    })

def init_app():
    """Initialize the application"""
    # Check if MongoDB has recipes
    recipe_count = recipes_collection.count_documents({})
    if recipe_count == 0:
        print("No recipes found in MongoDB. Please run the scraper first.")
    else:
        print(f"Found {recipe_count} recipes in MongoDB")
    
    # Try to initialize the recipe processor
    global recipe_processor
    recipe_processor.load_data_from_mongodb()
    if recipe_processor.recipes_df is not None:
        print("Initializing ML models...")
        recipe_processor.preprocess_ingredients()
        recipe_processor.vectorize_ingredients()
        recipe_processor.apply_kmeans_clustering()
        recipe_processor.apply_hierarchical_clustering()
        print("ML models initialized")
    
    return app

if __name__ == '__main__':
    # Initialize the app
    app = init_app()
    
    # Run the app
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True) 