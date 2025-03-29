# Ingreedy

A recipe recommendation chatbot that suggests recipes based on ingredients you have.

## Overview

Ingreedy is a web application that:
- Takes ingredients as input
- Recommends recipes based on available ingredients
- Uses machine learning to find similar recipes when exact matches aren't found

## Tech Stack

- **Frontend**: Streamlit
- **Backend**: Flask + FastAPI
- **Database**: MongoDB
- **ML Algorithms**: KMeans clustering, Hierarchical clustering

## Project Structure

```
ingreedy/
├── frontend/              # Streamlit application
├── backend/               # Flask and FastAPI services
│   ├── api/               # FastAPI implementation
│   ├── services/          # Business logic and ML models
│   └── data/              # Data processing utilities
└── data/                  # Data scraped from AllRecipes.com
```

## Setup Instructions

### Prerequisites

- Python 3.8+
- MongoDB Community Edition

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ingreedy.git
cd ingreedy
```

2. Create a virtual environment:
```bash
python -m venv venv
.\venv\Scripts\activate
```

3. Install dependencies:
```
```

4. Copy the example environment file:
```
copy .env.example .env
```

5. Populate the database with recipes:
```
python run_scraper.py
```

6. Process the recipe data for ML algorithms:
```
python run_processor.py
```

7. Run all services using the provided script:
```
python run_all.py
```

The application should now start successfully. You can access it at:
- Frontend UI: http://localhost:8501
- API Documentation: http://localhost:8000/docs
- Flask API: http://localhost:5000