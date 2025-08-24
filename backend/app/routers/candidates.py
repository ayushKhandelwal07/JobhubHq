# Candidates Profile API Router
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import logging

from app.database import get_db
from app.models import User, Candidate
from app.schemas import CandidateResponse, CandidateUpdate
from app.services.auth import get_current_active_user

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/profile", response_model=Optional[CandidateResponse])
async def get_candidate_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get the current user's candidate profile."""
    try:
        if current_user.user_type != "candidate":
            raise HTTPException(status_code=403, detail="Only candidates can access profile")
        
        candidate = db.query(Candidate).filter(Candidate.user_id == current_user.id).first()
        
        if not candidate:
            # Create empty candidate profile if it doesn't exist
            candidate = Candidate(user_id=current_user.id)
            db.add(candidate)
            db.commit()
            db.refresh(candidate)
        
        logger.info(f"Retrieved candidate profile for user {current_user.id}")
        return candidate
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get candidate profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to get candidate profile")

@router.put("/profile", response_model=CandidateResponse)
async def update_candidate_profile(
    profile_data: CandidateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update the current user's candidate profile."""
    try:
        if current_user.user_type != "candidate":
            raise HTTPException(status_code=403, detail="Only candidates can update profile")
        
        candidate = db.query(Candidate).filter(Candidate.user_id == current_user.id).first()
        
        if not candidate:
            # Create new candidate profile
            candidate = Candidate(user_id=current_user.id)
            db.add(candidate)
        
        # Update fields
        update_data = profile_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(candidate, field, value)
        
        db.commit()
        db.refresh(candidate)
        
        logger.info(f"Updated candidate profile for user {current_user.id}")
        return candidate
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update candidate profile: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update candidate profile")

@router.get("/profile/analysis")
async def get_profile_analysis(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get AI-powered analysis of candidate profile."""
    try:
        if current_user.user_type != "candidate":
            raise HTTPException(status_code=403, detail="Only candidates can get profile analysis")
        
        candidate = db.query(Candidate).filter(Candidate.user_id == current_user.id).first()
        
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate profile not found")
        
        # Mock AI analysis
        analysis = {
            "profile_completeness": 75,
            "strengths": [
                "Strong technical skills in Python and JavaScript",
                "Good GitHub activity with diverse projects",
                "Relevant work experience in target role"
            ],
            "improvement_areas": [
                "Add more details to LinkedIn profile",
                "Include more specific achievements in resume",
                "Consider adding certifications"
            ],
            "skill_gaps": [
                {"skill": "Docker", "priority": "High", "reason": "Required by 80% of target jobs"},
                {"skill": "AWS", "priority": "Medium", "reason": "Cloud skills in high demand"}
            ],
            "market_position": {
                "percentile": 78,
                "comparable_profiles": 1250,
                "estimated_salary_range": "$95k - $140k"
            },
            "recommendations": [
                "Complete Docker certification to fill skill gap",
                "Update LinkedIn with recent projects",
                "Add quantifiable achievements to resume"
            ]
        }
        
        return analysis
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get profile analysis: {e}")
        raise HTTPException(status_code=500, detail="Failed to get profile analysis")

@router.post("/profile/optimize")
async def optimize_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get AI-powered profile optimization suggestions."""
    try:
        if current_user.user_type != "candidate":
            raise HTTPException(status_code=403, detail="Only candidates can optimize profile")
        
        candidate = db.query(Candidate).filter(Candidate.user_id == current_user.id).first()
        
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate profile not found")
        
        # Mock optimization suggestions
        optimization = {
            "linkedin_optimization": {
                "headline_suggestions": [
                    "Senior Software Engineer | Python & React Specialist | Building Scalable Web Applications",
                    "Full Stack Developer | 5+ Years Experience | Passionate About Clean Code & User Experience"
                ],
                "summary_improvements": [
                    "Add specific metrics and achievements",
                    "Include relevant keywords for ATS optimization",
                    "Highlight unique value proposition"
                ]
            },
            "resume_optimization": {
                "keyword_suggestions": [
                    "Add: microservices, containerization, CI/CD",
                    "Emphasize: scalability, performance optimization",
                    "Include: cloud platforms, database design"
                ],
                "format_improvements": [
                    "Use action verbs to start bullet points",
                    "Quantify achievements with numbers",
                    "Tailor content for target role"
                ]
            },
            "github_optimization": {
                "repository_suggestions": [
                    "Pin your best repositories",
                    "Add comprehensive README files",
                    "Include live demo links"
                ],
                "contribution_tips": [
                    "Maintain consistent commit activity",
                    "Contribute to open source projects",
                    "Document your code thoroughly"
                ]
            }
        }
        
        return optimization
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to optimize profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to optimize profile")
