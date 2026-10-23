from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class PreCallBriefResponse(BaseModel):
    id: str
    booking_id: str
    student_context_summary: str
    current_blocker: str
    key_questions_to_cover: List[str] = Field(..., min_length=3, max_length=3, description="Exactly three concrete discussion questions")
    recommended_preparation: str
    desired_outcome: str
    suggested_agenda: List[str]
    checklist: List[str] = []
    meeting_scheduled_at: Optional[datetime] = None
    meeting_timezone: Optional[str] = None
    meet_link: Optional[str] = None
    mentor_name: Optional[str] = None
    mentor_domain: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
