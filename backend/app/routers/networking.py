# Networking API Router
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

from app.database import get_db
from app.models import User, NetworkingContact
from app.schemas import NetworkingContactResponse, NetworkingContactCreate
from app.services.auth import get_current_active_user

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/expand")
async def expand_network(
    expansion_data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Expand professional network by reaching out to contacts."""
    try:
        target_companies = expansion_data.get("target_companies", [])
        target_roles = expansion_data.get("target_roles", [])
        message_template = expansion_data.get("message_template", "")
        max_connections_per_day = expansion_data.get("max_connections_per_day", 5)
        
        if not target_companies and not target_roles:
            raise HTTPException(status_code=400, detail="At least one target company or role is required")
        
        if not message_template:
            raise HTTPException(status_code=400, detail="Message template is required")
        
        # Start background task for network expansion
        background_tasks.add_task(
            process_network_expansion,
            current_user.id,
            target_companies,
            target_roles,
            message_template,
            max_connections_per_day,
            db
        )
        
        logger.info(f"Started network expansion for user {current_user.id}")
        
        return {
            "message": "Network expansion started successfully",
            "target_companies": target_companies,
            "target_roles": target_roles,
            "max_connections_per_day": max_connections_per_day,
            "estimated_contacts": min(len(target_companies) * 3, max_connections_per_day),
            "next_steps": [
                "AI will find relevant contacts at target companies",
                "Personalized messages will be sent based on your template",
                "Connection requests will be tracked",
                "Follow-up reminders will be scheduled"
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start network expansion: {e}")
        raise HTTPException(status_code=500, detail="Failed to start network expansion")

@router.get("/contacts")
async def get_networking_contacts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status_filter: Optional[str] = Query(None),
    company_filter: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user's networking contacts with optional filters."""
    try:
        query = db.query(NetworkingContact).filter(
            NetworkingContact.user_id == current_user.id
        )
        
        # Apply filters
        if status_filter and status_filter != 'all':
            query = query.filter(NetworkingContact.status == status_filter)
        
        if company_filter:
            query = query.filter(NetworkingContact.company.ilike(f"%{company_filter}%"))
        
        # Order by most recent first
        query = query.order_by(NetworkingContact.contacted_date.desc())
        
        contacts = query.offset(skip).limit(limit).all()
        
        logger.info(f"Retrieved {len(contacts)} networking contacts for user {current_user.id}")
        return contacts
        
    except Exception as e:
        logger.error(f"Failed to get networking contacts: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve networking contacts")

@router.post("/contacts", response_model=NetworkingContactResponse)
async def create_networking_contact(
    contact_data: NetworkingContactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new networking contact."""
    try:
        db_contact = NetworkingContact(
            user_id=current_user.id,
            contact_name=contact_data.contact_name,
            contact_title=contact_data.contact_title,
            company=contact_data.company,
            linkedin_url=contact_data.linkedin_url,
            email=contact_data.email,
            contact_method=contact_data.contact_method,
            status="pending",
            message_sent=contact_data.message_sent,
            contacted_date=datetime.utcnow(),
            notes=contact_data.notes
        )
        
        db.add(db_contact)
        db.commit()
        db.refresh(db_contact)
        
        logger.info(f"Created networking contact for {contact_data.contact_name} at {contact_data.company}")
        return db_contact
        
    except Exception as e:
        logger.error(f"Failed to create networking contact: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create networking contact")

@router.put("/contacts/{contact_id}")
async def update_networking_contact(
    contact_id: int,
    updates: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a networking contact."""
    try:
        contact = db.query(NetworkingContact).filter(
            NetworkingContact.id == contact_id,
            NetworkingContact.user_id == current_user.id
        ).first()
        
        if not contact:
            raise HTTPException(status_code=404, detail="Networking contact not found")
        
        # Update fields
        for field, value in updates.items():
            if hasattr(contact, field):
                setattr(contact, field, value)
        
        # Set response date if status changed to responded
        if updates.get("status") == "responded" and not contact.response_date:
            contact.response_date = datetime.utcnow()
        
        db.commit()
        db.refresh(contact)
        
        logger.info(f"Updated networking contact {contact_id} for user {current_user.id}")
        return contact
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update networking contact: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update networking contact")

@router.get("/stats")
async def get_networking_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get networking statistics for the user."""
    try:
        contacts = db.query(NetworkingContact).filter(
            NetworkingContact.user_id == current_user.id
        ).all()
        
        stats = {
            "total_contacts": len(contacts),
            "pending": len([c for c in contacts if c.status == "pending"]),
            "connected": len([c for c in contacts if c.status == "connected"]),
            "responded": len([c for c in contacts if c.status == "responded"]),
            "no_response": len([c for c in contacts if c.status == "no_response"]),
        }
        
        # Calculate response rate
        stats["response_rate"] = round(
            ((stats["connected"] + stats["responded"]) / stats["total_contacts"] * 100)
            if stats["total_contacts"] > 0 else 0, 1
        )
        
        # Recent activity (last 30 days)
        recent_date = datetime.utcnow() - timedelta(days=30)
        recent_contacts = [c for c in contacts if c.contacted_date >= recent_date]
        stats["recent_contacts"] = len(recent_contacts)
        
        # Top companies
        company_counts = {}
        for contact in contacts:
            if contact.company:
                company_counts[contact.company] = company_counts.get(contact.company, 0) + 1
        
        stats["top_companies"] = [
            {"company": comp, "count": count}
            for comp, count in sorted(company_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
        
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get networking stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get networking statistics")

@router.get("/suggestions")
async def get_networking_suggestions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get AI-powered networking suggestions."""
    try:
        # Mock networking suggestions
        suggestions = {
            "recommended_contacts": [
                {
                    "name": "Sarah Johnson",
                    "title": "Senior Engineering Manager",
                    "company": "TechCorp Inc",
                    "linkedin_url": "https://linkedin.com/in/sarah-johnson",
                    "mutual_connections": 3,
                    "match_score": 92,
                    "reason": "Works at target company, similar background",
                    "suggested_message": "Hi Sarah, I noticed we have mutual connections and I'm interested in opportunities at TechCorp..."
                },
                {
                    "name": "Michael Chen",
                    "title": "Principal Software Engineer",
                    "company": "StartupXYZ",
                    "linkedin_url": "https://linkedin.com/in/michael-chen",
                    "mutual_connections": 1,
                    "match_score": 87,
                    "reason": "Similar technical skills, active in Python community",
                    "suggested_message": "Hi Michael, I saw your recent post about Python best practices and found it very insightful..."
                }
            ],
            "networking_tips": [
                "Personalize your connection requests with specific details",
                "Follow up within a week of sending initial message",
                "Engage with their content before reaching out",
                "Offer value or assistance in your initial message"
            ],
            "optimal_timing": {
                "best_days": ["Tuesday", "Wednesday", "Thursday"],
                "best_times": ["9-11 AM", "2-4 PM"],
                "timezone": "Based on target contacts' locations"
            }
        }
        
        return suggestions
        
    except Exception as e:
        logger.error(f"Failed to get networking suggestions: {e}")
        raise HTTPException(status_code=500, detail="Failed to get networking suggestions")

async def process_network_expansion(
    user_id: int,
    target_companies: List[str],
    target_roles: List[str],
    message_template: str,
    max_connections_per_day: int,
    db: Session
):
    """Background task to process network expansion."""
    try:
        logger.info(f"Processing network expansion for user {user_id}")
        
        # Mock network expansion logic
        # In a real implementation, this would:
        # 1. Search LinkedIn for contacts at target companies
        # 2. Filter by target roles
        # 3. Send personalized connection requests
        # 4. Track responses
        
        # Simulate finding and contacting people
        mock_contacts = []
        
        for company in target_companies[:max_connections_per_day]:
            contact_data = {
                "user_id": user_id,
                "contact_name": f"Professional at {company}",
                "contact_title": target_roles[0] if target_roles else "Software Engineer",
                "company": company,
                "linkedin_url": f"https://linkedin.com/in/professional-{company.lower().replace(' ', '-')}",
                "contact_method": "linkedin",
                "status": "pending",
                "message_sent": message_template,
                "contacted_date": datetime.utcnow(),
                "notes": f"Auto-contacted via network expansion for {company}"
            }
            
            db_contact = NetworkingContact(**contact_data)
            db.add(db_contact)
            mock_contacts.append(contact_data)
        
        db.commit()
        
        logger.info(f"Network expansion completed: contacted {len(mock_contacts)} people for user {user_id}")
        
    except Exception as e:
        logger.error(f"Network expansion processing failed for user {user_id}: {e}")
        db.rollback()
