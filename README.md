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

#### Windows
- Python 3.8 or higher (Download from [python.org](https://www.python.org/downloads/))
- MongoDB Community Edition (Download from [mongodb.com](https://www.mongodb.com/try/download/community))
- Git (Download from [git-scm.com](https://git-scm.com/download/win))

#### macOS
- Python 3.8 or higher (Install using Homebrew: `brew install python@3.8`)
- MongoDB Community Edition (Install using Homebrew: `brew tap mongodb/brew && brew install mongodb-community`)
- Git (Install using Homebrew: `brew install git`)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ingreedy.git
cd ingreedy
```

2. Create and activate a virtual environment:

#### Windows:
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# If you get a PowerShell execution policy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### macOS:
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

3. Upgrade pip and install wheel:
```bash
# Windows & macOS
python -m pip install --upgrade pip
pip install wheel
```

4. Install dependencies:
```bash
# Windows & macOS
pip install -r requirements.txt
```

5. Create and configure environment variables:

#### Windows:
```bash
# Copy environment file
copy .env.example .env

# Edit .env file using Notepad
notepad .env
```

#### macOS:
```bash
# Copy environment file
cp .env.example .env

# Edit .env file using nano or your preferred editor
nano .env
```

Add the following to your `.env` file:
```
MONGO_URI=mongodb://localhost:27017
DB_NAME=ingreedy
```

6. Start MongoDB:

#### Windows:
- Open Services (Win + R, type `services.msc`)
- Find "MongoDB" service
- Right-click and select "Start"
- Or use Command Prompt as Administrator:
```bash
net start MongoDB
```

#### macOS:
```bash
# Start MongoDB service
brew services start mongodb-community

# Verify MongoDB is running
brew services list
```

7. Initialize the database:
```bash
# Windows & macOS
python backend/data/init_db.py
```

8. Start the services:

Open two separate terminal windows and run:

#### Windows:
Terminal 1 (FastAPI Backend):
```bash
cd backend/api
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Terminal 2 (Streamlit Frontend):
```bash
cd frontend
python -m streamlit run app.py
```

#### macOS:
Terminal 1 (FastAPI Backend):
```bash
cd backend/api
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Terminal 2 (Streamlit Frontend):
```bash
cd frontend
python3 -m streamlit run app.py
```

The application should now be accessible at:
- Frontend UI: http://localhost:8501
- API Documentation: http://localhost:8000/docs
- FastAPI Backend: http://localhost:8000

## Troubleshooting

### Windows-specific Issues:
1. If you get "python not found" error:
   - Add Python to PATH during installation
   - Or use full path: `C:\Users\YourUsername\AppData\Local\Programs\Python\Python3x\python.exe`

2. If MongoDB fails to start:
   - Check Services app for MongoDB service status
   - Run Command Prompt as Administrator and try: `net start MongoDB`
   - Verify MongoDB installation path in System Environment Variables

3. If you get permission errors:
   - Run Command Prompt or PowerShell as Administrator
   - Check Windows Defender Firewall settings

### macOS-specific Issues:
1. If you get "command not found" errors:
   - Add Homebrew to PATH: `echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc`
   - Restart terminal or run: `source ~/.zshrc`

2. If MongoDB fails to start:
   - Check MongoDB status: `brew services list`
   - Restart MongoDB: `brew services restart mongodb-community`
   - Check MongoDB logs: `tail -f /usr/local/var/log/mongodb/mongo.log`

3. If you get port conflicts:
   - Check if ports are in use: `lsof -i :8000` or `lsof -i :8501`
   - Kill processes using those ports: `kill -9 <PID>`

### General Issues:
1. If you encounter MongoDB connection issues:
   - Ensure MongoDB is running
   - Check if the MongoDB URI in .env is correct
   - Verify MongoDB port (default: 27017) is not blocked

2. If you get dependency errors:
   - Try installing dependencies one by one
   - Ensure you're using Python 3.8 or higher
   - Check if your virtual environment is activated

3. If the services fail to start:
   - Check if the required ports (8000, 8501) are available
   - Ensure all environment variables are set correctly
   - Check the logs for specific error messages

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.