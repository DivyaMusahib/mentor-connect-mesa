import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    Index,
)
from sqlalchemy.orm import relationship
from app.database import Base


def utcnow() -> datetime:
    """Return timezone-aware current UTC time."""
    return datetime.now(timezone.utc)


def ensure_utc(dt: Optional[datetime]) -> Optional[datetime]:
    """Ensure datetime is timezone-aware UTC datetime for safe cross-database comparisons."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def generate_uuid() -> str:
    """Generate a 32-character hex UUID string."""
    return uuid.uuid4().hex


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    google_id = Column(String(128), unique=True, index=True, nullable=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    avatar_url = Column(String(512), nullable=True)
    role = Column(String(32), default="student", nullable=False)  # "student" | "admin"
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    # Relationships
    sessions = relationship("ApplicationSession", back_populates="user", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="user", cascade="all, delete-orphan")
    action_items = relationship("ActionItem", back_populates="user", cascade="all, delete-orphan")
    career_goals = relationship("CareerGoal", back_populates="user", cascade="all, delete-orphan")
    career_milestones = relationship("CareerMilestone", back_populates="user", cascade="all, delete-orphan")
    roadmap_steps = relationship("CareerRoadmapStep", back_populates="user", cascade="all, delete-orphan")


class ApplicationSession(Base):
    __tablename__ = "application_sessions"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    is_revoked = Column(Boolean, default=False, nullable=False)
    user_agent = Column(String(512), nullable=True)
    ip_address = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    last_accessed_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    user = relationship("User", back_populates="sessions")


class Mentor(Base):
    __tablename__ = "mentors"

    mentor_id = Column(String(16), primary_key=True)  # M001 - M050
    name = Column(String(255), nullable=False)
    contact = Column(String(64), nullable=True)
    email = Column(String(255), nullable=True)
    linkedin = Column(String(512), nullable=True)
    city = Column(String(128), nullable=True)
    domain = Column(String(255), nullable=True)
    company = Column(String(255), nullable=True)
    master_sector = Column(String(255), nullable=True)
    sectors_of_expertise = Column(Text, nullable=True)
    roles_of_expertise = Column(Text, nullable=True)
    seniority = Column(String(64), nullable=True)
    ai_native = Column(String(32), nullable=True)
    built_ai_product = Column(String(64), nullable=True)
    ai_sub_domain = Column(String(128), nullable=True)
    ai_tools_of_expertise = Column(Text, nullable=True)
    tableau = Column(String(32), nullable=True)
    hubspot = Column(String(32), nullable=True)
    google_analytics = Column(String(32), nullable=True)
    jira = Column(String(32), nullable=True)
    excel = Column(String(32), nullable=True)
    mixpanel = Column(String(32), nullable=True)
    quality_of_mentorship = Column(String(64), nullable=True)
    activities_participated = Column(String(64), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    bookings = relationship("Booking", back_populates="mentor")


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), default="Career Diagnosis Session", nullable=False)
    status = Column(String(32), default="clarifying", nullable=False)  # clarifying | matched | no_exact_match | out_of_scope
    candidate_mentor_id = Column(String(16), nullable=True)  # optional mentor selected in directory
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan", order_by="ChatMessage.created_at")
    diagnostic_result = relationship("DiagnosticResult", back_populates="session", uselist=False, cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    sender = Column(String(32), nullable=False)  # "user" | "assistant" | "system"
    content = Column(Text, nullable=False)
    metadata_json = Column(Text, nullable=True)  # JSON for structured assistant data / stage
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    session = relationship("ChatSession", back_populates="messages")


class DiagnosticResult(Base):
    __tablename__ = "diagnostic_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("chat_sessions.id", ondelete="CASCADE"), unique=True, nullable=False)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    current_situation = Column(Text, nullable=True)
    career_goal = Column(Text, nullable=True)
    immediate_blocker = Column(Text, nullable=True)
    existing_skills = Column(Text, nullable=True)
    previous_attempts = Column(Text, nullable=True)
    desired_outcome = Column(Text, nullable=True)
    constraints = Column(Text, nullable=True)
    stage = Column(String(32), default="clarifying", nullable=False)  # clarifying | matched | no_exact_match | out_of_scope
    eligible_for_booking = Column(Boolean, default=False, nullable=False)
    recommended_mentor_ids = Column(Text, nullable=True)  # JSON list of strings e.g. ["M042", "M030"]
    match_explanations_json = Column(Text, nullable=True)  # JSON structured explanations
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    session = relationship("ChatSession", back_populates="diagnostic_result")
    bookings = relationship("Booking", back_populates="diagnostic")


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    mentor_id = Column(String(16), ForeignKey("mentors.mentor_id"), nullable=False, index=True)
    diagnostic_id = Column(String(36), ForeignKey("diagnostic_results.id"), nullable=True)
    scheduled_at = Column(DateTime(timezone=True), nullable=False, index=True)
    duration_minutes = Column(Integer, default=45, nullable=False)
    timezone = Column(String(64), default="Asia/Kolkata", nullable=False)
    # Status: pending | confirmed | rescheduled | cancelled | completed | no_show
    status = Column(String(32), default="pending", nullable=False, index=True)
    meet_link = Column(String(512), nullable=True)
    calendar_event_id = Column(String(255), nullable=True)
    idempotency_key = Column(String(64), unique=True, index=True, nullable=False)
    reschedule_token = Column(String(64), unique=True, index=True, nullable=True)
    reschedule_token_expires_at = Column(DateTime(timezone=True), nullable=True)
    cancel_reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    user = relationship("User", back_populates="bookings")
    mentor = relationship("Mentor", back_populates="bookings")
    diagnostic = relationship("DiagnosticResult", back_populates="bookings")
    calendar_event = relationship("CalendarEvent", back_populates="booking", uselist=False, cascade="all, delete-orphan")
    pre_call_brief = relationship("PreCallBrief", back_populates="booking", uselist=False, cascade="all, delete-orphan")
    transcript = relationship("Transcript", back_populates="booking", uselist=False, cascade="all, delete-orphan")
    post_call_report = relationship("PostCallReport", back_populates="booking", uselist=False, cascade="all, delete-orphan")
    action_items = relationship("ActionItem", back_populates="booking", cascade="all, delete-orphan")
    email_logs = relationship("EmailLog", back_populates="booking", cascade="all, delete-orphan")
    automation_events = relationship("AutomationEvent", back_populates="booking", cascade="all, delete-orphan")


class CalendarEvent(Base):
    __tablename__ = "calendar_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    booking_id = Column(String(36), ForeignKey("bookings.id", ondelete="CASCADE"), unique=True, nullable=False)
    calendar_id = Column(String(255), default="primary", nullable=False)
    event_id = Column(String(255), nullable=False)
    status = Column(String(64), default="confirmed", nullable=False)
    html_link = Column(String(512), nullable=True)
    meet_link = Column(String(512), nullable=True)
    summary = Column(String(255), nullable=True)
    raw_response_json = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    booking = relationship("Booking", back_populates="calendar_event")


class PreCallBrief(Base):
    __tablename__ = "pre_call_briefs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    booking_id = Column(String(36), ForeignKey("bookings.id", ondelete="CASCADE"), unique=True, nullable=False)
    student_context_summary = Column(Text, nullable=False)
    current_blocker = Column(Text, nullable=False)
    key_questions_json = Column(Text, nullable=False)  # JSON list of exactly 3 questions
    recommended_preparation = Column(Text, nullable=False)
    desired_outcome = Column(Text, nullable=False)
    suggested_agenda_json = Column(Text, nullable=False)  # JSON list of agenda items
    checklist_json = Column(Text, nullable=True)  # JSON list of actionable prep steps
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    booking = relationship("Booking", back_populates="pre_call_brief")


class Transcript(Base):
    __tablename__ = "transcripts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    booking_id = Column(String(36), ForeignKey("bookings.id", ondelete="CASCADE"), unique=True, nullable=False)
    provider = Column(String(64), default="simulation", nullable=False)  # recall_ai | fireflies | simulation
    provider_task_id = Column(String(128), nullable=True)
    raw_text = Column(Text, nullable=False)
    duration_seconds = Column(Integer, default=0, nullable=False)
    word_count = Column(Integer, default=0, nullable=False)
    # Status: pending | processing | completed | failed
    status = Column(String(32), default="completed", nullable=False)
    webhook_payload_json = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    booking = relationship("Booking", back_populates="transcript")
    segments = relationship("TranscriptSegment", back_populates="transcript", cascade="all, delete-orphan", order_by="TranscriptSegment.segment_index")


class TranscriptSegment(Base):
    __tablename__ = "transcript_segments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    transcript_id = Column(String(36), ForeignKey("transcripts.id", ondelete="CASCADE"), nullable=False, index=True)
    segment_index = Column(Integer, nullable=False)
    speaker = Column(String(64), nullable=False)
    text = Column(Text, nullable=False)
    start_time_ms = Column(Integer, default=0, nullable=False)
    end_time_ms = Column(Integer, default=0, nullable=False)

    transcript = relationship("Transcript", back_populates="segments")
    evidence_items = relationship("ReportEvidence", back_populates="segment")


class PostCallReport(Base):
    __tablename__ = "post_call_reports"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    booking_id = Column(String(36), ForeignKey("bookings.id", ondelete="CASCADE"), unique=True, nullable=False)
    transcript_id = Column(String(36), ForeignKey("transcripts.id"), nullable=True)
    summary_points_json = Column(Text, nullable=False)  # 3-4 points
    key_insights_json = Column(Text, nullable=False)  # Insights grounded in transcript
    what_to_work_on_json = Column(Text, nullable=False)  # 2-3 skill/artifact improvements
    next_milestone = Column(Text, nullable=False)
    open_questions_json = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    booking = relationship("Booking", back_populates="post_call_report")
    evidence_items = relationship("ReportEvidence", back_populates="report", cascade="all, delete-orphan")


class ReportEvidence(Base):
    __tablename__ = "report_evidence"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    report_id = Column(String(36), ForeignKey("post_call_reports.id", ondelete="CASCADE"), nullable=False, index=True)
    insight_index = Column(Integer, nullable=False)
    transcript_segment_id = Column(String(36), ForeignKey("transcript_segments.id", ondelete="SET NULL"), nullable=True)
    quote = Column(Text, nullable=False)
    timestamp_seconds = Column(Integer, default=0, nullable=False)
    speaker = Column(String(64), nullable=True)
    relevance_note = Column(Text, nullable=True)

    report = relationship("PostCallReport", back_populates="evidence_items")
    segment = relationship("TranscriptSegment", back_populates="evidence_items")


class ActionItem(Base):
    __tablename__ = "action_items"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    booking_id = Column(String(36), ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    deliverable = Column(String(255), nullable=True)
    priority = Column(String(16), default="medium", nullable=False)  # high | medium | low
    due_date = Column(DateTime(timezone=True), nullable=True)
    is_completed = Column(Boolean, default=False, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    sort_order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    booking = relationship("Booking", back_populates="action_items")
    user = relationship("User", back_populates="action_items")


class CareerGoal(Base):
    __tablename__ = "career_goals"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    objective = Column(Text, nullable=False)
    current_blocker = Column(Text, nullable=True)
    next_milestone = Column(Text, nullable=True)
    target_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(32), default="active", nullable=False)  # active | achieved | revised
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    user = relationship("User", back_populates="career_goals")


class CareerMilestone(Base):
    __tablename__ = "career_milestones"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    booking_id = Column(String(36), ForeignKey("bookings.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    achieved_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    milestone_type = Column(String(64), default="session_completed", nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    user = relationship("User", back_populates="career_milestones")


class CareerRoadmapStep(Base):
    __tablename__ = "career_roadmap_steps"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    time_estimate = Column(String(64), nullable=True)
    order_index = Column(Integer, default=0, nullable=False)
    is_completed = Column(Boolean, default=False, nullable=False)
    linked_action_item_id = Column(String(36), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    user = relationship("User", back_populates="roadmap_steps")


class EmailLog(Base):
    __tablename__ = "email_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    booking_id = Column(String(36), ForeignKey("bookings.id", ondelete="CASCADE"), nullable=True, index=True)
    email_type = Column(String(64), nullable=False)  # booking_confirmation | reminder_24h | reminder_30m | reschedule_magic_link | post_call_followup
    recipient_email = Column(String(255), nullable=False)
    recipient_role = Column(String(32), nullable=False)  # student | mentor
    status = Column(String(32), default="pending", nullable=False)  # pending | accepted | delivered | failed | simulated
    subject = Column(String(255), nullable=False)
    body_preview = Column(Text, nullable=True)
    provider_message_id = Column(String(128), nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    booking = relationship("Booking", back_populates="email_logs")


class AutomationEvent(Base):
    __tablename__ = "automation_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    booking_id = Column(String(36), ForeignKey("bookings.id", ondelete="CASCADE"), nullable=True, index=True)
    event_type = Column(String(64), nullable=False)  # calendar_create | email_send | reminder_schedule | transcript_sync | etc.
    n8n_execution_id = Column(String(128), nullable=True)
    status = Column(String(32), default="pending", nullable=False)  # pending | processing | completed | failed | simulated
    idempotency_key = Column(String(64), index=True, nullable=True)
    request_payload_json = Column(Text, nullable=True)
    response_payload_json = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    booking = relationship("Booking", back_populates="automation_events")


class UnmatchedMentorGap(Base):
    __tablename__ = "unmatched_mentor_gaps"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    chat_session_id = Column(String(36), ForeignKey("chat_sessions.id", ondelete="SET NULL"), nullable=True)
    requested_domain = Column(String(255), nullable=True)
    requested_sector = Column(String(255), nullable=True)
    requested_skills = Column(Text, nullable=True)
    student_query = Column(Text, nullable=False)
    diagnostic_summary = Column(Text, nullable=True)
    status = Column(String(32), default="unreviewed", nullable=False)  # unreviewed | reviewed
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String(64), nullable=False)  # login | logout | book_meeting | reschedule | cancel | etc.
    resource_type = Column(String(64), nullable=False)
    resource_id = Column(String(64), nullable=True)
    metadata_json = Column(Text, nullable=True)
    ip_address = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
