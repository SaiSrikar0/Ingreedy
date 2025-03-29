#!/usr/bin/env python
"""
Run all services for the Ingreedy application
"""
import os
import sys
import subprocess
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get port configurations
FLASK_PORT = os.getenv("PORT", "5000")
FASTAPI_PORT = os.getenv("FASTAPI_PORT", "8000")
STREAMLIT_PORT = os.getenv("STREAMLIT_PORT", "8501")

def run_command(command, cwd=None):
    """Run a command in a subprocess"""
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        cwd=cwd
    )
    return process

def main():
    """Main function to run all services"""
    print("Starting Ingreedy services...")
    
    # Make sure MongoDB is running
    print("Make sure MongoDB is running before continuing.")
    input("Press Enter to continue...")
    
    # Start Flask backend (using simple version for now)
    print(f"Starting Flask backend on port {FLASK_PORT}...")
    flask_process = run_command(f"python simple_app.py", cwd="backend")
    
    # Wait for Flask to start
    time.sleep(2)
    
    # Start FastAPI (using simple version for now)
    print(f"Starting FastAPI on port {FASTAPI_PORT}...")
    fastapi_process = run_command(
        f"uvicorn simple_main:app --reload --port {FASTAPI_PORT}", 
        cwd="backend/api"
    )
    
    # Wait for FastAPI to start
    time.sleep(2)
    
    # Start Streamlit frontend
    print(f"Starting Streamlit frontend on port {STREAMLIT_PORT}...")
    streamlit_process = run_command("streamlit run app.py", cwd="frontend")
    
    print("\nAll services are running!")
    print(f"- Flask API: http://localhost:{FLASK_PORT}")
    print(f"- FastAPI: http://localhost:{FASTAPI_PORT}")
    print(f"- FastAPI Docs: http://localhost:{FASTAPI_PORT}/docs")
    print(f"- Streamlit Frontend: http://localhost:{STREAMLIT_PORT}")
    
    print("\nPress Ctrl+C to stop all services.")
    
    try:
        # Print output from processes
        while True:
            for process, name in [
                (flask_process, "Flask"),
                (fastapi_process, "FastAPI"),
                (streamlit_process, "Streamlit")
            ]:
                output = process.stdout.readline()
                if output:
                    print(f"[{name}] {output.strip()}")
            
            time.sleep(0.1)
    except KeyboardInterrupt:
        # Stop all processes
        print("\nStopping all services...")
        flask_process.terminate()
        fastapi_process.terminate()
        streamlit_process.terminate()
        print("All services stopped.")

if __name__ == "__main__":
    main() 