import requests
import time
import random
import json
import os
from bs4 import BeautifulSoup
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

# Headers to mimic a browser visit
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
}

# Categories to scrape
categories = [
    "https://www.allrecipes.com/recipes/76/appetizers-and-snacks/",
    "https://www.allrecipes.com/recipes/156/bread/",
    "https://www.allrecipes.com/recipes/78/breakfast-and-brunch/",
    "https://www.allrecipes.com/recipes/79/desserts/",
    "https://www.allrecipes.com/recipes/17562/dinner/",
    "https://www.allrecipes.com/recipes/1642/everyday-cooking/",
    "https://www.allrecipes.com/recipes/84/healthy-recipes/",
    "https://www.allrecipes.com/recipes/85/holidays-and-events/",
    "https://www.allrecipes.com/recipes/92/meat-and-poultry/",
    "https://www.allrecipes.com/recipes/95/pasta-and-noodles/",
    "https://www.allrecipes.com/recipes/96/salad/",
    "https://www.allrecipes.com/recipes/93/seafood/",
    "https://www.allrecipes.com/recipes/94/soups-stews-and-chili/",
    "https://www.allrecipes.com/recipes/87/side-dish/",
    "https://www.allrecipes.com/recipes/1227/world-cuisine/"
]

def get_recipe_links(category_url, max_pages=3):
    """Extract recipe links from category pages"""
    recipe_links = []
    
    for page_num in range(1, max_pages + 1):
        url = f"{category_url}?page={page_num}"
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find recipe cards
                recipe_cards = soup.find_all("a", class_="mntl-card-list-items")
                
                for card in recipe_cards:
                    link = card.get('href')
                    if link and '/recipe/' in link:
                        recipe_links.append(link)
                
                # Random delay between requests to avoid being blocked
                time.sleep(random.uniform(2, 5))
            else:
                print(f"Failed to fetch {url}, status code: {response.status_code}")
        except Exception as e:
            print(f"Error fetching {url}: {e}")
    
    return recipe_links

def parse_recipe(url):
    """Parse a single recipe page"""
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch {url}, status code: {response.status_code}")
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Get recipe title
        title_element = soup.find("h1", class_="article-heading")
        title = title_element.text.strip() if title_element else "Unknown Recipe"
        
        # Get ingredients
        ingredients_list = []
        ingredients_elements = soup.find_all("li", class_="mntl-structured-ingredients__list-item")
        for ingredient in ingredients_elements:
            ingredients_list.append(ingredient.text.strip())
        
        # Get instructions
        instructions_list = []
        instructions_elements = soup.find_all("li", class_="comp mntl-sc-block-group--LI")
        for instruction in instructions_elements:
            instructions_list.append(instruction.text.strip())
        
        # Get image URL
        image_element = soup.find("img", class_="primary-image")
        image_url = image_element.get('src') if image_element else None
        
        # Get preparation and cooking time
        prep_time_element = soup.find("div", class_="mntl-recipe-details__item--prep-time")
        prep_time = prep_time_element.text.strip() if prep_time_element else "Not specified"
        
        cook_time_element = soup.find("div", class_="mntl-recipe-details__item--cook-time")
        cook_time = cook_time_element.text.strip() if cook_time_element else "Not specified"
        
        # Get serving size
        serving_element = soup.find("div", class_="mntl-recipe-details__item--servings")
        servings = serving_element.text.strip() if serving_element else "Not specified"
        
        # Get categories/tags
        tags = []
        tags_elements = soup.find_all("a", class_="mntl-breadcrumbs__link")
        for tag in tags_elements:
            tags.append(tag.text.strip())
        
        # Create recipe object
        recipe = {
            "title": title,
            "url": url,
            "ingredients": ingredients_list,
            "instructions": instructions_list,
            "image_url": image_url,
            "prep_time": prep_time,
            "cook_time": cook_time,
            "servings": servings,
            "tags": tags,
            "ingredients_simple": [i.split(',')[0].strip().lower() for i in ingredients_list],
            "scraped_at": time.time()
        }
        
        return recipe
    
    except Exception as e:
        print(f"Error parsing {url}: {e}")
        return None

def save_to_mongodb(recipe):
    """Save recipe to MongoDB"""
    try:
        # Check if recipe already exists
        existing = recipes_collection.find_one({"url": recipe["url"]})
        if existing:
            recipes_collection.update_one({"url": recipe["url"]}, {"$set": recipe})
            print(f"Updated recipe: {recipe['title']}")
        else:
            recipes_collection.insert_one(recipe)
            print(f"Inserted recipe: {recipe['title']}")
    except Exception as e:
        print(f"Error saving to MongoDB: {e}")

def save_to_json(recipe, filename="recipes.json"):
    """Save recipe to JSON file as backup"""
    try:
        # Load existing data
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                recipes = json.load(f)
        else:
            recipes = []
        
        # Check if recipe already exists
        for i, existing in enumerate(recipes):
            if existing["url"] == recipe["url"]:
                recipes[i] = recipe
                break
        else:
            recipes.append(recipe)
        
        # Save updated data
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(recipes, f, indent=2, ensure_ascii=False)
    
    except Exception as e:
        print(f"Error saving to JSON: {e}")

def main():
    """Main function to run the scraper"""
    all_recipe_links = []
    
    # Create data directory if it doesn't exist
    os.makedirs("raw_data", exist_ok=True)
    
    for category_url in categories:
        category_name = category_url.split('/')[-2]
        print(f"Scraping category: {category_name}")
        
        recipe_links = get_recipe_links(category_url, max_pages=2)
        all_recipe_links.extend(recipe_links)
        
        print(f"Found {len(recipe_links)} recipes in {category_name}")
        
        # Save links to file
        with open(f"raw_data/links_{category_name}.txt", "w") as f:
            for link in recipe_links:
                f.write(f"{link}\n")
    
    # Remove duplicates
    all_recipe_links = list(set(all_recipe_links))
    print(f"Total unique recipes to scrape: {len(all_recipe_links)}")
    
    # Scrape recipes
    for i, link in enumerate(all_recipe_links):
        print(f"Scraping recipe {i+1}/{len(all_recipe_links)}: {link}")
        
        recipe = parse_recipe(link)
        if recipe:
            save_to_mongodb(recipe)
            save_to_json(recipe, "raw_data/recipes.json")
        
        # Random delay between requests
        time.sleep(random.uniform(3, 7))

if __name__ == "__main__":
    main() 