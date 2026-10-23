import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Cookie, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.models import ApplicationSession, User, AuditEvent, utcnow, ensure_utc, generate_uuid


def create_session(
    db: Session,
    user: User,
    response: Response,
    request: Optional[Request] = None,
) -> ApplicationSession:
    """Create a new server-side session and set an HttpOnly cookie."""
    session_id = secrets.token_urlsafe(32)
    expires_at = utcnow() + timedelta(seconds=settings.SESSION_MAX_AGE_SECONDS)

    ip_address = None
    user_agent = None
    if request:
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

    db_session = ApplicationSession(
        id=session_id,
        user_id=user.id,
        expires_at=expires_at,
        is_revoked=False,
        ip_address=ip_address,
        user_agent=user_agent,
        created_at=utcnow(),
        last_accessed_at=utcnow(),
    )
    db.add(db_session)

    # Log audit event
    audit = AuditEvent(
        user_id=user.id,
        action="login",
        resource_type="session",
        resource_id=session_id,
        ip_address=ip_address,
    )
    db.add(audit)
    db.commit()
    db.refresh(db_session)

    # Set secure HttpOnly cookie
    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=session_id,
        max_age=settings.SESSION_MAX_AGE_SECONDS,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        domain=settings.COOKIE_DOMAIN,
        path="/",
    )
    return db_session


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    """Validate the incoming session cookie and retrieve active authenticated user."""
    session_id = request.cookies.get(settings.SESSION_COOKIE_NAME)
    
    # Also support Authorization: Bearer <session_id> for API testing
    if not session_id:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            session_id = auth_header[7:].strip()

    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please sign in.",
        )

    db_session = (
        db.query(ApplicationSession)
        .filter(
            ApplicationSession.id == session_id,
            ApplicationSession.is_revoked == False,
        )
        .first()
    )

    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session not found or revoked. Please sign in again.",
        )

    # Check expiration
    now = utcnow()
    if ensure_utc(db_session.expires_at) <= now:
        db_session.is_revoked = True
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired. Please sign in again.",
        )

    # Update last accessed
    db_session.last_accessed_at = now
    db.commit()

    user = db.query(User).filter(User.id == db_session.user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is deactivated or not found.",
        )

    return user


def get_optional_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Retrieve current user if authenticated, otherwise return None without raising."""
    try:
        return get_current_user(request=request, db=db)
    except HTTPException:
        return None


def require_admin(
    user: User = Depends(get_current_user),
) -> User:
    """Enforce administrator role for protected administrative endpoints."""
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrative privileges required to access this resource.",
        )
    return user


def revoke_session(
    db: Session,
    request: Request,
    response: Response,
) -> None:
    """Revoke session in database and delete the session cookie."""
    session_id = request.cookies.get(settings.SESSION_COOKIE_NAME)
    if not session_id:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            session_id = auth_header[7:].strip()

    if session_id:
        db_session = db.query(ApplicationSession).filter(ApplicationSession.id == session_id).first()
        if db_session:
            db_session.is_revoked = True
            audit = AuditEvent(
                user_id=db_session.user_id,
                action="logout",
                resource_type="session",
                resource_id=session_id,
            )
            db.add(audit)
            db.commit()

    # Clear cookie
    response.delete_cookie(
        key=settings.SESSION_COOKIE_NAME,
        path="/",
        domain=settings.COOKIE_DOMAIN,
    )
