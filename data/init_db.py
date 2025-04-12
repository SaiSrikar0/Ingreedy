import os
from processor import RecipeProcessor
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()
    
    # Create necessary directories
    os.makedirs(os.path.join("data", "processed_data"), exist_ok=True)
    
    # Initialize processor
    processor = RecipeProcessor()
    
    # Load data from JSON
    print("Loading data from JSON...")
    json_path = os.path.join("data", "raw_data", "recipes.json")
    if not processor.load_data_from_json(json_path):
        print("Failed to load data from JSON")
        return
        
    # Split data into training and testing sets
    print("Splitting data into training and testing sets...")
    train_df, test_df = processor.split_data()
    print(f"Training set size: {len(train_df)}")
    print(f"Testing set size: {len(test_df)}")
    
    # Preprocess ingredients
    print("Preprocessing ingredients...")
    processor.preprocess_ingredients()
    
    # Vectorize ingredients
    print("Vectorizing ingredients...")
    processor.vectorize_ingredients()
    
    # Apply clustering
    print("Applying K-means clustering...")
    processor.apply_kmeans_clustering()
    
    print("Applying hierarchical clustering...")
    processor.apply_hierarchical_clustering()
    
    # Save processed data
    print("Saving processed data...")
    processor.save_processed_data()
    
    print("Data processing completed successfully!")

if __name__ == "__main__":
    main() 