import pytest
from app.config import settings


def test_auth_me_unauthorized(client):
    """Accessing /auth/me without a session cookie must return 401 Unauthorized."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
    assert "Authentication required" in response.json()["detail"]


def test_demo_login_student(client):
    """Demo login as student should set session cookie and return student profile."""
    response = client.post("/api/v1/auth/demo", json={"role": "student"})
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "student"
    assert "email" in data
    assert settings.SESSION_COOKIE_NAME in response.cookies

    # Profile check with session cookie
    me_resp = client.get("/api/v1/auth/me")
    assert me_resp.status_code == 200
    assert me_resp.json()["id"] == data["id"]


def test_demo_login_admin(client):
    """Demo login as administrator should grant admin role."""
    response = client.post("/api/v1/auth/demo", json={"role": "admin"})
    assert response.status_code == 200
    assert response.json()["role"] == "admin"


def test_logout_revokes_session(client):
    """Logging out should revoke server session and clear cookie."""
    # First sign in
    client.post("/api/v1/auth/demo", json={"role": "student"})
    assert client.get("/api/v1/auth/me").status_code == 200

    # Logout
    logout_resp = client.post("/api/v1/auth/logout")
    assert logout_resp.status_code == 200

    # Subsequent request should be 401
    assert client.get("/api/v1/auth/me").status_code == 401


def test_google_callback_invalid_state(client):
    """Google OAuth callback with mismatched or missing state must return 400."""
    response = client.get("/api/v1/auth/google/callback?code=mock_code&state=invalid_state")
    assert response.status_code == 400
    assert "OAuth state" in response.json()["detail"]


def test_admin_role_authorization_enforced(authenticated_student_client):
    """Student cannot access protected admin overview endpoint (403 Forbidden)."""
    response = authenticated_student_client.get("/api/v1/admin/overview")
    assert response.status_code == 403
    assert "Administrative privileges required" in response.json()["detail"]
