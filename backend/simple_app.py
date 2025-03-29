import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create and configure app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Sample data
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

@app.route('/')
def index():
    """Home endpoint"""
    return jsonify({
        "message": "Welcome to the Ingreedy API (Simple Version)",
        "endpoints": {
            "GET /": "This help message",
            "GET /recipes": "Get sample recipes",
            "GET /recipes/search?ingredients=ing1,ing2,...": "Search recipes by ingredients",
            "GET /ingredients": "Get list of ingredients"
        }
    })

@app.route('/recipes')
def get_recipes():
    """Get all recipes"""
    return jsonify({
        "page": 1,
        "limit": 10,
        "total": len(sample_recipes),
        "recipes": sample_recipes
    })

@app.route('/recipes/search')
def search_recipes():
    """Simple search endpoint that always returns sample recipes"""
    return jsonify({
        "ingredients": ["sample", "ingredients"],
        "recipes": sample_recipes,
        "count": len(sample_recipes)
    })

@app.route('/ingredients')
def get_ingredients():
    """Get a list of all ingredients"""
    # Extract ingredients from sample recipes
    all_ingredients = []
    for recipe in sample_recipes:
        all_ingredients.extend(recipe["ingredients_simple"])
    
    # Get unique ingredients
    unique_ingredients = sorted(list(set(all_ingredients)))
    
    return jsonify({
        "ingredients": unique_ingredients,
        "count": len(unique_ingredients)
    })

if __name__ == '__main__':
    # Run the app
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True) 