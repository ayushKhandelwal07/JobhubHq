# Job Application Tracker Agent
# Portia-powered job application tracking with Gmail and Google Sheets integration

from typing import Dict, Any
import logging
from .base import PortiaJobAgent

logger = logging.getLogger(__name__)

class JobApplicationTrackerAgent(PortiaJobAgent):
    """
    Portia-powered job application tracking agent
    Uses Gmail, Google Sheets, and web scraping tools
    """
    
    def __init__(self):
        super().__init__(
            name="Job Application Tracker",
            description="Tracks job applications across platforms using Gmail monitoring and Google Sheets sync"
        )
    
    async def track_applications(self, user_email: str, user_id: str) -> Dict[str, Any]:
        """Track job applications using Gmail and Google Sheets tools"""
        task = f"""
        Track job applications for user {user_email}:
        
        1. Use Gmail tool to scan emails for:
           - Job application confirmations
           - Interview invitations
           - Rejection/acceptance emails
           - Follow-up communications
        
        2. Extract application details:
           - Company name
           - Position title
           - Application date
           - Current status
           - Next steps
        
        3. Use Google Sheets tool to:
           - Update application tracking spreadsheet
           - Add new applications found
           - Update status of existing applications
        
        4. Generate summary of:
           - New applications found
           - Status updates
           - Recommended follow-up actions
        
        Please be thorough and accurate in extracting information.
        """
        
        return await self.execute_with_planning(
            task=task,
            context={"user_email": user_email, "user_id": user_id},
            end_user=user_id
        )
    
    async def sync_chrome_extension_data(self, job_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Process job data from Chrome extension and sync to tracking systems"""
        task = f"""
        Process job application data from Chrome extension:
        
        Job Data: {job_data}
        
        1. Validate and clean the extracted job data
        2. Check for duplicates in existing tracking systems
        3. Use Google Sheets tool to add new job application entry
        4. Use Gmail tool to search for related emails about this application
        5. Generate tracking entry with:
           - Standardized company name
           - Clean job title
           - Salary range (if available)
           - Application date
           - Source platform (LinkedIn, Indeed, etc.)
           - Application status
        
        Ensure data quality and consistency across all tracking systems.
        """
        
        return await self.execute_with_planning(
            task=task,
            context={"job_data": job_data, "user_id": user_id},
            end_user=user_id
        )
