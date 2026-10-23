from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class CareerGoalResponse(BaseModel):
    id: str
    user_id: str
    objective: str
    current_blocker: Optional[str] = None
    next_milestone: Optional[str] = None
    target_date: Optional[datetime] = None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CareerGoalUpdate(BaseModel):
    objective: Optional[str] = None
    current_blocker: Optional[str] = None
    next_milestone: Optional[str] = None
    target_date: Optional[datetime] = None
    status: Optional[str] = None


class CareerRoadmapStepResponse(BaseModel):
    id: str
    user_id: str
    title: str
    description: str
    time_estimate: Optional[str] = None
    order_index: int
    is_completed: bool
    linked_action_item_id: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CareerRoadmapStepUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    time_estimate: Optional[str] = None
    is_completed: Optional[bool] = None


class CareerRoadmapResponse(BaseModel):
    goal: Optional[CareerGoalResponse] = None
    steps: List[CareerRoadmapStepResponse] = []
    completion_percentage: float = 0.0


class TimelineEvent(BaseModel):
    id: str
    event_type: str  # problem_identified | mentor_matched | meeting_booked | meeting_completed | action_items_created | milestone_achieved
    title: str
    description: str
    timestamp: datetime
    metadata: Optional[dict] = None
