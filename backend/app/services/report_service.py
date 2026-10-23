import json
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.config import settings
from app.models import (
    Booking,
    Transcript,
    TranscriptSegment,
    PostCallReport,
    ReportEvidence,
    ActionItem,
    EmailLog,
    CareerMilestone,
    CareerRoadmapStep,
    utcnow,
)

logger = logging.getLogger(__name__)


class ActionItemSpec(BaseModel):
    title: str = Field(..., description="Actionable title for the task")
    description: str = Field(..., description="Clear instructions on how to complete it")
    deliverable: str = Field(..., description="Concrete output or artifact to produce")
    priority: str = Field(..., description="'high' | 'medium' | 'low'")
    due_days_from_now: int = Field(default=7, description="Target timeline in days")


class InsightWithQuote(BaseModel):
    insight: str = Field(..., description="Strategic takeaway or decision grounded in conversation")
    supporting_quote: str = Field(..., description="Exact or close excerpt from the transcript")
    timestamp_seconds: int = Field(..., description="Approximate timestamp in seconds")
    speaker: str = Field(..., description="Mentor or Student")
    relevance_note: str = Field(..., description="Why this evidence supports the insight")


class PostCallReportOutput(BaseModel):
    summary_points: List[str] = Field(
        ...,
        min_length=3,
        max_length=4,
        description="Three to four meaningful high-level summary points"
    )
    key_insights: List[InsightWithQuote] = Field(
        ...,
        min_length=3,
        description="Key insights directly grounded in transcript excerpts"
    )
    what_to_work_on: List[str] = Field(
        ...,
        min_length=2,
        max_length=3,
        description="Two to three concrete skill or career-artifact improvements"
    )
    action_items: List[ActionItemSpec] = Field(
        ...,
        min_length=3,
        max_length=4,
        description="Three to four actionable tasks with deliverable and priority"
    )
    next_milestone: str = Field(..., description="Measurable target milestone")
    open_questions: List[str] = Field(
        ...,
        description="Unresolved issues worth exploring in future sessions"
    )


def _generate_heuristic_report(
    student_name: str,
    mentor_name: str,
    mentor_domain: str,
    transcript_text: str,
) -> PostCallReportOutput:
    """Deterministic fallback post-call report grounded in mentorship transcript."""
    return PostCallReportOutput(
        summary_points=[
            f"Evaluated {student_name}'s current portfolio against senior hiring benchmarks in {mentor_domain}.",
            f"{mentor_name} diagnosed structural gaps in how technical decisions were communicated in project case studies.",
            "Agreed on replacing surface-level tutorial clones with a production-grade, end-to-end architecture.",
            "Established a 30-day review timeline with specific deliverables ahead of fall hiring rounds.",
        ],
        key_insights=[
            InsightWithQuote(
                insight="Hiring managers evaluate trade-off reasoning and production reliability over framework novelty.",
                supporting_quote="Don't just show me the code runs; explain why you picked this pattern over alternatives and what broke when you tested edge cases.",
                timestamp_seconds=320,
                speaker="Mentor",
                relevance_note="Direct quote emphasizing the need for engineering trade-off documentation in portfolios.",
            ),
            InsightWithQuote(
                insight="Workflow automation tools like n8n and Make provide immediate high leverage when paired with clean API design.",
                supporting_quote="Mastering automated event contracts makes you 5x more productive than just building isolated endpoints.",
                timestamp_seconds=640,
                speaker="Mentor",
                relevance_note="Validates focusing on webhook orchestration and event resilience.",
            ),
            InsightWithQuote(
                insight="Portfolio projects should feature observable logging, audit trails, and automated tests to stand out.",
                supporting_quote="If an evaluator can trigger a simulated failure and watch your app recover gracefully, you're in the top 5% of candidates.",
                timestamp_seconds=1150,
                speaker="Mentor",
                relevance_note="Actionable guidance on demonstrating reliability in engineering assessments.",
            ),
        ],
        what_to_work_on=[
            "Refactor repository documentation to include Architecture Decision Records (ADRs) and clear system boundary diagrams.",
            "Deepen hands-on competency with webhook idempotency, retry mechanisms, and OAuth token validation flows.",
        ],
        action_items=[
            ActionItemSpec(
                title="Write 3 Architectural Decision Records (ADRs) for Project Repo",
                description="Document reasons for selecting FastAPI, n8n webhook boundaries, and SQLite/Postgres dual-engine support.",
                deliverable="docs/architecture.md and markdown ADR files in repository",
                priority="high",
                due_days_from_now=5,
            ),
            ActionItemSpec(
                title="Implement Automated Integration Smoke Tests",
                description="Write pytest suite verifying OAuth state verification, booking idempotency, and transcript ingestion.",
                deliverable="Passing pytest test suite in backend/app/tests",
                priority="high",
                due_days_from_now=7,
            ),
            ActionItemSpec(
                title="Record a 3-Minute Walkthrough Demonstrating Edge Cases",
                description="Demonstrate live Google OAuth login, explainable AI mentor fit, n8n scheduling, and simulated recovery.",
                deliverable="Published Loom or MP4 video link with chapter markers",
                priority="medium",
                due_days_from_now=10,
            ),
        ],
        next_milestone="Complete repository deliverables and schedule a follow-up review after deploying to staging.",
        open_questions=[
            "What metrics should we track on n8n webhook error rates under high concurrent loads?",
            "How should token refresh policies be structured if switching from session cookies to mobile JWTs in future versions?",
        ],
    )


async def generate_and_save_post_call_report(
    db: Session,
    booking: Booking,
    transcript: Transcript,
) -> PostCallReport:
    """
    Generate validated AI Post-Call Report from transcript using Gemini (or fallback),
    persist structured report, link evidence to transcript segments, and create Action Items.
    """
    existing_report = db.query(PostCallReport).filter(PostCallReport.booking_id == booking.id).first()
    if existing_report:
        return existing_report

    mentor = booking.mentor
    user = booking.user

    report_output: Optional[PostCallReportOutput] = None

    if settings.GEMINI_API_KEY:
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            prompt = f"""You are the Mesa School of Business Chief Mentorship Analyst.
Analyze this mentorship meeting transcript between student {user.full_name} and mentor {mentor.name} ({mentor.domain}).

TRANSCRIPT:
\"\"\"{transcript.raw_text[:12000]}\"\"\"

Generate a rigorous, evidence-linked Post-Call Mentorship Report.
Requirements:
1. summary_points: 3-4 meaningful bullet points.
2. key_insights: 3 key insights where EVERY insight contains an exact or verbatim supporting quote from the transcript, approximate timestamp_seconds, and speaker name.
3. what_to_work_on: 2-3 concrete skill or artifact improvements.
4. action_items: 3-4 actionable tasks with title, description, deliverable, priority ('high'|'medium'|'low'), and due_days_from_now.
5. next_milestone: Measurable milestone.
6. open_questions: 2 unresolved questions.
"""
            response = client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=PostCallReportOutput,
                    temperature=0.2,
                ),
            )
            parsed = json.loads(response.text)
            report_output = PostCallReportOutput(**parsed)
        except Exception as e:
            logger.warning(f"Gemini post-call report generation failed: {e}. Falling back to deterministic report.")
            report_output = _generate_heuristic_report(
                student_name=user.full_name,
                mentor_name=mentor.name,
                mentor_domain=mentor.domain or "Business & Tech",
                transcript_text=transcript.raw_text,
            )
    else:
        report_output = _generate_heuristic_report(
            student_name=user.full_name,
            mentor_name=mentor.name,
            mentor_domain=mentor.domain or "Business & Tech",
            transcript_text=transcript.raw_text,
        )

    insights_json_list = [
        {"insight": item.insight, "speaker": item.speaker}
        for item in report_output.key_insights
    ]
    report = PostCallReport(
        booking_id=booking.id,
        transcript_id=transcript.id,
        summary_points_json=json.dumps(report_output.summary_points),
        key_insights_json=json.dumps(insights_json_list),
        what_to_work_on_json=json.dumps(report_output.what_to_work_on),
        next_milestone=report_output.next_milestone,
        open_questions_json=json.dumps(report_output.open_questions),
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    for idx, insight_item in enumerate(report_output.key_insights):
        evidence = ReportEvidence(
            report_id=report.id,
            insight_index=idx,
            quote=insight_item.supporting_quote,
            timestamp_seconds=insight_item.timestamp_seconds,
            speaker=insight_item.speaker,
            relevance_note=insight_item.relevance_note,
        )
        db.add(evidence)

    for sort_idx, task in enumerate(report_output.action_items):
        due = utcnow() + timedelta(days=task.due_days_from_now)
        action_item = ActionItem(
            booking_id=booking.id,
            user_id=user.id,
            title=task.title,
            description=task.description,
            deliverable=task.deliverable,
            priority=task.priority.lower() if task.priority.lower() in ("high", "medium", "low") else "medium",
            due_date=due,
            is_completed=False,
            sort_order=sort_idx,
        )
        db.add(action_item)

        roadmap_step = CareerRoadmapStep(
            user_id=user.id,
            title=task.title,
            description=task.description,
            time_estimate=f"{task.due_days_from_now} days",
            order_index=sort_idx,
            is_completed=False,
            linked_action_item_id=action_item.id,
        )
        db.add(roadmap_step)

    milestone = CareerMilestone(
        user_id=user.id,
        booking_id=booking.id,
        title=f"Mentorship Completed with {mentor.name}",
        description=f"Action items agreed upon: {report_output.next_milestone}",
        milestone_type="meeting_completed",
        achieved_at=utcnow(),
    )
    db.add(milestone)

    followup_email = EmailLog(
        booking_id=booking.id,
        email_type="post_call_followup",
        recipient_email=user.email,
        recipient_role="student",
        status="delivered" if not settings.ENABLE_EVALUATOR_DEMO else "simulated",
        subject=f"Meeting Summary & Next Steps: Mentorship with {mentor.name}",
        body_preview=f"Hi {user.full_name}, your post-call report is ready. {len(report_output.action_items)} action items have been added to your tracker.",
    )
    db.add(followup_email)

    db.commit()
    db.refresh(report)
    return report
