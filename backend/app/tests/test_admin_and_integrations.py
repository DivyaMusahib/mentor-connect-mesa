from datetime import datetime, timedelta, timezone
import pytest


def test_admin_metrics_overview(authenticated_admin_client):
    """Admin overview should return aggregated metrics calculated from database tables."""
    response = authenticated_admin_client.get("/api/v1/admin/overview")
    assert response.status_code == 200
    metrics = response.json()
    assert "total_students" in metrics
    assert "diagnostic_sessions" in metrics
    assert "total_bookings" in metrics
    assert "mentor_demand_by_domain" in metrics
    assert isinstance(metrics["mentor_demand_by_domain"], dict)


def test_n8n_callback_meeting_created(client, authenticated_student_client):
    """Asynchronous callback from n8n updates booking state with verified calendar data."""
    # Create booking
    future_time = datetime.now(timezone.utc) + timedelta(days=3)
    b_resp = authenticated_student_client.post("/api/v1/bookings", json={
        "mentor_id": "M010",
        "scheduled_at": future_time.isoformat(),
        "duration_minutes": 45,
        "timezone": "Asia/Kolkata",
        "idempotency_key": "idem_n8n_cb_test",
    })
    booking_id = b_resp.json()["id"]

    # Inbound callback from n8n
    callback_payload = {
        "event_type": "meeting_created",
        "booking_id": booking_id,
        "status": "success",
        "calendar_event_id": "google_cal_12345",
        "meet_link": "https://meet.google.com/real-call-link",
        "execution_id": "n8n_exec_9999",
    }
    headers = {"X-FastAPI-Key": "mentor-connect-fastapi-callback-secret-key"}

    cb_resp = client.post(
        "/api/v1/integrations/n8n/meeting-created",
        json=callback_payload,
        headers=headers,
    )
    assert cb_resp.status_code == 200

    # Verify updated booking
    check_resp = authenticated_student_client.get(f"/api/v1/bookings/{booking_id}")
    assert check_resp.status_code == 200
    updated_booking = check_resp.json()
    assert updated_booking["meet_link"] == "https://meet.google.com/real-call-link"
    assert updated_booking["calendar_event_id"] == "google_cal_12345"


def test_integration_health_endpoint(client):
    """Health endpoint reports database connection and integration states."""
    response = client.get("/api/v1/integrations/health")
    assert response.status_code == 200
    health = response.json()
    assert health["database_connected"] is True
    assert health["evaluator_demo_mode"] is True


def test_evaluator_demo_seed_and_reset(authenticated_student_client):
    """Seed demo environment and reset demo database cleanly."""
    seed_resp = authenticated_student_client.post("/api/v1/demo/seed")
    assert seed_resp.status_code == 200
    assert seed_resp.json()["status"] == "success"

    reset_resp = authenticated_student_client.post("/api/v1/demo/reset")
    assert reset_resp.status_code == 200
    assert reset_resp.json()["status"] == "success"


def test_fathom_transcription_webhook(client, authenticated_student_client):
    """Incoming transcript webhook from Fathom via n8n triggers AI report generation."""
    future_time = datetime.now(timezone.utc) + timedelta(days=4)
    book_resp = authenticated_student_client.post("/api/v1/bookings", json={
        "mentor_id": "M015",
        "scheduled_at": future_time.isoformat(),
        "duration_minutes": 45,
        "timezone": "Asia/Kolkata",
        "idempotency_key": "idem_fathom_test",
    })
    assert book_resp.status_code == 201
    booking_id = book_resp.json()["id"]

    fathom_payload = {
        "provider": "fathom",
        "provider_task_id": "fathom_rec_9999",
        "booking_id": booking_id,
        "status": "completed",
        "transcript_text": "[Mentor]: Focus on system design and trade-offs. [Student]: I will document our decision records this week.",
        "duration_seconds": 2700,
        "segments": [
            {
                "speaker": "Mentor",
                "text": "Focus on system design and trade-offs.",
                "start_time_ms": 0,
                "end_time_ms": 15000,
            },
            {
                "speaker": "Student",
                "text": "I will document our decision records this week.",
                "start_time_ms": 15000,
                "end_time_ms": 30000,
            }
        ]
    }
    headers = {"X-FastAPI-Key": "mentor-connect-fastapi-callback-secret-key"}

    resp = client.post("/api/v1/integrations/transcription/webhook", json=fathom_payload, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert "transcript_id" in data
    assert "report_id" in data

    # Verify booking status transitioned to completed
    b_check = authenticated_student_client.get(f"/api/v1/bookings/{booking_id}")
    assert b_check.json()["status"] == "completed"

    # Verify transcript provider is recorded as fathom
    tr_check = authenticated_student_client.get(f"/api/v1/bookings/{booking_id}/transcript")
    assert tr_check.status_code == 200
    assert tr_check.json()["provider"] == "fathom"

