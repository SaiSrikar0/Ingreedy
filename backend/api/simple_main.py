import os
from typing import List, Optional
from fastapi import FastAPI, Query
from pydantic import BaseModel

# Create FastAPI app
app = FastAPI(
    title="Ingreedy API",
    description="Simple API for Ingreedy recipe recommendation system",
    version="1.0.0"
)

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

# Define models
class RecipeRequest(BaseModel):
    ingredients: List[str]
    max_results: Optional[int] = 5

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

@app.get("/ingredients")
async def get_ingredients():
    """Get all unique ingredients"""
    # Extract all ingredients from sample recipes
    all_ingredients = []
    for recipe in sample_recipes:
        all_ingredients.extend(recipe["ingredients_simple"])
    
    # Return unique ingredients
    unique_ingredients = sorted(list(set(all_ingredients)))
    return unique_ingredients

@app.post("/recipes/search")
async def search_recipes(request: RecipeRequest):
    """Search for recipes based on ingredients"""
    # Simple search logic to find recipes containing any of the requested ingredients
    matching_recipes = []
    for recipe in sample_recipes:
        recipe_ingredients = recipe["ingredients_simple"]
        # Check if any requested ingredient is in the recipe
        if any(ing in recipe_ingredients for ing in request.ingredients):
            matching_recipes.append(recipe)
    
    return {
        "ingredients": request.ingredients,
        "recipes": matching_recipes[:request.max_results],
        "count": len(matching_recipes[:request.max_results]),
        "search_method": "Simple Matching"
    }

@app.get("/recipes/random")
async def get_random_recipe():
    """Get a random recipe"""
    # Always return the first recipe as "random" for simplicity
    return sample_recipes[0]

@app.get("/recipes")
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