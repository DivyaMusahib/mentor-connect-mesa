from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, ConfigDict, Field


class ChatSessionCreate(BaseModel):
    title: Optional[str] = "Career Diagnosis Session"
    candidate_mentor_id: Optional[str] = None  # If student clicked "Check Fit with AI" on a mentor


class ChatMessageCreate(BaseModel):
    content: str


class ChatMessageResponse(BaseModel):
    id: str
    session_id: str
    sender: str  # "user" | "assistant" | "system"
    content: str
    metadata_json: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExplainableMatch(BaseModel):
    mentor_id: str
    mentor_name: str
    domain: Optional[str] = None
    company: Optional[str] = None
    fit_score: float = Field(..., description="Transparent domain and skill overlap heuristic (0.0 to 1.0)")
    why_matched: str = Field(..., description="Clear explanation of why this mentor fits the diagnosed problem")
    relevant_verified_expertise: List[str] = Field(..., description="Verified expertise fields from the dataset")
    what_mentor_could_help_with: List[str] = Field(..., description="Concrete topics to discuss with this mentor")
    uncertainties: Optional[str] = Field(None, description="What remains uncertain or where background might differ")
    why_other_may_be_less_suitable: Optional[str] = Field(None, description="Contrast against other available profiles")


class DiagnosticResultResponse(BaseModel):
    id: str
    session_id: str
    user_id: str
    current_situation: Optional[str] = None
    career_goal: Optional[str] = None
    immediate_blocker: Optional[str] = None
    existing_skills: Optional[str] = None
    previous_attempts: Optional[str] = None
    desired_outcome: Optional[str] = None
    constraints: Optional[str] = None
    stage: str  # clarifying | matched | no_exact_match | out_of_scope
    eligible_for_booking: bool
    recommended_mentors: List[ExplainableMatch] = []
    missing_expertise_logged: bool = False
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatSessionResponse(BaseModel):
    id: str
    user_id: str
    title: str
    status: str
    candidate_mentor_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    messages: List[ChatMessageResponse] = []
    diagnostic_result: Optional[DiagnosticResultResponse] = None

    model_config = ConfigDict(from_attributes=True)
