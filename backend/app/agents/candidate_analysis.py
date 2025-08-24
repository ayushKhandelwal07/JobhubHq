# Candidate Analysis Agent
# Portia-powered candidate evaluation with bias-free analysis

from typing import Dict, Any
import logging
from .base import PortiaJobAgent

logger = logging.getLogger(__name__)

class CandidateAnalysisAgent(PortiaJobAgent):
    """
    Portia-powered candidate evaluation agent for recruiters
    Uses GitHub, LinkedIn, and bias-free analysis
    """
    
    def __init__(self):
        super().__init__(
            name="Candidate Analysis Agent",
            description="Provides comprehensive, bias-free candidate evaluation using multiple data sources"
        )
    
    async def analyze_candidate(self, candidate_data: Dict[str, Any], job_requirements: Dict[str, Any], recruiter_id: str) -> Dict[str, Any]:
        """Comprehensive candidate analysis with bias detection"""
        task = f"""
        Analyze candidate comprehensively and objectively:
        
        Candidate: {candidate_data}
        Job Requirements: {job_requirements}
        
        1. Use GitHub tool to analyze technical skills:
           - Code quality and style
           - Project complexity
           - Collaboration patterns
           - Technical breadth and depth
        
        2. Use LinkedIn tool to evaluate:
           - Professional experience
           - Career progression
           - Industry involvement
           - Recommendation quality
        
        3. Perform bias-free evaluation:
           - Focus on skills and experience
           - Ignore demographic indicators
           - Use structured scoring criteria
           - Flag potential bias in job requirements
        
        4. Generate analysis report:
           - Technical skill assessment (1-10)
           - Experience relevance score
           - Cultural fit indicators
           - Growth potential
           - Areas for development
           - Interview recommendations
        
        5. PAUSE for human review of bias indicators
        
        CRITICAL: Ensure analysis is fair, objective, and legally compliant.
        """
        
        return await self.execute_with_planning(
            task=task,
            context={"candidate": candidate_data, "requirements": job_requirements},
            end_user=recruiter_id
        )
    
    async def batch_analyze_candidates(self, candidates_data: List[Dict[str, Any]], job_requirements: Dict[str, Any], recruiter_id: str) -> Dict[str, Any]:
        """Analyze multiple candidates and provide ranking"""
        task = f"""
        Batch analyze and rank candidates:
        
        Candidates: {len(candidates_data)} candidates
        Job Requirements: {job_requirements}
        
        1. For each candidate, perform comprehensive analysis using GitHub and LinkedIn tools
        2. Apply consistent, bias-free evaluation criteria
        3. Generate comparative analysis report
        4. Rank candidates based on objective criteria
        5. Identify top candidates with detailed reasoning
        6. Flag any potential bias concerns
        
        IMPORTANT: Ensure fair and consistent evaluation across all candidates.
        """
        
        return await self.execute_with_planning(
            task=task,
            context={"candidates": candidates_data, "requirements": job_requirements},
            end_user=recruiter_id
        )
