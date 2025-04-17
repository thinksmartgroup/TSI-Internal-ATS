from browser_use import Agent
from browser_tool.browser_config import SimpleBrowserConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from pydantic import SecretStr
import os
import asyncio
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def use_browser(task_description, browser_config=None, return_config=False):
    """
    Use the browser to perform a task.
    
    Args:
        task_description: A description of the task to perform
        browser_config: Optional existing browser configuration to reuse
        return_config: Whether to return the browser config along with the result
        
    Returns:
        The result of the task, and optionally the browser configuration
    """
    # Load environment variables
    load_dotenv()
    google_api_key = os.getenv("GEMINI_API_KEY")

    if not google_api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")

    # Initialize the LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp", 
        api_key=SecretStr(google_api_key)
    )
    
    # Create a browser configuration that handles captcha verification
    if browser_config is None:
        browser_config = SimpleBrowserConfig()
    
    # Create an enhanced task description that includes captcha handling
    enhanced_task = f"""
    {task_description}
    
    If you encounter a captcha verification:
    1. Wait for 30 seconds to allow manual verification
    2. Inform the user that they need to complete the verification
    3. Continue with the task after verification is complete
    """
    
    # Initialize the agent with the enhanced task, browser context, and LLM
    agent = Agent(task=enhanced_task, browser_context=browser_config, llm=llm)
    
    try:
        # Run the agent
        result = await agent.run()
        
        # Handle the result based on its type
        final_result = None
        if result is None:
            final_result = "No result returned from the agent."
        elif hasattr(result, 'final_result'):
            # If the result has a final_result method, call it
            final_result = result.final_result()
        elif hasattr(result, 'to_json'):
            # If the result has a to_json method, call it
            final_result = result.to_json()
        elif isinstance(result, (dict, list)):
            # If the result is a dict or list, convert it to JSON
            final_result = json.dumps(result)
        else:
            # Otherwise, convert the result to a string
            final_result = str(result)
            
        if return_config:
            return final_result, browser_config
        else:
            return final_result
    except Exception as e:
        logger.exception(f"Error in browser tool: {e}")
        # Return a JSON string with the error message
        error_result = json.dumps({"error": str(e)})
        if return_config:
            return error_result, browser_config
        else:
            return error_result
