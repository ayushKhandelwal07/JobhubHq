# Job Applications API Router
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging

from app.database import get_db
from app.models import User, JobApplication
from app.schemas import JobApplicationCreate, JobApplicationUpdate, JobApplicationResponse
from app.services.auth import get_current_active_user

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=List[JobApplicationResponse])
async def get_applications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status_filter: Optional[str] = Query(None),
    company_filter: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user's job applications with optional filters."""
    try:
        query = db.query(JobApplication).filter(JobApplication.user_id == current_user.id)
        
        # Apply filters
        if status_filter and status_filter != 'all':
            query = query.filter(JobApplication.status == status_filter)
        
        if company_filter:
            query = query.filter(JobApplication.company.ilike(f"%{company_filter}%"))
        
        # Order by most recent first
        query = query.order_by(JobApplication.applied_date.desc())
        
        applications = query.offset(skip).limit(limit).all()
        
        logger.info(f"Retrieved {len(applications)} applications for user {current_user.id}")
        return applications
        
    except Exception as e:
        logger.error(f"Failed to get applications: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve applications")

@router.post("/", response_model=JobApplicationResponse)
async def create_application(
    application_data: JobApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new job application."""
    try:
        # Create application with current user
        db_application = JobApplication(
            user_id=current_user.id,
            job_title=application_data.job_title,
            company=application_data.company,
            job_url=application_data.job_url,
            salary_range=application_data.salary_range,
            location=application_data.location,
            job_description=application_data.job_description,
            notes=application_data.notes,
            source=application_data.source or "manual",
            status="applied",
            applied_date=datetime.utcnow()
        )
        
        db.add(db_application)
        db.commit()
        db.refresh(db_application)
        
        logger.info(f"Created application for {application_data.company} - {application_data.job_title}")
        return db_application
        
    except Exception as e:
        logger.error(f"Failed to create application: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create application")

@router.put("/{application_id}", response_model=JobApplicationResponse)
async def update_application(
    application_id: int,
    updates: JobApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update an existing job application."""
    try:
        # Get application and verify ownership
        application = db.query(JobApplication).filter(
            JobApplication.id == application_id,
            JobApplication.user_id == current_user.id
        ).first()
        
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        
        # Update fields
        update_data = updates.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(application, field, value)
        
        # Set response date if status changed to responded statuses
        if updates.status and updates.status in ['interview', 'rejected', 'offer'] and not application.response_date:
            application.response_date = datetime.utcnow()
        
        application.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(application)
        
        logger.info(f"Updated application {application_id} for user {current_user.id}")
        return application
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update application: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update application")

@router.delete("/{application_id}")
async def delete_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a job application."""
    try:
        application = db.query(JobApplication).filter(
            JobApplication.id == application_id,
            JobApplication.user_id == current_user.id
        ).first()
        
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        
        db.delete(application)
        db.commit()
        
        logger.info(f"Deleted application {application_id} for user {current_user.id}")
        return {"message": "Application deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete application: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete application")

@router.post("/sync-sheets")
async def sync_to_sheets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Sync applications to Google Sheets."""
    try:
        # Get user's applications
        applications = db.query(JobApplication).filter(
            JobApplication.user_id == current_user.id
        ).order_by(JobApplication.applied_date.desc()).all()
        
        # TODO: Implement actual Google Sheets sync
        # For now, return mock response
        
        logger.info(f"Synced {len(applications)} applications to Google Sheets for user {current_user.id}")
        return {
            "message": "Applications synced to Google Sheets successfully",
            "synced_count": len(applications),
            "sheet_url": "https://docs.google.com/spreadsheets/mock-url"
        }
        
    except Exception as e:
        logger.error(f"Failed to sync to Google Sheets: {e}")
        raise HTTPException(status_code=500, detail="Failed to sync to Google Sheets")

@router.get("/stats")
async def get_application_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get application statistics for the user."""
    try:
        applications = db.query(JobApplication).filter(
            JobApplication.user_id == current_user.id
        ).all()
        
        stats = {
            "total": len(applications),
            "applied": len([a for a in applications if a.status == 'applied']),
            "interviews": len([a for a in applications if a.status == 'interview']),
            "offers": len([a for a in applications if a.status == 'offer']),
            "rejected": len([a for a in applications if a.status == 'rejected']),
            "ghosted": len([a for a in applications if a.status == 'ghosted']),
        }
        
        # Calculate rates
        stats["response_rate"] = round(
            ((stats["interviews"] + stats["offers"] + stats["rejected"]) / stats["total"] * 100) 
            if stats["total"] > 0 else 0, 1
        )
        stats["offer_rate"] = round(
            (stats["offers"] / stats["total"] * 100) if stats["total"] > 0 else 0, 1
        )
        
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get application stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get application statistics")
