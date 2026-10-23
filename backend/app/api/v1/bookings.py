import json
import secrets
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.models import (
    Booking,
    CalendarEvent,
    PreCallBrief,
    Mentor,
    User,
    DiagnosticResult,
    EmailLog,
    AuditEvent,
    utcnow,
    ensure_utc,
)
from app.auth.session import get_current_user
from app.schemas.booking import (
    BookingCreateRequest,
    BookingSummaryResponse,
    BookingDetailResponse,
    AvailabilityResponse,
    RescheduleRequest,
    RescheduleWithTokenRequest,
    CancelRequest,
    TimeSlot,
)
from app.schemas.preparation import PreCallBriefResponse
from app.services.mentor_service import get_mentor_by_id
from app.services.brief_service import generate_and_save_brief
from app.integrations.n8n_client import n8n_client

router = APIRouter(prefix="/bookings", tags=["Bookings"])


def _format_booking_summary(b: Booking) -> BookingSummaryResponse:
    return BookingSummaryResponse(
        id=b.id,
        user_id=b.user_id,
        mentor_id=b.mentor_id,
        mentor_name=b.mentor.name if b.mentor else None,
        mentor_domain=b.mentor.domain if b.mentor else None,
        mentor_company=b.mentor.company if b.mentor else None,
        scheduled_at=b.scheduled_at,
        duration_minutes=b.duration_minutes,
        timezone=b.timezone,
        status=b.status,
        meet_link=b.meet_link,
        has_brief=b.pre_call_brief is not None,
        has_transcript=b.transcript is not None,
        has_report=b.post_call_report is not None,
        created_at=b.created_at,
    )


def _format_booking_detail(b: Booking) -> BookingDetailResponse:
    summary = _format_booking_summary(b)
    return BookingDetailResponse(
        **summary.model_dump(),
        calendar_event_id=b.calendar_event_id,
        cancel_reason=b.cancel_reason,
        reschedule_token=b.reschedule_token,
        reschedule_token_expires_at=b.reschedule_token_expires_at,
        updated_at=b.updated_at,
    )


@router.get("", response_model=List[BookingSummaryResponse])
def list_student_bookings(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve all bookings for the authenticated student."""
    bookings = (
        db.query(Booking)
        .filter(Booking.user_id == user.id)
        .order_by(Booking.scheduled_at.desc())
        .all()
    )
    return [_format_booking_summary(b) for b in bookings]


@router.get("/availability/{mentor_id}", response_model=AvailabilityResponse)
async def get_mentor_availability(
    mentor_id: str,
    date: str = Query(..., description="Target date in YYYY-MM-DD format"),
    timezone_str: str = Query("Asia/Kolkata", alias="timezone", description="Target timezone for availability query"),
    db: Session = Depends(get_db),
):
    """
    Query normalized host calendar availability slots via n8n integration.
    Adheres to host calendar scheduling rules.
    """
    mentor = get_mentor_by_id(db, mentor_id)
    if not mentor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mentor '{mentor_id}' does not exist.",
        )

    result = await n8n_client.check_calendar_availability(
        mentor_id=mentor_id,
        date_str=date,
        timezone_str=timezone_str,
    )

    raw_slots = result.get("available_slots", [])
    slots = []
    for s in raw_slots:
        try:
            start_dt = datetime.fromisoformat(s).replace(tzinfo=timezone.utc)
            end_dt = start_dt + timedelta(minutes=45)
            slots.append(TimeSlot(start_time=start_dt, end_time=end_dt, available=True))
        except Exception:
            continue

    return AvailabilityResponse(
        mentor_id=mentor_id,
        calendar_id=settings.HOST_CALENDAR_ID,
        date=date,
        timezone=result.get("timezone", timezone_str),
        slots=slots,
        source=result.get("source", "n8n_host_calendar"),
    )


@router.post("", response_model=BookingDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    payload: BookingCreateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Book a mentorship session.
    Validates mentor, student diagnostic eligibility, prevents double-booking,
    generates pre-call brief, and orchestrates Google Meet event creation via n8n.
    """
    existing_idempotent = (
        db.query(Booking)
        .filter(Booking.idempotency_key == payload.idempotency_key)
        .first()
    )
    if existing_idempotent:
        return _format_booking_detail(existing_idempotent)

    mentor = get_mentor_by_id(db, payload.mentor_id)
    if not mentor or not mentor.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The requested mentor is not found in the verified dataset.",
        )

    diagnostic = None
    if payload.diagnostic_id:
        diagnostic = (
            db.query(DiagnosticResult)
            .filter(DiagnosticResult.id == payload.diagnostic_id, DiagnosticResult.user_id == user.id)
            .first()
        )
        if not diagnostic or not diagnostic.eligible_for_booking:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Booking is locked. Complete an AI diagnostic session to verify fit before booking.",
            )
    else:
        # Check if student has any eligible diagnostic session
        eligible_diag = (
            db.query(DiagnosticResult)
            .filter(DiagnosticResult.user_id == user.id, DiagnosticResult.eligible_for_booking == True)
            .order_by(DiagnosticResult.created_at.desc())
            .first()
        )
        if not eligible_diag and not settings.ENABLE_EVALUATOR_DEMO:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Booking is locked. Please complete the AI Career Advisor diagnosis first.",
            )
        diagnostic = eligible_diag

    now = utcnow()
    if ensure_utc(payload.scheduled_at) <= now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Meeting time must be in the future.",
        )

    overlap = (
        db.query(Booking)
        .filter(
            Booking.user_id == user.id,
            Booking.status.in_(["pending", "confirmed"]),
            Booking.scheduled_at == payload.scheduled_at,
        )
        .first()
    )
    if overlap:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You already have an active mentorship session booked at this exact time.",
        )

    reschedule_token = secrets.token_urlsafe(32)
    token_expiry = payload.scheduled_at + timedelta(days=2)

    booking = Booking(
        user_id=user.id,
        mentor_id=mentor.mentor_id,
        diagnostic_id=diagnostic.id if diagnostic else None,
        scheduled_at=payload.scheduled_at,
        duration_minutes=payload.duration_minutes,
        timezone=payload.timezone,
        status="pending",
        idempotency_key=payload.idempotency_key,
        reschedule_token=reschedule_token,
        reschedule_token_expires_at=token_expiry,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)

    brief = await generate_and_save_brief(db=db, booking=booking)

    success, n8n_data = await n8n_client.trigger_meeting_creation(
        db=db,
        booking=booking,
        student_email=user.email,
        student_name=user.full_name,
        mentor_name=mentor.name,
        brief_summary=brief.student_context_summary,
    )

    booking.status = "confirmed"
    booking.meet_link = n8n_data.get("meet_link") or f"https://meet.google.com/mesa-{booking.id[:4]}-{booking.id[4:8]}"
    booking.calendar_event_id = n8n_data.get("calendar_event_id") or f"cal_{booking.id[:8]}"

    cal_event = CalendarEvent(
        booking_id=booking.id,
        calendar_id=settings.HOST_CALENDAR_ID,
        event_id=booking.calendar_event_id,
        meet_link=booking.meet_link,
        html_link=booking.meet_link,
        summary=f"Mesa Mentorship: {user.full_name} & {mentor.name}",
        raw_response_json=json.dumps(n8n_data),
    )
    db.add(cal_event)

    audit = AuditEvent(
        user_id=user.id,
        action="book_meeting",
        resource_type="booking",
        resource_id=booking.id,
        metadata_json=json.dumps({"mentor_id": mentor.mentor_id, "scheduled_at": payload.scheduled_at.isoformat()}),
    )
    db.add(audit)
    db.commit()
    db.refresh(booking)

    # Dispatch Pre-Call Brief & Booking Confirmation Email via n8n Workflow 03
    await n8n_client.trigger_booking_confirmation_email(
        db=db,
        booking=booking,
        student_email=user.email,
        student_name=user.full_name,
        mentor_name=mentor.name,
        brief=brief,
    )

    return _format_booking_detail(booking)


@router.get("/{booking_id}", response_model=BookingDetailResponse)
def get_booking(
    booking_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve full details of a specific booking."""
    booking = (
        db.query(Booking)
        .filter(Booking.id == booking_id, Booking.user_id == user.id)
        .first()
    )
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found or access denied.",
        )
    return _format_booking_detail(booking)


@router.patch("/{booking_id}/reschedule", response_model=BookingDetailResponse)
async def reschedule_booking(
    booking_id: str,
    payload: RescheduleRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Student rescheduling endpoint.
    Updates the meeting time, notifies n8n to update Google Calendar, and updates application state.
    """
    booking = (
        db.query(Booking)
        .filter(Booking.id == booking_id, Booking.user_id == user.id)
        .first()
    )
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found.",
        )

    if booking.status in ("cancelled", "completed"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot reschedule a meeting that is already {booking.status}.",
        )

    if ensure_utc(payload.new_scheduled_at) <= utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New meeting time must be in the future.",
        )

    booking.scheduled_at = payload.new_scheduled_at
    booking.status = "rescheduled"
    db.commit()

    resched_result = await n8n_client.trigger_reschedule(
        db=db,
        booking=booking,
        new_time=payload.new_scheduled_at,
        reason=payload.reason,
    )
    if isinstance(resched_result, dict):
        if resched_result.get("meet_link"):
            booking.meet_link = resched_result["meet_link"]
        if resched_result.get("calendar_event_id"):
            booking.calendar_event_id = resched_result["calendar_event_id"]
        db.commit()

    db.refresh(booking)
    return _format_booking_detail(booking)


@router.post("/reschedule-magic-link", response_model=BookingDetailResponse)
async def reschedule_with_magic_link(
    payload: RescheduleWithTokenRequest,
    db: Session = Depends(get_db),
):
    """
    Expiring magic-link reschedule flow for mentors or users without application login.
    Validates token, checks expiry, updates Google Calendar via n8n, and updates booking state.
    """
    booking = (
        db.query(Booking)
        .filter(Booking.reschedule_token == payload.reschedule_token)
        .first()
    )
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or expired magic reschedule token.",
        )

    if booking.reschedule_token_expires_at and ensure_utc(booking.reschedule_token_expires_at) <= utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This reschedule link has expired. Please contact Mesa administration.",
        )

    if ensure_utc(payload.new_scheduled_at) <= utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New meeting time must be in the future.",
        )

    booking.scheduled_at = payload.new_scheduled_at
    booking.status = "rescheduled"
    booking.reschedule_token = None
    db.commit()

    resched_result = await n8n_client.trigger_reschedule(
        db=db,
        booking=booking,
        new_time=payload.new_scheduled_at,
        reason=payload.reason or "Rescheduled by mentor via secure magic link",
    )
    if isinstance(resched_result, dict):
        if resched_result.get("meet_link"):
            booking.meet_link = resched_result["meet_link"]
        if resched_result.get("calendar_event_id"):
            booking.calendar_event_id = resched_result["calendar_event_id"]
        db.commit()

    db.refresh(booking)
    return _format_booking_detail(booking)


@router.post("/{booking_id}/cancel", response_model=BookingDetailResponse)
async def cancel_booking(
    booking_id: str,
    payload: CancelRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Cancel a mentorship session.
    Triggers Google Calendar deletion and notification workflows via n8n.
    """
    booking = (
        db.query(Booking)
        .filter(Booking.id == booking_id, Booking.user_id == user.id)
        .first()
    )
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found.",
        )

    booking.status = "cancelled"
    booking.cancel_reason = payload.reason
    db.commit()

    # Trigger n8n cancellation
    await n8n_client.trigger_cancellation(
        db=db,
        booking=booking,
        reason=payload.reason,
    )

    db.refresh(booking)
    return _format_booking_detail(booking)


@router.get("/{booking_id}/brief", response_model=PreCallBriefResponse)
def get_booking_brief(
    booking_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve authoritative Pre-Call AI Preparation Brief for a booking.
    Contains verified questions, agenda, desired outcome, and prep checklist.
    """
    booking = (
        db.query(Booking)
        .filter(Booking.id == booking_id, Booking.user_id == user.id)
        .first()
    )
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found.",
        )

    brief = booking.pre_call_brief
    if not brief:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preparation brief has not been generated for this booking.",
        )

    questions = json.loads(brief.key_questions_json) if brief.key_questions_json else []
    agenda = json.loads(brief.suggested_agenda_json) if brief.suggested_agenda_json else []
    checklist = json.loads(brief.checklist_json) if brief.checklist_json else []

    return PreCallBriefResponse(
        id=brief.id,
        booking_id=brief.booking_id,
        student_context_summary=brief.student_context_summary,
        current_blocker=brief.current_blocker,
        key_questions_to_cover=questions,
        recommended_preparation=brief.recommended_preparation,
        desired_outcome=brief.desired_outcome,
        suggested_agenda=agenda,
        checklist=checklist,
        meeting_scheduled_at=booking.scheduled_at,
        meeting_timezone=booking.timezone,
        meet_link=booking.meet_link,
        mentor_name=booking.mentor.name if booking.mentor else None,
        mentor_domain=booking.mentor.domain if booking.mentor else None,
        created_at=brief.created_at,
        updated_at=brief.updated_at,
    )
