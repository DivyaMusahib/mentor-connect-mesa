import json
import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.config import settings
from app.models import Booking, PreCallBrief, Mentor, User, DiagnosticResult, EmailLog, utcnow

logger = logging.getLogger(__name__)


class PreCallBriefOutput(BaseModel):
    student_context_summary: str = Field(..., description="Concise 2-sentence summary of student situation")
    current_blocker: str = Field(..., description="Specific obstacle or decision facing the student")
    key_questions_to_cover: List[str] = Field(
        ...,
        min_length=3,
        max_length=3,
        description="Exactly three concrete, high-leverage discussion questions"
    )
    recommended_preparation: str = Field(..., description="Concrete documents, metrics, or notes student should prepare")
    desired_outcome: str = Field(..., description="Target tangible outcome by the end of the 45-minute session")
    suggested_agenda: List[str] = Field(..., description="Time-boxed 45-minute discussion agenda")
    checklist: List[str] = Field(..., description="Actionable pre-meeting checklist items")


def _generate_heuristic_brief(
    student_name: str,
    mentor_name: str,
    mentor_domain: str,
    blocker: str,
    career_goal: str,
) -> PreCallBriefOutput:
    """Deterministic fallback brief generator when Gemini API is unconfigured."""
    clean_blocker = blocker or "Accelerating career transition and identifying industry best practices."
    clean_goal = career_goal or f"Securing a high-impact role in {mentor_domain}."

    return PreCallBriefOutput(
        student_context_summary=(
            f"{student_name} is actively working toward {clean_goal}. "
            f"They seek tactical industry guidance from {mentor_name} to overcome current execution challenges."
        ),
        current_blocker=clean_blocker,
        key_questions_to_cover=[
            f"Given your experience in {mentor_domain}, what are the top 2 hiring criteria teams actually screen for?",
            f"How should I structure my current project/portfolio to demonstrate real capability against my blocker?",
            "What common junior-to-mid career traps should I avoid in this domain over the next 6-12 months?",
        ],
        recommended_preparation=(
            "Review your recent project deliverables, have your GitHub/portfolio and resume open, "
            "and prepare a 2-minute concise pitch of your blocker."
        ),
        desired_outcome="A validated action roadmap with 3 specific tactical priorities for the next 30 days.",
        suggested_agenda=[
            "00:00 - 00:05: Introductions and session goal alignment",
            "00:05 - 00:20: Deep dive into current blocker and live review of project artifacts",
            "00:20 - 00:35: Mentor strategic feedback, frameworks, and practical recommendations",
            "00:35 - 00:45: Action items agreement, accountability timeline, and next milestone",
        ],
        checklist=[
            "Test your microphone, camera, and Google Meet connection 5 minutes before the call.",
            "Open your resume and relevant project links in separate tabs.",
            "Have a notebook or document ready to capture action items and tactical suggestions.",
            "Review the mentor's verified background and have your 3 key questions ready.",
        ],
    )


async def generate_and_save_brief(
    db: Session,
    booking: Booking,
) -> PreCallBrief:
    """
    Generate the authoritative Pre-Call AI Preparation Brief using Gemini (or fallback),
    persist it to pre_call_briefs table, and return it.
    """
    existing = db.query(PreCallBrief).filter(PreCallBrief.booking_id == booking.id).first()
    if existing:
        return existing

    user = booking.user
    mentor = booking.mentor
    diagnostic = booking.diagnostic

    blocker = diagnostic.immediate_blocker if diagnostic else "Career strategy and skills transition"
    goal = diagnostic.career_goal if diagnostic else f"Excellence in {mentor.domain or 'Business'}"

    brief_data: Optional[PreCallBriefOutput] = None

    if settings.GEMINI_API_KEY:
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            prompt = f"""Generate a personalized Pre-Call Meeting Preparation Brief for a 45-minute mentorship session at Mesa School of Business.

Student: {user.full_name}
Mentor: {mentor.name}
Mentor Domain: {mentor.domain}
Mentor Sectors: {mentor.sectors_of_expertise}
Mentor Roles: {mentor.roles_of_expertise}
Mentor AI Tools: {mentor.ai_tools_of_expertise}
Student Problem / Blocker: {blocker}
Student Career Goal: {goal}

Strict requirements:
- key_questions_to_cover must contain EXACTLY 3 concrete, insightful discussion questions.
- suggested_agenda must cover a structured 45-minute session.
- checklist must have 4 clear student preparation actions.
"""
            response = client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=PreCallBriefOutput,
                    temperature=0.2,
                ),
            )
            parsed = json.loads(response.text)
            brief_data = PreCallBriefOutput(**parsed)
        except Exception as e:
            logger.warning(f"Gemini API brief generation failed: {e}. Using deterministic brief.")
            brief_data = _generate_heuristic_brief(
                student_name=user.full_name,
                mentor_name=mentor.name,
                mentor_domain=mentor.domain or "Tech & Business",
                blocker=blocker,
                career_goal=goal,
            )
    else:
        brief_data = _generate_heuristic_brief(
            student_name=user.full_name,
            mentor_name=mentor.name,
            mentor_domain=mentor.domain or "Tech & Business",
            blocker=blocker,
            career_goal=goal,
        )

    brief = PreCallBrief(
        booking_id=booking.id,
        student_context_summary=brief_data.student_context_summary,
        current_blocker=brief_data.current_blocker,
        key_questions_json=json.dumps(brief_data.key_questions_to_cover),
        recommended_preparation=brief_data.recommended_preparation,
        desired_outcome=brief_data.desired_outcome,
        suggested_agenda_json=json.dumps(brief_data.suggested_agenda),
        checklist_json=json.dumps(brief_data.checklist),
    )
    db.add(brief)
    db.commit()
    db.refresh(brief)

    # Log initial booking confirmation email event
    student_email_log = EmailLog(
        booking_id=booking.id,
        email_type="booking_confirmation",
        recipient_email=user.email,
        recipient_role="student",
        status="delivered" if not settings.ENABLE_EVALUATOR_DEMO else "simulated",
        subject=f"Confirmed: Mesa Mentorship with {mentor.name} on {booking.scheduled_at.strftime('%b %d, %Y')}",
        body_preview=f"Hi {user.full_name}, your session with {mentor.name} is booked. Meet Link: {booking.meet_link}. Your personalized brief is ready.",
    )
    db.add(student_email_log)
    db.commit()

    return brief
