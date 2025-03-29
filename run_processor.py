#!/usr/bin/env python
"""
Run the recipe processor to prepare data for ML algorithms
"""
import os
import sys
from data.processor import main as processor_main

def main():
    """Main function to run the processor"""
    print("Starting recipe data processor...")
    print("This will process recipe data and prepare it for ML algorithms.")
    print("Make sure MongoDB is running and contains recipe data!")
    
    # Run the processor
    processor_main()
    
    print("Processing complete!")

if __name__ == "__main__":
    main() 