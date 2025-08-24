# Recruiter API Router
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from app.database import get_db
from app.models import User, JobPosting, Interview, Candidate
from app.schemas import JobPostingCreate, JobPostingResponse, InterviewCreate
from app.services.auth import get_current_active_user

logger = logging.getLogger(__name__)
router = APIRouter()

def verify_recruiter(current_user: User):
    """Verify user is a recruiter."""
    if current_user.user_type != "recruiter":
        raise HTTPException(status_code=403, detail="Recruiter access required")
    return current_user

@router.post("/jobs", response_model=JobPostingResponse)
async def create_job_posting(
    job_data: JobPostingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new job posting."""
    try:
        verify_recruiter(current_user)
        db_job = JobPosting(
            recruiter_id=current_user.id,
            title=job_data.title,
            company=job_data.company,
            description=job_data.description,
            requirements=job_data.requirements,
            salary_range=job_data.salary_range,
            location=job_data.location,
            remote_ok=job_data.remote_ok,
            employment_type=job_data.employment_type,
            experience_level=job_data.experience_level,
            department=job_data.department,
            is_active=True
        )
        
        db.add(db_job)
        db.commit()
        db.refresh(db_job)
        
        logger.info(f"Created job posting: {job_data.title} at {job_data.company}")
        return db_job
        
    except Exception as e:
        logger.error(f"Failed to create job posting: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create job posting")

@router.get("/jobs", response_model=List[JobPostingResponse])
async def get_job_postings(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get recruiter's job postings."""
    try:
        verify_recruiter(current_user)
        query = db.query(JobPosting).filter(JobPosting.recruiter_id == current_user.id)
        
        if active_only:
            query = query.filter(JobPosting.is_active == True)
        
        jobs = query.order_by(JobPosting.created_at.desc()).offset(skip).limit(limit).all()
        
        logger.info(f"Retrieved {len(jobs)} job postings for recruiter {current_user.id}")
        return jobs
        
    except Exception as e:
        logger.error(f"Failed to get job postings: {e}")
        raise HTTPException(status_code=500, detail="Failed to get job postings")

@router.put("/jobs/{job_id}")
async def update_job_posting(
    job_id: int,
    updates: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a job posting."""
    try:
        verify_recruiter(current_user)
        job = db.query(JobPosting).filter(
            JobPosting.id == job_id,
            JobPosting.recruiter_id == current_user.id
        ).first()
        
        if not job:
            raise HTTPException(status_code=404, detail="Job posting not found")
        
        # Update fields
        for field, value in updates.items():
            if hasattr(job, field):
                setattr(job, field, value)
        
        job.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(job)
        
        logger.info(f"Updated job posting {job_id}")
        return job
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update job posting: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update job posting")

@router.post("/rank-candidates/{job_id}")
async def rank_candidates(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Rank candidates for a specific job posting using AI."""
    try:
        verify_recruiter(current_user)
        # Verify job belongs to recruiter
        job = db.query(JobPosting).filter(
            JobPosting.id == job_id,
            JobPosting.recruiter_id == current_user.id
        ).first()
        
        if not job:
            raise HTTPException(status_code=404, detail="Job posting not found")
        
        # Get all candidates (in real app, would filter by applications or search criteria)
        candidates = db.query(Candidate).limit(20).all()  # Limit for demo
        
        # Mock AI ranking algorithm
        ranked_candidates = []
        for candidate in candidates:
            # Calculate match score based on various factors
            match_score = calculate_candidate_match_score(candidate, job)
            
            candidate_data = {
                "candidate_id": candidate.id,
                "user_id": candidate.user_id,
                "match_score": match_score,
                "skills": candidate.skills or [],
                "experience_years": candidate.experience_years,
                "github_url": candidate.github_url,
                "linkedin_url": candidate.linkedin_url,
                "resume_url": candidate.resume_url,
                "match_reasons": generate_match_reasons(candidate, job, match_score),
                "red_flags": generate_red_flags(candidate, job),
                "interview_recommendation": "recommend" if match_score > 70 else "maybe" if match_score > 50 else "skip"
            }
            
            ranked_candidates.append(candidate_data)
        
        # Sort by match score
        ranked_candidates.sort(key=lambda x: x["match_score"], reverse=True)
        
        logger.info(f"Ranked {len(ranked_candidates)} candidates for job {job_id}")
        
        return {
            "job_id": job_id,
            "job_title": job.title,
            "total_candidates": len(ranked_candidates),
            "recommended_candidates": len([c for c in ranked_candidates if c["match_score"] > 70]),
            "ranked_candidates": ranked_candidates[:10],  # Top 10
            "ranking_criteria": [
                "Skills alignment with job requirements",
                "Years of relevant experience",
                "GitHub activity and code quality",
                "LinkedIn profile completeness",
                "Previous work experience relevance"
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to rank candidates: {e}")
        raise HTTPException(status_code=500, detail="Failed to rank candidates")

@router.post("/schedule-interview")
async def schedule_interview(
    interview_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Schedule an interview with a candidate."""
    try:
        verify_recruiter(current_user)
        job_posting_id = interview_data.get("job_posting_id")
        candidate_id = interview_data.get("candidate_id")
        scheduled_time = interview_data.get("scheduled_time")
        
        if not all([job_posting_id, candidate_id, scheduled_time]):
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        # Verify job belongs to recruiter
        job = db.query(JobPosting).filter(
            JobPosting.id == job_posting_id,
            JobPosting.recruiter_id == current_user.id
        ).first()
        
        if not job:
            raise HTTPException(status_code=404, detail="Job posting not found")
        
        # Verify candidate exists
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        # Create interview
        interview = Interview(
            job_posting_id=job_posting_id,
            candidate_id=candidate_id,
            scheduled_time=datetime.fromisoformat(scheduled_time.replace('Z', '+00:00')),
            interview_type=interview_data.get("interview_type", "technical"),
            duration_minutes=interview_data.get("duration_minutes", 60),
            meeting_link=interview_data.get("meeting_link"),
            notes=interview_data.get("notes", ""),
            status="scheduled"
        )
        
        db.add(interview)
        db.commit()
        db.refresh(interview)
        
        logger.info(f"Scheduled interview for candidate {candidate_id} and job {job_posting_id}")
        
        return {
            "message": "Interview scheduled successfully",
            "interview_id": interview.id,
            "job_title": job.title,
            "candidate_id": candidate_id,
            "scheduled_time": interview.scheduled_time,
            "interview_type": interview.interview_type,
            "meeting_link": interview.meeting_link,
            "next_steps": [
                "Calendar invite will be sent to candidate",
                "Interview preparation materials will be shared",
                "Reminder notifications will be scheduled"
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to schedule interview: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to schedule interview")

@router.get("/interviews")
async def get_interviews(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status_filter: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get interviews for recruiter's job postings."""
    try:
        verify_recruiter(current_user)
        # Get interviews for jobs posted by this recruiter
        query = db.query(Interview).join(JobPosting).filter(
            JobPosting.recruiter_id == current_user.id
        )
        
        if status_filter:
            query = query.filter(Interview.status == status_filter)
        
        interviews = query.order_by(Interview.scheduled_time.desc()).offset(skip).limit(limit).all()
        
        # Format response
        interview_list = []
        for interview in interviews:
            interview_data = {
                "id": interview.id,
                "job_posting_id": interview.job_posting_id,
                "candidate_id": interview.candidate_id,
                "scheduled_time": interview.scheduled_time,
                "interview_type": interview.interview_type,
                "duration_minutes": interview.duration_minutes,
                "status": interview.status,
                "meeting_link": interview.meeting_link,
                "notes": interview.notes,
                "job_title": interview.job_posting.title if interview.job_posting else None,
                "candidate_name": None  # Would get from candidate profile
            }
            interview_list.append(interview_data)
        
        return {
            "interviews": interview_list,
            "total_count": query.count()
        }
        
    except Exception as e:
        logger.error(f"Failed to get interviews: {e}")
        raise HTTPException(status_code=500, detail="Failed to get interviews")

def calculate_candidate_match_score(candidate: Candidate, job: JobPosting) -> int:
    """Calculate how well a candidate matches a job posting."""
    score = 0
    
    # Skills matching (40% of score)
    candidate_skills = set(skill.lower() for skill in (candidate.skills or []))
    job_requirements = set(req.lower() for req in (job.requirements or []))
    
    if candidate_skills and job_requirements:
        skill_overlap = len(candidate_skills.intersection(job_requirements))
        skill_score = min((skill_overlap / len(job_requirements)) * 40, 40)
        score += skill_score
    
    # Experience (30% of score)
    exp_score = min(candidate.experience_years * 6, 30)  # Max 30 points for 5+ years
    score += exp_score
    
    # Profile completeness (20% of score)
    profile_items = [
        candidate.github_url,
        candidate.linkedin_url,
        candidate.resume_url,
        candidate.career_goals
    ]
    completeness = sum(1 for item in profile_items if item) / len(profile_items)
    score += completeness * 20
    
    # Location match (10% of score)
    if job.remote_ok:
        score += 10
    
    return min(int(score), 100)

def generate_match_reasons(candidate: Candidate, job: JobPosting, score: int) -> List[str]:
    """Generate reasons why candidate matches the job."""
    reasons = []
    
    if score > 80:
        reasons.append("Excellent skills alignment with job requirements")
    elif score > 60:
        reasons.append("Good skills match with most requirements")
    
    if candidate.experience_years >= 3:
        reasons.append(f"{candidate.experience_years} years of relevant experience")
    
    if candidate.github_url:
        reasons.append("Active GitHub profile with code samples")
    
    if candidate.linkedin_url:
        reasons.append("Complete LinkedIn professional profile")
    
    if job.remote_ok:
        reasons.append("Open to remote work opportunities")
    
    return reasons

def generate_red_flags(candidate: Candidate, job: JobPosting) -> List[str]:
    """Generate potential red flags for the candidate."""
    red_flags = []
    
    if not candidate.resume_url:
        red_flags.append("No resume uploaded")
    
    if not candidate.skills:
        red_flags.append("No skills listed in profile")
    
    if candidate.experience_years == 0:
        red_flags.append("No professional experience listed")
    
    if not candidate.github_url and "developer" in job.title.lower():
        red_flags.append("No GitHub profile for technical role")
    
    return red_flags
