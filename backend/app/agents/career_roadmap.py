# Career Roadmap Agent
# Portia-powered career development planning with GitHub and LinkedIn analysis

from typing import Dict, Any
import logging
from .base import PortiaJobAgent

logger = logging.getLogger(__name__)

class CareerRoadmapAgent(PortiaJobAgent):
    """
    Portia-powered career development planning agent
    Uses GitHub, LinkedIn, and web research tools
    """
    
    def __init__(self):
        super().__init__(
            name="Career Roadmap Planner",
            description="Creates personalized career development plans using GitHub analysis and market research"
        )
    
    async def create_career_roadmap(self, user_profile: Dict[str, Any], career_goal: str, timeline: str, user_id: str) -> Dict[str, Any]:
        """Create comprehensive career development roadmap"""
        task = f"""
        Create detailed career roadmap for user:
        
        Current Profile: {user_profile}
        Career Goal: {career_goal}
        Timeline: {timeline}
        
        1. Use GitHub tool to analyze user's repositories:
           - Current technical skills
           - Code quality and patterns
           - Project complexity
           - Contribution frequency
        
        2. Use LinkedIn tool to research:
           - Professionals in target role
           - Required skills and experience
           - Career progression paths
           - Industry trends
        
        3. Use web research to find:
           - Current job market demands
           - Salary ranges for target role
           - Top companies hiring
           - Required certifications
        
        4. Generate comprehensive roadmap with:
           - Skill gap analysis
           - Learning resources (courses, books, tutorials)
           - Project recommendations
           - Timeline with milestones
           - Networking strategies
           - Portfolio development plan
        
        5. Create actionable monthly goals and tracking metrics
        """
        
        return await self.execute_with_planning(
            task=task,
            context={"profile": user_profile, "goal": career_goal, "timeline": timeline},
            end_user=user_id
        )
    
    async def track_skill_progress(self, user_github: str, user_linkedin: str, roadmap_id: str, user_id: str) -> Dict[str, Any]:
        """Track progress on career development goals"""
        task = f"""
        Track career development progress:
        
        GitHub: {user_github}
        LinkedIn: {user_linkedin}
        Roadmap ID: {roadmap_id}
        
        1. Use GitHub tool to analyze recent activity:
           - New repositories created
           - Languages used
           - Commit frequency
           - Code quality improvements
        
        2. Use LinkedIn tool to check:
           - Profile updates
           - New connections
           - Posts and engagement
           - Skills added
        
        3. Compare against roadmap milestones
        4. Generate progress report with:
           - Completed objectives
           - Current skill level
           - Recommendations for next steps
           - Areas needing attention
        
        5. Update roadmap based on progress and market changes
        """
        
        return await self.execute_with_planning(
            task=task,
            context={"github": user_github, "linkedin": user_linkedin, "roadmap_id": roadmap_id},
            end_user=user_id
        )
