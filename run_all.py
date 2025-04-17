import subprocess
import sys
import os
import signal
import time
import threading

def run_streamlit():
    """Run the Streamlit app"""
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])

def run_voice_assistant():
    """Run the voice assistant"""
    subprocess.run([sys.executable, "main.py"])

def main():
    """Run both the Streamlit app and voice assistant"""
    print("Starting ThinkSmart Internal ATS...")
    
    # Create threads for each process
    streamlit_thread = threading.Thread(target=run_streamlit)
    voice_assistant_thread = threading.Thread(target=run_voice_assistant)
    
    # Set threads as daemon so they exit when the main thread exits
    streamlit_thread.daemon = True
    voice_assistant_thread.daemon = True
    
    # Start the threads
    streamlit_thread.start()
    print("Streamlit app started. Access it at http://localhost:8501")
    
    # Wait a bit before starting the voice assistant
    time.sleep(2)
    
    voice_assistant_thread.start()
    print("Voice assistant started. Speak to interact with the dashboard.")
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0)

if __name__ == "__main__":
    main() 