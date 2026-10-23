import pytest


def test_list_all_50_mentors(client):
    """Authoritative catalogue must contain exactly 50 verified mentors."""
    response = client.get("/api/v1/mentors")
    assert response.status_code == 200
    mentors = response.json()
    assert len(mentors) == 50
    ids = [m["mentor_id"] for m in mentors]
    assert "M001" in ids
    assert "M050" in ids


def test_get_valid_mentor_details(client):
    """Retrieve detailed verified profile of mentor M042."""
    response = client.get("/api/v1/mentors/M042")
    assert response.status_code == 200
    mentor = response.json()
    assert mentor["mentor_id"] == "M042"
    assert mentor["domain"] == "Marketing"
    assert "Edtech" in mentor["master_sector"] or "Edtech" in mentor["sectors_of_expertise"]


def test_get_unknown_mentor_returns_404(client):
    """Querying an unverified/hallucinated mentor ID must return 404."""
    response = client.get("/api/v1/mentors/M999")
    assert response.status_code == 404
    assert "not found in the verified catalogue" in response.json()["detail"]


def test_filter_mentors_by_domain(client):
    """Filter mentors by 'Product Management' domain."""
    response = client.get("/api/v1/mentors?domain=Product")
    assert response.status_code == 200
    mentors = response.json()
    assert len(mentors) > 0
    for m in mentors:
        assert "product" in m["domain"].lower() or "product" in (m["roles_of_expertise"] or "").lower()


def test_filter_mentors_by_ai_tool(client):
    """Filter mentors by verified AI tool 'n8n'."""
    response = client.get("/api/v1/mentors?ai_tool=n8n")
    assert response.status_code == 200
    mentors = response.json()
    assert len(mentors) > 0
    for m in mentors:
        assert "n8n" in (m["ai_tools_of_expertise"] or "").lower()
