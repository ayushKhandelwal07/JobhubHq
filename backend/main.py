# Portia AI Job Application Platform - CLEAN & MINIMAL
# Maximum Portia Integration with Google Gemini

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
import logging

# Core imports
from app.config import settings
from app.database import engine, get_db, Base
from app.models import User, Candidate
from app.schemas import UserCreate, UserResponse, LoginRequest, Token
from app.services.auth import AuthService, get_current_active_user

# Portia AI Integration
from app.agents import PORTIA_AGENTS, get_agent_info
from app.portia_client import portia_client

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Portia AI Job Application Platform",
    description="Maximum Portia AI Integration with Google Gemini - AgentHack 2025",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS - Allow all origins in development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
auth_service = AuthService()

# Initialize Portia-powered agents
logger.info("🚀 Initializing Portia AI agents with Google Gemini...")
portia_agents = PORTIA_AGENTS
logger.info(f"✅ Initialized {len(portia_agents)} Portia agents: {list(portia_agents.keys())}")

if portia_client:
    logger.info("✅ Portia client initialized with maximum tool integration")
else:
    logger.warning("⚠️ Portia client not initialized - check configuration")

# Include all API routers
from app.routers import (
    portia_ai, applications, jobs, candidates, analytics, 
    career_roadmap, auto_apply, networking, integrations,
    upload, admin, recruiter
)

# Core feature routers
app.include_router(applications.router, prefix="/api/applications", tags=["applications"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])
app.include_router(candidates.router, prefix="/api/candidates", tags=["candidates"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(career_roadmap.router, prefix="/api/career-roadmap", tags=["career-roadmap"])
app.include_router(auto_apply.router, prefix="/api/auto-apply", tags=["auto-apply"])
app.include_router(networking.router, prefix="/api/networking", tags=["networking"])
app.include_router(integrations.router, prefix="/api/integrations", tags=["integrations"])
app.include_router(upload.router, prefix="/api/upload", tags=["upload"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(recruiter.router, prefix="/api/recruiter", tags=["recruiter"])

# AI-powered features
app.include_router(portia_ai.router, prefix="/api/portia", tags=["portia-ai"])

# ============================================================================
# CORE ENDPOINTS
# ============================================================================

@app.get("/api/health")
async def health_check():
    """Health check endpoint with Portia status."""
    portia_status = "active" if portia_client else "inactive"
    gemini_configured = bool(settings.GOOGLE_GEMINI_API_KEY)
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "2.0.0",
        "portia_status": portia_status,
        "gemini_configured": gemini_configured,
        "agents_count": len(portia_agents),
        "features": [
            "Maximum Portia Integration",
            "Google Gemini Primary LLM",
            "Human-in-the-loop workflows",
            "Multi-tool orchestration",
            "Browser automation",
            "Gmail/LinkedIn/GitHub tools"
        ]
    }

# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.post("/api/auth/register", response_model=UserResponse)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = auth_service.get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        user_type=user_data.user_type,
        password_hash=hashed_password,
        preferences=user_data.preferences or {}
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create candidate profile if user is a candidate
    if user_data.user_type == "candidate":
        candidate = Candidate(user_id=db_user.id)
        db.add(candidate)
        db.commit()
    
    logger.info(f"✅ New {user_data.user_type} registered: {user_data.email}")
    return db_user

@app.post("/api/auth/login", response_model=Token)
async def login_user(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Login user and return access token."""
    user = auth_service.authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth_service.create_access_token(data={"sub": user.email})
    logger.info(f"✅ User logged in: {user.email}")
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information."""
    return current_user

# ============================================================================
# SYSTEM STATUS
# ============================================================================

@app.get("/api/system/status")
async def get_system_status(current_user: User = Depends(get_current_active_user)):
    """Get comprehensive system status."""
    return {
        "user": {
            "email": current_user.email,
            "type": current_user.user_type,
            "id": current_user.id
        },
        "portia": {
            "client_active": portia_client is not None,
            "agents_available": len(portia_agents),
            "agent_names": list(portia_agents.keys()),
            "agent_info": get_agent_info()
        },
        "configuration": {
            "gemini_configured": bool(settings.GOOGLE_GEMINI_API_KEY),
            "portia_api_configured": bool(settings.PORTIA_API_KEY),
            "github_configured": bool(settings.GITHUB_TOKEN),
            "gmail_configured": bool(settings.SMTP_USER)
        }
    }

# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with project information."""
    return {
        "project": "Portia AI Job Application Platform",
        "version": "2.0.0",
        "description": "Maximum Portia AI Integration with Google Gemini for AgentHack 2025",
        "features": [
            "🤖 7 Portia-powered AI agents",
            "🧠 Google Gemini as primary LLM",
            "🛠️ Complete tool integration",
            "🌐 Browser automation",
            "👥 Human-in-the-loop workflows"
        ],
        "endpoints": {
            "docs": "/docs",
            "health": "/api/health",
            "auth": "/api/auth/",
            "applications": "/api/applications/",
            "jobs": "/api/jobs/",
            "candidates": "/api/candidates/",
            "analytics": "/api/analytics/",
            "career_roadmap": "/api/career-roadmap/",
            "auto_apply": "/api/auto-apply/",
            "networking": "/api/network/",
            "integrations": "/api/integrations/",
            "upload": "/api/upload/",
            "admin": "/api/admin/",
            "recruiter": "/api/recruiter/",
            "portia_ai": "/api/portia/",
            "system_status": "/api/system/status"
        },
        "hackathon": "AgentHack 2025",
        "portia_integration_score": "10/10"
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Portia AI Job Application Platform...")
    logger.info("AgentHack 2025 - Maximum Portia Integration")
    logger.info("Google Gemini + Portia AI = WINNING COMBINATION!")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=settings.DEBUG)
