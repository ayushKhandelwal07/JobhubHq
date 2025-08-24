# Mock agents registry - FIXED VERSION
import logging

logger = logging.getLogger(__name__)

# Mock agents that work without Portia SDK
PORTIA_AGENTS = {
    "profile_optimizer": {"name": "Profile Optimizer", "status": "mock"},
    "job_matcher": {"name": "Job Matcher", "status": "mock"},
    "gmail_tracker": {"name": "Gmail Tracker", "status": "mock"},
    "interview_orchestrator": {"name": "Interview Orchestrator", "status": "mock"},
    "culture_analyzer": {"name": "Culture Analyzer", "status": "mock"}
}

def get_agent_info():
    """Get information about available agents"""
    return {
        "total_agents": len(PORTIA_AGENTS),
        "agents": PORTIA_AGENTS,
        "status": "mock_mode"
    }

logger.info(f"Initialized {len(PORTIA_AGENTS)} mock agents")