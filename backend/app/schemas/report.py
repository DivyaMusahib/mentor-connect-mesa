from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class TranscriptSegmentResponse(BaseModel):
    id: str
    segment_index: int
    speaker: str
    text: str
    start_time_ms: int
    end_time_ms: int

    model_config = ConfigDict(from_attributes=True)


class TranscriptResponse(BaseModel):
    id: str
    booking_id: str
    provider: str
    raw_text: str
    duration_seconds: int
    word_count: int
    status: str
    segments: List[TranscriptSegmentResponse] = []
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReportEvidenceItem(BaseModel):
    id: Optional[str] = None
    insight_index: int
    quote: str
    timestamp_seconds: int
    speaker: Optional[str] = None
    relevance_note: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class KeyInsightWithEvidence(BaseModel):
    insight: str
    evidence: Optional[ReportEvidenceItem] = None


class ActionItemResponse(BaseModel):
    id: str
    booking_id: str
    user_id: str
    title: str
    description: str
    deliverable: Optional[str] = None
    priority: str  # high | medium | low
    due_date: Optional[datetime] = None
    is_completed: bool
    completed_at: Optional[datetime] = None
    sort_order: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ActionItemUpdate(BaseModel):
    is_completed: Optional[bool] = None
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None


class PostCallReportResponse(BaseModel):
    id: str
    booking_id: str
    transcript_id: Optional[str] = None
    summary_points: List[str] = Field(..., description="3-4 meaningful summary points")
    key_insights: List[KeyInsightWithEvidence] = Field(..., description="Insights grounded in the transcript with evidence links")
    what_to_work_on: List[str] = Field(..., description="2-3 concrete skill or career artifact improvements")
    next_milestone: str = Field(..., description="Measurable next milestone")
    open_questions: List[str] = Field(..., description="Unresolved issues worth exploring")
    action_items: List[ActionItemResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
