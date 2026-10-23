import secrets
from urllib.parse import urlencode
from typing import Dict, Any, Optional
import httpx
from fastapi import HTTPException, status
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from app.config import settings

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"


def generate_oauth_state() -> str:
    """Generate a cryptographically secure random state parameter."""
    return secrets.token_urlsafe(32)


def get_google_auth_url(state: str) -> str:
    """Construct Google OAuth 2.0 authorization URL."""
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google Client ID is not configured in backend settings.",
        )

    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "online",
        "prompt": "select_account",
    }
    return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"


async def exchange_code_for_tokens(code: str) -> Dict[str, Any]:
    """Exchange authorization code for Google tokens."""
    if not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google Client Secret is not configured in backend settings.",
        )

    data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(GOOGLE_TOKEN_URL, data=data)
        if response.status_code != 200:
            error_data = response.json() if "application/json" in response.headers.get("content-type", "") else response.text
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Google token exchange failed: {error_data}",
            )
        return response.json()


def verify_google_id_token(token: str) -> Dict[str, Any]:
    """
    Verify Google ID Token using official google-auth library.
    Enforces signature verification, issuer, audience, and expiry checks.
    """
    try:
        request = google_requests.Request()
        id_info = id_token.verify_oauth2_token(
            token,
            request,
            audience=settings.GOOGLE_CLIENT_ID,
            clock_skew_in_seconds=10,
        )

        issuer = id_info.get("iss")
        if issuer not in ("accounts.google.com", "https://accounts.google.com"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid Google ID token issuer: {issuer}",
            )

        if not id_info.get("email"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Google token payload is missing email address.",
            )

        return id_info
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Google ID token verification failed: {str(e)}",
        )
