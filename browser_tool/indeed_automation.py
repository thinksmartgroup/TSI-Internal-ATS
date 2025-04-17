import asyncio
import json
import logging
import os
from typing import List, Dict, Any, Optional

from browser_tool.agent import use_browser
from browser_tool.browser_config import SimpleBrowserConfig

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variable to store the browser configuration for tab management
_browser_config = None

async def login_to_indeed():
    """
    Log in to the Indeed employer dashboard.
    
    Returns:
        A success message or error details.
    """
    global _browser_config
    
    task = """
    Log in to the Indeed employer dashboard:
    1. Navigate to https://employers.indeed.com/
    2. Enter your email and password
    3. Click the login button
    4. Wait for the dashboard to load
    5. Return a success message when logged in
    """
    
    try:
        result, config = await use_browser(task, return_config=True)
        # Store the browser config for future use
        _browser_config = config
        return result
    except Exception as e:
        logger.exception(f"Error logging in to Indeed: {e}")
        return json.dumps({"error": f"Failed to log in to Indeed: {str(e)}"})

async def open_job_post(job_title: str):
    """
    Open a specific job post on Indeed.
    
    Args:
        job_title: The title of the job to open
        
    Returns:
        Job details or error message
    """
    task = f"""
    Open the job post for '{job_title}' on Indeed:
    1. Navigate to the Indeed employer dashboard
    2. Find the job post titled '{job_title}'
    3. Click on the job post to open it
    4. Extract and return the following information in JSON format:
       - job_id: The job ID
       - title: The job title
       - status: The job status (active, paused, etc.)
       - applicants_count: The number of applicants
       - posted_date: The date the job was posted
    """
    
    try:
        result = await use_browser(task)
        return result
    except Exception as e:
        logger.exception(f"Error opening job post '{job_title}': {e}")
        return json.dumps({"error": f"Failed to open job post '{job_title}': {str(e)}"})

async def open_job_in_new_tab(job_title: str):
    """
    Open a specific job post in a new tab.
    
    Args:
        job_title: The title of the job to open
        
    Returns:
        Job details or error message
    """
    global _browser_config
    
    if not _browser_config:
        return json.dumps({"error": "Browser not initialized. Please log in first."})
    
    try:
        # First, navigate to the jobs dashboard
        task = """
        Navigate to the Indeed employer jobs dashboard to get a list of all jobs
        """
        await use_browser(task, browser_config=_browser_config)
        
        # Now open the specific job in a new tab
        await _browser_config.open_new_tab()
        
        task = f"""
        Find and open the job post titled '{job_title}':
        1. Search for the job titled '{job_title}'
        2. Click on the job post to open it
        3. Extract and return information about the job
        """
        
        result = await use_browser(task, browser_config=_browser_config)
        return result
    except Exception as e:
        logger.exception(f"Error opening job post '{job_title}' in new tab: {e}")
        return json.dumps({"error": f"Failed to open job post '{job_title}' in new tab: {str(e)}"})

async def get_applicants(job_title: str):
    """
    Get all applicants for a specific job.
    
    Args:
        job_title: The title of the job
        
    Returns:
        List of applicants or error message
    """
    task = f"""
    Get all applicants for the job '{job_title}' on Indeed:
    1. Navigate to the Indeed employer dashboard
    2. Find the job post titled '{job_title}'
    3. Click on the job post to open it
    4. Navigate to the applicants tab
    5. Extract and return all applicant information in JSON format with the following fields for each applicant:
       - name: Applicant's full name
       - position: Job position applied for
       - date: Application date
       - status: Current status (New, Reviewed, Interviewed, etc.)
       - experience: Years of experience
       - skills: Array of skills
    """
    
    try:
        result = await use_browser(task)
        return result
    except Exception as e:
        logger.exception(f"Error getting applicants for '{job_title}': {e}")
        return json.dumps({"error": f"Failed to get applicants for '{job_title}': {str(e)}"})

async def switch_tabs(tab_index_or_title):
    """
    Switch to a different tab by index or title.
    
    Args:
        tab_index_or_title: The index (0-based) or title of the tab to switch to
        
    Returns:
        Success message or error details
    """
    global _browser_config
    
    if not _browser_config:
        return json.dumps({"error": "Browser not initialized. Please log in first."})
    
    try:
        success = await _browser_config.switch_to_tab(tab_index_or_title)
        if success:
            return json.dumps({"success": f"Switched to tab: {tab_index_or_title}"})
        else:
            return json.dumps({"error": f"Failed to switch to tab: {tab_index_or_title}"})
    except Exception as e:
        logger.exception(f"Error switching to tab: {e}")
        return json.dumps({"error": f"Failed to switch to tab: {str(e)}"})

async def open_new_tab(url=None):
    """
    Open a new tab in the browser.
    
    Args:
        url: Optional URL to open in the new tab
        
    Returns:
        Success message or error details
    """
    global _browser_config
    
    if not _browser_config:
        return json.dumps({"error": "Browser not initialized. Please log in first."})
    
    try:
        new_page = await _browser_config.open_new_tab(url)
        if new_page:
            return json.dumps({"success": f"Opened new tab with URL: {url if url else 'about:blank'}"})
        else:
            return json.dumps({"error": "Failed to open new tab"})
    except Exception as e:
        logger.exception(f"Error opening new tab: {e}")
        return json.dumps({"error": f"Failed to open new tab: {str(e)}"})

async def send_invite(job_title: str, applicant_name: Optional[str] = None):
    """
    Send an interview invite to applicants.
    
    Args:
        job_title: The title of the job
        applicant_name: Optional name of a specific applicant. If None, send to all applicants.
        
    Returns:
        Success message or error details
    """
    if applicant_name:
        task = f"""
        Send an interview invite to the applicant '{applicant_name}' for the job '{job_title}' on Indeed:
        1. Navigate to the Indeed employer dashboard
        2. Find the job post titled '{job_title}'
        3. Click on the job post to open it
        4. Navigate to the applicants tab
        5. Find the applicant named '{applicant_name}'
        6. Click on the applicant to view their profile
        7. Click the 'Send Interview Invite' button
        8. Fill in the interview details (date, time, location/meeting link)
        9. Send the invite
        10. Return a success message when the invite is sent
        """
    else:
        task = f"""
        Send interview invites to all applicants for the job '{job_title}' on Indeed:
        1. Navigate to the Indeed employer dashboard
        2. Find the job post titled '{job_title}'
        3. Click on the job post to open it
        4. Navigate to the applicants tab
        5. Select all applicants
        6. Click the 'Send Interview Invite' button
        7. Fill in the interview details (date, time, location/meeting link)
        8. Send the invites
        9. Return a success message when the invites are sent
        """
    
    try:
        result = await use_browser(task)
        return result
    except Exception as e:
        logger.exception(f"Error sending invite for '{job_title}': {e}")
        return json.dumps({"error": f"Failed to send invite for '{job_title}': {str(e)}"})

async def update_application_status(job_title: str, applicant_name: str, new_status: str):
    """
    Update the status of an applicant.
    
    Args:
        job_title: The title of the job
        applicant_name: The name of the applicant
        new_status: The new status to set (e.g., 'Reviewed', 'Interviewed', 'Hired', 'Rejected')
        
    Returns:
        Success message or error details
    """
    task = f"""
    Update the status of the applicant '{applicant_name}' for the job '{job_title}' to '{new_status}' on Indeed:
    1. Navigate to the Indeed employer dashboard
    2. Find the job post titled '{job_title}'
    3. Click on the job post to open it
    4. Navigate to the applicants tab
    5. Find the applicant named '{applicant_name}'
    6. Click on the applicant to view their profile
    7. Update their status to '{new_status}'
    8. Save the changes
    9. Return a success message when the status is updated
    """
    
    try:
        result = await use_browser(task)
        return result
    except Exception as e:
        logger.exception(f"Error updating status for '{applicant_name}': {e}")
        return json.dumps({"error": f"Failed to update status for '{applicant_name}': {str(e)}"})

async def search_jobs(query: str):
    """
    Search for jobs on Indeed.
    
    Args:
        query: The search query
        
    Returns:
        List of matching jobs or error message
    """
    task = f"""
    Search for jobs matching '{query}' on Indeed:
    1. Navigate to the Indeed employer dashboard
    2. Use the search functionality to find jobs matching '{query}'
    3. Extract and return all matching job information in JSON format with the following fields for each job:
       - job_id: The job ID
       - title: The job title
       - status: The job status (active, paused, etc.)
       - applicants_count: The number of applicants
       - posted_date: The date the job was posted
    """
    
    try:
        result = await use_browser(task)
        return result
    except Exception as e:
        logger.exception(f"Error searching for jobs with query '{query}': {e}")
        return json.dumps({"error": f"Failed to search for jobs with query '{query}': {str(e)}"})

async def create_job_post(job_details: Dict[str, Any]):
    """
    Create a new job post on Indeed.
    
    Args:
        job_details: A dictionary containing job details
        
    Returns:
        Success message or error details
    """
    # Convert job details to a formatted string
    job_details_str = json.dumps(job_details, indent=2)
    
    task = f"""
    Create a new job post on Indeed with the following details:
    {job_details_str}
    
    Steps:
    1. Navigate to the Indeed employer dashboard
    2. Click on 'Post a Job'
    3. Fill in all the job details as specified above
    4. Review the job post
    5. Publish the job post
    6. Return a success message with the job ID when the job is published
    """
    
    try:
        result = await use_browser(task)
        return result
    except Exception as e:
        logger.exception(f"Error creating job post: {e}")
        return json.dumps({"error": f"Failed to create job post: {str(e)}"}) 