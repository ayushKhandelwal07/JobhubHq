from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

# User Schemas
class UserType(str, Enum):
    CANDIDATE = "candidate"
    RECRUITER = "recruiter"

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    user_type: UserType

class UserCreate(UserBase):
    password: str
    preferences: Optional[Dict[str, Any]] = {}

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Authentication Schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# Candidate Schemas
class CandidateBase(BaseModel):
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    leetcode_username: Optional[str] = None
    skills: List[str] = []
    experience_years: int = 0
    preferred_roles: List[str] = []
    career_goals: Optional[str] = None

class CandidateCreate(CandidateBase):
    pass

class CandidateUpdate(BaseModel):
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    leetcode_username: Optional[str] = None
    skills: Optional[List[str]] = None
    experience_years: Optional[int] = None
    preferred_roles: Optional[List[str]] = None
    career_goals: Optional[str] = None

class CandidateResponse(CandidateBase):
    id: int
    user_id: int
    resume_url: Optional[str]
    score: float
    github_stats: Dict[str, Any]
    leetcode_stats: Dict[str, Any]
    linkedin_stats: Dict[str, Any]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Job Application Schemas
class ApplicationStatus(str, Enum):
    APPLIED = "applied"
    INTERVIEW = "interview"
    REJECTED = "rejected"
    GHOSTED = "ghosted"
    OFFER = "offer"

class JobApplicationBase(BaseModel):
    job_title: str
    company: str
    job_url: Optional[str] = None
    salary_range: Optional[str] = None
    location: Optional[str] = None
    job_description: Optional[str] = None
    notes: Optional[str] = None
    source: str = "manual"

class JobApplicationCreate(JobApplicationBase):
    pass

class JobApplicationUpdate(BaseModel):
    status: Optional[ApplicationStatus] = None
    notes: Optional[str] = None
    response_date: Optional[datetime] = None

class JobApplicationResponse(JobApplicationBase):
    id: int
    user_id: int
    status: ApplicationStatus
    applied_date: datetime
    response_date: Optional[datetime]
    application_method: Optional[str]
    cover_letter: Optional[str]
    
    class Config:
        from_attributes = True

# Career Roadmap Schemas
class CareerRoadmapBase(BaseModel):
    goal: str
    timeline: str

class CareerRoadmapCreate(CareerRoadmapBase):
    pass

class CareerRoadmapResponse(CareerRoadmapBase):
    id: int
    user_id: int
    skills_to_learn: List[str]
    resources: List[Dict[str, Any]]
    milestones: List[Dict[str, Any]]
    progress: Dict[str, Any]
    completion_percentage: float
    created_at: datetime
    
    class Config:
        from_attributes = True

class MilestoneUpdate(BaseModel):
    milestone_id: str
    completed: bool

# Job Posting Schemas
class JobPostingBase(BaseModel):
    title: str
    company: str
    description: str
    requirements: List[str]
    salary_range: Optional[str] = None
    location: str
    remote_ok: bool = False
    employment_type: str = "full-time"
    experience_level: Optional[str] = None
    department: Optional[str] = None

class JobPostingCreate(JobPostingBase):
    pass

class JobPostingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[List[str]] = None
    salary_range: Optional[str] = None
    location: Optional[str] = None
    remote_ok: Optional[bool] = None
    is_active: Optional[bool] = None

class JobPostingResponse(JobPostingBase):
    id: int
    recruiter_id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Interview Schemas
class InterviewBase(BaseModel):
    scheduled_time: datetime
    interview_type: str = "technical"
    duration_minutes: int = 60
    meeting_link: Optional[str] = None

class InterviewCreate(InterviewBase):
    job_posting_id: int
    candidate_id: int

class InterviewUpdate(BaseModel):
    scheduled_time: Optional[datetime] = None
    status: Optional[str] = None
    feedback: Optional[str] = None
    rating: Optional[float] = None

class InterviewResponse(InterviewBase):
    id: int
    job_posting_id: int
    candidate_id: int
    status: str
    questions: List[Dict[str, Any]]
    feedback: Optional[str]
    rating: Optional[float]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Networking Schemas
class NetworkingContactBase(BaseModel):
    contact_name: str
    contact_title: Optional[str] = None
    company: Optional[str] = None
    linkedin_url: Optional[str] = None
    email: Optional[str] = None
    contact_method: str = "linkedin"

class NetworkingContactCreate(NetworkingContactBase):
    message_sent: str

class NetworkingContactResponse(NetworkingContactBase):
    id: int
    user_id: int
    status: str
    message_sent: str
    response_received: Optional[str]
    contacted_date: datetime
    response_date: Optional[datetime]
    notes: Optional[str]
    
    class Config:
        from_attributes = True

# Agent Activity Schemas
class AgentActivityResponse(BaseModel):
    id: int
    user_id: int
    agent_name: str
    activity_type: str
    status: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    error_message: Optional[str]
    started_at: datetime
    completed_at: Optional[datetime]
    execution_time_seconds: Optional[float]
    
    class Config:
        from_attributes = True

# Analytics Schemas
class AnalyticsResponse(BaseModel):
    id: int
    user_id: int
    metric_type: str
    metric_value: float
    metric_data: Dict[str, Any]
    date_recorded: datetime
    period: str
    
    class Config:
        from_attributes = True

# Dashboard Schemas
class ApplicationFunnelData(BaseModel):
    total_applications: int
    interviews: int
    offers: int
    rejections: int
    pending: int
    response_rate: float
    offer_rate: float

class SkillProgressData(BaseModel):
    skill_name: str
    current_level: int
    target_level: int
    progress_percentage: float
    resources_completed: int
    total_resources: int

class CandidateScorecard(BaseModel):
    overall_score: float
    technical_score: float
    experience_score: float
    activity_score: float
    github_contributions: int
    leetcode_problems_solved: int
    linkedin_connections: int
    application_success_rate: float

class DashboardData(BaseModel):
    application_funnel: ApplicationFunnelData
    skill_progress: List[SkillProgressData]
    scorecard: CandidateScorecard
    recent_activities: List[AgentActivityResponse]

# Auto-Application Schemas
class AutoApplicationPreferences(BaseModel):
    keywords: List[str]
    locations: List[str]
    companies_blacklist: List[str] = []
    companies_whitelist: List[str] = []
    salary_min: Optional[int] = None
    remote_only: bool = False
    max_applications_per_day: int = 10
    cover_letter_template: Optional[str] = None

class JobSearchRequest(BaseModel):
    keywords: str
    location: Optional[str] = None
    company: Optional[str] = None
    salary_min: Optional[int] = None
    remote_only: bool = False

# Network Expansion Schemas
class NetworkExpansionRequest(BaseModel):
    target_companies: List[str]
    target_roles: List[str]
    message_template: str
    max_connections_per_day: int = 5

class ConnectionRequest(BaseModel):
    profiles: List[str]
    message_template: str

# Integration Schemas
class LinkedInIntegration(BaseModel):
    linkedin_url: str

class GitHubIntegration(BaseModel):
    github_username: str

class LeetCodeIntegration(BaseModel):
    leetcode_username: str

# File Upload Schemas
class FileUploadResponse(BaseModel):
    filename: str
    file_url: str
    file_size: int
    upload_date: datetime

# Bulk Operations
class BulkJobApplicationCreate(BaseModel):
    applications: List[JobApplicationCreate]

class BulkOperationResponse(BaseModel):
    success_count: int
    error_count: int
    errors: List[Dict[str, Any]]

# Ranking Schemas
class CandidateRanking(BaseModel):
    candidate_id: int
    score: float
    ranking_factors: Dict[str, float]
    strengths: List[str]
    weaknesses: List[str]

class RankingResponse(BaseModel):
    job_posting_id: int
    ranked_candidates: List[CandidateRanking]
    ranking_criteria: Dict[str, float]
