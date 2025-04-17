import asyncio
import json
import logging
import os
import re
from typing import Dict, Any, List, Optional

from browser_tool.indeed_automation import (
    login_to_indeed,
    open_job_post,
    get_applicants,
    send_invite,
    update_application_status,
    search_jobs,
    create_job_post
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IndeedAssistant:
    """
    A chat-based assistant for managing job applications on Indeed.
    """
    
    def __init__(self):
        """
        Initialize the Indeed Assistant.
        """
        self.is_logged_in = False
        self.current_job = None
        self.current_applicants = []
    
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
            return "No job title found in the current job."
        
        result = await update_application_status(job_title, applicant_name, new_status)
        try:
            result_dict = json.loads(result)
            if "error" in result_dict:
                return f"Failed to update status: {result_dict['error']}"
            else:
                return f"Successfully updated the status of {applicant_name} to {new_status}."
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
        
        result = await search_jobs(query)
        try:
            result_dict = json.loads(result)
            if "error" in result_dict:
                return f"Failed to search for jobs: {result_dict['error']}"
            else:
                job_count = len(result_dict) if isinstance(result_dict, list) else 0
                return f"Found {job_count} jobs matching '{query}'."
        except json.JSONDecodeError:
            return f"Search result: {result}"
    
    async def _handle_create_job(self, job_title: str) -> str:
        """
        Handle the create job command.
        
        Args:
            job_title: The title of the job
            
        Returns:
            A response to the user
        """
        if not self.is_logged_in:
            return "Please log in to Indeed first."
        
        # Create a basic job details dictionary
        job_details = {
            "title": job_title,
            "description": f"Job description for {job_title}",
            "location": "Remote",
            "employment_type": "Full-time",
            "salary": "Competitive",
            "required_skills": ["Skill 1", "Skill 2", "Skill 3"],
            "preferred_skills": ["Skill 4", "Skill 5"],
            "required_experience": "3+ years",
            "education": "Bachelor's degree or equivalent"
        }
        
        result = await create_job_post(job_details)
        try:
            result_dict = json.loads(result)
            if "error" in result_dict:
                return f"Failed to create job post: {result_dict['error']}"
            else:
                return f"Successfully created a job post for '{job_title}'."
        except json.JSONDecodeError:
            return f"Job creation result: {result}"

async def run_indeed_assistant():
    """
    Run the Indeed Assistant in interactive mode.
    """
    assistant = IndeedAssistant()
    
    print("Welcome to the Indeed Assistant!")
    print("Type 'exit' to quit.")
    
    while True:
        command = input("\nWhat would you like me to do? > ")
        
        if command.lower() == 'exit':
            print("Goodbye!")
            break
        
        response = await assistant.process_command(command)
        print(f"\n{response}")

if __name__ == "__main__":
    asyncio.run(run_indeed_assistant()) 