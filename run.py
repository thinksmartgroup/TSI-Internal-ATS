import subprocess
import sys
import os
import time
import threading

def run_streamlit():
    """Run the Streamlit app"""
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])

def main():
    """Run the Streamlit app"""
    print("Starting ThinkSmart Internal ATS Dashboard...")
    
    # Run the Streamlit app
    run_streamlit()
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0)

if __name__ == "__main__":
    main() 