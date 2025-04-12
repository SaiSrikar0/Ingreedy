from data.processor import RecipeProcessor

def print_recipe(recipe, show_instructions=False):
    """Helper function to print recipe details"""
    print(f"\n{recipe['title']}")
    print(f"Similarity score: {float(recipe['similarity']):.2f}")
    print(f"Cuisine: {recipe['cuisine']}")
    print(f"Diet Type: {recipe['diet_type']}")
    print(f"Difficulty: {recipe['difficulty']}")
    print(f"Calories: {recipe['calories_per_serving']} per serving")
    print(f"Cook Time: {recipe['cook_time']}")
    print("\nIngredients:")
    for ingredient in recipe['ingredients'][:5]:
        print(f"  - {ingredient}")
    if len(recipe['ingredients']) > 5:
        print("  ...")
        
    if show_instructions:
        print("\nInstructions:")
        for i, step in enumerate(recipe['instructions'], 1):
            print(f"  {i}. {step}")

def test_recipe_search():
    # Initialize processor
    processor = RecipeProcessor()
    
    # Load processed data
    if not processor.load_processed_data():
        print("Failed to load processed data")
        return
        
    # Print database statistics
    print("\n=== Recipe Database Statistics ===")
    stats = processor.get_recipe_stats()
    print(f"Total Recipes: {stats['total_recipes']}")
    print("\nCuisine Types:")
    for cuisine, count in stats['cuisines'].items():
        print(f"  - {cuisine}: {count}")
    print("\nDiet Types:")
    for diet, count in stats['diet_types'].items():
        print(f"  - {diet}: {count}")
    print(f"\nAverage Calories: {float(stats['avg_calories']):.0f}")
    print(f"Average Cook Time: {float(stats['avg_cook_time']):.0f} minutes")
    
    # Test 1: Basic ingredient search
    print("\n=== Test 1: Basic Ingredient Search ===")
    ingredients = ['chicken', 'vegetables']
    print(f"Searching for recipes with ingredients: {ingredients}")
    recipes = processor.find_recipes_by_ingredients(ingredients)
    for recipe in recipes:
        print_recipe(recipe)
        
    # Test 2: Filtered search
    print("\n=== Test 2: Filtered Search ===")
    print("Searching for vegetarian recipes with max 400 calories")
    recipes = processor.find_recipes_by_ingredients(
        ingredients=['vegetables', 'beans'],
        diet_type='Vegetarian',
        max_calories=400,
        max_cook_time=30
    )
    for recipe in recipes:
        print_recipe(recipe)
        
    # Test 3: Recipe recommendations
    print("\n=== Test 3: Recipe Recommendations ===")
    print("Getting recommendations similar to Spaghetti Bolognese")
    recommendations = processor.get_recipe_recommendations("1")
    for recipe in recommendations:
        print_recipe(recipe)

if __name__ == "__main__":
    test_recipe_search() 