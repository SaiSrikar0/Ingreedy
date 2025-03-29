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
        
    def load_data_from_mongodb(self):
        """Load recipe data from MongoDB"""
        recipes = list(recipes_collection.find())
        if not recipes:
            print("No recipes found in MongoDB. Please run the scraper first.")
            return False
        
        self.recipes_df = pd.DataFrame(recipes)
        print(f"Loaded {len(self.recipes_df)} recipes from MongoDB")
        return True
    
    def load_data_from_json(self, filename="raw_data/recipes.json"):
        """Load recipe data from JSON file as fallback"""
        if not os.path.exists(filename):
            print(f"File {filename} not found")
            return False
        
        with open(filename, 'r', encoding='utf-8') as f:
            recipes = json.load(f)
        
        self.recipes_df = pd.DataFrame(recipes)
        print(f"Loaded {len(self.recipes_df)} recipes from JSON file")
        return True
    
    def preprocess_ingredients(self):
        """Preprocess ingredients for vectorization"""
        if self.recipes_df is None:
            print("No data loaded. Please load data first.")
            return False
        
        # Check if ingredients column exists and is not empty
        if 'ingredients' not in self.recipes_df.columns:
            print("No 'ingredients' column found in data")
            return False
        
        # Check for valid ingredients data
        valid_recipes = []
        for _, recipe in self.recipes_df.iterrows():
            if ('ingredients' in recipe and 
                isinstance(recipe['ingredients'], list) and 
                len(recipe['ingredients']) > 0):
                valid_recipes.append(True)
            else:
                valid_recipes.append(False)
        
        # Filter out invalid recipes
        if not all(valid_recipes):
            print(f"Found {valid_recipes.count(False)} recipes with invalid ingredients data")
            self.recipes_df = self.recipes_df[valid_recipes]
            print(f"Filtered to {len(self.recipes_df)} valid recipes")
        
        # Function to clean ingredients text
        def clean_ingredient(ingredient):
            if not isinstance(ingredient, str):
                return ""
            # Remove quantities and measurements
            cleaned = re.sub(r'^\d+\s*[/\d]*\s*[a-zA-Z]*\s', '', ingredient.lower())
            # Remove parentheses and their content
            cleaned = re.sub(r'\([^)]*\)', '', cleaned)
            # Remove additional specifications
            cleaned = re.sub(r',.*$', '', cleaned)
            # Remove special characters
            cleaned = re.sub(r'[^\w\s]', ' ', cleaned)
            # Remove extra whitespace
            cleaned = re.sub(r'\s+', ' ', cleaned).strip()
            return cleaned
        
        # Create clean ingredients text for vectorization
        self.recipes_df['ingredients_clean'] = self.recipes_df['ingredients'].apply(
            lambda ingredients: [clean_ingredient(ing) for ing in ingredients]
        )
        
        # Create text representation for vectorization
        self.recipes_df['ingredients_text'] = self.recipes_df['ingredients_clean'].apply(
            lambda ingredients: ' '.join([ing for ing in ingredients if ing])
        )
        
        # Create simplified list of ingredients for matching
        self.recipes_df['ingredients_simple'] = self.recipes_df['ingredients_clean'].apply(
            lambda ingredients: [ing for ing in ingredients if ing]
        )
        
        # Verify we have non-empty ingredients text
        empty_text = self.recipes_df['ingredients_text'].str.strip() == ''
        if empty_text.any():
            print(f"Warning: {empty_text.sum()} recipes have empty ingredients text")
            self.recipes_df = self.recipes_df[~empty_text]
            print(f"Filtered to {len(self.recipes_df)} recipes with non-empty ingredients")
        
        print("Preprocessed ingredients")
        # Print sample ingredients
        print("Sample preprocessed ingredients:")
        for i, (_, recipe) in enumerate(self.recipes_df.head(3).iterrows()):
            print(f"Recipe {i+1}:")
            print(f"  Original: {recipe['ingredients'][:3]}...")
            print(f"  Cleaned: {recipe['ingredients_clean'][:3]}...")
            print(f"  Text: {recipe['ingredients_text'][:100]}...")
            print()
        
        return True
    
    def vectorize_ingredients(self):
        """Vectorize ingredients using TF-IDF"""
        if 'ingredients_text' not in self.recipes_df.columns:
            print("Ingredients not preprocessed. Please preprocess first.")
            return False
        
        # Check if we have valid data to vectorize
        if self.recipes_df['ingredients_text'].str.strip().str.len().sum() == 0:
            print("Warning: No ingredient text found to vectorize")
            return False
            
        # DEBUG: Print a sample of ingredients text
        print("Sample ingredients text for vectorization:")
        for text in self.recipes_df['ingredients_text'].head(3):
            print(f"- {text}")
        
        # Create TF-IDF vectors for ingredients
        self.ingredient_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words=None,  # No stop words to keep all food terms
            min_df=2,  # Minimum document frequency (remove very rare terms)
            ngram_range=(1, 2),
            token_pattern=r'(?u)\b\w+\b'  # Simple token pattern to capture more terms
        )
        
        try:
            # Fit and transform the data
            self.ingredient_vectors = self.ingredient_vectorizer.fit_transform(
                self.recipes_df['ingredients_text']
            )
            
            # Debug: Print vocabulary info
            vocabulary = self.ingredient_vectorizer.get_feature_names_out()
            print(f"Vectorized ingredients with {len(vocabulary)} features")
            if len(vocabulary) > 0:
                print(f"Sample features: {', '.join(list(vocabulary)[:10])}")
            else:
                print("WARNING: Empty vocabulary created")
            
            return True
        except ValueError as e:
            print(f"Error in vectorization: {e}")
            print("Attempting backup vectorization method...")
            
            # Backup vectorization with even simpler parameters
            self.ingredient_vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words=None,
                min_df=1,  # Include all terms
                token_pattern=r'(?u)\b\w\w+\b'  # At least 2 characters
            )
            
            self.ingredient_vectors = self.ingredient_vectorizer.fit_transform(
                self.recipes_df['ingredients_text']
            )
            
            vocabulary = self.ingredient_vectorizer.get_feature_names_out()
            print(f"Backup vectorization with {len(vocabulary)} features")
            print(f"Sample features: {', '.join(list(vocabulary)[:10])}")
            
            return True
    
    def apply_kmeans_clustering(self, n_clusters=20):
        """Apply KMeans clustering to ingredient vectors"""
        if self.ingredient_vectors is None:
            print("Ingredients not vectorized. Please vectorize first.")
            return False
        
        # If we have few recipes, adjust the number of clusters
        if len(self.recipes_df) < n_clusters:
            n_clusters = max(2, len(self.recipes_df) // 2)
            print(f"Adjusted number of clusters to {n_clusters} based on data size")
        
        # Apply KMeans clustering
        self.kmeans_model = KMeans(
            n_clusters=n_clusters,
            random_state=42,
            n_init=10
        )
        
        clusters = self.kmeans_model.fit_predict(self.ingredient_vectors)
        self.recipes_df['cluster_kmeans'] = clusters
        
        # Get cluster centers for later similarity calculations
        self.cluster_centers = self.kmeans_model.cluster_centers_
        
        print(f"Applied KMeans clustering with {n_clusters} clusters")
        return True
    
    def apply_hierarchical_clustering(self, n_clusters=50):
        """Apply hierarchical clustering to ingredient vectors"""
        if self.ingredient_vectors is None:
            print("Ingredients not vectorized. Please vectorize first.")
            return False
        
        # If we have few recipes, adjust the number of clusters
        if len(self.recipes_df) < n_clusters:
            n_clusters = max(2, len(self.recipes_df) // 2)
            print(f"Adjusted number of clusters to {n_clusters} based on data size")
        
        # Apply hierarchical clustering
        self.hierarchical_model = AgglomerativeClustering(
            n_clusters=n_clusters,
            metric='euclidean',
            linkage='ward'
        )
        
        clusters = self.hierarchical_model.fit_predict(self.ingredient_vectors.toarray())
        self.recipes_df['cluster_hierarchical'] = clusters
        
        print(f"Applied hierarchical clustering with {n_clusters} clusters")
        return True
    
    def save_processed_data(self):
        """Save processed data to MongoDB"""
        if self.recipes_df is None:
            print("No data processed. Please process data first.")
            return False
        
        # Convert DataFrame to list of dictionaries
        recipes_list = self.recipes_df.to_dict('records')
        
        # Clear existing processed recipes
        processed_collection.delete_many({})
        
        # Insert processed recipes
        processed_collection.insert_many(recipes_list)
        
        print(f"Saved {len(recipes_list)} processed recipes to MongoDB")
        return True
    
    def find_recipes_by_ingredients(self, ingredients_list):
        """Find recipes that match the given ingredients"""
        if self.recipes_df is None:
            print("No data processed. Please process data first.")
            return []
        
        # Normalize input ingredients
        ingredients_list = [ingredient.lower().strip() for ingredient in ingredients_list]
        
        # First, try to find exact matches (recipes containing all ingredients)
        exact_matches = []
        for _, recipe in self.recipes_df.iterrows():
            recipe_ingredients = recipe['ingredients_simple']
            if all(any(query_ing in recipe_ing for recipe_ing in recipe_ingredients) 
                  for query_ing in ingredients_list):
                exact_matches.append(recipe.to_dict())
        
        if exact_matches:
            print(f"Found {len(exact_matches)} exact matches")
            return exact_matches
        
        # If no exact matches, use clustering
        print("No exact matches found, using clustering")
        return self.find_similar_recipes_by_clustering(ingredients_list)
    
    def find_similar_recipes_by_clustering(self, ingredients_list):
        """Find similar recipes using clustering"""
        if self.ingredient_vectorizer is None or self.kmeans_model is None:
            print("Models not trained. Please train models first.")
            return []
        
        # Create a document from the ingredients list
        ingredients_text = ' '.join(ingredients_list)
        
        # Vectorize the query ingredients
        query_vector = self.ingredient_vectorizer.transform([ingredients_text])
        
        # Try KMeans first
        kmeans_similar = self._find_by_kmeans(query_vector)
        if kmeans_similar:
            return kmeans_similar
        
        # If KMeans doesn't give good results, use hierarchical
        return self._find_by_hierarchical(ingredients_list)
    
    def _find_by_kmeans(self, query_vector):
        """Find similar recipes using KMeans clustering"""
        # Predict the cluster for the query
        cluster_id = self.kmeans_model.predict(query_vector)[0]
        
        # Find recipes in the same cluster
        cluster_recipes = self.recipes_df[self.recipes_df['cluster_kmeans'] == cluster_id]
        
        # If no recipes in cluster, return empty list
        if len(cluster_recipes) == 0:
            return []
        
        # Calculate similarity with each recipe in the cluster
        similarities = cosine_similarity(
            query_vector, 
            self.ingredient_vectors[cluster_recipes.index]
        )[0]
        
        # Add similarity scores
        cluster_recipes = cluster_recipes.copy()
        cluster_recipes['similarity'] = similarities
        
        # Sort by similarity
        similar_recipes = cluster_recipes.sort_values('similarity', ascending=False)
        
        # Return top 5 most similar recipes
        result = similar_recipes.head(5).to_dict('records')
        
        print(f"Found {len(result)} recipes using KMeans clustering")
        return result
    
    def _find_by_hierarchical(self, ingredients_list):
        """Find similar recipes using ingredient-by-ingredient matching"""
        # Create a score for each recipe based on matching ingredients
        scores = []
        for _, recipe in self.recipes_df.iterrows():
            recipe_ingredients = recipe['ingredients_simple']
            
            # Count how many query ingredients are in the recipe
            matches = sum(any(query_ing in recipe_ing for recipe_ing in recipe_ingredients) 
                          for query_ing in ingredients_list)
            
            # Calculate a match score
            match_ratio = matches / len(ingredients_list) if len(ingredients_list) > 0 else 0
            
            scores.append({
                'recipe': recipe.to_dict(),
                'match_score': match_ratio
            })
        
        # Sort by match score
        scores.sort(key=lambda x: x['match_score'], reverse=True)
        
        # Return top 5 matches
        result = [item['recipe'] for item in scores[:5]]
        
        print(f"Found {len(result)} recipes using hierarchical approach")
        return result

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