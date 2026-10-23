from datetime import datetime, timedelta, timezone
import pytest


def test_transcript_ingestion_and_ai_report_generation(authenticated_student_client):
    """Simulate meeting completion and verify evidence-linked AI report and action items."""
    future_time = datetime.now(timezone.utc) + timedelta(days=2)
    book_resp = authenticated_student_client.post("/api/v1/bookings", json={
        "mentor_id": "M042",
        "scheduled_at": future_time.isoformat(),
        "duration_minutes": 45,
        "timezone": "Asia/Kolkata",
        "idempotency_key": "idem_sim_report_test",
    })
    booking_id = book_resp.json()["id"]

    # 1. Trigger Evaluator Simulation of Completed Meeting
    sim_resp = authenticated_student_client.post(f"/api/v1/demo/simulate/complete-meeting/{booking_id}")
    assert sim_resp.status_code == 200
    assert sim_resp.json()["status"] == "success"

    # 2. Check Transcript
    tr_resp = authenticated_student_client.get(f"/api/v1/bookings/{booking_id}/transcript")
    assert tr_resp.status_code == 200
    transcript = tr_resp.json()
    assert transcript["word_count"] > 50
    assert len(transcript["segments"]) > 0

    # 3. Check Post-Call Report with Evidence Links
    rep_resp = authenticated_student_client.get(f"/api/v1/bookings/{booking_id}/report")
    assert rep_resp.status_code == 200
    report = rep_resp.json()

    assert 3 <= len(report["summary_points"]) <= 4
    assert len(report["key_insights"]) >= 3

    # Check evidence quote and timestamp exist
    first_insight = report["key_insights"][0]
    assert first_insight["insight"] is not None
    assert first_insight["evidence"] is not None
    assert len(first_insight["evidence"]["quote"]) > 0
    assert first_insight["evidence"]["timestamp_seconds"] >= 0

    # Check Action Items
    assert len(report["action_items"]) >= 3
    action_item = report["action_items"][0]
    assert action_item["is_completed"] is False
    assert action_item["deliverable"] is not None

    # 4. Check Action Item Toggle
    item_id = action_item["id"]
    patch_resp = authenticated_student_client.patch(
        f"/api/v1/action-items/{item_id}",
        json={"is_completed": True}
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["is_completed"] is True
    assert patch_resp.json()["completed_at"] is not None
