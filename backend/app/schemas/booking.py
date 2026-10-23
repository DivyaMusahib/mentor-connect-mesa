from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class TimeSlot(BaseModel):
    start_time: datetime
    end_time: datetime
    available: bool = True
    reason: Optional[str] = None


class AvailabilityResponse(BaseModel):
    mentor_id: str
    calendar_id: str
    date: str  # YYYY-MM-DD
    timezone: str = "Asia/Kolkata"
    slots: List[TimeSlot] = []
    source: str = "n8n_host_calendar"  # "n8n_host_calendar" | "simulated"


class BookingCreateRequest(BaseModel):
    mentor_id: str = Field(..., description="Target mentor ID (e.g. M042)")
    diagnostic_id: Optional[str] = Field(None, description="Diagnostic result unlocking this booking")
    scheduled_at: datetime = Field(..., description="Requested start time in ISO 8601 UTC")
    duration_minutes: int = Field(45, ge=15, le=120)
    timezone: str = Field("Asia/Kolkata")
    idempotency_key: str = Field(..., description="Unique client idempotency token")


class RescheduleRequest(BaseModel):
    new_scheduled_at: datetime
    timezone: Optional[str] = "Asia/Kolkata"
    reason: Optional[str] = None


class RescheduleWithTokenRequest(BaseModel):
    reschedule_token: str
    new_scheduled_at: datetime
    timezone: Optional[str] = "Asia/Kolkata"
    reason: Optional[str] = None


class CancelRequest(BaseModel):
    reason: Optional[str] = None


class BookingSummaryResponse(BaseModel):
    id: str
    user_id: str
    mentor_id: str
    mentor_name: Optional[str] = None
    mentor_domain: Optional[str] = None
    mentor_company: Optional[str] = None
    scheduled_at: datetime
    duration_minutes: int
    timezone: str
    status: str  # pending | confirmed | rescheduled | cancelled | completed | no_show
    meet_link: Optional[str] = None
    has_brief: bool = False
    has_transcript: bool = False
    has_report: bool = False
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BookingDetailResponse(BookingSummaryResponse):
    calendar_event_id: Optional[str] = None
    cancel_reason: Optional[str] = None
    reschedule_token: Optional[str] = None
    reschedule_token_expires_at: Optional[datetime] = None
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
