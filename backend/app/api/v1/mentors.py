from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Mentor
from app.schemas.mentors import MentorSummary, MentorDetail
from app.services.mentor_service import list_mentors, get_mentor_by_id

router = APIRouter(prefix="/mentors", tags=["Mentors"])


@router.get("", response_model=List[MentorSummary])
def get_mentors(
    domain: Optional[str] = Query(None, description="Filter by mentor domain"),
    sector: Optional[str] = Query(None, description="Filter by sector of expertise"),
    seniority: Optional[str] = Query(None, description="Filter by seniority level"),
    ai_tool: Optional[str] = Query(None, description="Filter by AI tools of expertise"),
    search: Optional[str] = Query(None, description="Full-text search in name, domain, company, tools"),
    db: Session = Depends(get_db),
):
    """
    Search and filter verified mentors from the authoritative 50-mentor dataset.
    Returns only verified dataset fields.
    """
    return list_mentors(
        db=db,
        domain=domain,
        sector=sector,
        seniority=seniority,
        ai_tool=ai_tool,
        search=search,
    )


@router.get("/{mentor_id}", response_model=MentorDetail)
def get_mentor(mentor_id: str, db: Session = Depends(get_db)):
    """Retrieve detailed profile of a verified mentor by ID."""
    mentor = get_mentor_by_id(db, mentor_id)
    if not mentor or not mentor.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mentor with ID '{mentor_id}' not found in the verified catalogue.",
        )
    return mentor
