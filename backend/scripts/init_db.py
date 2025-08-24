#!/usr/bin/env python3
"""
Database initialization script for Portia AI Job Platform
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import engine, Base
from app.models import *
from app.config import settings
from sqlalchemy import text

async def create_database():
    """Create the database if it doesn't exist."""
    try:
        # Try to connect to the database
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        sys.exit(1)

def create_tables():
    """Create all database tables."""
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")
        sys.exit(1)

def create_demo_data():
    """Create demo users for testing."""
    from app.services.auth import AuthService
    from sqlalchemy.orm import sessionmaker
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if demo users already exist
        existing_candidate = db.query(User).filter(User.email == "candidate@demo.com").first()
        existing_recruiter = db.query(User).filter(User.email == "recruiter@demo.com").first()
        
        if not existing_candidate:
            # Create demo candidate
            candidate_user = User(
                email="candidate@demo.com",
                full_name="Demo Candidate",
                user_type="candidate",
                password_hash=AuthService.get_password_hash("demo123"),
                preferences={"demo_account": True}
            )
            db.add(candidate_user)
            db.commit()
            db.refresh(candidate_user)
            
            # Create candidate profile
            candidate_profile = Candidate(
                user_id=candidate_user.id,
                skills=["Python", "JavaScript", "React", "FastAPI"],
                experience_years=3,
                preferred_roles=["Software Engineer", "Full Stack Developer"],
                career_goals="Join a FAANG company as Senior Software Engineer"
            )
            db.add(candidate_profile)
            print("✅ Demo candidate created: candidate@demo.com / demo123")
        
        if not existing_recruiter:
            # Create demo recruiter
            recruiter_user = User(
                email="recruiter@demo.com",
                full_name="Demo Recruiter",
                user_type="recruiter",
                password_hash=AuthService.get_password_hash("demo123"),
                preferences={"demo_account": True}
            )
            db.add(recruiter_user)
            db.commit()
            db.refresh(recruiter_user)
            
            # Create demo job posting
            job_posting = JobPosting(
                recruiter_id=recruiter_user.id,
                title="Senior Software Engineer",
                company="TechCorp Demo",
                description="Join our team as a Senior Software Engineer...",
                requirements=["Python", "React", "PostgreSQL", "Docker"],
                salary_range="$120,000 - $160,000",
                location="San Francisco, CA",
                remote_ok=True,
                employment_type="full-time",
                experience_level="senior"
            )
            db.add(job_posting)
            print("✅ Demo recruiter created: recruiter@demo.com / demo123")
        
        db.commit()
        
        if not existing_candidate and not existing_recruiter:
            print("✅ Demo data created successfully")
        elif existing_candidate or existing_recruiter:
            print("ℹ️  Demo users already exist")
            
    except Exception as e:
        print(f"❌ Failed to create demo data: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    """Main initialization function."""
    print("🚀 Initializing Portia AI Job Platform Database...")
    print(f"📍 Database URL: {settings.DATABASE_URL}")
    
    # Create database connection
    create_database()
    
    # Create tables
    create_tables()
    
    # Create demo data
    create_demo_data()
    
    print("🎉 Database initialization completed!")
    print("\n📋 Demo Accounts:")
    print("   Candidate: candidate@demo.com / demo123")
    print("   Recruiter: recruiter@demo.com / demo123")
    print("\n🌐 Access the application:")
    print("   Frontend: http://localhost:5173")
    print("   Backend API: http://localhost:8000")
    print("   API Docs: http://localhost:8000/docs")

if __name__ == "__main__":
    main()
