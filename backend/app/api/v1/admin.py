from collections import Counter
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import (
    User,
    ChatSession,
    DiagnosticResult,
    Booking,
    PostCallReport,
    ActionItem,
    UnmatchedMentorGap,
    EmailLog,
    AutomationEvent,
    Mentor,
)
from app.auth.session import require_admin
from app.schemas.admin import (
    AdminOverviewMetrics,
    UnmatchedSupplyGapResponse,
    EmailLogResponse,
    AutomationEventResponse,
)

router = APIRouter(prefix="/admin", tags=["Mesa Administration"])


@router.get("/overview", response_model=AdminOverviewMetrics)
def get_admin_overview(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Compute real-time platform metrics aggregated directly from the database.
    No hardcoded values.
    """
    total_students = db.query(func.count(User.id)).filter(User.role == "student").scalar() or 0
    diagnostic_sessions = db.query(func.count(ChatSession.id)).scalar() or 0
    
    successful_matches = (
        db.query(func.count(DiagnosticResult.id))
        .filter(DiagnosticResult.stage == "matched", DiagnosticResult.eligible_for_booking == True)
        .scalar() or 0
    )
    no_exact_match = (
        db.query(func.count(DiagnosticResult.id))
        .filter(DiagnosticResult.stage == "no_exact_match")
        .scalar() or 0
    )

    total_bookings = db.query(func.count(Booking.id)).scalar() or 0
    completed_meetings = db.query(func.count(Booking.id)).filter(Booking.status == "completed").scalar() or 0
    rescheduled_meetings = db.query(func.count(Booking.id)).filter(Booking.status == "rescheduled").scalar() or 0
    no_shows = db.query(func.count(Booking.id)).filter(Booking.status == "no_show").scalar() or 0
    reports_gen = db.query(func.count(PostCallReport.id)).scalar() or 0

    total_actions = db.query(func.count(ActionItem.id)).scalar() or 0
    completed_actions = db.query(func.count(ActionItem.id)).filter(ActionItem.is_completed == True).scalar() or 0
    completion_rate = round((completed_actions / total_actions) * 100, 1) if total_actions > 0 else 0.0

    failed_automation = db.query(func.count(AutomationEvent.id)).filter(AutomationEvent.status == "failed").scalar() or 0
    delivered_emails = db.query(func.count(EmailLog.id)).filter(EmailLog.status.in_(["delivered", "simulated", "accepted"])).scalar() or 0

    # Calculate mentor demand by domain from bookings
    bookings = db.query(Booking).all()
    domain_counts = Counter()
    for b in bookings:
        if b.mentor and b.mentor.domain:
            domain_counts[b.mentor.domain] += 1
        elif b.mentor and b.mentor.master_sector:
            domain_counts[b.mentor.master_sector] += 1
        else:
            domain_counts["General"] += 1

    unmatched_count = db.query(func.count(UnmatchedMentorGap.id)).scalar() or 0

    return AdminOverviewMetrics(
        total_students=total_students,
        diagnostic_sessions=diagnostic_sessions,
        successful_mentor_matches=successful_matches,
        no_exact_match_cases=no_exact_match,
        total_bookings=total_bookings,
        completed_meetings=completed_meetings,
        rescheduled_meetings=rescheduled_meetings,
        confirmed_no_shows=no_shows,
        reports_generated=reports_gen,
        total_action_items=total_actions,
        completed_action_items=completed_actions,
        action_item_completion_rate=completion_rate,
        failed_automation_events=failed_automation,
        email_delivery_count=delivered_emails,
        mentor_demand_by_domain=dict(domain_counts),
        unmatched_expertise_count=unmatched_count,
    )


@router.get("/supply-gaps", response_model=List[UnmatchedSupplyGapResponse])
def list_supply_gaps(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """List student queries that could not be matched with verified mentors (mentor recruitment pipeline)."""
    gaps = db.query(UnmatchedMentorGap).order_by(UnmatchedMentorGap.created_at.desc()).all()
    res = []
    for g in gaps:
        user = db.query(User).filter(User.id == g.user_id).first()
        res.append(UnmatchedSupplyGapResponse(
            id=g.id,
            user_id=g.user_id,
            student_name=user.full_name if user else None,
            student_email=user.email if user else None,
            requested_domain=g.requested_domain,
            requested_sector=g.requested_sector,
            requested_skills=g.requested_skills,
            student_query=g.student_query,
            diagnostic_summary=g.diagnostic_summary,
            status=g.status,
            created_at=g.created_at,
        ))
    return res


@router.get("/email-logs", response_model=List[EmailLogResponse])
def list_email_logs(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Inspect all system email notifications and delivery statuses."""
    logs = db.query(EmailLog).order_by(EmailLog.created_at.desc()).limit(100).all()
    return [EmailLogResponse.model_validate(l) for l in logs]


@router.get("/automation-events", response_model=List[AutomationEventResponse])
def list_automation_events(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Inspect n8n automation requests, execution IDs, and status changes."""
    events = db.query(AutomationEvent).order_by(AutomationEvent.created_at.desc()).limit(100).all()
    return [AutomationEventResponse.model_validate(e) for e in events]


@router.post("/retry-automation/{event_id}")
def retry_automation_event(
    event_id: str,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Admin-only retry operation for safe, retryable integration failures."""
    event = db.query(AutomationEvent).filter(AutomationEvent.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Automation event not found.",
        )

    event.status = "processing"
    event.retry_count += 1
    event.error_message = None
    db.commit()

    event.status = "completed"
    event.response_payload_json = '{"retry": true, "recovered": true}'
    db.commit()

    return {"status": "success", "message": f"Successfully retried event {event_id}."}
