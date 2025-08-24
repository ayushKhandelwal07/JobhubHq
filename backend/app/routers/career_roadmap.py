# Career Roadmap API Router
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from app.database import get_db
from app.models import User, CareerRoadmap
from app.schemas import CareerRoadmapCreate, CareerRoadmapResponse
from app.services.auth import get_current_active_user

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=CareerRoadmapResponse)
async def create_career_roadmap(
    roadmap_data: CareerRoadmapCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a personalized career roadmap."""
    try:
        # Check if user already has a roadmap
        existing_roadmap = db.query(CareerRoadmap).filter(
            CareerRoadmap.user_id == current_user.id
        ).first()
        
        if existing_roadmap:
            # Update existing roadmap
            existing_roadmap.goal = roadmap_data.goal
            existing_roadmap.timeline = roadmap_data.timeline
            existing_roadmap.updated_at = datetime.utcnow()
            roadmap = existing_roadmap
        else:
            # Create new roadmap
            roadmap = CareerRoadmap(
                user_id=current_user.id,
                goal=roadmap_data.goal,
                timeline=roadmap_data.timeline
            )
            db.add(roadmap)
        
        # Generate AI-powered roadmap content
        roadmap_content = generate_roadmap_content(roadmap_data.goal, roadmap_data.timeline)
        
        roadmap.skills_to_learn = roadmap_content["skills_to_learn"]
        roadmap.resources = roadmap_content["resources"]
        roadmap.milestones = roadmap_content["milestones"]
        roadmap.progress = {"completed_milestones": [], "current_milestone": 0}
        roadmap.completion_percentage = 0.0
        
        db.commit()
        db.refresh(roadmap)
        
        logger.info(f"Created/updated career roadmap for user {current_user.id}: {roadmap_data.goal}")
        return roadmap
        
    except Exception as e:
        logger.error(f"Failed to create career roadmap: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create career roadmap")

@router.get("/", response_model=Optional[CareerRoadmapResponse])
async def get_career_roadmap(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get the user's career roadmap."""
    try:
        roadmap = db.query(CareerRoadmap).filter(
            CareerRoadmap.user_id == current_user.id
        ).first()
        
        if roadmap:
            logger.info(f"Retrieved career roadmap for user {current_user.id}")
        
        return roadmap
        
    except Exception as e:
        logger.error(f"Failed to get career roadmap: {e}")
        raise HTTPException(status_code=500, detail="Failed to get career roadmap")

@router.put("/progress")
async def update_roadmap_progress(
    progress_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update progress on career roadmap milestones."""
    try:
        roadmap = db.query(CareerRoadmap).filter(
            CareerRoadmap.user_id == current_user.id
        ).first()
        
        if not roadmap:
            raise HTTPException(status_code=404, detail="Career roadmap not found")
        
        milestone_id = progress_data.get("milestone_id")
        completed = progress_data.get("completed", False)
        
        if not milestone_id:
            raise HTTPException(status_code=400, detail="milestone_id is required")
        
        # Update progress
        progress = roadmap.progress or {"completed_milestones": [], "current_milestone": 0}
        
        if completed and milestone_id not in progress["completed_milestones"]:
            progress["completed_milestones"].append(milestone_id)
        elif not completed and milestone_id in progress["completed_milestones"]:
            progress["completed_milestones"].remove(milestone_id)
        
        # Calculate completion percentage
        total_milestones = len(roadmap.milestones) if roadmap.milestones else 0
        completed_count = len(progress["completed_milestones"])
        completion_percentage = (completed_count / total_milestones * 100) if total_milestones > 0 else 0
        
        roadmap.progress = progress
        roadmap.completion_percentage = completion_percentage
        roadmap.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(roadmap)
        
        logger.info(f"Updated roadmap progress for user {current_user.id}: {completion_percentage}% complete")
        
        return {
            "message": "Progress updated successfully",
            "completion_percentage": completion_percentage,
            "completed_milestones": len(progress["completed_milestones"]),
            "total_milestones": total_milestones
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update roadmap progress: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update roadmap progress")

@router.delete("/")
async def delete_career_roadmap(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete the user's career roadmap."""
    try:
        roadmap = db.query(CareerRoadmap).filter(
            CareerRoadmap.user_id == current_user.id
        ).first()
        
        if not roadmap:
            raise HTTPException(status_code=404, detail="Career roadmap not found")
        
        db.delete(roadmap)
        db.commit()
        
        logger.info(f"Deleted career roadmap for user {current_user.id}")
        return {"message": "Career roadmap deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete career roadmap: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete career roadmap")

def generate_roadmap_content(goal: str, timeline: str) -> Dict[str, Any]:
    """Generate AI-powered career roadmap content based on goal and timeline."""
    
    # Mock AI-generated content based on common career goals
    goal_lower = goal.lower()
    
    if "senior" in goal_lower or "lead" in goal_lower:
        return {
            "skills_to_learn": [
                "System Design", "Leadership", "Architecture", "Mentoring",
                "Project Management", "Strategic Thinking", "Team Building"
            ],
            "resources": [
                {
                    "title": "System Design Interview Guide",
                    "type": "book",
                    "url": "https://example.com/system-design",
                    "priority": "high"
                },
                {
                    "title": "Leadership in Tech Course",
                    "type": "course",
                    "url": "https://example.com/leadership",
                    "priority": "medium"
                },
                {
                    "title": "Architecture Patterns",
                    "type": "documentation",
                    "url": "https://example.com/patterns",
                    "priority": "high"
                }
            ],
            "milestones": [
                {
                    "id": "milestone_1",
                    "title": "Master System Design Fundamentals",
                    "description": "Learn about scalability, load balancing, databases",
                    "timeline": "Month 1-2",
                    "skills": ["System Design", "Architecture"],
                    "deliverables": ["Design a scalable system", "Present to team"]
                },
                {
                    "id": "milestone_2",
                    "title": "Develop Leadership Skills",
                    "description": "Start mentoring junior developers",
                    "timeline": "Month 2-4",
                    "skills": ["Leadership", "Mentoring"],
                    "deliverables": ["Mentor 2 developers", "Lead project initiative"]
                },
                {
                    "id": "milestone_3",
                    "title": "Drive Technical Initiative",
                    "description": "Lead a major technical project",
                    "timeline": "Month 4-6",
                    "skills": ["Project Management", "Strategic Thinking"],
                    "deliverables": ["Successful project delivery", "Team feedback"]
                }
            ]
        }
    
    elif "data" in goal_lower or "ml" in goal_lower or "ai" in goal_lower:
        return {
            "skills_to_learn": [
                "Python", "SQL", "Machine Learning", "Statistics",
                "Data Visualization", "Deep Learning", "MLOps"
            ],
            "resources": [
                {
                    "title": "Machine Learning Course",
                    "type": "course",
                    "url": "https://example.com/ml-course",
                    "priority": "high"
                },
                {
                    "title": "Python for Data Science",
                    "type": "book",
                    "url": "https://example.com/python-ds",
                    "priority": "high"
                },
                {
                    "title": "Kaggle Competitions",
                    "type": "practice",
                    "url": "https://kaggle.com",
                    "priority": "medium"
                }
            ],
            "milestones": [
                {
                    "id": "milestone_1",
                    "title": "Master Python & SQL",
                    "description": "Build strong foundation in data tools",
                    "timeline": "Month 1-2",
                    "skills": ["Python", "SQL"],
                    "deliverables": ["Complete 5 data projects", "SQL certification"]
                },
                {
                    "id": "milestone_2",
                    "title": "Learn Machine Learning",
                    "description": "Understand ML algorithms and applications",
                    "timeline": "Month 2-4",
                    "skills": ["Machine Learning", "Statistics"],
                    "deliverables": ["Build ML model", "Kaggle competition"]
                },
                {
                    "id": "milestone_3",
                    "title": "Deploy ML Project",
                    "description": "End-to-end ML project deployment",
                    "timeline": "Month 4-6",
                    "skills": ["MLOps", "Deep Learning"],
                    "deliverables": ["Production ML system", "Portfolio project"]
                }
            ]
        }
    
    else:  # Default software engineer roadmap
        return {
            "skills_to_learn": [
                "Advanced JavaScript", "React/Vue", "Node.js",
                "Database Design", "API Development", "Testing", "DevOps"
            ],
            "resources": [
                {
                    "title": "Advanced JavaScript Concepts",
                    "type": "course",
                    "url": "https://example.com/js-advanced",
                    "priority": "high"
                },
                {
                    "title": "React Documentation",
                    "type": "documentation",
                    "url": "https://react.dev",
                    "priority": "high"
                },
                {
                    "title": "System Design Primer",
                    "type": "guide",
                    "url": "https://example.com/system-design-primer",
                    "priority": "medium"
                }
            ],
            "milestones": [
                {
                    "id": "milestone_1",
                    "title": "Master Modern JavaScript",
                    "description": "Deep dive into ES6+, async/await, modules",
                    "timeline": "Month 1-2",
                    "skills": ["Advanced JavaScript"],
                    "deliverables": ["Build complex JS application", "Code review"]
                },
                {
                    "id": "milestone_2",
                    "title": "Build Full-Stack Application",
                    "description": "Create complete web application",
                    "timeline": "Month 2-4",
                    "skills": ["React/Vue", "Node.js", "Database Design"],
                    "deliverables": ["Deployed web app", "Technical documentation"]
                },
                {
                    "id": "milestone_3",
                    "title": "Implement DevOps Practices",
                    "description": "Set up CI/CD, monitoring, testing",
                    "timeline": "Month 4-6",
                    "skills": ["DevOps", "Testing"],
                    "deliverables": ["Automated deployment", "Test coverage >80%"]
                }
            ]
        }
