import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import ChatSession, ChatMessage, DiagnosticResult, User
from app.auth.session import get_current_user
from app.schemas.chat import (
    ChatSessionCreate,
    ChatMessageCreate,
    ChatMessageResponse,
    ChatSessionResponse,
    DiagnosticResultResponse,
    ExplainableMatch,
)
from app.services.ai_diagnostic_service import process_chat_message

router = APIRouter(prefix="/chat", tags=["AI Diagnostic Assistant"])


def _format_diagnostic_result(diag: Optional[DiagnosticResult]) -> Optional[DiagnosticResultResponse]:
    """Helper to convert DiagnosticResult ORM model to Pydantic schema with parsed JSON."""
    if not diag:
        return None

    explanations = []
    if diag.match_explanations_json:
        try:
            raw_exps = json.loads(diag.match_explanations_json)
            for e in raw_exps:
                explanations.append(ExplainableMatch(**e))
        except Exception:
            explanations = []

    return DiagnosticResultResponse(
        id=diag.id,
        session_id=diag.session_id,
        user_id=diag.user_id,
        current_situation=diag.current_situation,
        career_goal=diag.career_goal,
        immediate_blocker=diag.immediate_blocker,
        existing_skills=diag.existing_skills,
        previous_attempts=diag.previous_attempts,
        desired_outcome=diag.desired_outcome,
        constraints=diag.constraints,
        stage=diag.stage,
        eligible_for_booking=diag.eligible_for_booking,
        recommended_mentors=explanations,
        missing_expertise_logged=diag.stage == "no_exact_match",
        created_at=diag.created_at,
    )


def _format_session_response(session: ChatSession) -> ChatSessionResponse:
    """Helper to build full ChatSessionResponse."""
    diag_resp = _format_diagnostic_result(session.diagnostic_result)
    messages = [
        ChatMessageResponse.model_validate(m)
        for m in sorted(session.messages, key=lambda x: x.created_at)
    ]
    return ChatSessionResponse(
        id=session.id,
        user_id=session.user_id,
        title=session.title,
        status=session.status,
        candidate_mentor_id=session.candidate_mentor_id,
        created_at=session.created_at,
        updated_at=session.updated_at,
        messages=messages,
        diagnostic_result=diag_resp,
    )


@router.post("/sessions", response_model=ChatSessionResponse)
def create_chat_session(
    payload: ChatSessionCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Initialize a new AI diagnostic chat session.
    Can optionally include candidate_mentor_id from the 'Check Fit with AI' directory action.
    """
    title = payload.title or "Career Diagnosis Session"
    if payload.candidate_mentor_id:
        title = f"Fit Assessment: Mentor {payload.candidate_mentor_id}"

    session = ChatSession(
        user_id=user.id,
        title=title,
        status="clarifying",
        candidate_mentor_id=payload.candidate_mentor_id,
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    # Initial welcome prompt from assistant
    welcome_content = (
        "Hello! I am your Mesa Career Diagnostic Advisor. "
        "Tell me about your current situation, what career goal or transition you're targeting, "
        "and the immediate blocker you're facing. I will diagnose your challenge and match you with "
        "verified industry mentors from our network."
    )
    if payload.candidate_mentor_id:
        welcome_content = (
            f"Hello! I see you are evaluating fit with Mentor {payload.candidate_mentor_id}. "
            "Please describe your current challenge and what you hope to achieve in this session. "
            "I will evaluate whether they are the optimal match or recommend other specialized mentors."
        )

    initial_msg = ChatMessage(
        session_id=session.id,
        sender="assistant",
        content=welcome_content,
    )
    db.add(initial_msg)
    db.commit()
    db.refresh(session)

    return _format_session_response(session)


@router.get("/sessions", response_model=List[ChatSessionResponse])
def list_chat_sessions(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all diagnostic chat sessions for the authenticated student."""
    sessions = (
        db.query(ChatSession)
        .filter(ChatSession.user_id == user.id)
        .order_by(ChatSession.updated_at.desc())
        .all()
    )
    return [_format_session_response(s) for s in sessions]


@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
def get_chat_session(
    session_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve full history and diagnostic result of a chat session."""
    session = (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id, ChatSession.user_id == user.id)
        .first()
    )
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found or does not belong to you.",
        )
    return _format_session_response(session)


@router.post("/sessions/{session_id}/messages", response_model=ChatSessionResponse)
async def send_chat_message(
    session_id: str,
    payload: ChatMessageCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Send a message to the AI Diagnostic Assistant.
    Runs diagnosis, updates match recommendations, and returns updated session.
    """
    session = (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id, ChatSession.user_id == user.id)
        .first()
    )
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found.",
        )

    await process_chat_message(
        db=db,
        session=session,
        user_message=payload.content,
        user=user,
    )

    db.refresh(session)
    return _format_session_response(session)
