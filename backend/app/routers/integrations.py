# Integrations API Router
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging
from datetime import datetime

from app.database import get_db
from app.models import User, Candidate
from app.services.auth import get_current_active_user

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/github")
async def connect_github(
    github_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Connect GitHub account and analyze profile."""
    try:
        github_username = github_data.get("github_username")
        if not github_username:
            raise HTTPException(status_code=400, detail="github_username is required")
        
        # Get or create candidate profile
        candidate = db.query(Candidate).filter(Candidate.user_id == current_user.id).first()
        if not candidate:
            candidate = Candidate(user_id=current_user.id)
            db.add(candidate)
        
        # Update GitHub URL
        candidate.github_url = f"https://github.com/{github_username}"
        
        # Mock GitHub analysis
        github_stats = analyze_github_profile(github_username)
        candidate.github_stats = github_stats
        
        # Update skills based on GitHub analysis
        detected_skills = github_stats.get("top_languages", [])
        current_skills = set(candidate.skills or [])
        new_skills = current_skills.union(set(detected_skills))
        candidate.skills = list(new_skills)
        
        db.commit()
        db.refresh(candidate)
        
        logger.info(f"Connected GitHub account {github_username} for user {current_user.id}")
        
        return {
            "message": "GitHub account connected successfully",
            "github_username": github_username,
            "github_url": candidate.github_url,
            "stats": github_stats,
            "detected_skills": detected_skills,
            "insights": [
                f"Found {github_stats['total_repos']} repositories",
                f"Most active in {github_stats['top_languages'][0] if github_stats['top_languages'] else 'various languages'}",
                f"Contribution streak: {github_stats['contribution_streak']} days",
                f"Profile strength: {github_stats['profile_strength']}/100"
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to connect GitHub: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to connect GitHub account")

@router.post("/leetcode")
async def connect_leetcode(
    leetcode_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Connect LeetCode account and analyze performance."""
    try:
        leetcode_username = leetcode_data.get("leetcode_username")
        if not leetcode_username:
            raise HTTPException(status_code=400, detail="leetcode_username is required")
        
        # Get or create candidate profile
        candidate = db.query(Candidate).filter(Candidate.user_id == current_user.id).first()
        if not candidate:
            candidate = Candidate(user_id=current_user.id)
            db.add(candidate)
        
        # Update LeetCode username
        candidate.leetcode_username = leetcode_username
        
        # Mock LeetCode analysis
        leetcode_stats = analyze_leetcode_profile(leetcode_username)
        candidate.leetcode_stats = leetcode_stats
        
        db.commit()
        db.refresh(candidate)
        
        logger.info(f"Connected LeetCode account {leetcode_username} for user {current_user.id}")
        
        return {
            "message": "LeetCode account connected successfully",
            "leetcode_username": leetcode_username,
            "stats": leetcode_stats,
            "insights": [
                f"Solved {leetcode_stats['problems_solved']} problems total",
                f"Difficulty breakdown: {leetcode_stats['easy_solved']} easy, {leetcode_stats['medium_solved']} medium, {leetcode_stats['hard_solved']} hard",
                f"Contest rating: {leetcode_stats['contest_rating']}",
                f"Problem-solving strength: {leetcode_stats['skill_level']}"
            ],
            "recommendations": [
                "Focus on medium difficulty problems to improve interview readiness",
                "Practice system design problems for senior roles",
                "Participate in weekly contests to improve speed",
                "Review solutions for problems you couldn't solve"
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to connect LeetCode: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to connect LeetCode account")

@router.post("/linkedin")
async def connect_linkedin(
    linkedin_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Connect LinkedIn profile and analyze professional presence."""
    try:
        linkedin_url = linkedin_data.get("linkedin_url")
        if not linkedin_url:
            raise HTTPException(status_code=400, detail="linkedin_url is required")
        
        # Validate LinkedIn URL format
        if "linkedin.com/in/" not in linkedin_url:
            raise HTTPException(status_code=400, detail="Invalid LinkedIn URL format")
        
        # Get or create candidate profile
        candidate = db.query(Candidate).filter(Candidate.user_id == current_user.id).first()
        if not candidate:
            candidate = Candidate(user_id=current_user.id)
            db.add(candidate)
        
        # Update LinkedIn URL
        candidate.linkedin_url = linkedin_url
        
        # Mock LinkedIn analysis
        linkedin_stats = analyze_linkedin_profile(linkedin_url)
        candidate.linkedin_stats = linkedin_stats
        
        db.commit()
        db.refresh(candidate)
        
        logger.info(f"Connected LinkedIn profile for user {current_user.id}")
        
        return {
            "message": "LinkedIn profile connected successfully",
            "linkedin_url": linkedin_url,
            "stats": linkedin_stats,
            "insights": [
                f"Profile completeness: {linkedin_stats['profile_completeness']}%",
                f"Network size: {linkedin_stats['connections']} connections",
                f"Industry presence: {linkedin_stats['industry_ranking']}/100",
                f"Content engagement: {linkedin_stats['engagement_score']}/100"
            ],
            "optimization_tips": [
                "Add a professional headshot to increase profile views",
                "Write a compelling headline with relevant keywords",
                "Get recommendations from colleagues and managers",
                "Post regularly about your industry to build thought leadership",
                "Join relevant professional groups in your field"
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to connect LinkedIn: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to connect LinkedIn profile")

@router.get("/status")
async def get_integration_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get status of all integrations."""
    try:
        candidate = db.query(Candidate).filter(Candidate.user_id == current_user.id).first()
        
        if not candidate:
            return {
                "github": {"connected": False, "url": None},
                "leetcode": {"connected": False, "username": None},
                "linkedin": {"connected": False, "url": None},
                "overall_score": 0
            }
        
        status = {
            "github": {
                "connected": bool(candidate.github_url),
                "url": candidate.github_url,
                "stats": candidate.github_stats if candidate.github_url else None
            },
            "leetcode": {
                "connected": bool(candidate.leetcode_username),
                "username": candidate.leetcode_username,
                "stats": candidate.leetcode_stats if candidate.leetcode_username else None
            },
            "linkedin": {
                "connected": bool(candidate.linkedin_url),
                "url": candidate.linkedin_url,
                "stats": candidate.linkedin_stats if candidate.linkedin_url else None
            }
        }
        
        # Calculate overall integration score
        connected_count = sum([
            status["github"]["connected"],
            status["leetcode"]["connected"],
            status["linkedin"]["connected"]
        ])
        status["overall_score"] = round((connected_count / 3) * 100, 1)
        status["connected_integrations"] = connected_count
        status["total_integrations"] = 3
        
        return status
        
    except Exception as e:
        logger.error(f"Failed to get integration status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get integration status")

@router.delete("/{integration_type}")
async def disconnect_integration(
    integration_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Disconnect a specific integration."""
    try:
        if integration_type not in ["github", "leetcode", "linkedin"]:
            raise HTTPException(status_code=400, detail="Invalid integration type")
        
        candidate = db.query(Candidate).filter(Candidate.user_id == current_user.id).first()
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate profile not found")
        
        # Disconnect the specified integration
        if integration_type == "github":
            candidate.github_url = None
            candidate.github_stats = {}
        elif integration_type == "leetcode":
            candidate.leetcode_username = None
            candidate.leetcode_stats = {}
        elif integration_type == "linkedin":
            candidate.linkedin_url = None
            candidate.linkedin_stats = {}
        
        db.commit()
        
        logger.info(f"Disconnected {integration_type} integration for user {current_user.id}")
        
        return {
            "message": f"{integration_type.title()} integration disconnected successfully",
            "integration_type": integration_type
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to disconnect {integration_type}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to disconnect {integration_type} integration")

def analyze_github_profile(username: str) -> Dict[str, Any]:
    """Mock GitHub profile analysis."""
    return {
        "username": username,
        "total_repos": 42,
        "public_repos": 38,
        "followers": 156,
        "following": 89,
        "contribution_streak": 45,
        "total_commits": 1247,
        "top_languages": ["Python", "JavaScript", "TypeScript", "Go"],
        "language_stats": {
            "Python": 45.2,
            "JavaScript": 28.7,
            "TypeScript": 15.1,
            "Go": 8.3,
            "Other": 2.7
        },
        "profile_strength": 85,
        "recent_activity": "Very Active",
        "best_repositories": [
            {"name": "awesome-project", "stars": 234, "language": "Python"},
            {"name": "web-scraper", "stars": 89, "language": "JavaScript"},
            {"name": "api-gateway", "stars": 67, "language": "Go"}
        ]
    }

def analyze_leetcode_profile(username: str) -> Dict[str, Any]:
    """Mock LeetCode profile analysis."""
    return {
        "username": username,
        "problems_solved": 387,
        "easy_solved": 156,
        "medium_solved": 189,
        "hard_solved": 42,
        "acceptance_rate": 73.2,
        "contest_rating": 1845,
        "global_ranking": 15420,
        "skill_level": "Advanced",
        "badges": ["50 Days Badge", "Annual Badge 2024", "Contest Badge"],
        "recent_submissions": 23,
        "favorite_topics": ["Dynamic Programming", "Trees", "Graphs", "Arrays"],
        "weak_areas": ["Backtracking", "Trie", "Segment Tree"],
        "preparation_score": 78
    }

def analyze_linkedin_profile(linkedin_url: str) -> Dict[str, Any]:
    """Mock LinkedIn profile analysis."""
    return {
        "url": linkedin_url,
        "profile_completeness": 87,
        "connections": 847,
        "industry_ranking": 76,
        "engagement_score": 64,
        "post_frequency": "2-3 times per week",
        "profile_views": 234,
        "search_appearances": 89,
        "headline_strength": 72,
        "summary_strength": 68,
        "skills_endorsements": 156,
        "recommendations_received": 12,
        "recommendations_given": 8,
        "groups_joined": 15,
        "content_performance": "Above Average",
        "network_quality": "High"
    }
