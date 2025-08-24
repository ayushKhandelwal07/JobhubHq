# Auto Application API Router
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import logging
from datetime import datetime

from app.database import get_db
from app.models import User, JobApplication
from app.services.auth import get_current_active_user

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory storage for auto-apply sessions (in production, use Redis or database)
auto_apply_sessions = {}

@router.post("/start")
async def start_auto_application(
    preferences: Dict[str, Any],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Start automated job application process."""
    try:
        # Validate preferences
        required_fields = ["keywords", "locations"]
        for field in required_fields:
            if field not in preferences:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Create auto-apply session
        session_id = f"user_{current_user.id}_{int(datetime.utcnow().timestamp())}"
        
        session_data = {
            "user_id": current_user.id,
            "status": "active",
            "preferences": preferences,
            "started_at": datetime.utcnow(),
            "applications_submitted": 0,
            "daily_limit": preferences.get("max_applications_per_day", 10),
            "target_keywords": preferences.get("keywords", []),
            "target_locations": preferences.get("locations", []),
            "companies_blacklist": preferences.get("companies_blacklist", []),
            "companies_whitelist": preferences.get("companies_whitelist", []),
            "salary_min": preferences.get("salary_min", 0),
            "remote_only": preferences.get("remote_only", False),
            "cover_letter_template": preferences.get("cover_letter_template", "")
        }
        
        auto_apply_sessions[session_id] = session_data
        
        # Start background task for auto-application
        background_tasks.add_task(process_auto_applications, session_id, db)
        
        logger.info(f"Started auto-application for user {current_user.id}")
        
        return {
            "message": "Auto-application process started successfully",
            "session_id": session_id,
            "preferences": preferences,
            "estimated_applications_per_day": min(preferences.get("max_applications_per_day", 10), 25),
            "next_steps": [
                "AI will search for matching jobs",
                "Applications will be submitted with your preferences",
                "You'll receive notifications for each application",
                "Progress can be monitored in real-time"
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start auto-application: {e}")
        raise HTTPException(status_code=500, detail="Failed to start auto-application")

@router.post("/stop")
async def stop_auto_application(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Stop the automated job application process."""
    try:
        # Find active session for user
        user_sessions = [
            (session_id, session) for session_id, session in auto_apply_sessions.items()
            if session["user_id"] == current_user.id and session["status"] == "active"
        ]
        
        if not user_sessions:
            raise HTTPException(status_code=404, detail="No active auto-application session found")
        
        # Stop all active sessions for user
        stopped_sessions = []
        for session_id, session in user_sessions:
            session["status"] = "stopped"
            session["stopped_at"] = datetime.utcnow()
            stopped_sessions.append(session_id)
        
        logger.info(f"Stopped auto-application sessions for user {current_user.id}")
        
        return {
            "message": "Auto-application process stopped successfully",
            "stopped_sessions": len(stopped_sessions),
            "applications_submitted": sum(session["applications_submitted"] for _, session in user_sessions)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to stop auto-application: {e}")
        raise HTTPException(status_code=500, detail="Failed to stop auto-application")

@router.get("/status")
async def get_auto_application_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get status of auto-application process."""
    try:
        # Find sessions for user
        user_sessions = [
            session for session in auto_apply_sessions.values()
            if session["user_id"] == current_user.id
        ]
        
        if not user_sessions:
            return {
                "status": "inactive",
                "message": "No auto-application sessions found",
                "total_applications": 0
            }
        
        # Get most recent session
        latest_session = max(user_sessions, key=lambda x: x["started_at"])
        
        return {
            "status": latest_session["status"],
            "started_at": latest_session["started_at"],
            "applications_submitted": latest_session["applications_submitted"],
            "daily_limit": latest_session["daily_limit"],
            "preferences": latest_session["preferences"],
            "session_summary": {
                "target_keywords": latest_session["target_keywords"],
                "target_locations": latest_session["target_locations"],
                "remote_only": latest_session["remote_only"],
                "salary_min": latest_session["salary_min"]
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get auto-application status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get auto-application status")

@router.get("/history")
async def get_auto_application_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get history of auto-application sessions."""
    try:
        user_sessions = [
            {
                "session_id": session_id,
                "started_at": session["started_at"],
                "status": session["status"],
                "applications_submitted": session["applications_submitted"],
                "preferences": session["preferences"]
            }
            for session_id, session in auto_apply_sessions.items()
            if session["user_id"] == current_user.id
        ]
        
        # Sort by start time, most recent first
        user_sessions.sort(key=lambda x: x["started_at"], reverse=True)
        
        return {
            "sessions": user_sessions,
            "total_sessions": len(user_sessions),
            "total_applications": sum(session["applications_submitted"] for session in user_sessions)
        }
        
    except Exception as e:
        logger.error(f"Failed to get auto-application history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get auto-application history")

async def process_auto_applications(session_id: str, db: Session):
    """Background task to process auto-applications."""
    try:
        session = auto_apply_sessions.get(session_id)
        if not session or session["status"] != "active":
            return
        
        logger.info(f"Processing auto-applications for session {session_id}")
        
        # Mock auto-application logic
        # In a real implementation, this would:
        # 1. Search job boards for matching positions
        # 2. Filter based on preferences
        # 3. Apply to jobs automatically
        # 4. Track applications in database
        
        # Simulate finding and applying to jobs
        keywords = session["target_keywords"]
        locations = session["target_locations"]
        
        mock_applications = [
            {
                "job_title": f"Senior {keywords[0]} Developer",
                "company": "TechCorp Inc",
                "location": locations[0] if locations else "Remote",
                "salary_range": "$120k-$160k",
                "source": "auto_applied",
                "job_url": "https://example.com/job/1",
                "status": "applied"
            },
            {
                "job_title": f"{keywords[0]} Engineer",
                "company": "StartupXYZ",
                "location": locations[0] if locations else "Remote",
                "salary_range": "$100k-$140k",
                "source": "auto_applied",
                "job_url": "https://example.com/job/2",
                "status": "applied"
            }
        ]
        
        # Create applications in database
        applications_created = 0
        for app_data in mock_applications:
            if session["applications_submitted"] >= session["daily_limit"]:
                break
                
            # Create job application
            db_application = JobApplication(
                user_id=session["user_id"],
                job_title=app_data["job_title"],
                company=app_data["company"],
                location=app_data["location"],
                salary_range=app_data["salary_range"],
                source=app_data["source"],
                job_url=app_data["job_url"],
                status=app_data["status"],
                applied_date=datetime.utcnow(),
                notes=f"Auto-applied via AI system. Session: {session_id}"
            )
            
            db.add(db_application)
            applications_created += 1
            session["applications_submitted"] += 1
        
        db.commit()
        
        logger.info(f"Auto-applied to {applications_created} jobs for session {session_id}")
        
        # Mark session as completed if daily limit reached
        if session["applications_submitted"] >= session["daily_limit"]:
            session["status"] = "completed"
            session["completed_at"] = datetime.utcnow()
        
    except Exception as e:
        logger.error(f"Auto-application processing failed for session {session_id}: {e}")
        if session_id in auto_apply_sessions:
            auto_apply_sessions[session_id]["status"] = "error"
            auto_apply_sessions[session_id]["error"] = str(e)
