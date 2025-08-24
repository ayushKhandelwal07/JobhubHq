# Portia Agent Registry
# Central registry for all Portia-powered job platform agents

from typing import Dict, Optional
import logging

# Import all Portia agents
from .job_tracker import JobApplicationTrackerAgent
from .job_application import JobApplicationAgent
from .career_roadmap import CareerRoadmapAgent
from .networking import NetworkingAgent
from .candidate_analysis import CandidateAnalysisAgent
from .interview_coordination import InterviewCoordinationAgent
from .market_analytics import JobMarketAnalyticsAgent

logger = logging.getLogger(__name__)

# Agent registry for easy access
PORTIA_AGENTS = {
    "job_tracker": JobApplicationTrackerAgent(),
    "job_application": JobApplicationAgent(), 
    "career_roadmap": CareerRoadmapAgent(),
    "networking": NetworkingAgent(),
    "candidate_analysis": CandidateAnalysisAgent(),
    "interview_coordination": InterviewCoordinationAgent(),
    "market_analytics": JobMarketAnalyticsAgent()
}

def get_agent(agent_name: str) -> Optional[object]:
    """Get agent by name"""
    agent = PORTIA_AGENTS.get(agent_name)
    if agent:
        logger.info(f"Retrieved agent: {agent_name} - {agent.description}")
    else:
        logger.warning(f"Agent not found: {agent_name}")
    return agent

def get_all_agents() -> Dict[str, object]:
    """Get all available agents"""
    logger.info(f"Retrieved all {len(PORTIA_AGENTS)} agents")
    return PORTIA_AGENTS

def get_agent_info() -> Dict[str, Dict[str, str]]:
    """Get information about all agents"""
    return {
        name: {
            "name": agent.name,
            "description": agent.description,
            "class": agent.__class__.__name__
        }
        for name, agent in PORTIA_AGENTS.items()
    }

def list_agent_names() -> list:
    """Get list of all agent names"""
    return list(PORTIA_AGENTS.keys())

# Initialize agents on module import
logger.info(f"Initialized {len(PORTIA_AGENTS)} Portia agents:")
for name, agent in PORTIA_AGENTS.items():
    logger.info(f"  {name}: {agent.name}")

logger.info("All Portia agents ready for maximum integration!")
