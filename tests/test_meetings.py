import pytest
from httpx import AsyncClient
from unittest.mock import patch
from datetime import datetime, timedelta, timezone

@pytest.mark.asyncio
async def test_create_meeting_success(async_client: AsyncClient, test_client_token: dict, db_client):
    """Test successful creation of a video meeting."""
    headers = {"Authorization": f"Bearer {test_client_token['access_token']}"}
    meeting_data = {
        "title": "Client Consultation",
        "description": "Discuss legal strategy",
        "scheduledTime": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
        "duration": 60,
        "meetingType": "video"
    }
    
    with patch('backend.routers.meetings.EmailService.send_meeting_confirmation') as mock_send_email:
        response = await async_client.post("/api/meetings/create", json=meeting_data, headers=headers)
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert "meetingId" in response.json()
        assert "meetingUrl" in response.json()
        mock_send_email.assert_called_once() # Verify email was attempted to be sent
    
    meeting_in_db = db_client.meetings.find_one({"meetingId": response.json()["meetingId"]})
    assert meeting_in_db is not None
    assert meeting_in_db["title"] == meeting_data["title"]

@pytest.mark.asyncio
async def test_get_my_meetings_success(async_client: AsyncClient, test_client_token: dict, db_client):
    """Test retrieving all meetings for the authenticated client."""
    headers = {"Authorization": f"Bearer {test_client_token['access_token']}"}
    # Create a dummy meeting for this client
    meeting_data = {
        "title": "Another Meeting",
        "description": "Follow up",
        "scheduledTime": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat(),
        "duration": 30,
        "meetingType": "audio"
    }
    with patch('backend.routers.meetings.EmailService.send_meeting_confirmation'):
        await async_client.post("/api/meetings/create", json=meeting_data, headers=headers)
    
    response = await async_client.get("/api/meetings/my-meetings", headers=headers)
    assert response.status_code == 200
    assert "meetings" in response.json()
    assert response.json()["total"] >= 1
    assert any(m["title"] == "Another Meeting" for m in response.json()["meetings"])

@pytest.mark.asyncio
async def test_get_meeting_details_success(async_client: AsyncClient, test_client_token: dict, db_client):
    """Test retrieving details for a specific meeting."""
    headers = {"Authorization": f"Bearer {test_client_token['access_token']}"}
    meeting_data = {
        "title": "Specific Meeting",
        "description": "Detail check",
        "scheduledTime": (datetime.now(timezone.utc) + timedelta(days=3)).isoformat(),
        "duration": 45,
        "meetingType": "video"
    }
    with patch('backend.routers.meetings.EmailService.send_meeting_confirmation'):
        create_response = await async_client.post("/api/meetings/create", json=meeting_data, headers=headers)
    meeting_id = create_response.json()["meetingId"]
    
    response = await async_client.get(f"/api/meetings/{meeting_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["meetingId"] == meeting_id
    assert response.json()["title"] == meeting_data["title"]

@pytest.mark.asyncio
async def test_update_meeting_status_success(async_client: AsyncClient, test_client_token: dict, db_client):
    """Test updating the status of a meeting."""
    headers = {"Authorization": f"Bearer {test_client_token['access_token']}"}
    meeting_data = {
        "title": "Status Update Test",
        "description": "Update me",
        "scheduledTime": (datetime.now(timezone.utc) + timedelta(days=4)).isoformat(),
        "duration": 30,
        "meetingType": "video"
    }
    with patch('backend.routers.meetings.EmailService.send_meeting_confirmation'):
        create_response = await async_client.post("/api/meetings/create", json=meeting_data, headers=headers)
    meeting_id = create_response.json()["meetingId"]

    update_data = {"status": "in_progress"}
    response = await async_client.patch(f"/api/meetings/{meeting_id}/status", json=update_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["success"] is True
    
    meeting_in_db = db_client.meetings.find_one({"meetingId": meeting_id})
    assert meeting_in_db["status"] == "in_progress"
    assert meeting_in_db["startedAt"] is not None

@pytest.mark.asyncio
async def test_delete_meeting_success(async_client: AsyncClient, test_client_token: dict, db_client):
    """Test successful deletion of a meeting."""
    headers = {"Authorization": f"Bearer {test_client_token['access_token']}"}
    meeting_data = {
        "title": "Meeting to Delete",
        "description": "Cleanup",
        "scheduledTime": (datetime.now(timezone.utc) + timedelta(days=5)).isoformat(),
        "duration": 15,
        "meetingType": "audio"
    }
    with patch('backend.routers.meetings.EmailService.send_meeting_confirmation'):
        create_response = await async_client.post("/api/meetings/create", json=meeting_data, headers=headers)
    meeting_id = create_response.json()["meetingId"]

    response = await async_client.delete(f"/api/meetings/{meeting_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["success"] is True
    
    meeting_in_db = db_client.meetings.find_one({"meetingId": meeting_id})
    assert meeting_in_db is None

@pytest.mark.asyncio
async def test_delete_meeting_in_progress(async_client: AsyncClient, test_client_token: dict, db_client):
    """Test attempting to delete an in-progress meeting."""
    headers = {"Authorization": f"Bearer {test_client_token['access_token']}"}
    meeting_data = {
        "title": "In Progress Meeting",
        "description": "Cannot delete",
        "scheduledTime": (datetime.now(timezone.utc) + timedelta(days=6)).isoformat(),
        "duration": 90,
        "meetingType": "video"
    }
    with patch('backend.routers.meetings.EmailService.send_meeting_confirmation'):
        create_response = await async_client.post("/api/meetings/create", json=meeting_data, headers=headers)
    meeting_id = create_response.json()["meetingId"]

    # Manually set status to in_progress (simulate start of meeting)
    db_client.meetings.update_one(
        {"meetingId": meeting_id},
        {"$set": {"status": "in_progress", "startedAt": datetime.utcnow()}}
    )
    
    response = await async_client.delete(f"/api/meetings/{meeting_id}", headers=headers)
    assert response.status_code == 400
    assert "Cannot delete meeting that is in progress" in response.json()["detail"]
