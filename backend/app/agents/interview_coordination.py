# Interview Coordination Agent
# Portia-powered interview scheduling and preparation with calendar and email automation

from typing import Dict, Any, List
import logging
from .base import PortiaJobAgent

logger = logging.getLogger(__name__)

class InterviewCoordinationAgent(PortiaJobAgent):
    """
    Portia-powered interview scheduling and preparation agent
    Uses calendar integration and email automation
    """
    
    def __init__(self):
        super().__init__(
            name="Interview Coordination Agent", 
            description="Manages interview scheduling, preparation, and follow-up using calendar and email tools"
        )
    
    async def schedule_interview(self, candidate_email: str, interviewer_emails: List[str], job_title: str, recruiter_id: str) -> Dict[str, Any]:
        """Schedule interview with automatic coordination"""
        task = f"""
        Schedule interview efficiently:
        
        Candidate: {candidate_email}
        Interviewers: {interviewer_emails}
        Position: {job_title}
        
        1. Use Google Calendar tool to:
           - Find common availability for all participants
           - Suggest 3 optimal time slots
           - Create calendar invites with:
             - Interview details
             - Meeting link (if virtual)
             - Preparation materials
        
        2. Use Gmail tool to:
           - Send interview confirmation to candidate
           - Notify interviewers with candidate info
           - Include interview guide and questions
        
        3. Generate interview preparation package:
           - Candidate background summary
           - Relevant technical questions
           - Behavioral interview scenarios
           - Evaluation criteria
        
        4. Schedule follow-up reminders:
           - 24 hours before interview
           - Post-interview feedback collection
        
        5. PAUSE for approval of interview schedule
        """
        
        return await self.execute_with_planning(
            task=task,
            context={
                "candidate": candidate_email,
                "interviewers": interviewer_emails,
                "job_title": job_title
            },
            end_user=recruiter_id
        )
    
    async def prepare_interview_materials(self, candidate_data: Dict[str, Any], job_requirements: Dict[str, Any], interview_type: str, recruiter_id: str) -> Dict[str, Any]:
        """Generate personalized interview preparation materials"""
        task = f"""
        Prepare comprehensive interview materials:
        
        Candidate: {candidate_data}
        Job Requirements: {job_requirements}
        Interview Type: {interview_type}
        
        1. Analyze candidate background and generate:
           - Tailored technical questions based on their experience
           - Behavioral questions relevant to the role
           - Scenario-based problem-solving challenges
        
        2. Create interviewer guide with:
           - Candidate highlights to explore
           - Red flags to watch for
           - Evaluation rubric
           - Follow-up question suggestions
        
        3. Prepare candidate-specific materials:
           - Company information packet
           - Role expectations document
           - Interview agenda and logistics
        
        4. Generate post-interview follow-up templates
        """
        
        return await self.execute_with_planning(
            task=task,
            context={
                "candidate": candidate_data,
                "requirements": job_requirements,
                "interview_type": interview_type
            },
            end_user=recruiter_id
        )
    
    async def follow_up_interview(self, interview_id: str, feedback_data: Dict[str, Any], recruiter_id: str) -> Dict[str, Any]:
        """Handle post-interview follow-up and next steps"""
        task = f"""
        Manage post-interview follow-up:
        
        Interview ID: {interview_id}
        Feedback: {feedback_data}
        
        1. Use Gmail tool to:
           - Send thank you note to candidate
           - Collect feedback from all interviewers
           - Notify relevant stakeholders of outcomes
        
        2. Use Calendar tool to:
           - Schedule next round if proceeding
           - Block time for decision making
           - Set follow-up reminders
        
        3. Generate next steps based on feedback:
           - Proceed to next round
           - Request additional information
           - Provide constructive feedback if not proceeding
        
        4. Update candidate tracking systems
        """
        
        return await self.execute_with_planning(
            task=task,
            context={"interview_id": interview_id, "feedback": feedback_data},
            end_user=recruiter_id
        )
