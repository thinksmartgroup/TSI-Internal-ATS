import asyncio
import json
import logging
import os
import streamlit as st
from typing import Dict, Any, List, Optional

from chat_interface import ChatInterface

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'chat_interface' not in st.session_state:
    st.session_state.chat_interface = None

async def handle_message(message: str):
    """
    Handle a message from the chat interface.
    
    Args:
        message: The message to handle
    """
    st.session_state.messages.append({"role": "assistant", "content": message})
    st.rerun()

async def process_command(command: str):
    """
    Process a command using the chat interface.
    
    Args:
        command: The command to process
    """
    if st.session_state.chat_interface is None:
        st.session_state.chat_interface = ChatInterface(message_callback=handle_message)
    
    response = await st.session_state.chat_interface.process_command(command)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

def main():
    """
    Main function for the dashboard.
    """
    st.title("Indeed Assistant Dashboard")
    
    # Sidebar for job information
    with st.sidebar:
        st.header("Current Job")
        if st.session_state.chat_interface and st.session_state.chat_interface.current_job:
            job = st.session_state.chat_interface.current_job
            st.write(f"**Title:** {job.get('title', 'N/A')}")
            st.write(f"**ID:** {job.get('job_id', 'N/A')}")
            st.write(f"**Status:** {job.get('status', 'N/A')}")
            st.write(f"**Applicants:** {job.get('applicants_count', 'N/A')}")
        else:
            st.write("No job selected")
        
        st.header("Quick Actions")
        if st.button("Log in to Indeed"):
            asyncio.run(process_command("Log in to Indeed"))
        
        if st.button("Search for Jobs"):
            query = st.text_input("Search query")
            if query:
                asyncio.run(process_command(f"Search for jobs matching {query}"))
    
    # Main chat area
    st.header("Chat with Indeed Assistant")
    
    # Display messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("What would you like me to do?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Process the command
        asyncio.run(process_command(prompt))

if __name__ == "__main__":
    main() 