# Admin API Router
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import Dict, Any
from datetime import datetime, timedelta
import logging

from app.database import get_db
from app.models import User, JobApplication, Candidate, CareerRoadmap, NetworkingContact
from app.services.auth import get_current_active_user

logger = logging.getLogger(__name__)
router = APIRouter()

def verify_admin(current_user: User):
    """Verify user has admin privileges."""
    if current_user.user_type != "admin" and current_user.email not in ["admin@portia.ai", "admin@example.com"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

@router.get("/stats")
async def get_admin_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get comprehensive admin statistics."""
    try:
        verify_admin(current_user)
        # User statistics
        total_users = db.query(User).count()
        candidates = db.query(User).filter(User.user_type == "candidate").count()
        recruiters = db.query(User).filter(User.user_type == "recruiter").count()
        
        # Recent user registrations (last 30 days)
        recent_date = datetime.utcnow() - timedelta(days=30)
        recent_users = db.query(User).filter(User.created_at >= recent_date).count()
        
        # Application statistics
        total_applications = db.query(JobApplication).count()
        recent_applications = db.query(JobApplication).filter(
            JobApplication.applied_date >= recent_date
        ).count()
        
        # Application status breakdown
        status_counts = db.query(
            JobApplication.status,
            func.count(JobApplication.id)
        ).group_by(JobApplication.status).all()
        
        status_breakdown = {status: count for status, count in status_counts}
        
        # Career roadmaps
        total_roadmaps = db.query(CareerRoadmap).count()
        
        # Networking contacts
        total_contacts = db.query(NetworkingContact).count()
        
        # Active users (users with applications in last 30 days)
        active_users = db.query(JobApplication.user_id).filter(
            JobApplication.applied_date >= recent_date
        ).distinct().count()
        
        # Monthly growth data
        monthly_data = []
        for i in range(6):  # Last 6 months
            month_start = datetime.utcnow().replace(day=1) - timedelta(days=30*i)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            month_users = db.query(User).filter(
                User.created_at >= month_start,
                User.created_at <= month_end
            ).count()
            
            month_apps = db.query(JobApplication).filter(
                JobApplication.applied_date >= month_start,
                JobApplication.applied_date <= month_end
            ).count()
            
            monthly_data.append({
                "month": month_start.strftime("%Y-%m"),
                "new_users": month_users,
                "applications": month_apps
            })
        
        monthly_data.reverse()  # Most recent first
        
        stats = {
            "user_metrics": {
                "total_users": total_users,
                "candidates": candidates,
                "recruiters": recruiters,
                "recent_signups": recent_users,
                "active_users": active_users,
                "user_activity_rate": round((active_users / total_users * 100) if total_users > 0 else 0, 1)
            },
            "application_metrics": {
                "total_applications": total_applications,
                "recent_applications": recent_applications,
                "avg_apps_per_user": round(total_applications / candidates if candidates > 0 else 0, 1),
                "status_breakdown": status_breakdown
            },
            "feature_usage": {
                "career_roadmaps": total_roadmaps,
                "networking_contacts": total_contacts,
                "roadmap_adoption": round((total_roadmaps / candidates * 100) if candidates > 0 else 0, 1),
                "networking_adoption": round((total_contacts / candidates * 100) if candidates > 0 else 0, 1)
            },
            "growth_data": {
                "monthly_trends": monthly_data,
                "user_growth_rate": calculate_growth_rate(monthly_data, "new_users"),
                "application_growth_rate": calculate_growth_rate(monthly_data, "applications")
            },
            "system_health": {
                "database_status": "healthy",
                "last_updated": datetime.utcnow(),
                "uptime_days": 30,  # Mock data
                "api_response_time": "125ms"  # Mock data
            }
        }
        
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get admin stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get admin statistics")

@router.get("/users")
async def get_user_list(
    skip: int = 0,
    limit: int = 100,
    user_type: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get list of users for admin management."""
    try:
        verify_admin(current_user)
        query = db.query(User)
        
        if user_type:
            query = query.filter(User.user_type == user_type)
        
        users = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()
        
        # Add additional info for each user
        user_list = []
        for user in users:
            user_data = {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "user_type": user.user_type,
                "is_active": user.is_active,
                "created_at": user.created_at,
                "last_login": None,  # Would track this in real app
                "application_count": 0,
                "profile_completeness": 0
            }
            
            # Get application count
            if user.user_type == "candidate":
                app_count = db.query(JobApplication).filter(JobApplication.user_id == user.id).count()
                user_data["application_count"] = app_count
                
                # Get profile completeness
                candidate = db.query(Candidate).filter(Candidate.user_id == user.id).first()
                if candidate:
                    completeness = calculate_profile_completeness(candidate)
                    user_data["profile_completeness"] = completeness
            
            user_list.append(user_data)
        
        return {
            "users": user_list,
            "total_count": query.count(),
            "page_info": {
                "skip": skip,
                "limit": limit,
                "has_more": len(user_list) == limit
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user list: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user list")

@router.get("/analytics/overview")
async def get_analytics_overview(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get analytics overview for admin dashboard."""
    try:
        verify_admin(current_user)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Key metrics
        metrics = {
            "user_engagement": {
                "daily_active_users": 45,  # Mock data
                "weekly_active_users": 156,
                "monthly_active_users": 289,
                "avg_session_duration": "12m 34s"
            },
            "feature_adoption": {
                "job_tracking": 78.5,
                "career_roadmaps": 45.2,
                "networking": 34.8,
                "auto_apply": 23.1
            },
            "success_metrics": {
                "avg_response_rate": 18.7,
                "avg_interview_rate": 12.3,
                "avg_offer_rate": 4.2,
                "user_satisfaction": 4.6
            },
            "platform_health": {
                "api_uptime": 99.8,
                "avg_response_time": 125,
                "error_rate": 0.2,
                "database_performance": "excellent"
            }
        }
        
        return metrics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get analytics overview: {e}")
        raise HTTPException(status_code=500, detail="Failed to get analytics overview")

def calculate_growth_rate(monthly_data: list, metric: str) -> float:
    """Calculate growth rate for a metric."""
    if len(monthly_data) < 2:
        return 0.0
    
    current = monthly_data[-1][metric]
    previous = monthly_data[-2][metric]
    
    if previous == 0:
        return 100.0 if current > 0 else 0.0
    
    return round(((current - previous) / previous * 100), 1)

def calculate_profile_completeness(candidate: Candidate) -> int:
    """Calculate profile completeness percentage."""
    fields = [
        candidate.linkedin_url,
        candidate.github_url,
        candidate.resume_url,
        candidate.skills,
        candidate.career_goals,
        candidate.preferred_roles
    ]
    
    completed = sum(1 for field in fields if field)
    return round((completed / len(fields)) * 100)
