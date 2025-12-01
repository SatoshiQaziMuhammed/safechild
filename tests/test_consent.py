import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_log_consent_success(async_client: AsyncClient, db_client):
    """Test successful logging of user consent."""
    consent_data = {
        "sessionId": "session_123",
        "permissions": {
            "location": True,
            "browser": False,
            "camera": True,
            "files": False,
            "forensic": True
        },
        "userAgent": "pytest-client",
        "clientNumber": "TST123456"
    }
    response = await async_client.post("/api/consent", json=consent_data)
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "consentId" in response.json()
    assert "timestamp" in response.json()
    
    consent_in_db = await db_client.consents.find_one({"sessionId": consent_data["sessionId"]})
    assert consent_in_db is not None
    assert consent_in_db["consentType"] == consent_data["consentType"]

@pytest.mark.asyncio
async def test_get_consent_details_success(async_client: AsyncClient, db_client):
    """Test retrieving consent details for an existing session."""
    session_id = "session_456"
    consent_data = {
        "sessionId": session_id,
        "permissions": {
            "location": False,
            "browser": True,
            "camera": False,
            "files": True,
            "forensic": False
        },
        "userAgent": "pytest-client-2",
        "clientNumber": "TST789012"
    }
    await async_client.post("/api/consent", json=consent_data)
    
    response = await async_client.get(f"/api/consent/{session_id}")
    assert response.status_code == 200
    assert response.json()["sessionId"] == session_id
    assert response.json()["agreed"] is False

@pytest.mark.asyncio
async def test_get_consent_details_not_found(async_client: AsyncClient):
    """Test retrieving consent details for a non-existent session."""
    response = await async_client.get("/api/consent/nonexistent_session")
    assert response.status_code == 404
    assert "Consent not found" in response.json()["detail"]
