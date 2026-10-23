from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class N8NOutboundWebhookRequest(BaseModel):
    event_type: str
    schema_version: str = "1.0"
    idempotency_key: str
    resource_id: str
    timestamp: str
    payload: Dict[str, Any]


class N8NMeetingCreationCallback(BaseModel):
    event_type: str = "meeting_created"
    booking_id: str
    status: str = Field(..., description="'success' or 'failure'")
    calendar_event_id: Optional[str] = None
    meet_link: Optional[str] = None
    execution_id: Optional[str] = None
    error_message: Optional[str] = None


class N8NMeetingUpdateCallback(BaseModel):
    event_type: str  # meeting_rescheduled | meeting_cancelled
    booking_id: str
    status: str
    calendar_event_id: Optional[str] = None
    execution_id: Optional[str] = None
    error_message: Optional[str] = None


class TranscriptionWebhookPayload(BaseModel):
    provider: str  # fathom | recall_ai | fireflies | simulation
    provider_task_id: str
    booking_id: str
    status: str  # completed | failed
    transcript_text: Optional[str] = None
    duration_seconds: Optional[int] = 0
    segments: Optional[list] = []
    error_message: Optional[str] = None
