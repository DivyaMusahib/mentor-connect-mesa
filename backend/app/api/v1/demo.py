import json
import uuid
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.models import (
    User,
    Mentor,
    ChatSession,
    ChatMessage,
    DiagnosticResult,
    Booking,
    CalendarEvent,
    PreCallBrief,
    Transcript,
    PostCallReport,
    ActionItem,
    CareerGoal,
    CareerRoadmapStep,
    CareerMilestone,
    EmailLog,
    AutomationEvent,
    UnmatchedMentorGap,
    AuditEvent,
    utcnow,
)
from app.auth.session import get_current_user
from app.services.brief_service import generate_and_save_brief
from app.services.transcription_service import simulate_completed_meeting

router = APIRouter(prefix="/demo", tags=["Evaluator Demo & Simulation"])


@router.post("/seed")
async def seed_demo_environment(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Seed a rich demo environment for evaluators:
    1. Creates/verifies student and admin accounts.
    2. Seeds an upcoming meeting with pre-call brief.
    3. Seeds a completed meeting with transcript, evidence-linked report, and action items.
    4. Seeds unmatched supply gaps for Mesa recruitment analytics.
    5. Seeds n8n workflow activity and email logs.
    """
    goal = db.query(CareerGoal).filter(CareerGoal.user_id == user.id).first()
    if not goal:
        goal = CareerGoal(
            user_id=user.id,
            objective="Transition into High-Impact AI/Automation Product Management Role",
            current_blocker="Proving real full-stack architecture judgment and workflow automation experience",
            next_milestone="Deploy production-ready Mentor Connect platform with n8n and Google OAuth",
            status="active",
        )
        db.add(goal)

    mentor_42 = db.query(Mentor).filter(Mentor.mentor_id == "M042").first()
    if mentor_42:
        past_booking = (
            db.query(Booking)
            .filter(Booking.user_id == user.id, Booking.mentor_id == "M042", Booking.status == "completed")
            .first()
        )
        if not past_booking:
            past_time = utcnow() - timedelta(days=3)
            past_booking = Booking(
                user_id=user.id,
                mentor_id="M042",
                scheduled_at=past_time,
                duration_minutes=45,
                timezone="Asia/Kolkata",
                status="confirmed",
                meet_link="https://meet.google.com/mesa-m42-demo",
                calendar_event_id="cal_event_demo_m42",
                idempotency_key=f"demo_past_{uuid.uuid4().hex[:8]}",
            )
            db.add(past_booking)
            db.commit()
            db.refresh(past_booking)

            # Generate brief
            await generate_and_save_brief(db=db, booking=past_booking)

            # Simulate meeting completion and report generation
            await simulate_completed_meeting(db=db, booking=past_booking)

    mentor_30 = db.query(Mentor).filter(Mentor.mentor_id == "M030").first()
    if mentor_30:
        upcoming_booking = (
            db.query(Booking)
            .filter(Booking.user_id == user.id, Booking.mentor_id == "M030", Booking.status == "confirmed")
            .first()
        )
        if not upcoming_booking:
            future_time = utcnow() + timedelta(days=2, hours=3)
            upcoming_booking = Booking(
                user_id=user.id,
                mentor_id="M030",
                scheduled_at=future_time,
                duration_minutes=45,
                timezone="Asia/Kolkata",
                status="confirmed",
                meet_link="https://meet.google.com/mesa-m30-live",
                calendar_event_id="cal_event_demo_m30",
                idempotency_key=f"demo_future_{uuid.uuid4().hex[:8]}",
            )
            db.add(upcoming_booking)
            db.commit()
            db.refresh(upcoming_booking)

            # Generate authoritative brief
            await generate_and_save_brief(db=db, booking=upcoming_booking)

            # Log reminder automation event
            auto_event = AutomationEvent(
                booking_id=upcoming_booking.id,
                event_type="reminder_scheduled",
                status="completed",
                idempotency_key=f"remind_sched_{upcoming_booking.id}",
                request_payload_json=json.dumps({"scheduled_reminders": ["24h_before", "30m_before"]}),
                response_payload_json='{"status": "n8n_scheduled", "reminders_active": 2}',
            )
            db.add(auto_event)

    existing_gap = db.query(UnmatchedMentorGap).first()
    if not existing_gap:
        sample_gaps = [
            ("Quantum Computing & Cryptography", "Deeptech", "Qiskit, Post-Quantum Security", "How can I prepare for quantum security roles?"),
            ("Clinical Trial Data Science", "Biotech", "FDA Compliance, Biostatistics", "Transitioning from generic data science into clinical biotech."),
        ]
        for dom, sec, sk, q in sample_gaps:
            db.add(UnmatchedMentorGap(
                user_id=user.id,
                requested_domain=dom,
                requested_sector=sec,
                requested_skills=sk,
                student_query=q,
                diagnostic_summary="Student query falls outside current 50-mentor business & tech dataset.",
                status="unreviewed",
            ))

    db.commit()
    return {"status": "success", "message": "Demo data successfully seeded for evaluation."}


@router.post("/simulate/complete-meeting/{booking_id}")
async def simulate_complete_meeting_endpoint(
    booking_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Evaluator Simulation: Trigger simulated meeting completion for any booking.
    Generates realistic timestamped transcript, runs AI Post-Call Report,
    populates evidence-linked insights, and creates action items.
    """
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found.",
        )

    transcript, report = await simulate_completed_meeting(db=db, booking=booking)
    return {
        "status": "success",
        "simulation": True,
        "booking_id": booking.id,
        "transcript_id": transcript.id,
        "report_id": report.id,
        "message": "Simulated meeting completed. Real AI report and action items generated and persisted.",
    }


@router.post("/simulate/reschedule-conflict/{booking_id}")
async def simulate_mentor_reschedule(
    booking_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Evaluator Simulation: Mentor requests rescheduling due to an urgent conflict."""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found.")

    new_time = booking.scheduled_at + timedelta(days=1, hours=2)
    booking.scheduled_at = new_time
    booking.status = "rescheduled"

    # Log email to student
    email = EmailLog(
        booking_id=booking.id,
        email_type="reschedule_magic_link",
        recipient_email=user.email,
        recipient_role="student",
        status="simulated",
        subject=f"Rescheduled: Mentorship session with {booking.mentor.name}",
        body_preview=f"Your mentor had a calendar conflict. The session was moved to {new_time.strftime('%b %d, %Y at %I:%M %p')}.",
    )
    db.add(email)
    db.commit()

    return {
        "status": "success",
        "simulation": True,
        "new_scheduled_at": new_time.isoformat(),
        "message": "Simulated mentor conflict and automatic reschedule triggered.",
    }


@router.post("/simulate/transcription-failure/{booking_id}")
def simulate_transcription_failure(
    booking_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Evaluator Simulation: Provider fails to generate transcript (test recoverable state)."""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found.")

    auto_event = AutomationEvent(
        booking_id=booking.id,
        event_type="transcription_sync",
        status="failed",
        idempotency_key=f"fail_{booking.id[:8]}",
        error_message="Simulated Transcription Provider 503: Audio recording degraded / insufficient mic quality.",
        retry_count=0,
    )
    db.add(auto_event)
    db.commit()

    return {
        "status": "simulated_failure_recorded",
        "message": "Simulated transcription failure recorded. Inspect under Mesa Admin -> Automation Activity.",
    }


@router.post("/reset")
def reset_demo_database(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Evaluator Simulation: Reset demo data for clean evaluation run."""
    # Delete user's chat sessions, bookings, action items, roadmaps
    db.query(ActionItem).filter(ActionItem.user_id == user.id).delete()
    db.query(CareerRoadmapStep).filter(CareerRoadmapStep.user_id == user.id).delete()
    db.query(CareerMilestone).filter(CareerMilestone.user_id == user.id).delete()
    db.query(Booking).filter(Booking.user_id == user.id).delete()
    db.query(ChatSession).filter(ChatSession.user_id == user.id).delete()
    db.commit()

    return {"status": "success", "message": "Demo data reset successfully for this evaluator session."}
