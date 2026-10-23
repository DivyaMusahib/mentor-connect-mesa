import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import (
    Booking,
    Transcript,
    PostCallReport,
    ReportEvidence,
    ActionItem,
    CareerRoadmapStep,
    User,
    utcnow,
)
from app.auth.session import get_current_user
from app.schemas.report import (
    TranscriptResponse,
    TranscriptSegmentResponse,
    PostCallReportResponse,
    KeyInsightWithEvidence,
    ReportEvidenceItem,
    ActionItemResponse,
    ActionItemUpdate,
)

router = APIRouter(tags=["Reports & Action Items"])


@router.get("/bookings/{booking_id}/transcript", response_model=TranscriptResponse)
def get_booking_transcript(
    booking_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve full meeting transcript and timestamped speaker segments."""
    booking = (
        db.query(Booking)
        .filter(Booking.id == booking_id, Booking.user_id == user.id)
        .first()
    )
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found.",
        )

    transcript = booking.transcript
    if not transcript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transcript not yet available for this booking.",
        )

    segments = [
        TranscriptSegmentResponse.model_validate(s)
        for s in sorted(transcript.segments, key=lambda x: x.segment_index)
    ]

    return TranscriptResponse(
        id=transcript.id,
        booking_id=transcript.booking_id,
        provider=transcript.provider,
        raw_text=transcript.raw_text,
        duration_seconds=transcript.duration_seconds,
        word_count=transcript.word_count,
        status=transcript.status,
        segments=segments,
        created_at=transcript.created_at,
    )


@router.get("/bookings/{booking_id}/report", response_model=PostCallReportResponse)
def get_booking_report(
    booking_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve AI Post-Call Report for a completed booking.
    Includes summary points, evidence-linked insights, what to work on, action items, and next milestone.
    """
    booking = (
        db.query(Booking)
        .filter(Booking.id == booking_id, Booking.user_id == user.id)
        .first()
    )
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found.",
        )

    report = booking.post_call_report
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post-call report has not yet been generated for this booking.",
        )

    summary_pts = json.loads(report.summary_points_json) if report.summary_points_json else []
    raw_insights = json.loads(report.key_insights_json) if report.key_insights_json else []
    what_to_work = json.loads(report.what_to_work_on_json) if report.what_to_work_on_json else []
    open_q = json.loads(report.open_questions_json) if report.open_questions_json else []

    # Map evidence items to insights
    evidence_by_idx = {e.insight_index: e for e in report.evidence_items}
    insights_with_evidence = []
    for idx, item in enumerate(raw_insights):
        insight_text = item.get("insight") if isinstance(item, dict) else str(item)
        ev_item = evidence_by_idx.get(idx)
        ev_schema = None
        if ev_item:
            ev_schema = ReportEvidenceItem(
                id=ev_item.id,
                insight_index=ev_item.insight_index,
                quote=ev_item.quote,
                timestamp_seconds=ev_item.timestamp_seconds,
                speaker=ev_item.speaker,
                relevance_note=ev_item.relevance_note,
            )
        insights_with_evidence.append(
            KeyInsightWithEvidence(insight=insight_text, evidence=ev_schema)
        )

    action_items_resp = [
        ActionItemResponse.model_validate(ai)
        for ai in sorted(booking.action_items, key=lambda x: x.sort_order)
    ]

    return PostCallReportResponse(
        id=report.id,
        booking_id=report.booking_id,
        transcript_id=report.transcript_id,
        summary_points=summary_pts,
        key_insights=insights_with_evidence,
        what_to_work_on=what_to_work,
        next_milestone=report.next_milestone,
        open_questions=open_q,
        action_items=action_items_resp,
        created_at=report.created_at,
        updated_at=report.updated_at,
    )


@router.get("/action-items", response_model=List[ActionItemResponse])
def list_student_action_items(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve all persisted action items across all mentorship sessions for the student."""
    items = (
        db.query(ActionItem)
        .filter(ActionItem.user_id == user.id)
        .order_by(ActionItem.is_completed.asc(), ActionItem.created_at.desc())
        .all()
    )
    return [ActionItemResponse.model_validate(ai) for ai in items]


@router.patch("/action-items/{action_item_id}", response_model=ActionItemResponse)
def update_action_item(
    action_item_id: str,
    payload: ActionItemUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update action item completion status, priority, or due date.
    Syncs with career progress memory and roadmap.
    """
    item = (
        db.query(ActionItem)
        .filter(ActionItem.id == action_item_id, ActionItem.user_id == user.id)
        .first()
    )
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action item not found.",
        )

    if payload.is_completed is not None:
        item.is_completed = payload.is_completed
        item.completed_at = utcnow() if payload.is_completed else None

        # Update linked roadmap step if present
        linked_step = db.query(CareerRoadmapStep).filter(CareerRoadmapStep.linked_action_item_id == item.id).first()
        if linked_step:
            linked_step.is_completed = payload.is_completed

    if payload.title is not None:
        item.title = payload.title
    if payload.description is not None:
        item.description = payload.description
    if payload.priority is not None:
        item.priority = payload.priority
    if payload.due_date is not None:
        item.due_date = payload.due_date

    db.commit()
    db.refresh(item)
    return ActionItemResponse.model_validate(item)
