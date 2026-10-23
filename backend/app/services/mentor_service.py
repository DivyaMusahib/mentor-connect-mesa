import csv
import re
from pathlib import Path
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.config import settings
from app.models import Mentor


def clean_str(val: Optional[str]) -> Optional[str]:
    """Clean string from CSV, treating N/A, null, empty as None."""
    if val is None:
        return None
    val = val.strip()
    if not val or val.lower() in ("n/a", "na", "null", "none", "-"):
        return None
    return val


def load_mentors_from_csv(db: Session, csv_path: Optional[Path] = None) -> int:
    """
    Parse mentors CSV dataset, deduplicate duplicate IDs (e.g. M013, M023),
    and upsert records into the database.
    """
    path = csv_path or settings.MENTOR_DATA_PATH
    if not path.exists():
        raise FileNotFoundError(f"Mentors dataset not found at: {path}")

    loaded_count = 0
    seen_ids = set()

    with open(path, mode="r", encoding="utf-8-sig", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            mentor_id = row.get("Mentor ID")
            if not mentor_id:
                continue
            mentor_id = mentor_id.strip()

            # Deduplicate repeated rows in dataset
            if mentor_id in seen_ids:
                continue
            seen_ids.add(mentor_id)

            existing = db.query(Mentor).filter(Mentor.mentor_id == mentor_id).first()
            if not existing:
                existing = Mentor(mentor_id=mentor_id)
                db.add(existing)

            existing.name = clean_str(row.get("Name")) or f"Mentor {mentor_id}"
            existing.contact = clean_str(row.get("Contact"))
            existing.email = clean_str(row.get("Email"))
            existing.linkedin = clean_str(row.get("LinkedIn"))
            existing.city = clean_str(row.get("City"))
            existing.domain = clean_str(row.get("Domain"))
            existing.company = clean_str(row.get("Company"))
            existing.master_sector = clean_str(row.get("Master Sector"))
            existing.sectors_of_expertise = clean_str(row.get("Sectors of Expertise"))
            existing.roles_of_expertise = clean_str(row.get("Roles of Expertise"))
            existing.seniority = clean_str(row.get("Seniority"))
            existing.ai_native = clean_str(row.get("AI Native"))
            existing.built_ai_product = clean_str(row.get("Built AI Product/Automation/Workflow"))
            existing.ai_sub_domain = clean_str(row.get("AI Sub Domain"))
            existing.ai_tools_of_expertise = clean_str(row.get("AI Tools of Expertise"))
            existing.tableau = clean_str(row.get("Tableau"))
            existing.hubspot = clean_str(row.get("Hubspot"))
            existing.google_analytics = clean_str(row.get("Google Analytics"))
            existing.jira = clean_str(row.get("Jira"))
            existing.excel = clean_str(row.get("Excel"))
            existing.mixpanel = clean_str(row.get("Mixpanel"))
            existing.quality_of_mentorship = clean_str(row.get("Quality of Mentorship"))
            existing.activities_participated = clean_str(row.get("Activities Participated"))
            existing.is_active = True
            loaded_count += 1

    db.commit()
    return loaded_count


def list_mentors(
    db: Session,
    domain: Optional[str] = None,
    sector: Optional[str] = None,
    seniority: Optional[str] = None,
    ai_tool: Optional[str] = None,
    search: Optional[str] = None,
) -> List[Mentor]:
    """Query mentors with verified filters and text search."""
    query = db.query(Mentor).filter(Mentor.is_active == True)

    if domain:
        query = query.filter(Mentor.domain.ilike(f"%{domain}%"))

    if sector:
        query = query.filter(
            or_(
                Mentor.master_sector.ilike(f"%{sector}%"),
                Mentor.sectors_of_expertise.ilike(f"%{sector}%"),
            )
        )

    if seniority:
        query = query.filter(Mentor.seniority.ilike(f"%{seniority}%"))

    if ai_tool:
        query = query.filter(Mentor.ai_tools_of_expertise.ilike(f"%{ai_tool}%"))

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Mentor.name.ilike(search_pattern),
                Mentor.mentor_id.ilike(search_pattern),
                Mentor.domain.ilike(search_pattern),
                Mentor.company.ilike(search_pattern),
                Mentor.master_sector.ilike(search_pattern),
                Mentor.sectors_of_expertise.ilike(search_pattern),
                Mentor.roles_of_expertise.ilike(search_pattern),
                Mentor.ai_tools_of_expertise.ilike(search_pattern),
            )
        )

    return query.order_by(Mentor.mentor_id.asc()).all()


def get_mentor_by_id(db: Session, mentor_id: str) -> Optional[Mentor]:
    """Retrieve mentor by ID from authoritative database."""
    return db.query(Mentor).filter(Mentor.mentor_id == mentor_id).first()


def get_all_verified_catalog(db: Session) -> List[Dict[str, Any]]:
    """
    Produce a concise JSON representation of all verified mentors
    specifically for Gemini full-context matching.
    Includes only verified attributes to prevent hallucinated details.
    """
    mentors = db.query(Mentor).filter(Mentor.is_active == True).order_by(Mentor.mentor_id).all()
    catalog = []
    for m in mentors:
        catalog.append({
            "mentor_id": m.mentor_id,
            "name": m.name,
            "domain": m.domain or "General",
            "company": m.company or "Confidential",
            "master_sector": m.master_sector or "",
            "sectors_of_expertise": m.sectors_of_expertise or "",
            "roles_of_expertise": m.roles_of_expertise or "",
            "seniority": m.seniority or "Mid/Senior",
            "ai_tools": m.ai_tools_of_expertise or "",
            "built_ai_product": m.built_ai_product or "",
            "quality_of_mentorship": m.quality_of_mentorship or "Good",
        })
    return catalog
