# Analytics API Router
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

from app.database import get_db
from app.models import User, JobApplication, Candidate
from app.services.auth import get_current_active_user

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/dashboard")
async def get_dashboard_analytics(
    time_range: str = Query("30_days"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get comprehensive dashboard analytics for the user."""
    try:
        # Convert time_range to days
        time_range_map = {
            "7_days": 7,
            "30_days": 30,
            "90_days": 90,
            "180_days": 180,
            "365_days": 365
        }
        days = time_range_map.get(time_range, 30)
        
        end_date = datetime.utcnow().replace(tzinfo=None)
        start_date = end_date - timedelta(days=days)
        
        # Get applications in date range
        applications = db.query(JobApplication).filter(
            JobApplication.user_id == current_user.id,
            JobApplication.applied_date >= start_date
        ).all()
        
        # Basic stats
        total_applications = len(applications)
        status_counts = {}
        for app in applications:
            status_counts[app.status] = status_counts.get(app.status, 0) + 1
        
        # Calculate rates
        responses = status_counts.get('interview', 0) + status_counts.get('rejected', 0) + status_counts.get('offer', 0)
        response_rate = (responses / total_applications * 100) if total_applications > 0 else 0
        offer_rate = (status_counts.get('offer', 0) / total_applications * 100) if total_applications > 0 else 0
        
        # Weekly application trend
        weekly_data = []
        for i in range(days // 7):
            week_start = start_date + timedelta(weeks=i)
            week_end = week_start + timedelta(days=7)
            week_apps = [app for app in applications if week_start <= app.applied_date.replace(tzinfo=None) < week_end]
            weekly_data.append({
                "week": week_start.strftime("%Y-%m-%d"),
                "applications": len(week_apps)
            })
        
        # Top companies applied to
        company_counts = {}
        for app in applications:
            company_counts[app.company] = company_counts.get(app.company, 0) + 1
        
        top_companies = sorted(company_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Response time analysis
        response_times = []
        for app in applications:
            if app.response_date and app.applied_date:
                applied_date_naive = app.applied_date.replace(tzinfo=None) if app.applied_date.tzinfo else app.applied_date
                response_date_naive = app.response_date.replace(tzinfo=None) if app.response_date.tzinfo else app.response_date
                diff = (response_date_naive - applied_date_naive).days
                response_times.append(diff)
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        dashboard_data = {
            "overview": {
                "total_applications": total_applications,
                "response_rate": round(response_rate, 1),
                "offer_rate": round(offer_rate, 1),
                "avg_response_time_days": round(avg_response_time, 1)
            },
            "status_breakdown": status_counts,
            "weekly_trend": weekly_data,
            "top_companies": [{"company": comp, "count": count} for comp, count in top_companies],
            "performance_metrics": {
                "applications_per_week": round(total_applications / (days / 7), 1),
                "interview_conversion": round((status_counts.get('interview', 0) / total_applications * 100) if total_applications > 0 else 0, 1),
                "offer_conversion": round(offer_rate, 1)
            }
        }
        
        return dashboard_data
        
    except Exception as e:
        logger.error(f"Failed to get dashboard analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get dashboard analytics")

@router.get("/funnel")
async def get_application_funnel(
    time_range: str = Query("90_days"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get application funnel analysis."""
    try:
        # Convert time_range to days
        time_range_map = {
            "7_days": 7,
            "30_days": 30,
            "90_days": 90,
            "180_days": 180,
            "365_days": 365
        }
        days = time_range_map.get(time_range, 90)
        
        end_date = datetime.utcnow().replace(tzinfo=None)
        start_date = end_date - timedelta(days=days)
        
        applications = db.query(JobApplication).filter(
            JobApplication.user_id == current_user.id,
            JobApplication.applied_date >= start_date
        ).all()
        
        # Calculate funnel stages
        total_applied = len(applications)
        responded = len([app for app in applications if app.status in ['interview', 'rejected', 'offer']])
        interviews = len([app for app in applications if app.status == 'interview'])
        offers = len([app for app in applications if app.status == 'offer'])
        
        funnel_data = {
            "stages": [
                {
                    "stage": "Applied",
                    "count": total_applied,
                    "percentage": 100.0,
                    "conversion_rate": None
                },
                {
                    "stage": "Response Received",
                    "count": responded,
                    "percentage": round((responded / total_applied * 100) if total_applied > 0 else 0, 1),
                    "conversion_rate": round((responded / total_applied * 100) if total_applied > 0 else 0, 1)
                },
                {
                    "stage": "Interview",
                    "count": interviews,
                    "percentage": round((interviews / total_applied * 100) if total_applied > 0 else 0, 1),
                    "conversion_rate": round((interviews / responded * 100) if responded > 0 else 0, 1)
                },
                {
                    "stage": "Offer",
                    "count": offers,
                    "percentage": round((offers / total_applied * 100) if total_applied > 0 else 0, 1),
                    "conversion_rate": round((offers / interviews * 100) if interviews > 0 else 0, 1)
                }
            ],
            "insights": [
                f"Your response rate of {round((responded / total_applied * 100) if total_applied > 0 else 0, 1)}% is {'above' if (responded / total_applied * 100) > 20 else 'below'} average",
                f"You've received {interviews} interviews from {total_applied} applications",
                f"Your offer conversion rate is {round((offers / interviews * 100) if interviews > 0 else 0, 1)}%"
            ]
        }
        
        return funnel_data
        
    except Exception as e:
        logger.error(f"Failed to get funnel analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get funnel analytics")

@router.get("/trends")
@router.get("/market-trends")  # Add alias for frontend compatibility
async def get_market_trends(
    role: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get market trends and insights."""
    try:
        # Mock market trends data
        trends_data = {
            "salary_trends": {
                "role": role or "Software Engineer",
                "location": location or "United States",
                "current_range": "$95k - $165k",
                "growth_rate": "+8.5%",
                "market_demand": "Very High",
                "monthly_data": [
                    {"month": "2024-07", "avg_salary": 125000},
                    {"month": "2024-08", "avg_salary": 127000},
                    {"month": "2024-09", "avg_salary": 128500},
                    {"month": "2024-10", "avg_salary": 130000},
                    {"month": "2024-11", "avg_salary": 132000},
                    {"month": "2024-12", "avg_salary": 133500},
                    {"month": "2025-01", "avg_salary": 135000}
                ]
            },
            "skill_demand": [
                {"skill": "Python", "demand_score": 95, "growth": "+12%"},
                {"skill": "React", "demand_score": 88, "growth": "+15%"},
                {"skill": "AWS", "demand_score": 82, "growth": "+20%"},
                {"skill": "Docker", "demand_score": 78, "growth": "+18%"},
                {"skill": "TypeScript", "demand_score": 75, "growth": "+22%"}
            ],
            "hiring_trends": {
                "remote_percentage": 68,
                "hybrid_percentage": 25,
                "onsite_percentage": 7,
                "fastest_growing_companies": [
                    {"company": "OpenAI", "growth": "+150%"},
                    {"company": "Anthropic", "growth": "+120%"},
                    {"company": "Stripe", "growth": "+85%"}
                ]
            },
            "industry_insights": [
                "AI/ML roles have seen 45% growth in job postings",
                "Remote work opportunities remain high at 68%",
                "Companies are prioritizing full-stack developers",
                "Salary ranges have increased 8.5% year-over-year"
            ]
        }
        
        return trends_data
        
    except Exception as e:
        logger.error(f"Failed to get market trends: {e}")
        raise HTTPException(status_code=500, detail="Failed to get market trends")

@router.get("/performance")
async def get_performance_metrics(
    time_range: str = Query("30_days"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get detailed performance metrics and benchmarks."""
    try:
        applications = db.query(JobApplication).filter(
            JobApplication.user_id == current_user.id
        ).all()
        
        if not applications:
            return {
                "message": "No applications found. Start applying to see performance metrics!",
                "metrics": {}
            }
        
        # Calculate various performance metrics
        total_apps = len(applications)
        interviews = len([app for app in applications if app.status == 'interview'])
        offers = len([app for app in applications if app.status == 'offer'])
        rejections = len([app for app in applications if app.status == 'rejected'])
        
        # Time-based analysis
        time_range_map = {
            "7_days": 7,
            "30_days": 30,
            "90_days": 90,
            "180_days": 180,
            "365_days": 365
        }
        days = time_range_map.get(time_range, 30)
        cutoff_date = datetime.utcnow().replace(tzinfo=None) - timedelta(days=days)
        recent_apps = [app for app in applications if app.applied_date.replace(tzinfo=None) >= cutoff_date]
        
        performance_data = {
            "overall_metrics": {
                "total_applications": total_apps,
                "interview_rate": round((interviews / total_apps * 100), 1),
                "offer_rate": round((offers / total_apps * 100), 1),
                "rejection_rate": round((rejections / total_apps * 100), 1)
            },
            "recent_performance": {
                "last_30_days": len(recent_apps),
                "weekly_average": round(len(recent_apps) / 4.3, 1),
                "trend": "increasing" if len(recent_apps) > total_apps * 0.3 else "stable"
            },
            "benchmarks": {
                "industry_interview_rate": 15.0,
                "industry_offer_rate": 3.0,
                "your_performance": "above_average" if (interviews / total_apps * 100) > 15 else "below_average"
            },
            "recommendations": [
                "Focus on quality over quantity in applications",
                "Tailor your resume for each application",
                "Follow up on applications after 1 week",
                "Network within target companies"
            ]
        }
        
        return performance_data
        
    except Exception as e:
        logger.error(f"Failed to get performance metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get performance metrics")
