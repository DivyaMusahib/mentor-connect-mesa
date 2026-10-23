from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict


class AdminOverviewMetrics(BaseModel):
    total_students: int
    diagnostic_sessions: int
    successful_mentor_matches: int
    no_exact_match_cases: int
    total_bookings: int
    completed_meetings: int
    rescheduled_meetings: int
    confirmed_no_shows: int
    reports_generated: int
    total_action_items: int
    completed_action_items: int
    action_item_completion_rate: float
    failed_automation_events: int
    email_delivery_count: int
    mentor_demand_by_domain: Dict[str, int] = {}
    unmatched_expertise_count: int = 0


class UnmatchedSupplyGapResponse(BaseModel):
    id: str
    user_id: str
    student_name: Optional[str] = None
    student_email: Optional[str] = None
    requested_domain: Optional[str] = None
    requested_sector: Optional[str] = None
    requested_skills: Optional[str] = None
    student_query: str
    diagnostic_summary: Optional[str] = None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EmailLogResponse(BaseModel):
    id: str
    booking_id: Optional[str] = None
    email_type: str
    recipient_email: str
    recipient_role: str
    status: str
    subject: str
    body_preview: Optional[str] = None
    provider_message_id: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AutomationEventResponse(BaseModel):
    id: str
    booking_id: Optional[str] = None
    event_type: str
    n8n_execution_id: Optional[str] = None
    status: str
    idempotency_key: Optional[str] = None
    request_payload_json: Optional[str] = None
    response_payload_json: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class IntegrationHealthStatus(BaseModel):
    google_oauth_configured: bool
    gemini_ai_configured: bool
    n8n_cloud_configured: bool
    n8n_base_url: str
    transcription_provider: str
    database_connected: bool
    evaluator_demo_mode: bool
