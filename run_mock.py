import subprocess
import sys
import os
import time

def main():
    """Run the mock Streamlit app"""
    print("Starting ThinkSmart Internal ATS Dashboard (Mock Data)...")
    
    # Run the Streamlit app
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app_mock.py"])
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0)

if __name__ == "__main__":
    main() 