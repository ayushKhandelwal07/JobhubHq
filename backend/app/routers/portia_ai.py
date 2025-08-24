# Portia AI-Powered API Endpoints
# Maximum Portia integration with planning, tools, and human-in-the-loop workflows

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from app.database import get_db
from app.models import User, JobApplication, JobPosting
from app.schemas import *
from app.services.auth import get_current_active_user
from app.agents import get_agent_info, PORTIA_AGENTS
from app.portia_client import portia_client

logger = logging.getLogger(__name__)
router = APIRouter()

# ============================================================================
# JOB APPLICATION TRACKING WITH PORTIA
# ============================================================================

@router.post("/track-applications", response_model=Dict[str, Any])
async def track_job_applications(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Track job applications using Portia Gmail and Google Sheets tools
    Implements human-in-the-loop workflow for verification
    """
    try:
        agent = get_agent("job_tracker")
        if not agent:
            raise HTTPException(status_code=500, detail="Job tracker agent not available")
        
        # Execute with Portia planning and tools
        result = await agent.track_applications(
            user_email=current_user.email,
            user_id=str(current_user.id)
        )
        
        return {
            "message": "Job application tracking initiated with Portia AI",
            "agent_result": result,
            "portia_features_used": [
                "Gmail tool for email scanning",
                "Google Sheets tool for data sync", 
                "Human-in-the-loop verification",
                "Structured planning workflow"
            ]
        }
        
    except Exception as e:
        logger.error(f"Job tracking failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sync-chrome-extension", response_model=Dict[str, Any])
async def sync_chrome_extension_data(
    job_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Process Chrome extension job data with Portia validation and deduplication
    """
    try:
        agent = get_agent("job_tracker")
        if not agent:
            raise HTTPException(status_code=500, detail="Job tracker agent not available")
        
        result = await agent.sync_chrome_extension_data(
            job_data=job_data,
            user_id=str(current_user.id)
        )
        
        return {
            "message": "Chrome extension data processed with Portia AI",
            "agent_result": result,
            "portia_features_used": [
                "Data validation and cleaning",
                "Duplicate detection",
                "Google Sheets integration",
                "Gmail correlation"
            ]
        }
        
    except Exception as e:
        logger.error(f"Chrome extension sync failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# AUTOMATED JOB APPLICATION WITH PORTIA
# ============================================================================

@router.post("/auto-apply", response_model=Dict[str, Any])
async def start_auto_job_application(
    job_preferences: Dict[str, Any],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Start automated job application process with Portia browser automation
    Includes human approval workflow for each application
    """
    try:
        agent = get_agent("job_application")
        if not agent:
            raise HTTPException(status_code=500, detail="Job application agent not available")
        
        user_profile = {
            "name": current_user.full_name,
            "email": current_user.email,
            "skills": getattr(current_user, 'skills', []),
            "experience": getattr(current_user, 'experience', {}),
            "resume": getattr(current_user, 'resume_url', '')
        }
        
        # Execute auto-application with human oversight
        result = await agent.auto_apply_to_jobs(
            user_profile=user_profile,
            job_preferences=job_preferences,
            user_id=str(current_user.id)
        )
        
        return {
            "message": "Auto job application started with Portia AI",
            "agent_result": result,
            "portia_features_used": [
                "Browser automation for job sites",
                "Human-in-the-loop approval workflow",
                "Gmail tool for follow-up emails",
                "LinkedIn tool for networking",
                "Personalized cover letter generation"
            ]
        }
        
    except Exception as e:
        logger.error(f"Auto job application failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/recruiter-outreach", response_model=Dict[str, Any])
async def send_recruiter_outreach(
    company: str,
    position: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Send personalized recruiter outreach using Portia LinkedIn and Gmail tools
    """
    try:
        agent = get_agent("job_application")
        if not agent:
            raise HTTPException(status_code=500, detail="Job application agent not available")
        
        user_profile = {
            "name": current_user.full_name,
            "email": current_user.email,
            "linkedin": getattr(current_user, 'linkedin_url', ''),
            "experience": getattr(current_user, 'experience', {}),
            "skills": getattr(current_user, 'skills', [])
        }
        
        result = await agent.send_recruiter_outreach(
            company=company,
            position=position,
            user_profile=user_profile,
            user_id=str(current_user.id)
        )
        
        return {
            "message": f"Recruiter outreach initiated for {position} at {company}",
            "agent_result": result,
            "portia_features_used": [
                "LinkedIn tool for recruiter research",
                "Personalized message generation",
                "Gmail tool for email outreach",
                "Human approval before sending"
            ]
        }
        
    except Exception as e:
        logger.error(f"Recruiter outreach failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# CAREER DEVELOPMENT WITH PORTIA
# ============================================================================

@router.post("/career-roadmap", response_model=Dict[str, Any])
async def create_career_roadmap(
    career_goal: str,
    timeline: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create personalized career roadmap using Portia GitHub and LinkedIn analysis
    """
    try:
        agent = get_agent("career_roadmap")
        if not agent:
            raise HTTPException(status_code=500, detail="Career roadmap agent not available")
        
        user_profile = {
            "name": current_user.full_name,
            "email": current_user.email,
            "github": getattr(current_user, 'github_username', ''),
            "linkedin": getattr(current_user, 'linkedin_url', ''),
            "current_role": getattr(current_user, 'current_role', ''),
            "skills": getattr(current_user, 'skills', []),
            "experience": getattr(current_user, 'experience', {})
        }
        
        result = await agent.create_career_roadmap(
            user_profile=user_profile,
            career_goal=career_goal,
            timeline=timeline,
            user_id=str(current_user.id)
        )
        
        return {
            "message": f"Career roadmap created for {career_goal}",
            "agent_result": result,
            "portia_features_used": [
                "GitHub tool for code analysis",
                "LinkedIn tool for market research",
                "Web research for industry trends",
                "Structured planning workflow"
            ]
        }
        
    except Exception as e:
        logger.error(f"Career roadmap creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/track-skill-progress", response_model=Dict[str, Any])
async def track_skill_progress(
    roadmap_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Track skill development progress using Portia GitHub and LinkedIn monitoring
    """
    try:
        agent = get_agent("career_roadmap")
        if not agent:
            raise HTTPException(status_code=500, detail="Career roadmap agent not available")
        
        result = await agent.track_skill_progress(
            user_github=getattr(current_user, 'github_username', ''),
            user_linkedin=getattr(current_user, 'linkedin_url', ''),
            roadmap_id=roadmap_id,
            user_id=str(current_user.id)
        )
        
        return {
            "message": "Skill progress tracking completed",
            "agent_result": result,
            "portia_features_used": [
                "GitHub tool for activity analysis",
                "LinkedIn tool for profile monitoring",
                "Progress comparison against milestones"
            ]
        }
        
    except Exception as e:
        logger.error(f"Skill progress tracking failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# PROFESSIONAL NETWORKING WITH PORTIA
# ============================================================================

@router.post("/expand-network", response_model=Dict[str, Any])
async def expand_professional_network(
    target_companies: List[str],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Expand professional network using Portia LinkedIn automation
    """
    try:
        agent = get_agent("networking")
        if not agent:
            raise HTTPException(status_code=500, detail="Networking agent not available")
        
        user_profile = {
            "name": current_user.full_name,
            "linkedin": getattr(current_user, 'linkedin_url', ''),
            "current_role": getattr(current_user, 'current_role', ''),
            "industry": getattr(current_user, 'industry', ''),
            "location": getattr(current_user, 'location', '')
        }
        
        result = await agent.expand_network(
            user_profile=user_profile,
            target_companies=target_companies,
            user_id=str(current_user.id)
        )
        
        return {
            "message": f"Network expansion initiated for {len(target_companies)} companies",
            "agent_result": result,
            "portia_features_used": [
                "LinkedIn tool for prospect research",
                "Personalized connection messages",
                "Human approval workflow",
                "Relationship tracking"
            ]
        }
        
    except Exception as e:
        logger.error(f"Network expansion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# RECRUITER FEATURES WITH PORTIA
# ============================================================================

@router.post("/analyze-candidate", response_model=Dict[str, Any])
async def analyze_candidate_with_portia(
    candidate_id: int,
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Comprehensive candidate analysis using Portia GitHub and LinkedIn tools
    Includes bias detection and human oversight
    """
    try:
        # Verify recruiter permissions
        if current_user.user_type != "recruiter":
            raise HTTPException(status_code=403, detail="Recruiter access required")
        
        candidate = db.query(User).filter(User.id == candidate_id).first()
        job = db.query(Job).filter(Job.id == job_id).first()
        
        if not candidate or not job:
            raise HTTPException(status_code=404, detail="Candidate or job not found")
        
        agent = get_agent("candidate_analysis")
        if not agent:
            raise HTTPException(status_code=500, detail="Candidate analysis agent not available")
        
        candidate_data = {
            "name": candidate.full_name,
            "email": candidate.email,
            "github": getattr(candidate, 'github_username', ''),
            "linkedin": getattr(candidate, 'linkedin_url', ''),
            "resume": getattr(candidate, 'resume_url', ''),
            "skills": getattr(candidate, 'skills', []),
            "experience": getattr(candidate, 'experience', {})
        }
        
        job_requirements = {
            "title": job.title,
            "description": job.description,
            "requirements": getattr(job, 'requirements', []),
            "company": job.company,
            "level": getattr(job, 'level', '')
        }
        
        result = await agent.analyze_candidate(
            candidate_data=candidate_data,
            job_requirements=job_requirements,
            recruiter_id=str(current_user.id)
        )
        
        return {
            "message": f"Candidate analysis completed for {candidate.full_name}",
            "agent_result": result,
            "portia_features_used": [
                "GitHub tool for technical assessment",
                "LinkedIn tool for experience evaluation",
                "Bias detection and mitigation",
                "Human review workflow",
                "Structured scoring criteria"
            ]
        }
        
    except Exception as e:
        logger.error(f"Candidate analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/schedule-interview", response_model=Dict[str, Any])
async def schedule_interview_with_portia(
    candidate_id: int,
    job_id: int,
    interviewer_emails: List[str],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Schedule interview using Portia Calendar and Gmail tools
    """
    try:
        if current_user.user_type != "recruiter":
            raise HTTPException(status_code=403, detail="Recruiter access required")
        
        candidate = db.query(User).filter(User.id == candidate_id).first()
        job = db.query(Job).filter(Job.id == job_id).first()
        
        if not candidate or not job:
            raise HTTPException(status_code=404, detail="Candidate or job not found")
        
        agent = get_agent("interview_coordination")
        if not agent:
            raise HTTPException(status_code=500, detail="Interview coordination agent not available")
        
        result = await agent.schedule_interview(
            candidate_email=candidate.email,
            interviewer_emails=interviewer_emails,
            job_title=job.title,
            recruiter_id=str(current_user.id)
        )
        
        return {
            "message": f"Interview scheduling initiated for {candidate.full_name}",
            "agent_result": result,
            "portia_features_used": [
                "Google Calendar tool for availability",
                "Gmail tool for notifications",
                "Automated interview preparation",
                "Human approval workflow"
            ]
        }
        
    except Exception as e:
        logger.error(f"Interview scheduling failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# MARKET INTELLIGENCE WITH PORTIA
# ============================================================================

@router.post("/market-analysis", response_model=Dict[str, Any])
async def analyze_job_market(
    role: str,
    location: str = "",
    company_size: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Comprehensive job market analysis using Portia web research tools
    """
    try:
        agent = get_agent("market_analytics")
        if not agent:
            raise HTTPException(status_code=500, detail="Market analytics agent not available")
        
        result = await agent.analyze_job_market(
            role=role,
            location=location,
            company_size=company_size,
            user_id=str(current_user.id)
        )
        
        return {
            "message": f"Market analysis completed for {role}",
            "agent_result": result,
            "portia_features_used": [
                "Web research tools for market data",
                "LinkedIn tool for professional insights",
                "Data analysis and trend identification",
                "Actionable recommendations"
            ]
        }
        
    except Exception as e:
        logger.error(f"Market analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# PORTIA SYSTEM STATUS AND DEBUGGING
# ============================================================================

@router.get("/portia-status", response_model=Dict[str, Any])
async def get_portia_status(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get Portia AI system status and available tools
    """
    try:
        if not portia_client:
            return {
                "status": "error",
                "message": "Portia client not initialized",
                "available_agents": 0,
                "available_tools": []
            }
        
        available_tools = portia_client.get_available_tools()
        
        return {
            "status": "active",
            "message": "Portia AI system operational",
            "available_agents": len(PORTIA_AGENTS),
            "agent_names": list(PORTIA_AGENTS.keys()),
            "available_tools": available_tools,
            "portia_features": [
                "Cloud storage for plans",
                "Human-in-the-loop workflows",
                "Multi-tool orchestration",
                "Browser automation",
                "Gmail integration",
                "LinkedIn automation",
                "GitHub analysis",
                "Google Calendar integration"
            ]
        }
        
    except Exception as e:
        logger.error(f"Portia status check failed: {e}")
        return {
            "status": "error",
            "message": str(e),
            "available_agents": 0,
            "available_tools": []
        }

@router.post("/test-portia-task", response_model=Dict[str, Any])
async def test_portia_task(
    task: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Test Portia AI with a custom task (for debugging and demonstration)
    """
    try:
        if not portia_client:
            raise HTTPException(status_code=500, detail="Portia client not available")
        
        # Execute simple task to test Portia integration
        result = portia_client.run_task(task, end_user=str(current_user.id))
        
        return {
            "message": "Portia task executed successfully",
            "task": task,
            "result": str(result),
            "portia_features_demonstrated": [
                "Task planning",
                "Tool orchestration", 
                "Human oversight",
                "Cloud storage"
            ]
        }
        
    except Exception as e:
        logger.error(f"Portia task test failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
