import time
from typing import Dict
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.models import User, utcnow
from app.auth.session import create_session, get_current_user, revoke_session
from app.auth.google_oauth import generate_oauth_state, get_google_auth_url, exchange_code_for_tokens, verify_google_id_token
from app.schemas.auth import UserResponse, DemoLoginRequest, GoogleOAuthUrlResponse, MessageResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

STATE_COOKIE_NAME = "mentor_oauth_state"
_OAUTH_ACTIVE_STATES: Dict[str, float] = {}


@router.get("/google/login")
def google_login(response: Response, redirect_mode: bool = True):
    """
    Initiate Google OAuth 2.0 flow.
    Generates a cryptographically random state parameter and redirects to Google.
    """
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth is not configured. Please use Evaluator Demo Login or configure GOOGLE_CLIENT_ID.",
        )

    state = generate_oauth_state()
    auth_url = get_google_auth_url(state)

    # Record state in server-side registry with timestamp
    now = time.time()
    _OAUTH_ACTIVE_STATES[state] = now
    # Evict expired states (10-minute window)
    expired = [k for k, t in _OAUTH_ACTIVE_STATES.items() if now - t > 600]
    for k in expired:
        _OAUTH_ACTIVE_STATES.pop(k, None)

    if redirect_mode:
        redirect_resp = RedirectResponse(url=auth_url, status_code=status.HTTP_302_FOUND)
        redirect_resp.set_cookie(
            key=STATE_COOKIE_NAME,
            value=state,
            max_age=600,
            httponly=True,
            secure=settings.COOKIE_SECURE,
            samesite="lax",
            path="/",
        )
        return redirect_resp

    response.set_cookie(
        key=STATE_COOKIE_NAME,
        value=state,
        max_age=600,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        path="/",
    )
    return GoogleOAuthUrlResponse(authorization_url=auth_url, state=state)


@router.get("/google/callback")
async def google_callback(
    request: Request,
    response: Response,
    code: str = Query(...),
    state: str = Query(...),
    db: Session = Depends(get_db),
):
    """
    Handle Google OAuth callback.
    Validates state parameter, exchanges code for ID token, verifies Google signature & claims,
    finds or creates user, and establishes an opaque server-side session.
    """
    stored_state = request.cookies.get(STATE_COOKIE_NAME)
    is_cookie_valid = bool(stored_state and stored_state == state)
    is_server_valid = bool(
        state in _OAUTH_ACTIVE_STATES and (time.time() - _OAUTH_ACTIVE_STATES.get(state, 0)) < 600
    )

    if not (is_cookie_valid or is_server_valid):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OAuth state parameter. Please try logging in again.",
        )

    # State verified; consume it
    _OAUTH_ACTIVE_STATES.pop(state, None)

    tokens = await exchange_code_for_tokens(code)
    id_token_str = tokens.get("id_token")
    if not id_token_str:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google OAuth response did not contain an id_token.",
        )

    google_claims = verify_google_id_token(id_token_str)
    google_id = google_claims["sub"]
    email = google_claims["email"].lower().strip()
    full_name = google_claims.get("name") or email.split("@")[0]
    avatar_url = google_claims.get("picture")

    user = db.query(User).filter(User.google_id == google_id).first()
    if not user:
        user = db.query(User).filter(User.email == email).first()
        if user:
            user.google_id = google_id
            if avatar_url:
                user.avatar_url = avatar_url
        else:
            user = User(
                google_id=google_id,
                email=email,
                full_name=full_name,
                avatar_url=avatar_url,
                role="student",
                is_active=True,
            )
            db.add(user)
        db.commit()
        db.refresh(user)

    redirect_target = f"{settings.FRONTEND_URL}/overview?login_success=true"
    redirect_resp = RedirectResponse(url=redirect_target, status_code=status.HTTP_302_FOUND)
    redirect_resp.delete_cookie(key=STATE_COOKIE_NAME, path="/")
    create_session(db=db, user=user, response=redirect_resp, request=request)
    return redirect_resp


@router.get("/me", response_model=UserResponse)
def get_me(user: User = Depends(get_current_user)):
    """Return profile of currently authenticated user."""
    return user


@router.post("/logout", response_model=MessageResponse)
def logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    """Log out user, revoking server session and clearing cookies."""
    revoke_session(db=db, request=request, response=response)
    return MessageResponse(message="Successfully logged out.")


@router.post("/demo", response_model=UserResponse)
def demo_login(
    payload: DemoLoginRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    """
    Evaluator Demo Login.
    Provides instant 1-click access for evaluators to review the entire platform
    without needing real Google OAuth credentials.
    """
    if not settings.ENABLE_EVALUATOR_DEMO:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Evaluator demo mode is disabled in production settings.",
        )

    target_role = "admin" if payload.role == "admin" else "student"
    email = payload.email or (
        "evaluator.admin@mesa.edu" if target_role == "admin" else "arjun.bansal.student@mesa.edu"
    )
    full_name = payload.full_name or (
        "Mesa Evaluator (Admin)" if target_role == "admin" else "Arjun Bansal (Mesa Student)"
    )

    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            email=email,
            full_name=full_name,
            role=target_role,
            avatar_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80",
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    create_session(db=db, user=user, response=response, request=request)
    return user
