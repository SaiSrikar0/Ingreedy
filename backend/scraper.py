import requests
from bs4 import BeautifulSoup
import time
import random
from database import save_recipe, save_ingredients, init_db
import re
from urllib.parse import urljoin

class AllRecipesScraper:
    def __init__(self):
        self.base_url = "https://www.allrecipes.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def get_recipe_links(self, category_url, max_pages=5):
        """Get recipe links from category pages"""
        recipe_links = set()
        
        for page in range(1, max_pages + 1):
            url = f"{category_url}?page={page}"
            try:
                response = requests.get(url, headers=self.headers)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find recipe links
                links = soup.find_all('a', href=re.compile(r'/recipe/\d+'))
                for link in links:
                    recipe_links.add(urljoin(self.base_url, link['href']))
                
                time.sleep(random.uniform(1, 2))  # Be nice to the server
                
            except Exception as e:
                print(f"Error fetching page {page}: {e}")
                continue
        
        return list(recipe_links)

    def parse_recipe(self, url):
        """Parse a single recipe page"""
        try:
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract recipe data
            title_elem = soup.find('h1', class_='headline')
            if not title_elem:
                print(f"⚠️ Could not find title for {url}")
                return None
            title = title_elem.text.strip()
            
            # Get ingredients
            ingredients = []
            ingredients_simple = []
            ingredient_section = soup.find('div', class_='ingredients-section')
            if ingredient_section:
                for item in ingredient_section.find_all('li', class_='ingredients-item'):
                    ingredient = item.text.strip()
                    ingredients.append(ingredient)
                    # Create simplified version for searching
                    simple_ingredient = re.sub(r'\d+\s*(?:cup|tablespoon|teaspoon|ounce|pound|g|ml|tsp|tbsp|oz|lb)s?\s*', '', ingredient.lower())
                    simple_ingredient = re.sub(r'\([^)]*\)', '', simple_ingredient)
                    simple_ingredient = simple_ingredient.strip()
                    if simple_ingredient:
                        ingredients_simple.append(simple_ingredient)
            else:
                print(f"⚠️ Could not find ingredients for {url}")
                return None
            
            # Get instructions
            instructions = []
            instructions_section = soup.find('div', class_='instructions-section')
            if instructions_section:
                for item in instructions_section.find_all('li', class_='instructions-section-item'):
                    instructions.append(item.text.strip())
            else:
                print(f"⚠️ Could not find instructions for {url}")
                return None
            
            # Get recipe details with fallbacks
            try:
                prep_time = soup.find('div', class_='recipe-meta-item', text=re.compile('Prep')).find_next('div').text.strip()
            except:
                prep_time = "N/A"
            
            try:
                cook_time = soup.find('div', class_='recipe-meta-item', text=re.compile('Cook')).find_next('div').text.strip()
            except:
                cook_time = "N/A"
            
            try:
                servings = soup.find('div', class_='recipe-meta-item', text=re.compile('Servings')).find_next('div').text.strip()
            except:
                servings = "N/A"
            
            # Get tags
            tags = []
            tags_section = soup.find('div', class_='recipe-tags')
            if tags_section:
                for tag in tags_section.find_all('a'):
                    tags.append(tag.text.strip().lower())
            
            # Get image URL
            image_url = None
            image_section = soup.find('div', class_='primary-image')
            if image_section and image_section.find('img'):
                image_url = image_section.find('img').get('src', None)
            
            recipe_data = {
                "title": title,
                "url": url,
                "ingredients": ingredients,
                "ingredients_simple": ingredients_simple,
                "instructions": instructions,
                "prep_time": prep_time,
                "cook_time": cook_time,
                "servings": servings,
                "tags": tags,
                "image_url": image_url,
                "source": "allrecipes.com"
            }
            
            return recipe_data
            
        except Exception as e:
            print(f"⚠️ Error parsing recipe {url}: {e}")
            return None

    def scrape_category(self, category_url, max_pages=5):
        """Scrape all recipes from a category"""
        print(f"Scraping category: {category_url}")
        recipe_links = self.get_recipe_links(category_url, max_pages)
        
        for link in recipe_links:
            try:
                recipe_data = self.parse_recipe(link)
                if recipe_data:
                    # Save recipe
                    save_recipe(recipe_data)
                    # Save ingredients
                    save_ingredients(recipe_data['ingredients_simple'])
                    print(f"Saved recipe: {recipe_data['title']}")
                
                time.sleep(random.uniform(2, 3))  # Be nice to the server
                
            except Exception as e:
                print(f"Error processing recipe {link}: {e}")
                continue

def main():
    # Initialize database
    init_db()
    
    # Create scraper
    scraper = AllRecipesScraper()
    
    # Define categories to scrape
    categories = [
        "/recipes/276/desserts/cakes/",
        "/recipes/78/drinks/",
        "/recipes/17562/lunch-and-dinner/",
        "/recipes/76/appetizers-and-snacks/",
        "/recipes/156/international/",
        "/recipes/84/healthy-recipes/",
        "/recipes/17561/breakfast-and-brunch/"
    ]
    
    # Scrape each category
    for category in categories:
        category_url = urljoin(scraper.base_url, category)
        scraper.scrape_category(category_url, max_pages=3)

if __name__ == "__main__":
    main() 