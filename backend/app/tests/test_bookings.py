from datetime import datetime, timedelta, timezone
import pytest


def test_calendar_availability_query(client):
    """Querying availability for verified mentor M042 returns open slots."""
    future_date = (datetime.now(timezone.utc) + timedelta(days=3)).strftime("%Y-%m-%d")
    response = client.get(f"/api/v1/bookings/availability/M042?date={future_date}")
    assert response.status_code == 200
    data = response.json()
    assert data["mentor_id"] == "M042"
    assert len(data["slots"]) > 0


def test_booking_creation_and_pre_call_brief(authenticated_student_client):
    """Booking a verified mentor creates booking, meet link, and authoritative Pre-Call Brief."""
    future_time = datetime.now(timezone.utc) + timedelta(days=2, hours=2)
    payload = {
        "mentor_id": "M042",
        "scheduled_at": future_time.isoformat(),
        "duration_minutes": 45,
        "timezone": "Asia/Kolkata",
        "idempotency_key": "test_idem_booking_123",
    }

    response = authenticated_student_client.post("/api/v1/bookings", json=payload)
    assert response.status_code == 201
    booking = response.json()
    assert booking["status"] == "confirmed"
    assert booking["mentor_id"] == "M042"
    assert booking["meet_link"] is not None
    assert booking["reschedule_token"] is not None

    booking_id = booking["id"]

    # Verify Pre-Call Brief was automatically compiled and saved
    brief_resp = authenticated_student_client.get(f"/api/v1/bookings/{booking_id}/brief")
    assert brief_resp.status_code == 200
    brief = brief_resp.json()
    assert len(brief["key_questions_to_cover"]) == 3
    assert len(brief["suggested_agenda"]) > 0
    assert len(brief["checklist"]) > 0


def test_booking_past_time_rejected(authenticated_student_client):
    """Booking time in the past must be rejected with 400 Bad Request."""
    past_time = datetime.now(timezone.utc) - timedelta(hours=2)
    payload = {
        "mentor_id": "M042",
        "scheduled_at": past_time.isoformat(),
        "duration_minutes": 45,
        "timezone": "Asia/Kolkata",
        "idempotency_key": "test_idem_past_time",
    }
    response = authenticated_student_client.post("/api/v1/bookings", json=payload)
    assert response.status_code == 400
    assert "future" in response.json()["detail"]


def test_double_booking_prevention(authenticated_student_client):
    """Student cannot book two overlapping sessions at the exact same time (409 Conflict)."""
    future_time = datetime.now(timezone.utc) + timedelta(days=4)
    payload1 = {
        "mentor_id": "M042",
        "scheduled_at": future_time.isoformat(),
        "duration_minutes": 45,
        "timezone": "Asia/Kolkata",
        "idempotency_key": "idem_double_1",
    }
    r1 = authenticated_student_client.post("/api/v1/bookings", json=payload1)
    assert r1.status_code == 201

    payload2 = {
        "mentor_id": "M030",
        "scheduled_at": future_time.isoformat(),
        "duration_minutes": 45,
        "timezone": "Asia/Kolkata",
        "idempotency_key": "idem_double_2",
    }
    r2 = authenticated_student_client.post("/api/v1/bookings", json=payload2)
    assert r2.status_code == 409
    assert "already have an active mentorship session booked" in r2.json()["detail"]


def test_reschedule_and_cancel_lifecycle(authenticated_student_client):
    """Test full reschedule and cancel lifecycle."""
    future_time = datetime.now(timezone.utc) + timedelta(days=5)
    r1 = authenticated_student_client.post("/api/v1/bookings", json={
        "mentor_id": "M001",
        "scheduled_at": future_time.isoformat(),
        "duration_minutes": 45,
        "timezone": "Asia/Kolkata",
        "idempotency_key": "idem_resched_test",
    })
    booking_id = r1.json()["id"]

    # 1. Reschedule
    new_time = future_time + timedelta(hours=3)
    resched_resp = authenticated_student_client.patch(
        f"/api/v1/bookings/{booking_id}/reschedule",
        json={"new_scheduled_at": new_time.isoformat(), "reason": "Conflict"}
    )
    assert resched_resp.status_code == 200
    assert resched_resp.json()["status"] == "rescheduled"

    # 2. Cancel
    cancel_resp = authenticated_student_client.post(
        f"/api/v1/bookings/{booking_id}/cancel",
        json={"reason": "No longer needed"}
    )
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()["status"] == "cancelled"
