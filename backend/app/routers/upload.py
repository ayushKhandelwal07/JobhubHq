# File Upload API Router
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import logging
import os
import uuid
from datetime import datetime

from app.database import get_db
from app.models import User, Candidate
from app.services.auth import get_current_active_user
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

ALLOWED_EXTENSIONS = {'.pdf', '.doc', '.docx'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

@router.post("/resume")
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Upload user's resume."""
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file selected")
        
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # Check file size
        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large. Maximum size: 10MB")
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        filename = f"{file_id}_{current_user.id}{file_ext}"
        
        # Create upload directory if it doesn't exist
        upload_dir = getattr(settings, 'UPLOAD_DIR', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_dir, filename)
        with open(file_path, 'wb') as f:
            f.write(contents)
        
        # Update candidate profile
        candidate = db.query(Candidate).filter(Candidate.user_id == current_user.id).first()
        if not candidate:
            candidate = Candidate(user_id=current_user.id)
            db.add(candidate)
        
        candidate.resume_url = f"/uploads/{filename}"
        db.commit()
        
        logger.info(f"Resume uploaded successfully for user {current_user.id}")
        
        return {
            "message": "Resume uploaded successfully",
            "filename": file.filename,
            "file_url": candidate.resume_url,
            "file_size": len(contents),
            "upload_date": datetime.utcnow()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload resume: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload resume")

@router.delete("/resume")
async def delete_resume(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete user's resume."""
    try:
        candidate = db.query(Candidate).filter(Candidate.user_id == current_user.id).first()
        if not candidate or not candidate.resume_url:
            raise HTTPException(status_code=404, detail="No resume found")
        
        # Delete file from filesystem
        upload_dir = getattr(settings, 'UPLOAD_DIR', 'uploads')
        filename = candidate.resume_url.replace('/uploads/', '')
        file_path = os.path.join(upload_dir, filename)
        
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Remove from database
        candidate.resume_url = None
        db.commit()
        
        logger.info(f"Resume deleted for user {current_user.id}")
        
        return {"message": "Resume deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete resume: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete resume")
