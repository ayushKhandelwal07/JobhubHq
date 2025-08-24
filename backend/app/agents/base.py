# Base Portia Agent Class
# Foundation for all Portia-powered job platform agents

from typing import Dict, Any, Optional
import logging
from datetime import datetime

from app.portia_client import portia_client
from app.config import settings

logger = logging.getLogger(__name__)

class PortiaJobAgent:
    """Base class for all Portia-powered job platform agents"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.portia = portia_client
        
    async def execute_with_planning(self, task: str, context: Dict[str, Any] = None, end_user: str = None) -> Dict[str, Any]:
        """Execute task with Portia planning and human oversight"""
        try:
            if not self.portia:
                raise Exception("Portia client not initialized")
            
            # Add context to task if provided
            if context:
                task_with_context = f"{task}\n\nContext: {context}"
            else:
                task_with_context = task
            
            # Execute with Portia
            plan_run = self.portia.run_task(task_with_context, end_user=end_user)
            
            return {
                "status": "success",
                "agent": self.name,
                "result": plan_run.outputs.final_output if hasattr(plan_run.outputs, 'final_output') else str(plan_run),
                "plan_id": getattr(plan_run, 'id', None),
                "execution_time": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Agent {self.name} execution failed: {e}")
            return {
                "status": "error",
                "agent": self.name,
                "error": str(e),
                "execution_time": datetime.utcnow().isoformat()
            }
