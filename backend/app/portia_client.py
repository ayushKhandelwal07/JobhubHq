# Portia AI Client - FIXED VERSION
import logging
from typing import Optional, Any
from app.config import settings

logger = logging.getLogger(__name__)

class MockPortiaClient:
    """Mock Portia client that works without the actual SDK"""
    
    def __init__(self):
        logger.info("Using mock Portia client - SDK not available")
    
    def run_task(self, task: str, end_user: str = None) -> Any:
        logger.info(f"Mock execution of task: {task}")
        return {"status": "mock_completed", "task": task}
    
    def plan_task(self, task: str) -> Any:
        logger.info(f"Mock planning of task: {task}")
        return {"status": "mock_planned", "task": task}
    
    def get_available_tools(self) -> list:
        return ["mock_tool"]

# Try to import Portia, fallback to mock if not available
try:
    from portia import PortiaClient
    portia_client = PortiaClient(api_key=settings.PORTIA_API_KEY) if settings.PORTIA_API_KEY else None
    logger.info("Real Portia client initialized")
except ImportError as e:
    logger.warning(f"Portia SDK not available: {e}, using mock client")
    portia_client = MockPortiaClient()
except Exception as e:
    logger.error(f"Failed to initialize Portia client: {e}, using mock client")
    portia_client = MockPortiaClient()