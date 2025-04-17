import asyncio
import json
import logging
import os
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from chat_interface import ChatInterface

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Indeed Assistant API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (for the HTML dashboard)
app.mount("/static", StaticFiles(directory="."), name="static")

# Store active chat interfaces
chat_interfaces: Dict[str, ChatInterface] = {}

class CommandRequest(BaseModel):
    command: str
    session_id: Optional[str] = None

class CommandResponse(BaseModel):
    response: str
    session_id: str

@app.get("/")
async def root():
    """
    Serve the dashboard HTML file.
    """
    return {"message": "Indeed Assistant API is running. Visit /static/dashboard.html for the dashboard."}

@app.post("/api/command", response_model=CommandResponse)
async def process_command(request: CommandRequest):
    """
    Process a command using the chat interface.
    
    Args:
        request: The command request
        
    Returns:
        The command response
    """
    # Get or create a chat interface for this session
    session_id = request.session_id or "default"
    if session_id not in chat_interfaces:
        chat_interfaces[session_id] = ChatInterface()
    
    # Process the command
    response = await chat_interfaces[session_id].process_command(request.command)
    
    return CommandResponse(response=response, session_id=session_id)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time chat.
    
    Args:
        websocket: The WebSocket connection
    """
    await websocket.accept()
    
    # Create a chat interface for this session
    chat_interface = ChatInterface()
    
    # Define a callback to send messages to the client
    async def send_message(message: str):
        await websocket.send_text(json.dumps({"role": "assistant", "content": message}))
    
    # Set the callback
    chat_interface.message_callback = send_message
    
    try:
        # Send welcome message
        await websocket.send_text(json.dumps({
            "role": "assistant",
            "content": "Welcome to the Indeed Assistant! I can help you manage your job applications on Indeed.\n\nPlease let me know what you'd like me to do."
        }))
        
        # Process commands from the client
        while True:
            data = await websocket.receive_text()
            request = json.loads(data)
            
            # Process the command
            response = await chat_interface.process_command(request["command"])
            
            # Send the response
            await websocket.send_text(json.dumps({
                "role": "assistant",
                "content": response
            }))
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.exception(f"Error in WebSocket: {e}")
        try:
            await websocket.send_text(json.dumps({
                "role": "assistant",
                "content": f"Error: {str(e)}"
            }))
        except:
            pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 