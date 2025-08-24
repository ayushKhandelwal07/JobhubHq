# Job Search API Router
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import logging

from app.database import get_db
from app.models import User
from app.services.auth import get_current_active_user

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/search")
async def search_jobs(
    search_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Search for jobs based on criteria."""
    try:
        keywords = search_data.get("keywords", "")
        location = search_data.get("location", "")
        company = search_data.get("company", "")
        salary_min = search_data.get("salary_min", 0)
        remote_only = search_data.get("remote_only", False)
        
        # Mock job search results for now
        # In a real implementation, this would integrate with job boards APIs
        mock_jobs = [
            {
                "id": 1,
                "title": f"Senior {keywords} Developer",
                "company": "TechCorp Inc",
                "location": location or "San Francisco, CA",
                "salary_range": f"${salary_min + 20000}-${salary_min + 40000}",
                "description": f"We are looking for a skilled {keywords} developer...",
                "url": "https://example.com/job/1",
                "posted_date": "2025-01-24",
                "remote_ok": True,
                "employment_type": "full-time"
            },
            {
                "id": 2,
                "title": f"{keywords} Engineer",
                "company": "StartupXYZ",
                "location": location or "New York, NY",
                "salary_range": f"${salary_min + 10000}-${salary_min + 30000}",
                "description": f"Join our team as a {keywords} engineer...",
                "url": "https://example.com/job/2",
                "posted_date": "2025-01-23",
                "remote_ok": remote_only,
                "employment_type": "full-time"
            },
            {
                "id": 3,
                "title": f"Lead {keywords} Developer",
                "company": company or "MegaCorp",
                "location": "Remote",
                "salary_range": f"${salary_min + 30000}-${salary_min + 60000}",
                "description": f"Lead our {keywords} development team...",
                "url": "https://example.com/job/3",
                "posted_date": "2025-01-22",
                "remote_ok": True,
                "employment_type": "full-time"
            }
        ]
        
        # Filter based on criteria
        filtered_jobs = []
        for job in mock_jobs:
            if remote_only and not job["remote_ok"]:
                continue
            if company and company.lower() not in job["company"].lower():
                continue
            filtered_jobs.append(job)
        
        logger.info(f"Found {len(filtered_jobs)} jobs for search: {keywords}")
        
        return {
            "jobs": filtered_jobs,
            "total_count": len(filtered_jobs),
            "search_criteria": search_data
        }
        
    except Exception as e:
        logger.error(f"Job search failed: {e}")
        raise HTTPException(status_code=500, detail="Job search failed")

@router.get("/trending")
async def get_trending_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get trending job categories and skills."""
    try:
        # Mock trending data
        trending_data = {
            "trending_roles": [
                {"role": "AI/ML Engineer", "growth": "+45%", "avg_salary": "$150k"},
                {"role": "Full Stack Developer", "growth": "+32%", "avg_salary": "$120k"},
                {"role": "DevOps Engineer", "growth": "+28%", "avg_salary": "$135k"},
                {"role": "Data Scientist", "growth": "+25%", "avg_salary": "$140k"},
                {"role": "Product Manager", "growth": "+22%", "avg_salary": "$160k"}
            ],
            "trending_skills": [
                {"skill": "Python", "demand": "Very High", "jobs_count": 15420},
                {"skill": "React", "demand": "Very High", "jobs_count": 12890},
                {"skill": "AWS", "demand": "High", "jobs_count": 11340},
                {"skill": "Docker", "demand": "High", "jobs_count": 9870},
                {"skill": "TypeScript", "demand": "High", "jobs_count": 8760}
            ],
            "hot_companies": [
                {"company": "OpenAI", "hiring_growth": "+150%"},
                {"company": "Anthropic", "hiring_growth": "+120%"},
                {"company": "Stripe", "hiring_growth": "+85%"},
                {"company": "Vercel", "hiring_growth": "+70%"},
                {"company": "Linear", "hiring_growth": "+65%"}
            ]
        }
        
        return trending_data
        
    except Exception as e:
        logger.error(f"Failed to get trending jobs: {e}")
        raise HTTPException(status_code=500, detail="Failed to get trending jobs")

@router.get("/recommendations")
async def get_job_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get personalized job recommendations based on user profile."""
    try:
        # Get user's candidate profile if available
        candidate = getattr(current_user, 'candidate_profile', None)
        
        # Mock recommendations based on user profile
        recommendations = [
            {
                "id": 101,
                "title": "Senior Software Engineer",
                "company": "Tech Innovators Inc",
                "location": "San Francisco, CA",
                "salary_range": "$130k-$180k",
                "match_score": 95,
                "match_reasons": [
                    "Skills match: Python, React, AWS",
                    "Experience level: Senior (5+ years)",
                    "Location preference: Bay Area"
                ],
                "url": "https://example.com/recommended/1",
                "remote_ok": True
            },
            {
                "id": 102,
                "title": "Full Stack Developer",
                "company": "Growth Startup",
                "location": "Remote",
                "salary_range": "$110k-$150k",
                "match_score": 87,
                "match_reasons": [
                    "Remote work preference",
                    "Full stack experience",
                    "Startup environment fit"
                ],
                "url": "https://example.com/recommended/2",
                "remote_ok": True
            }
        ]
        
        return {
            "recommendations": recommendations,
            "total_count": len(recommendations),
            "last_updated": "2025-01-24T10:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"Failed to get job recommendations: {e}")
        raise HTTPException(status_code=500, detail="Failed to get job recommendations")
