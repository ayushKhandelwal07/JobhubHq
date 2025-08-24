from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    user_type = Column(String, nullable=False)  # "candidate" or "recruiter"
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    preferences = Column(JSON, default={})
    
    # Relationships
    candidate_profile = relationship("Candidate", back_populates="user", uselist=False)
    job_applications = relationship("JobApplication", back_populates="user")
    career_roadmaps = relationship("CareerRoadmap", back_populates="user")
    job_postings = relationship("JobPosting", back_populates="recruiter")

class Candidate(Base):
    __tablename__ = "candidates"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    resume_url = Column(String)
    linkedin_url = Column(String)
    github_url = Column(String)
    leetcode_username = Column(String)
    skills = Column(JSON, default=[])
    experience_years = Column(Integer, default=0)
    preferred_roles = Column(JSON, default=[])
    career_goals = Column(Text)
    score = Column(Float, default=0.0)
    github_stats = Column(JSON, default={})
    leetcode_stats = Column(JSON, default={})
    linkedin_stats = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="candidate_profile")
    interviews = relationship("Interview", back_populates="candidate")

class JobApplication(Base):
    __tablename__ = "job_applications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    job_title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    job_url = Column(String)
    status = Column(String, default="applied")  # applied, interview, rejected, ghosted, offer
    applied_date = Column(DateTime(timezone=True), server_default=func.now())
    response_date = Column(DateTime(timezone=True))
    notes = Column(Text)
    source = Column(String, default="manual")  # linkedin, indeed, angellist, manual
    salary_range = Column(String)
    location = Column(String)
    job_description = Column(Text)
    application_method = Column(String)  # auto, manual
    cover_letter = Column(Text)
    
    # Relationships
    user = relationship("User", back_populates="job_applications")

class CareerRoadmap(Base):
    __tablename__ = "career_roadmaps"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    goal = Column(String, nullable=False)
    timeline = Column(String, nullable=False)
    skills_to_learn = Column(JSON, default=[])
    resources = Column(JSON, default=[])
    milestones = Column(JSON, default=[])
    progress = Column(JSON, default={})
    completion_percentage = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="career_roadmaps")

class JobPosting(Base):
    __tablename__ = "job_postings"
    
    id = Column(Integer, primary_key=True, index=True)
    recruiter_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    requirements = Column(JSON, default=[])
    salary_range = Column(String)
    location = Column(String, nullable=False)
    remote_ok = Column(Boolean, default=False)
    employment_type = Column(String, default="full-time")  # full-time, part-time, contract
    experience_level = Column(String)  # entry, mid, senior
    department = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    recruiter = relationship("User", back_populates="job_postings")
    interviews = relationship("Interview", back_populates="job_posting")

class Interview(Base):
    __tablename__ = "interviews"
    
    id = Column(Integer, primary_key=True, index=True)
    job_posting_id = Column(Integer, ForeignKey("job_postings.id"))
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    scheduled_time = Column(DateTime(timezone=True))
    interview_type = Column(String, default="technical")  # technical, behavioral, cultural
    status = Column(String, default="scheduled")  # scheduled, completed, cancelled, rescheduled
    duration_minutes = Column(Integer, default=60)
    meeting_link = Column(String)
    questions = Column(JSON, default=[])
    feedback = Column(Text)
    rating = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    job_posting = relationship("JobPosting", back_populates="interviews")
    candidate = relationship("Candidate", back_populates="interviews")

class NetworkingContact(Base):
    __tablename__ = "networking_contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    contact_name = Column(String, nullable=False)
    contact_title = Column(String)
    company = Column(String)
    linkedin_url = Column(String)
    email = Column(String)
    contact_method = Column(String)  # linkedin, email, referral
    status = Column(String, default="pending")  # pending, connected, responded, no_response
    message_sent = Column(Text)
    response_received = Column(Text)
    contacted_date = Column(DateTime(timezone=True), server_default=func.now())
    response_date = Column(DateTime(timezone=True))
    notes = Column(Text)

class AgentActivity(Base):
    __tablename__ = "agent_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    agent_name = Column(String, nullable=False)
    activity_type = Column(String, nullable=False)  # job_search, application, networking, etc.
    status = Column(String, default="running")  # running, completed, failed
    input_data = Column(JSON, default={})
    output_data = Column(JSON, default={})
    error_message = Column(Text)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    execution_time_seconds = Column(Float)

class Analytics(Base):
    __tablename__ = "analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    metric_type = Column(String, nullable=False)  # application_rate, response_rate, skill_progress
    metric_value = Column(Float, nullable=False)
    metric_data = Column(JSON, default={})
    date_recorded = Column(DateTime(timezone=True), server_default=func.now())
    period = Column(String, default="daily")  # daily, weekly, monthly

class IntegrationCredential(Base):
    __tablename__ = "integration_credentials"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    service_name = Column(String, nullable=False)  # linkedin, github, google, etc.
    encrypted_credentials = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))
    last_used = Column(DateTime(timezone=True))
