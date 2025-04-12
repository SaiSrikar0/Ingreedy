from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from database import (
    search_recipes_by_ingredients,
    get_all_ingredients,
    get_recipe_by_id,
    init_db
)

app = FastAPI(title="Ingreedy API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
init_db()

class RecipeResponse(BaseModel):
    title: str
    url: str
    ingredients: List[str]
    ingredients_simple: List[str]
    instructions: List[str]
    prep_time: str
    cook_time: str
    servings: str
    tags: List[str]
    image_url: Optional[str]
    source: str

@app.get("/")
async def root():
    return {"message": "Welcome to Ingreedy API"}

@app.get("/ingredients")
async def get_ingredients():
    """Get all available ingredients"""
    try:
        ingredients = get_all_ingredients()
        return {"ingredients": ingredients}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/recipes")
async def search_recipes(ingredients: str, max_results: int = 5):
    """Search recipes by ingredients"""
    try:
        # Split ingredients string into list
        ingredient_list = [ing.strip() for ing in ingredients.split(",")]
        
        # Search recipes
        recipes = search_recipes_by_ingredients(ingredient_list, max_results)
        
        # Format response
        return {
            "recipes": recipes,
            "count": len(recipes),
            "search_method": "MongoDB",
            "ingredients": ingredient_list
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/recipes/{recipe_id}")
async def get_recipe(recipe_id: str):
    """Get a specific recipe by ID"""
    try:
        recipe = get_recipe_by_id(recipe_id)
        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")
        return recipe
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 