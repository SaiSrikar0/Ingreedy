import os
import sys
import json
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from pymongo import MongoClient
from dotenv import load_dotenv

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

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

# Create FastAPI app
app = FastAPI(
    title="Ingreedy API",
    description="API for Ingreedy recipe recommendation system",
    version="1.0.0"
)

# Create a global RecipeProcessor instance
recipe_processor = RecipeProcessor()

# Initialize the RecipeProcessor
if not recipe_processor.load_data_from_mongodb():
    if not recipe_processor.load_data_from_json():
        print("Warning: No recipe data available")
    else:
        recipe_processor.preprocess_ingredients()
        recipe_processor.vectorize_ingredients()
        recipe_processor.apply_kmeans_clustering()
        recipe_processor.apply_hierarchical_clustering()
else:
    recipe_processor.preprocess_ingredients()
    recipe_processor.vectorize_ingredients()
    recipe_processor.apply_kmeans_clustering()
    recipe_processor.apply_hierarchical_clustering()

# Define models
class Ingredient(BaseModel):
    name: str

class RecipeRequest(BaseModel):
    ingredients: List[str]
    max_results: Optional[int] = 5

class RecipeResponse(BaseModel):
    title: str
    url: str
    ingredients: List[str]
    instructions: List[str]
    image_url: Optional[str] = None
    prep_time: Optional[str] = None
    cook_time: Optional[str] = None
    servings: Optional[str] = None
    similarity: Optional[float] = None

class RecipeSearchResponse(BaseModel):
    ingredients: List[str]
    recipes: List[dict]
    count: int
    search_method: str

# Routes
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to the Ingreedy API",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/ingredients", response_model=List[str])
async def get_ingredients():
    """Get all unique ingredients"""
    try:
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
        
        return unique_ingredients
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/recipes/search", response_model=RecipeSearchResponse)
async def search_recipes(request: RecipeRequest):
    """Search for recipes based on ingredients"""
    try:
        # Check if the recipe processor is initialized
        if recipe_processor.recipes_df is None:
            # Try to load and initialize
            if not recipe_processor.load_data_from_mongodb():
                if not recipe_processor.load_data_from_json():
                    raise HTTPException(
                        status_code=500, 
                        detail="No recipe data available"
                    )
            recipe_processor.preprocess_ingredients()
            recipe_processor.vectorize_ingredients()
            recipe_processor.apply_kmeans_clustering()
            recipe_processor.apply_hierarchical_clustering()
        
        # Find recipes
        matching_recipes = recipe_processor.find_recipes_by_ingredients(request.ingredients)
        
        # Determine which search method was used
        search_method = "Exact Match"
        if not matching_recipes:
            search_method = "No matches found"
        elif hasattr(matching_recipes[0], 'get') and matching_recipes[0].get('similarity') is not None:
            search_method = "KMeans Clustering"
        else:
            search_method = "Hierarchical Clustering"
        
        # Limit results if needed
        if request.max_results and request.max_results < len(matching_recipes):
            matching_recipes = matching_recipes[:request.max_results]
        
        return {
            "ingredients": request.ingredients,
            "recipes": matching_recipes,
            "count": len(matching_recipes),
            "search_method": search_method
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/recipes/{recipe_id}")
async def get_recipe(recipe_id: str):
    """Get a recipe by ID"""
    try:
        recipe = recipes_collection.find_one({"_id": recipe_id}, {'_id': 0})
        
        if recipe:
            return recipe
        else:
            raise HTTPException(status_code=404, detail="Recipe not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/recipes/random", response_model=dict)
async def get_random_recipe():
    """Get a random recipe"""
    try:
        # Get a random recipe
        pipeline = [{"$sample": {"size": 1}}]
        random_recipe = list(recipes_collection.aggregate(pipeline))
        
        if random_recipe:
            recipe = random_recipe[0]
            # Convert ObjectId to string
            recipe['_id'] = str(recipe['_id'])
            return recipe
        else:
            raise HTTPException(status_code=404, detail="No recipes available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Add route for ingredient-based search with query parameters
@app.get("/recipes", response_model=RecipeSearchResponse)
async def search_recipes_by_query(
    ingredients: str = Query(..., description="Comma-separated list of ingredients"),
    max_results: int = Query(5, description="Maximum number of results to return")
):
    """Search recipes by ingredients using query parameters"""
    # Split ingredients string into a list
    ingredients_list = [ing.strip() for ing in ingredients.split(',')]
    
    # Create a request object
    request = RecipeRequest(ingredients=ingredients_list, max_results=max_results)
    
    # Use the post endpoint logic
    return await search_recipes(request) 