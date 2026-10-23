from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import (
    CareerGoal,
    CareerMilestone,
    CareerRoadmapStep,
    ActionItem,
    Booking,
    ChatSession,
    User,
    utcnow,
)
from app.auth.session import get_current_user
from app.schemas.career import (
    CareerGoalResponse,
    CareerGoalUpdate,
    CareerRoadmapStepResponse,
    CareerRoadmapStepUpdate,
    CareerRoadmapResponse,
    TimelineEvent,
)

router = APIRouter(prefix="/career", tags=["Career Progress & Roadmap"])


@router.get("/roadmap", response_model=CareerRoadmapResponse)
def get_career_roadmap(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve current student's personalized career roadmap, goals,
    and progress against agreed mentorship action items.
    """
    goal = (
        db.query(CareerGoal)
        .filter(CareerGoal.user_id == user.id, CareerGoal.status == "active")
        .order_by(CareerGoal.created_at.desc())
        .first()
    )
    if not goal:
        goal = CareerGoal(
            user_id=user.id,
            objective="Transition into High-Impact Technology / Product Leadership Role",
            current_blocker="Bridging practical engineering execution gaps and portfolio credibility",
            next_milestone="Complete 3 production-grade project deliverables and review with mentor",
            status="active",
        )
        db.add(goal)
        db.commit()
        db.refresh(goal)

    steps = (
        db.query(CareerRoadmapStep)
        .filter(CareerRoadmapStep.user_id == user.id)
        .order_by(CareerRoadmapStep.order_index.asc())
        .all()
    )

    # If steps are empty, seed sensible default steps
    if not steps:
        defaults = [
            ("Diagnose Core Blocker with AI Advisor", "Complete an interactive career diagnostic session and evaluate mentor fit.", "Day 1", True),
            ("Conduct 45-Min Mentorship Session", "Engage with verified industry mentor and align on actionable priorities.", "Week 1", False),
            ("Implement Agreed Action Items", "Build and push code deliverables identified in post-call report.", "Week 2-3", False),
            ("Validate Architecture & Deliverables", "Re-engage with mentor or submit portfolio for Mesa review.", "Week 4", False),
        ]
        for idx, (title, desc, estimate, comp) in enumerate(defaults):
            s = CareerRoadmapStep(
                user_id=user.id,
                title=title,
                description=desc,
                time_estimate=estimate,
                order_index=idx,
                is_completed=comp,
            )
            db.add(s)
            steps.append(s)
        db.commit()

    completed_count = sum(1 for s in steps if s.is_completed)
    pct = round((completed_count / len(steps)) * 100, 1) if steps else 0.0

    return CareerRoadmapResponse(
        goal=CareerGoalResponse.model_validate(goal),
        steps=[CareerRoadmapStepResponse.model_validate(s) for s in steps],
        completion_percentage=pct,
    )


@router.patch("/roadmap/goal", response_model=CareerGoalResponse)
def update_career_goal(
    payload: CareerGoalUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update student career objective, current blocker, or target date."""
    goal = (
        db.query(CareerGoal)
        .filter(CareerGoal.user_id == user.id, CareerGoal.status == "active")
        .order_by(CareerGoal.created_at.desc())
        .first()
    )
    if not goal:
        goal = CareerGoal(user_id=user.id, objective="Career Acceleration", status="active")
        db.add(goal)

    if payload.objective is not None:
        goal.objective = payload.objective
    if payload.current_blocker is not None:
        goal.current_blocker = payload.current_blocker
    if payload.next_milestone is not None:
        goal.next_milestone = payload.next_milestone
    if payload.target_date is not None:
        goal.target_date = payload.target_date
    if payload.status is not None:
        goal.status = payload.status

    db.commit()
    db.refresh(goal)
    return CareerGoalResponse.model_validate(goal)


@router.patch("/roadmap/steps/{step_id}", response_model=CareerRoadmapStepResponse)
def update_roadmap_step(
    step_id: str,
    payload: CareerRoadmapStepUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update status or description of a specific roadmap step."""
    step = (
        db.query(CareerRoadmapStep)
        .filter(CareerRoadmapStep.id == step_id, CareerRoadmapStep.user_id == user.id)
        .first()
    )
    if not step:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Roadmap step not found.",
        )

    if payload.title is not None:
        step.title = payload.title
    if payload.description is not None:
        step.description = payload.description
    if payload.time_estimate is not None:
        step.time_estimate = payload.time_estimate
    if payload.is_completed is not None:
        step.is_completed = payload.is_completed

    db.commit()
    db.refresh(step)
    return CareerRoadmapStepResponse.model_validate(step)


@router.get("/timeline", response_model=List[TimelineEvent])
def get_career_timeline(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve chronological student career journey timeline:
    Problem identified -> Mentor matched -> Meeting booked -> Meeting completed -> Action items created -> Milestone achieved.
    Strictly isolated per student.
    """
    timeline: List[TimelineEvent] = []

    chat_sessions = (
        db.query(ChatSession)
        .filter(ChatSession.user_id == user.id)
        .order_by(ChatSession.created_at.asc())
        .all()
    )
    for cs in chat_sessions:
        diag = cs.diagnostic_result
        timeline.append(TimelineEvent(
            id=f"chat_{cs.id}",
            event_type="problem_identified",
            title="Career Blocker Diagnosed with AI Advisor",
            description=diag.immediate_blocker if diag and diag.immediate_blocker else cs.title,
            timestamp=cs.created_at,
            metadata={"session_id": cs.id, "stage": cs.status},
        ))
        if diag and diag.eligible_for_booking:
            timeline.append(TimelineEvent(
                id=f"matched_{cs.id}",
                event_type="mentor_matched",
                title="Verified Industry Mentors Matched",
                description="AI recommended high-fit mentors based on verified domain overlap.",
                timestamp=diag.created_at,
                metadata={"mentor_ids": diag.recommended_mentor_ids},
            ))

    bookings = (
        db.query(Booking)
        .filter(Booking.user_id == user.id)
        .order_by(Booking.created_at.asc())
        .all()
    )
    for b in bookings:
        m_name = b.mentor.name if b.mentor else b.mentor_id
        timeline.append(TimelineEvent(
            id=f"book_{b.id}",
            event_type="meeting_booked",
            title=f"Mentorship Session Booked with {m_name}",
            description=f"Scheduled for {b.scheduled_at.strftime('%b %d, %Y at %I:%M %p %Z')}. Pre-call brief prepared.",
            timestamp=b.created_at,
            metadata={"booking_id": b.id, "meet_link": b.meet_link},
        ))
        if b.status == "completed":
            timeline.append(TimelineEvent(
                id=f"comp_{b.id}",
                event_type="meeting_completed",
                title=f"Session Completed with {m_name}",
                description="Meeting concluded. AI transcript analyzed and evidence-linked report generated.",
                timestamp=b.updated_at,
                metadata={"booking_id": b.id},
            ))

    milestones = (
        db.query(CareerMilestone)
        .filter(CareerMilestone.user_id == user.id)
        .order_by(CareerMilestone.achieved_at.asc())
        .all()
    )
    for m in milestones:
        timeline.append(TimelineEvent(
            id=f"ms_{m.id}",
            event_type="milestone_achieved",
            title=m.title,
            description=m.description or "Target milestone achieved.",
            timestamp=m.achieved_at,
            metadata={"milestone_id": m.id},
        ))

    # Sort chronological
    timeline.sort(key=lambda x: x.timestamp, reverse=True)
    return timeline
