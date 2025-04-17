import asyncio
import json
import logging
import os
import re
from typing import Dict, Any, List, Optional, Callable, Awaitable

from browser_tool.indeed_automation import (
    login_to_indeed,
    open_job_post,
    get_applicants,
    send_invite,
    update_application_status,
    search_jobs,
    create_job_post,
    open_job_in_new_tab,
    open_new_tab,
    switch_tabs
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatInterface:
    """
    A chat-based interface for the Indeed Assistant that can be integrated with a dashboard.
    """
    
    def __init__(self, message_callback: Optional[Callable[[str], Awaitable[None]]] = None):
        """
        Initialize the Chat Interface.
        
        Args:
            message_callback: Optional callback function to handle messages
        """
        self.is_logged_in = False
        self.current_job = None
        self.current_applicants = []
        self.message_callback = message_callback
    
    async def send_message(self, message: str) -> None:
        """
        Send a message to the callback function if one is provided.
        
        Args:
            message: The message to send
        """
        if self.message_callback:
            await self.message_callback(message)
        else:
            print(message)
    
    async def process_command(self, command: str) -> str:
        """
        Process a user command and return a response.
        
        Args:
            command: The user's command
            
        Returns:
            A response to the user
        """
        # Convert command to lowercase for easier matching
        command_lower = command.lower()
        
        # Check if the command is a login command
        if re.search(r'log\s+in|login|sign\s+in', command_lower):
            return await self._handle_login()
        
        # Check if the command is to open a job post
        job_match = re.search(r'open\s+(?:the\s+)?(?:job\s+)?(?:post\s+)?(?:for\s+)?(?:the\s+)?([^"]+)', command_lower)
        if job_match:
            job_title = job_match.group(1).strip()
            # Check if we should open in a new tab
            if 'new tab' in command_lower or 'new window' in command_lower:
                return await self._handle_open_job_in_new_tab(job_title)
            else:
                return await self._handle_open_job(job_title)
        
        # Check if the command is to get applicants
        applicants_match = re.search(r'(?:get|show|list|view)\s+(?:all\s+)?applicants\s+(?:for\s+)?(?:the\s+)?(?:job\s+)?(?:post\s+)?(?:for\s+)?(?:the\s+)?([^"]+)', command_lower)
        if applicants_match:
            job_title = applicants_match.group(1).strip()
            return await self._handle_get_applicants(job_title)
        
        # Check if the command is to send an invite
        invite_match = re.search(r'send\s+(?:an\s+)?invite\s+(?:to\s+)?(?:all\s+)?applicants?\s+(?:for\s+)?(?:the\s+)?(?:job\s+)?(?:post\s+)?(?:for\s+)?(?:the\s+)?([^"]+)', command_lower)
        if invite_match:
            job_title = invite_match.group(1).strip()
            # Check if a specific applicant is mentioned
            applicant_match = re.search(r'to\s+([^"]+?)(?:\s+for\s+|\s*$)', command_lower)
            applicant_name = applicant_match.group(1).strip() if applicant_match else None
            return await self._handle_send_invite(job_title, applicant_name)
        
        # Check if the command is to update an applicant's status
        status_match = re.search(r'update\s+(?:the\s+)?status\s+of\s+([^"]+)\s+to\s+([^"]+)', command_lower)
        if status_match:
            applicant_name = status_match.group(1).strip()
            new_status = status_match.group(2).strip()
            return await self._handle_update_status(applicant_name, new_status)
        
        # Check if the command is to search for jobs
        search_match = re.search(r'search\s+for\s+(?:jobs?\s+)?(?:matching\s+)?([^"]+)', command_lower)
        if search_match:
            query = search_match.group(1).strip()
            return await self._handle_search_jobs(query)
        
        # Check if the command is to create a job post
        create_match = re.search(r'create\s+(?:a\s+)?(?:new\s+)?job\s+post\s+(?:for\s+)?([^"]+)', command_lower)
        if create_match:
            job_title = create_match.group(1).strip()
            return await self._handle_create_job(job_title)
        
        # Check if the command is to open a new tab
        if re.search(r'open\s+(?:a\s+)?new\s+tab', command_lower):
            # Check if a URL is specified
            url_match = re.search(r'with\s+(?:url\s+)?(?:to\s+)?(?:https?://)?([^\s]+)', command_lower)
            url = f"https://{url_match.group(1)}" if url_match else None
            return await self._handle_open_new_tab(url)
        
        # Check if the command is to switch tabs
        switch_match = re.search(r'switch\s+(?:to\s+)?(?:tab\s+)?(\d+|[^"]+tab)', command_lower)
        if switch_match:
            tab_identifier = switch_match.group(1).strip()
            # Check if it's a number
            if tab_identifier.isdigit():
                tab_identifier = int(tab_identifier) - 1  # Convert to 0-based index
            return await self._handle_switch_tabs(tab_identifier)
        
        # If no specific command is recognized, return a helpful message
        return """
        I'm your Indeed Assistant. I can help you with the following tasks:
        
        1. Log in to Indeed
        2. Open a job post (e.g., "Open the Network Engineer job")
        3. Get applicants for a job (e.g., "Get applicants for the Test Engineer role")
        4. Send invites to applicants (e.g., "Send an invite to all applicants for the Test Engineer role")
        5. Update an applicant's status (e.g., "Update the status of John Doe to Interviewed")
        6. Search for jobs (e.g., "Search for jobs matching Software Engineer")
        7. Create a job post (e.g., "Create a job post for Senior Developer")
        8. Tab management:
           - Open a new tab (e.g., "Open a new tab")
           - Open a job in a new tab (e.g., "Open the Software Engineer job in a new tab")
           - Switch between tabs (e.g., "Switch to tab 2" or "Switch to the Indeed tab")
        
        Please let me know what you'd like me to do.
        """
    
    async def _handle_login(self) -> str:
        """
        Handle the login command.
        
        Returns:
            A response to the user
        """
        if self.is_logged_in:
            return "You are already logged in to Indeed."
        
        await self.send_message("Logging in to Indeed...")
        result = await login_to_indeed()
        try:
            result_dict = json.loads(result)
            if "error" in result_dict:
                return f"Failed to log in: {result_dict['error']}"
            else:
                self.is_logged_in = True
                return "Successfully logged in to Indeed."
        except json.JSONDecodeError:
            if "success" in result.lower() or "logged in" in result.lower():
                self.is_logged_in = True
                return "Successfully logged in to Indeed."
            else:
                return f"Login result: {result}"
    
    async def _handle_open_job(self, job_title: str) -> str:
        """
        Handle the open job command.
        
        Args:
            job_title: The title of the job to open
            
        Returns:
            A response to the user
        """
        if not self.is_logged_in:
            return "Please log in to Indeed first."
        
        await self.send_message(f"Opening job post for '{job_title}'...")
        result = await open_job_post(job_title)
        try:
            result_dict = json.loads(result)
            if "error" in result_dict:
                return f"Failed to open job post: {result_dict['error']}"
            else:
                self.current_job = result_dict
                return f"Successfully opened the job post for '{job_title}'. Job ID: {result_dict.get('job_id', 'N/A')}"
        except json.JSONDecodeError:
            return f"Job post result: {result}"
    
    async def _handle_open_job_in_new_tab(self, job_title: str) -> str:
        """
        Handle the open job in new tab command.
        
        Args:
            job_title: The title of the job to open
            
        Returns:
            A response to the user
        """
        if not self.is_logged_in:
            return "Please log in to Indeed first."
        
        await self.send_message(f"Opening job post for '{job_title}' in a new tab...")
        result = await open_job_in_new_tab(job_title)
        try:
            result_dict = json.loads(result)
            if "error" in result_dict:
                return f"Failed to open job post in new tab: {result_dict['error']}"
            else:
                self.current_job = result_dict
                return f"Successfully opened the job post for '{job_title}' in a new tab. Job ID: {result_dict.get('job_id', 'N/A')}"
        except json.JSONDecodeError:
            return f"Job post result: {result}"
    
    async def _handle_open_new_tab(self, url: Optional[str] = None) -> str:
        """
        Handle the open new tab command.
        
        Args:
            url: Optional URL to open in the new tab
            
        Returns:
            A response to the user
        """
        if not self.is_logged_in:
            return "Please log in to Indeed first."
        
        if url:
            await self.send_message(f"Opening new tab with URL: {url}...")
        else:
            await self.send_message("Opening new tab...")
            
        result = await open_new_tab(url)
        try:
            result_dict = json.loads(result)
            if "error" in result_dict:
                return f"Failed to open new tab: {result_dict['error']}"
            else:
                return "Successfully opened a new tab."
        except json.JSONDecodeError:
            return f"New tab result: {result}"
    
    async def _handle_switch_tabs(self, tab_identifier) -> str:
        """
        Handle the switch tabs command.
        
        Args:
            tab_identifier: The index or title of the tab to switch to
            
        Returns:
            A response to the user
        """
        if not self.is_logged_in:
            return "Please log in to Indeed first."
        
        await self.send_message(f"Switching to tab: {tab_identifier}...")
        result = await switch_tabs(tab_identifier)
        try:
            result_dict = json.loads(result)
            if "error" in result_dict:
                return f"Failed to switch tabs: {result_dict['error']}"
            else:
                return f"Successfully switched to tab: {tab_identifier}"
        except json.JSONDecodeError:
            return f"Switch tabs result: {result}"
    
    async def _handle_get_applicants(self, job_title: str) -> str:
        """
        Handle the get applicants command.
        
        Args:
            job_title: The title of the job
            
        Returns:
            A response to the user
        """
        if not self.is_logged_in:
            return "Please log in to Indeed first."
        
        await self.send_message(f"Getting applicants for '{job_title}'...")
        result = await get_applicants(job_title)
        try:
            result_dict = json.loads(result)
            if "error" in result_dict:
                return f"Failed to get applicants: {result_dict['error']}"
            else:
                self.current_applicants = result_dict
                applicant_count = len(result_dict) if isinstance(result_dict, list) else 0
                return f"Found {applicant_count} applicants for '{job_title}'."
        except json.JSONDecodeError:
            return f"Applicants result: {result}"
    
    async def _handle_send_invite(self, job_title: str, applicant_name: Optional[str] = None) -> str:
        """
        Handle the send invite command.
        
        Args:
            job_title: The title of the job
            applicant_name: Optional name of a specific applicant
            
        Returns:
            A response to the user
        """
        if not self.is_logged_in:
            return "Please log in to Indeed first."
        
        if applicant_name:
            await self.send_message(f"Sending invite to {applicant_name} for '{job_title}'...")
        else:
            await self.send_message(f"Sending invites to all applicants for '{job_title}'...")
        
        result = await send_invite(job_title, applicant_name)
        try:
            result_dict = json.loads(result)
            if "error" in result_dict:
                return f"Failed to send invite: {result_dict['error']}"
            else:
                if applicant_name:
                    return f"Successfully sent an invite to {applicant_name} for the job '{job_title}'."
                else:
                    return f"Successfully sent invites to all applicants for the job '{job_title}'."
        except json.JSONDecodeError:
            return f"Invite result: {result}"
    
    async def _handle_update_status(self, applicant_name: str, new_status: str) -> str:
        """
        Handle the update status command.
        
        Args:
            applicant_name: The name of the applicant
            new_status: The new status to set
            
        Returns:
            A response to the user
        """
        if not self.is_logged_in:
            return "Please log in to Indeed first."
        
        if not self.current_job:
            return "Please open a job post first."
        
        job_title = self.current_job.get('title', '')
        if not job_title:
            return "Current job information is incomplete. Please open a job post first."
        
        await self.send_message(f"Updating status of {applicant_name} to '{new_status}'...")
        result = await update_application_status(job_title, applicant_name, new_status)
        try:
            result_dict = json.loads(result)
            if "error" in result_dict:
                return f"Failed to update status: {result_dict['error']}"
            else:
                return f"Successfully updated the status of {applicant_name} to '{new_status}'."
        except json.JSONDecodeError:
            return f"Status update result: {result}"
    
    async def _handle_search_jobs(self, query: str) -> str:
        """
        Handle the search jobs command.
        
        Args:
            query: The search query
            
        Returns:
            A response to the user
        """
        if not self.is_logged_in:
            return "Please log in to Indeed first."
        
        await self.send_message(f"Searching for jobs matching '{query}'...")
        result = await search_jobs(query)
        try:
            result_dict = json.loads(result)
            if "error" in result_dict:
                return f"Failed to search for jobs: {result_dict['error']}"
            else:
                job_count = len(result_dict) if isinstance(result_dict, list) else 0
                return f"Found {job_count} jobs matching '{query}'."
        except json.JSONDecodeError:
            return f"Job search result: {result}"
    
    async def _handle_create_job(self, job_title: str) -> str:
        """
        Handle the create job command.
        
        Args:
            job_title: The title of the job to create
            
        Returns:
            A response to the user
        """
        if not self.is_logged_in:
            return "Please log in to Indeed first."
        
        # Create a basic job post with the title
        job_details = {
            "title": job_title,
            "location": "Remote",
            "job_type": "Full-time",
            "description": f"We are looking for a {job_title} to join our team.",
            "salary": "Competitive",
            "requirements": ["Bachelor's degree", "1+ years of experience"]
        }
        
        await self.send_message(f"Creating job post for '{job_title}'...")
        result = await create_job_post(job_details)
        try:
            result_dict = json.loads(result)
            if "error" in result_dict:
                return f"Failed to create job post: {result_dict['error']}"
            else:
                return f"Successfully created job post for '{job_title}'."
        except json.JSONDecodeError:
            return f"Job creation result: {result}"

async def example_dashboard_integration():
    """
    Example of how to integrate with a dashboard.
    """
    interface = ChatInterface()
    
    async def handle_message(message: str):
        # In a real implementation, this would update the dashboard UI
        print(f"Dashboard update: {message}")
    
    interface.message_callback = handle_message
    
    # Example of processing a command
    response = await interface.process_command("Log in to Indeed")
    print(f"Response: {response}")
    
    response = await interface.process_command("Open the Software Engineer job")
    print(f"Response: {response}")
    
    response = await interface.process_command("Get applicants for the Software Engineer job")
    print(f"Response: {response}")

if __name__ == "__main__":
    # Example usage
    asyncio.run(example_dashboard_integration()) 