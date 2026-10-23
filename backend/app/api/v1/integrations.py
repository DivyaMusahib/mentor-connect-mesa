import json
import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.config import settings
from app.database import get_db
from app.models import Booking, AutomationEvent, CalendarEvent, utcnow
from app.schemas.integrations import N8NMeetingCreationCallback, TranscriptionWebhookPayload
from app.schemas.admin import IntegrationHealthStatus
from app.services.transcription_service import ingest_transcript

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/integrations", tags=["Integrations & Webhooks"])


def _verify_webhook_secret(secret_header: str = Header(None, alias="X-FastAPI-Key")):
    """Verify shared secret on incoming callbacks from n8n or transcription providers."""
    if not secret_header or secret_header != settings.FASTAPI_WEBHOOK_SECRET:
        if not settings.ENABLE_EVALUATOR_DEMO:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized webhook signature or key.",
            )


@router.post("/n8n/meeting-created")
async def n8n_meeting_created_callback(
    payload: N8NMeetingCreationCallback,
    db: Session = Depends(get_db),
    _auth=Depends(_verify_webhook_secret),
):
    """
    Asynchronous callback from n8n after Google Calendar event and Meet link creation.
    Updates the booking and calendar event state idempotently.
    """
    booking = db.query(Booking).filter(Booking.id == payload.booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking '{payload.booking_id}' not found.",
        )

    if payload.status == "success":
        booking.status = "confirmed"
        if payload.meet_link:
            booking.meet_link = payload.meet_link
        if payload.calendar_event_id:
            booking.calendar_event_id = payload.calendar_event_id

            cal_event = db.query(CalendarEvent).filter(CalendarEvent.booking_id == booking.id).first()
            if cal_event:
                cal_event.event_id = payload.calendar_event_id
                cal_event.meet_link = payload.meet_link
                cal_event.status = "confirmed"
    else:
        booking.status = "pending"  # Preserve recoverable state
        logger.error(f"n8n reported meeting creation failure for booking {booking.id}: {payload.error_message}")

    # Update automation event
    auto_event = (
        db.query(AutomationEvent)
        .filter(AutomationEvent.booking_id == booking.id, AutomationEvent.event_type == "create_meeting")
        .order_by(AutomationEvent.created_at.desc())
        .first()
    )
    if auto_event:
        auto_event.status = "completed" if payload.status == "success" else "failed"
        auto_event.n8n_execution_id = payload.execution_id
        auto_event.error_message = payload.error_message

    db.commit()
    return {"status": "accepted", "booking_id": booking.id}


@router.post("/transcription/webhook")
async def transcription_provider_webhook(
    payload: TranscriptionWebhookPayload,
    db: Session = Depends(get_db),
    _auth=Depends(_verify_webhook_secret),
):
    """
    Webhook endpoint for transcription providers (Fathom or configured provider).
    Ingests meeting transcript, stores segments, and automatically initiates AI report generation.
    """
    booking = db.query(Booking).filter(Booking.id == payload.booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking '{payload.booking_id}' not found.",
        )

    if payload.status == "completed" and payload.transcript_text:
        transcript, report = await ingest_transcript(
            db=db,
            booking=booking,
            provider=payload.provider,
            raw_text=payload.transcript_text,
            segments=payload.segments,
            provider_task_id=payload.provider_task_id,
        )
        return {
            "status": "success",
            "transcript_id": transcript.id,
            "report_id": report.id,
        }
    else:
        logger.warning(f"Transcription failed or empty for booking {booking.id}: {payload.error_message}")
        return {"status": "received", "detail": payload.error_message}


@router.api_route("/health", methods=["GET", "HEAD"], response_model=IntegrationHealthStatus)
def get_integration_health(db: Session = Depends(get_db)):
    """Report real-time connectivity and configuration status of all external services."""
    db_connected = False
    try:
        db.execute(text("SELECT 1"))
        db_connected = True
    except Exception:
        db_connected = False

    return IntegrationHealthStatus(
        google_oauth_configured=bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET),
        gemini_ai_configured=bool(settings.GEMINI_API_KEY),
        n8n_cloud_configured=bool(settings.N8N_BASE_URL and "app.n8n.cloud" in settings.N8N_BASE_URL),
        n8n_base_url=settings.N8N_BASE_URL,
        transcription_provider=settings.TRANSCRIPTION_PROVIDER,
        database_connected=db_connected,
        evaluator_demo_mode=settings.ENABLE_EVALUATOR_DEMO,
    )
