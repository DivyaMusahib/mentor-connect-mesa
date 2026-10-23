import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from app.models import (
    Booking,
    Transcript,
    TranscriptSegment,
    PostCallReport,
    AuditEvent,
    utcnow,
)
from app.services.report_service import generate_and_save_post_call_report

logger = logging.getLogger(__name__)


def generate_sample_transcript_dialogue(
    student_name: str,
    mentor_name: str,
    domain: str,
    company: str,
) -> List[Dict[str, Any]]:
    """Generate realistic timestamped dialogue segments for a 45-minute mentorship meeting."""
    return [
        {
            "speaker": mentor_name,
            "text": f"Hey {student_name}, great to meet you! I went through your pre-call brief and saw your questions about transitioning into {domain}. Let's jump right into your main blocker.",
            "start_time_ms": 0,
            "end_time_ms": 25000,
        },
        {
            "speaker": student_name,
            "text": f"Thanks so much for taking the time, {mentor_name}. Right now I'm building projects, but when I look at job descriptions for {domain} at companies like {company or 'leading startups'}, I'm not sure if my projects look like toy tutorials or real production systems.",
            "start_time_ms": 25000,
            "end_time_ms": 65000,
        },
        {
            "speaker": mentor_name,
            "text": "That is the single most common hurdle. Don't just show me the code runs; explain why you picked this pattern over alternatives and what broke when you tested edge cases. That's what hiring managers look for.",
            "start_time_ms": 65000,
            "end_time_ms": 115000,
        },
        {
            "speaker": mentor_name,
            "text": "For instance, in automated workflows, tools like n8n and Make provide immediate high leverage when paired with clean API design. Mastering automated event contracts makes you 5x more productive than just building isolated endpoints.",
            "start_time_ms": 115000,
            "end_time_ms": 165000,
        },
        {
            "speaker": student_name,
            "text": "That makes a lot of sense. So in my architecture documentation, should I specifically write out why I kept Google OAuth in FastAPI and delegated calendar automation to n8n?",
            "start_time_ms": 165000,
            "end_time_ms": 195000,
        },
        {
            "speaker": mentor_name,
            "text": "Yes, absolutely! Having Architecture Decision Records is gold. Also, if an evaluator can trigger a simulated failure and watch your app recover gracefully, you're in the top 5% of candidates.",
            "start_time_ms": 195000,
            "end_time_ms": 240000,
        },
        {
            "speaker": mentor_name,
            "text": "Let's agree on three deliverables for this week: write 3 ADRs, build automated integration smoke tests, and record a concise walkthrough demo of the end-to-end journey.",
            "start_time_ms": 240000,
            "end_time_ms": 270000,
        },
        {
            "speaker": student_name,
            "text": "Understood! I will finish these deliverables within the next 7 days and update my progress tracker. Thank you for this clarity!",
            "start_time_ms": 270000,
            "end_time_ms": 290000,
        },
    ]


async def ingest_transcript(
    db: Session,
    booking: Booking,
    provider: str,
    raw_text: str,
    segments: Optional[List[Dict[str, Any]]] = None,
    provider_task_id: Optional[str] = None,
    webhook_payload: Optional[Dict[str, Any]] = None,
) -> Tuple[Transcript, PostCallReport]:
    """
    Ingest transcript from webhook or simulation, store segments,
    transition booking status to 'completed', and trigger AI Post-Call Report.
    """
    existing = db.query(Transcript).filter(Transcript.booking_id == booking.id).first()
    if existing:
        report = db.query(PostCallReport).filter(PostCallReport.booking_id == booking.id).first()
        return existing, report

    duration_sec = 2700  # 45 mins default
    word_count = len(raw_text.split())

    transcript = Transcript(
        booking_id=booking.id,
        provider=provider,
        provider_task_id=provider_task_id,
        raw_text=raw_text,
        duration_seconds=duration_sec,
        word_count=word_count,
        status="completed",
        webhook_payload_json=json.dumps(webhook_payload) if webhook_payload else None,
    )
    db.add(transcript)
    db.commit()
    db.refresh(transcript)

    if segments:
        for idx, seg in enumerate(segments):
            db_segment = TranscriptSegment(
                transcript_id=transcript.id,
                segment_index=idx,
                speaker=seg.get("speaker", "Participant"),
                text=seg.get("text", ""),
                start_time_ms=seg.get("start_time_ms", 0),
                end_time_ms=seg.get("end_time_ms", 0),
            )
            db.add(db_segment)
        db.commit()

    booking.status = "completed"
    audit = AuditEvent(
        user_id=booking.user_id,
        action="complete_meeting",
        resource_type="booking",
        resource_id=booking.id,
        metadata_json=json.dumps({"provider": provider, "word_count": word_count}),
    )
    db.add(audit)
    db.commit()
    db.refresh(booking)

    report = await generate_and_save_post_call_report(
        db=db,
        booking=booking,
        transcript=transcript,
    )

    return transcript, report


async def simulate_completed_meeting(
    db: Session,
    booking: Booking,
) -> Tuple[Transcript, PostCallReport]:
    """
    Evaluator simulation method: Simulates a completed meeting by generating realistic
    timestamped dialogue segments, persisting transcript, and running the real AI report pipeline.
    """
    user = booking.user
    mentor = booking.mentor

    dialogue_segments = generate_sample_transcript_dialogue(
        student_name=user.full_name,
        mentor_name=mentor.name,
        domain=mentor.domain or "Business & Technology",
        company=mentor.company or "Industry Leader",
    )

    raw_text = "\n\n".join([f"[{s['speaker']}]: {s['text']}" for s in dialogue_segments])

    return await ingest_transcript(
        db=db,
        booking=booking,
        provider="simulation",
        raw_text=raw_text,
        segments=dialogue_segments,
        provider_task_id=f"sim_task_{booking.id[:8]}",
        webhook_payload={"simulation": True, "booking_id": booking.id},
    )
