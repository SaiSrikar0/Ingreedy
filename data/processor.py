import os
import pandas as pd
import numpy as np
import json
import re
from pymongo import MongoClient
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
from sklearn.model_selection import train_test_split
from typing import List, Dict, Tuple, Optional
import joblib

# Load environment variables
load_dotenv()

# MongoDB setup
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "ingreedy")
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
recipes_collection = db["recipes"]
processed_collection = db["processed_recipes"]

class RecipeProcessor:
    def __init__(self):
        self.recipes_df = None
        self.ingredient_vectorizer = None
        self.ingredient_vectors = None
        self.kmeans_model = None
        self.hierarchical_model = None
        self.vectorizer = TfidfVectorizer()
        self.kmeans = None
        self.hierarchical = None
        self.ingredients_vectors = None
        
    def load_data_from_mongodb(self):
        """Load recipe data from MongoDB"""
        recipes = list(recipes_collection.find())
        if not recipes:
            print("No recipes found in MongoDB. Please run the scraper first.")
            return False
        
        self.recipes_df = pd.DataFrame(recipes)
        print(f"Loaded {len(self.recipes_df)} recipes from MongoDB")
        return True
    
    def load_data_from_json(self, file_path: str = os.path.join("data", "raw_data", "recipes.json")) -> bool:
        """Load recipe data from JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.recipes_df = pd.DataFrame(data['recipes'])
                print(f"Loaded {len(self.recipes_df)} recipes from JSON")
                return True
        except Exception as e:
            print(f"Error loading data from JSON: {str(e)}")
            return False
    
    def preprocess_ingredients(self):
        """Preprocess ingredients for vectorization"""
        if self.recipes_df is None:
            raise ValueError("No data loaded. Call load_data_from_json first.")
            
        # Convert ingredients lists to strings
        self.recipes_df['ingredients_text'] = self.recipes_df['ingredients'].apply(
            lambda x: ' '.join(x) if isinstance(x, list) else x
        )
        
        print("Preprocessed ingredients")
        # Print sample ingredients
        print("Sample preprocessed ingredients:")
        for i, (_, recipe) in enumerate(self.recipes_df.head(3).iterrows()):
            print(f"Recipe {i+1}:")
            print(f"  Original: {recipe['ingredients'][:3]}...")
            print(f"  Text: {recipe['ingredients_text'][:100]}...")
            print()
        
    def vectorize_ingredients(self):
        """Convert ingredients to TF-IDF vectors"""
        if 'ingredients_text' not in self.recipes_df.columns:
            raise ValueError("Ingredients not preprocessed. Call preprocess_ingredients first.")
            
        self.ingredients_vectors = self.vectorizer.fit_transform(
            self.recipes_df['ingredients_text']
        )
        
        print("Vectorizing ingredients...")
        print("Sample ingredients text for vectorization:")
        for text in self.recipes_df['ingredients_text'].head(3):
            print(f"- {text}")
        
    def apply_kmeans_clustering(self, n_clusters: int = 5):
        """Apply K-means clustering to recipes"""
        if self.ingredients_vectors is None:
            raise ValueError("Ingredients not vectorized. Call vectorize_ingredients first.")
            
        # Adjust number of clusters based on dataset size
        n_samples = len(self.recipes_df)
        if n_samples < n_clusters:
            n_clusters = max(2, n_samples)
            print(f"Adjusted number of clusters to {n_clusters} based on dataset size")
            
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        self.recipes_df['kmeans_cluster'] = self.kmeans.fit_predict(self.ingredients_vectors)
        
    def apply_hierarchical_clustering(self, n_clusters: int = 5):
        """Apply hierarchical clustering to recipes"""
        if self.ingredients_vectors is None:
            raise ValueError("Ingredients not vectorized. Call vectorize_ingredients first.")
            
        # Adjust number of clusters based on dataset size
        n_samples = len(self.recipes_df)
        if n_samples < n_clusters:
            n_clusters = max(2, n_samples)
            print(f"Adjusted number of clusters to {n_clusters} based on dataset size")
            
        self.hierarchical = AgglomerativeClustering(n_clusters=n_clusters)
        self.recipes_df['hierarchical_cluster'] = self.hierarchical.fit_predict(
            self.ingredients_vectors.toarray()
        )
        
    def find_recipes_by_ingredients(self, 
                                  ingredients: List[str], 
                                  cuisine_type: Optional[str] = None,
                                  diet_type: Optional[str] = None,
                                  max_cook_time: Optional[int] = None,
                                  difficulty: Optional[str] = None,
                                  max_calories: Optional[int] = None,
                                  max_results: int = 5) -> List[Dict]:
        """
        Find recipes based on ingredients and additional filters
        
        Args:
            ingredients: List of ingredients to search for
            cuisine_type: Type of cuisine (e.g., 'Italian', 'Asian')
            diet_type: Type of diet (e.g., 'Vegetarian', 'Vegan')
            max_cook_time: Maximum cooking time in minutes
            difficulty: Recipe difficulty level (e.g., 'Easy', 'Medium')
            max_calories: Maximum calories per serving
            max_results: Maximum number of results to return
        """
        if self.recipes_df is None or self.ingredients_vectors is None:
            raise ValueError("Data not processed. Call load_data_from_json and process data first.")
            
        # Convert input ingredients to vector
        ingredients_text = ' '.join(ingredients)
        ingredients_vector = self.vectorizer.transform([ingredients_text])
        
        # Calculate similarity with all recipes
        similarities = cosine_similarity(ingredients_vector, self.ingredients_vectors)[0]
        
        # Create a copy of the DataFrame with similarities
        results_df = self.recipes_df.copy()
        results_df['similarity'] = similarities
        
        # Apply filters
        if cuisine_type:
            results_df = results_df[results_df['cuisine'].str.lower() == cuisine_type.lower()]
            
        if diet_type:
            results_df = results_df[results_df['diet_type'].str.lower() == diet_type.lower()]
            
        if max_cook_time:
            # Convert cook_time to minutes
            results_df['cook_minutes'] = results_df['cook_time'].str.extract('(\d+)').astype(float)
            results_df = results_df[results_df['cook_minutes'] <= max_cook_time]
            
        if difficulty:
            results_df = results_df[results_df['difficulty'].str.lower() == difficulty.lower()]
            
        if max_calories:
            results_df = results_df[results_df['calories_per_serving'] <= max_calories]
            
        # Sort by similarity and return top results
        top_recipes = results_df.nlargest(max_results, 'similarity')
        
        return top_recipes.to_dict('records')
    
    def get_recipe_stats(self) -> Dict:
        """Get statistics about the recipe database"""
        if self.recipes_df is None:
            raise ValueError("No data loaded")
            
        stats = {
            'total_recipes': len(self.recipes_df),
            'cuisines': self.recipes_df['cuisine'].value_counts().to_dict(),
            'diet_types': self.recipes_df['diet_type'].value_counts().to_dict(),
            'difficulty_levels': self.recipes_df['difficulty'].value_counts().to_dict(),
            'avg_calories': self.recipes_df['calories_per_serving'].mean(),
            'avg_cook_time': self.recipes_df['cook_time'].str.extract('(\d+)').astype(float).mean()
        }
        
        return stats
        
    def get_recipe_recommendations(self, recipe_id: str, max_results: int = 3) -> List[Dict]:
        """Get similar recipe recommendations based on a recipe ID"""
        if self.recipes_df is None or self.ingredients_vectors is None:
            raise ValueError("Data not processed")
            
        # Find the recipe
        recipe = self.recipes_df[self.recipes_df['id'] == recipe_id]
        if len(recipe) == 0:
            raise ValueError(f"Recipe with ID {recipe_id} not found")
            
        # Get the recipe's vector
        recipe_idx = recipe.index[0]
        recipe_vector = self.ingredients_vectors[recipe_idx]
        
        # Calculate similarities
        similarities = cosine_similarity(recipe_vector, self.ingredients_vectors)[0]
        
        # Add similarities to DataFrame
        results_df = self.recipes_df.copy()
        results_df['similarity'] = similarities
        
        # Remove the original recipe
        results_df = results_df[results_df['id'] != recipe_id]
        
        # Get top similar recipes
        recommendations = results_df.nlargest(max_results, 'similarity')
        
        return recommendations.to_dict('records')
    
    def save_processed_data(self):
        """Save processed data and models"""
        if self.recipes_df is None:
            raise ValueError("No data to save. Process data first.")
            
        os.makedirs(os.path.join("data", "processed_data"), exist_ok=True)
        
        # Save processed DataFrame
        self.recipes_df.to_json(os.path.join("data", "processed_data", "processed_recipes.json"), orient='records')
        
        # Save models
        joblib.dump(self.vectorizer, os.path.join("data", "processed_data", "vectorizer.joblib"))
        joblib.dump(self.kmeans, os.path.join("data", "processed_data", "kmeans.joblib"))
        joblib.dump(self.hierarchical, os.path.join("data", "processed_data", "hierarchical.joblib"))
        
    def split_data(self, test_size: float = 0.2, random_state: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Split data into training and testing sets"""
        if self.recipes_df is None:
            raise ValueError("No data loaded. Call load_data_from_json first.")
            
        train_df, test_df = train_test_split(
            self.recipes_df, 
            test_size=test_size, 
            random_state=random_state
        )
        
        # Save split datasets
        os.makedirs(os.path.join("data", "processed_data"), exist_ok=True)
        train_df.to_json(os.path.join("data", "processed_data", "train_recipes.json"), orient='records')
        test_df.to_json(os.path.join("data", "processed_data", "test_recipes.json"), orient='records')
        
        return train_df, test_df
    
    def load_processed_data(self):
        """Load processed data and models"""
        try:
            # Load processed DataFrame
            self.recipes_df = pd.read_json(os.path.join("data", "processed_data", "processed_recipes.json"))
            
            # Load models
            self.vectorizer = joblib.load(os.path.join("data", "processed_data", "vectorizer.joblib"))
            self.kmeans = joblib.load(os.path.join("data", "processed_data", "kmeans.joblib"))
            self.hierarchical = joblib.load(os.path.join("data", "processed_data", "hierarchical.joblib"))
            
            # Recreate ingredients vectors
            self.ingredients_vectors = self.vectorizer.transform(
                self.recipes_df['ingredients_text']
            )
            
            return True
        except Exception as e:
            print(f"Error loading processed data: {str(e)}")
            return False

def main():
    """Main function to process recipe data"""
    processor = RecipeProcessor()
    
    # Load data
    if not processor.load_data_from_mongodb():
        if not processor.load_data_from_json():
            print("Failed to load data")
            return
    
    # Process data
    processor.preprocess_ingredients()
    
    # Attempt vectorization
    if processor.vectorize_ingredients():
        processor.apply_kmeans_clustering()
        processor.apply_hierarchical_clustering()
        processor.save_processed_data()
        print("Data processing complete")
    else:
        print("Failed to vectorize ingredients. Data processing incomplete.")

if __name__ == "__main__":
    main() 