import os
import requests
import json
import streamlit as st
from streamlit_chat import message
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API URLs
FLASK_API_URL = os.getenv("FLASK_API_URL", "http://localhost:5000")
FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:8000")

# App configuration
st.set_page_config(
    page_title="Ingreedy - Recipe Finder",
    page_icon="🍲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif !important;
        color: #1a1a1a !important;
    }
    
    body {
        background: #ffffff !important;
        color: #1a1a1a !important;
    }
    
    .main {
        background: #ffffff !important;
    }
    
    .stApp {
        max-width: 1400px;
        margin: 0 auto;
        padding: 2rem;
        background: #ffffff !important;
    }
    
    .big-title {
        font-size: 4.5rem !important;
        font-weight: 800 !important;
        color: #FF6B6B !important;
        text-align: center;
        margin-bottom: 1rem !important;
        letter-spacing: -2px;
        text-shadow: none !important;
    }
    
    .subtitle {
        font-size: 1.8rem !important;
        color: #4a4a4a !important;
        font-weight: 500 !important;
        text-align: center;
        margin-bottom: 3rem !important;
        text-shadow: none !important;
    }
    
    .recipe-card {
        background: #ffffff;
        border-radius: 24px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid #e0e0e0;
        position: relative;
        overflow: hidden;
    }
    
    .recipe-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.12);
    }
    
    .recipe-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 6px;
        background: #FF6B6B;
    }
    
    .recipe-title {
        color: #1a1a1a !important;
        font-size: 2.4rem !important;
        font-weight: 700 !important;
        margin-bottom: 1.5rem !important;
        letter-spacing: -1px;
    }
    
    .ingredient-tag {
        background: #FFE3E3;
        border-radius: 50px;
        padding: 0.8rem 1.5rem;
        margin: 0.5rem;
        display: inline-block;
        font-size: 1rem;
        font-weight: 500;
        color: #FF6B6B !important;
        border: none;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.15);
        transition: all 0.3s ease;
    }
    
    .ingredient-tag:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(255, 107, 107, 0.2);
    }
    
    .chat-interface {
        background: #ffffff;
        border-radius: 24px;
        padding: 2rem;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
        max-height: 600px;
        overflow-y: auto;
        border: 1px solid #e0e0e0;
        position: relative;
    }
    
    .chat-interface::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 6px;
        background: #FF6B6B;
    }
    
    .chat-message {
        padding: 1.2rem;
        margin-bottom: 1.2rem;
        border-radius: 18px;
        max-width: 85%;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
        color: #1a1a1a !important;
    }
    
    .user-message {
        background: #FFE3E3;
        margin-left: auto;
        border: none;
    }
    
    .bot-message {
        background: #f5f5f5;
        margin-right: auto;
        border: none;
    }
    
    .stButton button {
        background: #FF6B6B;
        color: white !important;
        border-radius: 50px;
        padding: 1rem 2rem;
        font-weight: 600;
        font-size: 1.1rem !important;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.2);
        transition: all 0.3s ease;
        border: none;
        width: 100%;
    }
    
    .stButton button:hover {
        background: #FF8E53;
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(255, 107, 107, 0.3);
    }
    
    .stTextInput>div>div>input {
        font-size: 1.1rem !important;
        color: #1a1a1a !important;
        border-radius: 50px !important;
        padding: 1rem 1.5rem !important;
        border: 2px solid #e0e0e0 !important;
        transition: all 0.3s ease !important;
        background: white !important;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #FF6B6B !important;
        box-shadow: 0 0 0 4px rgba(255, 107, 107, 0.1) !important;
    }
    
    .recipe-detail {
        background: #f5f5f5;
        padding: 1rem 1.5rem;
        border-radius: 16px;
        margin-bottom: 1rem;
        display: inline-block;
        font-weight: 500;
        color: #1a1a1a !important;
        border: none;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
    }
    
    .section-title {
        color: #1a1a1a !important;
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        margin-bottom: 2rem !important;
        padding-bottom: 1rem !important;
        border-bottom: 3px solid #FF6B6B;
        letter-spacing: -1px;
    }
    
    .footer {
        text-align: center;
        padding: 2rem;
        color: #4a4a4a !important;
        font-size: 1rem !important;
        font-weight: 500;
        margin-top: 3rem;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #FF6B6B;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #FF8E53;
    }
    
    /* Additional text visibility improvements */
    p, li, div, span {
        color: #1a1a1a !important;
    }
    
    .stMarkdown {
        color: #1a1a1a !important;
    }
    
    .stText {
        color: #1a1a1a !important;
    }
    
    .stAlert {
        color: #1a1a1a !important;
    }
    
    /* Sidebar styling */
    .sidebar-content {
        background: #ffffff !important;
        padding: 1.5rem !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05) !important;
        margin-bottom: 1.5rem !important;
        border: 1px solid #e0e0e0 !important;
    }
    
    .sidebar-title {
        color: #FF6B6B !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        margin-bottom: 1rem !important;
        text-align: center !important;
    }
    
    .sidebar-subtitle {
        color: #1a1a1a !important;
        font-size: 1.4rem !important;
        font-weight: 600 !important;
        margin: 1.5rem 0 1rem 0 !important;
    }
    
    .sidebar-text {
        color: #4a4a4a !important;
        font-size: 1rem !important;
        line-height: 1.6 !important;
        margin-bottom: 1rem !important;
    }
    
    .sidebar-list {
        color: #4a4a4a !important;
        font-size: 1rem !important;
        line-height: 1.6 !important;
        padding-left: 1.5rem !important;
    }
    
    .sidebar-list li {
        color: #4a4a4a !important;
        margin-bottom: 0.5rem !important;
    }
    
    .status-connected {
        color: #2ecc71 !important;
        font-weight: 600 !important;
        background: #e8f5e9 !important;
        padding: 0.5rem 1rem !important;
        border-radius: 50px !important;
        display: inline-block !important;
        margin: 0.25rem 0 !important;
    }
    
    .status-disconnected {
        color: #e74c3c !important;
        font-weight: 600 !important;
        background: #ffebee !important;
        padding: 0.5rem 1rem !important;
        border-radius: 50px !important;
        display: inline-block !important;
        margin: 0.25rem 0 !important;
    }
    
    .api-status-container {
        background: #ffffff !important;
        padding: 1.5rem !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05) !important;
        margin-top: 1.5rem !important;
        border: 1px solid #e0e0e0 !important;
    }
    
    .api-status-title {
        color: #FF6B6B !important;
        font-size: 1.4rem !important;
        font-weight: 600 !important;
        margin-bottom: 1rem !important;
    }
    
    .api-status-item {
        display: flex !important;
        align-items: center !important;
        margin-bottom: 0.75rem !important;
    }
    
    .api-status-label {
        color: #4a4a4a !important;
        font-weight: 500 !important;
        margin-right: 0.5rem !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'generated' not in st.session_state:
    st.session_state['generated'] = []
if 'past' not in st.session_state:
    st.session_state['past'] = []
if 'ingredients' not in st.session_state:
    st.session_state['ingredients'] = []
if 'search_executed' not in st.session_state:
    st.session_state['search_executed'] = False
if 'found_recipes' not in st.session_state:
    st.session_state['found_recipes'] = []

# Function to check API connection with timeout handling
def is_api_connected(url, timeout=5):
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

# Functions
def get_ingredients():
    """Get all available ingredients from API"""
    try:
        if is_api_connected(f"{FASTAPI_URL}/ingredients", timeout=5):
            response = requests.get(f"{FASTAPI_URL}/ingredients", timeout=5)
            if response.status_code == 200:
                return response.json()
        
        if is_api_connected(f"{FLASK_API_URL}/ingredients", timeout=5):
            response = requests.get(f"{FLASK_API_URL}/ingredients", timeout=5)
            if response.status_code == 200:
                return response.json()['ingredients']
                
        return []
    except Exception as e:
        st.error(f"Error retrieving ingredients: {e}")
        return []

def search_recipes(ingredients):
    """Search for recipes with the given ingredients"""
    ingredients_str = ",".join(ingredients)
    
    try:
        # Try FastAPI first
        if is_api_connected(FASTAPI_URL, timeout=5):
            response = requests.get(
                f"{FASTAPI_URL}/recipes",
                params={"ingredients": ingredients_str, "max_results": 5},
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
        
        # If FastAPI fails, try Flask
        if is_api_connected(FLASK_API_URL, timeout=5):
            response = requests.get(
                f"{FLASK_API_URL}/recipes/search",
                params={"ingredients": ingredients_str},
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
        
        # If both APIs fail, return a fallback response
        st.warning("⚠️ Unable to connect to recipe APIs. Using demo mode with sample recipes.")
        return {
            "recipes": get_sample_recipes(),
            "count": 2,
            "search_method": "Demo Mode",
            "ingredients": ingredients
        }
    
    except Exception as e:
        st.error(f"Error searching recipes: {e}")
        return {
            "recipes": get_sample_recipes(),
            "count": 2,
            "search_method": "Demo Mode (Error occurred)",
            "ingredients": ingredients
        }

def get_sample_recipes():
    """Get sample recipes when APIs are not available"""
    return [
        {
            "title": "Simple Pasta with Garlic and Oil",
            "url": "http://example.com/simple-pasta",
            "ingredients": ["1 pound pasta", "2 tablespoons olive oil", "3 cloves garlic, minced", 
                          "1/4 teaspoon red pepper flakes", "1/2 cup grated Parmesan cheese"],
            "instructions": ["Cook pasta according to package directions.", 
                           "Heat oil in a large skillet over medium heat.", 
                           "Add garlic and red pepper flakes, cook for 1 minute.",
                           "Drain pasta and add to skillet, toss to coat.",
                           "Sprinkle with cheese before serving."],
            "image_url": "https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=880&q=80",
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
            "image_url": "https://images.unsplash.com/photo-1525351484163-7529414344d8?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=880&q=80",
            "prep_time": "2 minutes",
            "cook_time": "5 minutes",
            "servings": "2 servings",
            "tags": ["breakfast", "quick", "eggs"],
            "ingredients_simple": ["eggs", "milk", "salt", "black pepper", "butter"]
        }
    ]

def format_chat_message(ingredients):
    """Format the chat message for user input"""
    return f"I have {', '.join(ingredients)}. What can I make?"

def search_button_click():
    """Handle the search button click"""
    # Get ingredients from text input
    ingredients_text = st.session_state.ingredients_input
    
    if not ingredients_text.strip():
        st.warning("Please enter some ingredients first!")
        return
    
    # Split by commas
    ingredients = [ing.strip().lower() for ing in ingredients_text.split(',')]
    
    # Add user message to chat history
    user_message = ingredients_text
    st.session_state.past.append(user_message)
    
    # Search for recipes
    results = search_recipes(ingredients)
    
    # Format response
    if results['count'] > 0:
        message = f"I found {results['count']} recipes you can make with those ingredients! Here they are:"
        st.session_state.found_recipes = results['recipes']
    else:
        message = "I couldn't find any recipes with exactly those ingredients. Try adding more ingredients or checking the spelling."
        st.session_state.found_recipes = []
    
    # Add response to chat history
    st.session_state.generated.append(message)
    st.session_state.search_executed = True
    st.session_state.ingredients = ingredients

# Title and Description
st.markdown("<h1 class='big-title'>🍲 Ingreedy</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Find delicious recipes with the ingredients you already have!</p>", unsafe_allow_html=True)

# Main layout
col1, col2 = st.columns([1, 2], gap="large")

with col1:
    st.markdown("<h2 class='section-title'>What's in your pantry?</h2>", unsafe_allow_html=True)
    
    # Chat interface
    st.markdown("<div class='chat-interface'>", unsafe_allow_html=True)
    
    # Display chat history
    if st.session_state['generated']:
        for i in range(len(st.session_state['generated'])):
            # User message
            st.markdown(f"""
                <div class='chat-message user-message'>
                    <strong>You:</strong><br>
                    {st.session_state['past'][i]}
                </div>
            """, unsafe_allow_html=True)
            
            # Bot message
            st.markdown(f"""
                <div class='chat-message bot-message'>
                    <strong>Ingreedy:</strong><br>
                    {st.session_state['generated'][i]}
                </div>
            """, unsafe_allow_html=True)
    
    # Input box
    st.markdown("<div class='chat-input'>", unsafe_allow_html=True)
    st.text_input(
        "Enter your ingredients separated by commas:",
        key="ingredients_input",
        placeholder="e.g., eggs, butter, milk, flour"
    )
    st.button("Find Recipes", on_click=search_button_click)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Ingredient suggestions
    st.markdown("<h3 class='section-title'>Popular Ingredients</h3>", unsafe_allow_html=True)
    all_ingredients = get_ingredients()
    if all_ingredients:
        sample_ingredients = sorted(all_ingredients)[:15]  # Take first 15 alphabetically
        st.markdown("<div style='background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);'>", unsafe_allow_html=True)
        st.write("Try some of these ingredients:")
        
        # Display ingredient tags
        for ingredient in sample_ingredients:
            st.markdown(f'<span class="ingredient-tag">{ingredient}</span>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown(
            "<div class='info-box'>No ingredient suggestions available. Using demo mode.</div>",
            unsafe_allow_html=True
        )

with col2:
    st.markdown("<h2 class='section-title'>Recipe Results</h2>", unsafe_allow_html=True)
    
    if st.session_state.search_executed and st.session_state.found_recipes:
        for recipe in st.session_state.found_recipes:
            # Create a recipe card
            with st.container():
                st.markdown('<div class="recipe-card">', unsafe_allow_html=True)
                
                # Recipe title
                st.markdown(f"<h3 class='recipe-title'>{recipe['title']}</h3>", unsafe_allow_html=True)
                
                # Layout for image and details
                img_col, details_col = st.columns([1, 1])
                
                with img_col:
                    # Image
                    if 'image_url' in recipe and recipe['image_url']:
                        st.image(recipe['image_url'], caption="", use_column_width=True, 
                                output_format="JPEG")
                
                with details_col:
                    # Recipe details
                    st.markdown("<div style='padding: 10px 0;'>", unsafe_allow_html=True)
                    if 'prep_time' in recipe:
                        st.markdown(f"<span class='recipe-detail'>⏱️ Prep: {recipe['prep_time']}</span>", unsafe_allow_html=True)
                    if 'cook_time' in recipe:
                        st.markdown(f"<span class='recipe-detail'>⏲️ Cook: {recipe['cook_time']}</span>", unsafe_allow_html=True)
                    if 'servings' in recipe:
                        st.markdown(f"<span class='recipe-detail'>🍽️ Serves: {recipe['servings']}</span>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Highlight matched ingredients
                    if st.session_state.ingredients:
                        matched = []
                        for user_ing in st.session_state.ingredients:
                            for recipe_ing in recipe.get('ingredients_simple', []):
                                if user_ing in recipe_ing:
                                    matched.append(user_ing)
                                    break
                        
                        if matched:
                            st.markdown("<p><strong>Your ingredients used:</strong></p>", unsafe_allow_html=True)
                            st.markdown(", ".join(f"<span class='matched-ingredient'>{ing}</span>" 
                                                for ing in matched), unsafe_allow_html=True)
                
                # Ingredients
                st.markdown("<h4>Ingredients:</h4>", unsafe_allow_html=True)
                ingredients_list = recipe.get('ingredients', [])
                cols = st.columns(2)
                half = len(ingredients_list) // 2 + len(ingredients_list) % 2
                
                for i, ingredient in enumerate(ingredients_list[:half]):
                    cols[0].write(f"• {ingredient}")
                
                for i, ingredient in enumerate(ingredients_list[half:]):
                    cols[1].write(f"• {ingredient}")
                
                # Instructions
                with st.expander("Show Instructions"):
                    instructions = recipe.get('instructions', [])
                    for i, instruction in enumerate(instructions, 1):
                        st.write(f"{i}. {instruction}")
                
                # Recipe URL
                if 'url' in recipe:
                    st.markdown(f"<a href='{recipe['url']}' target='_blank' style='display: inline-block; margin-top: 15px; padding: 8px 15px; background-color: #2E7D32; color: white; text-decoration: none; border-radius: 5px;'>View Full Recipe</a>", unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
    elif st.session_state.search_executed:
        st.markdown(
            "<div class='info-box'>No recipes found with those ingredients. Try adding more ingredients or using different ones.</div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            "<div class='info-box'>Enter your ingredients and click 'Find Recipes' to discover delicious meals you can make!</div>",
            unsafe_allow_html=True
        )
        
        # Display a sample recipe as a suggestion
        st.markdown("<h3 class='section-title'>Try This Recipe</h3>", unsafe_allow_html=True)
        sample = get_sample_recipes()[0]
        with st.container():
            st.markdown('<div class="recipe-card">', unsafe_allow_html=True)
            st.markdown(f"<h3 class='recipe-title'>{sample['title']}</h3>", unsafe_allow_html=True)
            
            img_col, details_col = st.columns([1, 1])
            
            with img_col:
                if 'image_url' in sample and sample['image_url']:
                    st.image(sample['image_url'], caption="", use_column_width=True)
            
            with details_col:
                st.markdown("<div style='padding: 10px 0;'>", unsafe_allow_html=True)
                if 'prep_time' in sample:
                    st.markdown(f"<span class='recipe-detail'>⏱️ Prep: {sample['prep_time']}</span>", unsafe_allow_html=True)
                if 'cook_time' in sample:
                    st.markdown(f"<span class='recipe-detail'>⏲️ Cook: {sample['cook_time']}</span>", unsafe_allow_html=True)
                if 'servings' in sample:
                    st.markdown(f"<span class='recipe-detail'>🍽️ Serves: {sample['servings']}</span>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("<h4>Ingredients:</h4>", unsafe_allow_html=True)
            for ingredient in sample['ingredients'][:5]:
                st.write(f"• {ingredient}")
            
            with st.expander("Show Instructions"):
                for i, instruction in enumerate(sample['instructions'], 1):
                    st.write(f"{i}. {instruction}")
            
            if 'url' in sample:
                st.markdown(f"<a href='{sample['url']}' target='_blank' style='display: inline-block; margin-top: 15px; padding: 8px 15px; background-color: #2E7D32; color: white; text-decoration: none; border-radius: 5px;'>View Full Recipe</a>", unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<div class='footer'>Ingreedy - Find delicious recipes with ingredients you already have!<br>Data sourced from AllRecipes.com</div>", unsafe_allow_html=True)

# Sidebar with API status and information
with st.sidebar:
    st.markdown("<h2 class='sidebar-title'>About Ingreedy</h2>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="sidebar-content">
    <p class="sidebar-text">Ingreedy helps you find recipes based on ingredients you have at home.</p>
    
    <p class="sidebar-text">Just enter the ingredients you have separated by commas, and Ingreedy will find recipes you can make!</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="sidebar-content">
    <h3 class="sidebar-subtitle">How It Works</h3>
    <p class="sidebar-text">The app uses machine learning to match your ingredients to recipes:</p>
    <ol class="sidebar-list">
        <li><strong>Direct Match</strong>: First looks for recipes containing your ingredients</li>
        <li><strong>KMeans Clustering</strong>: If no direct match, finds similar recipes using KMeans</li>
        <li><strong>Hierarchical Search</strong>: Fallback approach to find recipes with at least some of your ingredients</li>
    </ol>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<h3 class='sidebar-subtitle'></h3>", unsafe_allow_html=True)
    
    # Safely check API status with proper exception handling
    try:
        flask_status = "✅ Connected" if is_api_connected(FLASK_API_URL) else "❌ Not Connected"
        flask_class = "status-connected" if is_api_connected(FLASK_API_URL) else "status-disconnected"
    except:
        flask_status = "❌ Not Connected"
        flask_class = "status-disconnected"
        
    try:
        fastapi_status = "✅ Connected" if is_api_connected(FASTAPI_URL) else "❌ Not Connected"
        fastapi_class = "status-connected" if is_api_connected(FASTAPI_URL) else "status-disconnected"
    except:
        fastapi_status = "❌ Not Connected"
        fastapi_class = "status-disconnected"
    
    st.markdown(f"""
    <div class="api-status-container">
    <h3 class="api-status-title">API Status</h3>
    <div class="api-status-item">
        <span class="api-status-label">Flask API:</span>
        <span class="{flask_class}">{flask_status}</span>
    </div>
    <div class="api-status-item">
        <span class="api-status-label">FastAPI:</span>
        <span class="{fastapi_class}">{fastapi_status}</span>
    </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Show a message if APIs aren't connected
    if flask_status == "❌ Not Connected" and fastapi_status == "❌ Not Connected":
        st.markdown("""
        <div class="sidebar-content" style="background-color: #ffebee; border-left: 4px solid #e74c3c;">
        <p class="sidebar-text" style="margin-top: 0;">⚠️ API servers not detected. The app is running in demo mode with sample recipes.</p>
        
        <p class="sidebar-text">To use the full application:
        <ol class="sidebar-list">
            <li>Make sure MongoDB is running</li>
            <li>Run <code>python run_all.py</code> from the command line</li>
        </ol>
        </p>
        </div>
        """, unsafe_allow_html=True) 