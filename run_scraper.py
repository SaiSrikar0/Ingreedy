#!/usr/bin/env python
"""
Run the recipe scraper to populate MongoDB with recipes from AllRecipes.com
"""
import os
import sys
from data.scraper import main as scraper_main

def main():
    """Main function to run the scraper"""
    print("Starting AllRecipes.com scraper...")
    print("This will scrape recipe data and save it to MongoDB.")
    print("Make sure MongoDB is running first!")
    
    # Create data directory if it doesn't exist
    os.makedirs("data/raw_data", exist_ok=True)
    
    # Run the scraper
    scraper_main()
    
    print("Scraping complete!")

if __name__ == "__main__":
    main() 