import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch, AsyncMock
from backend.models import Client, Document, ChatMessage, Consent, Meeting
from backend.auth import get_password_hash, create_access_token

@pytest.mark.asyncio
async def test_admin_get_all_clients(async_client: AsyncClient, admin_token_fixture: str, db_client):
    """Test admin can retrieve all clients."""
    headers = {"Authorization": f"Bearer {admin_token_fixture}"}
    # Ensure there's at least one client (admin user from conftest)
    response = await async_client.get("/api/admin/clients", headers=headers)
    assert response.status_code == 200
    assert "clients" in response.json()
    assert response.json()["total"] >= 1

@pytest.mark.asyncio
async def test_admin_get_client_details(async_client: AsyncClient, admin_token_fixture: str, test_client_token: dict, db_client):
    """Test admin can retrieve detailed client information."""
    headers = {"Authorization": f"Bearer {admin_token_fixture}"}
    client_number = test_client_token["client_number"]
    response = await async_client.get(f"/api/admin/clients/{client_number}", headers=headers)
    assert response.status_code == 200
    assert response.json()["client"]["clientNumber"] == client_number
    assert "documents" in response.json()
    assert "chatMessages" in response.json()

@pytest.mark.asyncio
async def test_admin_update_client(async_client: AsyncClient, admin_token_fixture: str, test_client_token: dict, db_client):
    """Test admin can update client information."""
    headers = {"Authorization": f"Bearer {admin_token_fixture}"}
    client_number = test_client_token["client_number"]
    update_data = {"firstName": "UpdatedTest", "phone": "9876543210"}
    response = await async_client.put(f"/api/admin/clients/{client_number}", json=update_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["success"] is True
    
    client_in_db = db_client.clients.find_one({"clientNumber": client_number})
    assert client_in_db["firstName"] == "UpdatedTest"
    assert client_in_db["phone"] == "9876543210"

@pytest.mark.asyncio
async def test_admin_delete_client_soft_delete(async_client: AsyncClient, admin_token_fixture: str, db_client):
    """Test admin can soft delete a client."""
    headers = {"Authorization": f"Bearer {admin_token_fixture}"}
    # Register a new client for deletion test
    register_data = {
        "firstName": "ToDelete", "lastName": "Client", "email": "todelete@example.com",
        "password": "DeleteMe1!", "phone": "1231231231", "country": "Testland", "caseType": "General"
    }
    response_reg = await async_client.post("/api/auth/register", json=register_data)
    client_number = response_reg.json()["clientNumber"]

    response = await async_client.delete(f"/api/admin/clients/{client_number}", headers=headers)
    assert response.status_code == 200
    assert response.json()["success"] is True
    
    client_in_db = db_client.clients.find_one({"clientNumber": client_number})
    assert client_in_db["status"] == "deleted"

@pytest.mark.asyncio
async def test_admin_get_all_documents(async_client: AsyncClient, admin_token_fixture: str, test_client_token: dict, tmp_path, clear_database):
    """Test admin can retrieve all documents."""
    headers = {"Authorization": f"Bearer {admin_token_fixture}"}
    # Upload a document as a test client for admin to see
    client_headers = {"Authorization": f"Bearer {test_client_token['access_token']}"}
    mock_file = tmp_path / "admin_doc.txt"
    mock_file.write_text("Admin test document")
    files = {"file": ("admin_doc.txt", mock_file.open("rb"), "text/plain")}
    await async_client.post("/api/documents/portal/upload", files=files, headers=client_headers)

    response = await async_client.get("/api/admin/documents", headers=headers)
    assert response.status_code == 200
    assert "documents" in response.json()
    assert response.json()["total"] >= 1
    assert any(d["fileName"] == "admin_doc.txt" for d in response.json()["documents"])

@pytest.mark.asyncio
async def test_admin_get_all_consents(async_client: AsyncClient, admin_token_fixture: str, db_client, clear_database):
    """Test admin can retrieve all consent logs."""
    headers = {"Authorization": f"Bearer {admin_token_fixture}"}
    # Log a consent as a dummy client
    consent_data = {"sessionId": "admin_session_1", "consentType": "Privacy", "agreed": True, "clientNumber": "TSTADMIN001"}
    await async_client.post("/api/consent", json=consent_data)

    response = await async_client.get("/api/admin/consents", headers=headers)
    assert response.status_code == 200
    assert "consents" in response.json()
    assert response.json()["total"] >= 1
    assert any(c["sessionId"] == "admin_session_1" for c in response.json()["consents"])

@pytest.mark.asyncio
async def test_admin_get_statistics(async_client: AsyncClient, admin_token_fixture: str, db_client):
    """Test admin can retrieve dashboard statistics."""
    headers = {"Authorization": f"Bearer {admin_token_fixture}"}
    response = await async_client.get("/api/admin/stats", headers=headers)
    assert response.status_code == 200
    stats = response.json()
    assert "totalClients" in stats
    assert "totalDocuments" in stats
    assert "totalForensicCases" in stats
    assert "totalMeetings" in stats

@pytest.mark.asyncio
async def test_admin_get_all_forensic_cases(async_client: AsyncClient, admin_token_fixture: str, db_client, mock_forensic_file: Path, test_client_token: dict):
    """Test admin can retrieve all forensic cases."""
    headers = {"Authorization": f"Bearer {admin_token_fixture}"}
    # Initiate a forensic analysis as a test client
    client_headers = {"Authorization": f"Bearer {test_client_token['access_token']}"}
    files = {"backup_file": ("admin_forensic.db", mock_forensic_file.open("rb"), "application/x-sqlite3")}
    with patch('backend.routers.forensics.SafeChildForensicsEngine.analyze_android_backup', new_callable=AsyncMock):
        await async_client.post("/api/forensics/analyze", files=files, headers=client_headers)

    response = await async_client.get("/api/admin/forensics", headers=headers)
    assert response.status_code == 200
    assert "cases" in response.json()
    assert response.json()["total"] >= 1
    assert any(c["file_name"] == "admin_forensic.db" for c in response.json()["cases"])

@pytest.mark.asyncio
async def test_admin_get_forensic_case_details(async_client: AsyncClient, admin_token_fixture: str, db_client, mock_forensic_file: Path, test_client_token: dict):
    """Test admin can retrieve detailed forensic case information."""
    headers = {"Authorization": f"Bearer {admin_token_fixture}"}
    # Initiate a forensic analysis
    client_headers = {"Authorization": f"Bearer {test_client_token['access_token']}"}
    files = {"backup_file": ("detail_forensic.db", mock_forensic_file.open("rb"), "application/x-sqlite3")}
    with patch('backend.routers.forensics.SafeChildForensicsEngine.analyze_android_backup', new_callable=AsyncMock):
        init_response = await async_client.post("/api/forensics/analyze", files=files, headers=client_headers)
    case_id = init_response.json()["case_id"]

    response = await async_client.get(f"/api/admin/forensics/{case_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["case_id"] == case_id
    assert response.json()["file_name"] == "detail_forensic.db"

@pytest.mark.asyncio
async def test_admin_delete_forensic_case(async_client: AsyncClient, admin_token_fixture: str, db_client, tmp_path, test_client_token: dict):
    """Test admin can force delete a forensic case and its associated files."""
    headers = {"Authorization": f"Bearer {admin_token_fixture}"}
    case_id = "CASE_ADMIN_DELETE"
    mock_uploaded_file = tmp_path / "uploaded_by_admin_test.db"
    mock_uploaded_file.write_text("admin delete content")
    mock_report_file = tmp_path / "report_by_admin_test.txt"
    mock_report_file.write_text("admin delete report content")

    db_client.forensic_analyses.insert_one({
        "case_id": case_id,
        "client_number": test_client_token["client_number"],
        "status": "processing", # Can delete even if processing
        "created_at": datetime.utcnow(),
        "uploaded_file": str(mock_uploaded_file),
        "report_txt": str(mock_report_file),
        "file_name": "admin_delete.db"
    })
    
    assert mock_uploaded_file.exists()
    assert mock_report_file.exists()

    response = await async_client.delete(f"/api/admin/forensics/{case_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["message"] == "Forensic case deleted successfully"

    case_in_db = db_client.forensic_analyses.find_one({"case_id": case_id})
    assert case_in_db is None

@pytest.mark.asyncio
async def test_admin_get_all_meetings(async_client: AsyncClient, admin_token_fixture: str, db_client, test_client_token: dict):
    """Test admin can retrieve all meetings."""
    headers = {"Authorization": f"Bearer {admin_token_fixture}"}
    # Create a meeting as a test client for admin to see
    client_headers = {"Authorization": f"Bearer {test_client_token['access_token']}"}
    meeting_data = {"title": "Admin View Meeting", "description": "Admin test", "scheduledTime": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(), "duration": 60, "meetingType": "video"}
    with patch('backend.routers.meetings.EmailService.send_meeting_confirmation'):
        await async_client.post("/api/meetings/create", json=meeting_data, headers=client_headers)

    response = await async_client.get("/api/admin/meetings", headers=headers)
    assert response.status_code == 200
    assert "meetings" in response.json()
    assert response.json()["total"] >= 1
    assert any(m["title"] == "Admin View Meeting" for m in response.json()["meetings"])

@pytest.mark.asyncio
async def test_admin_get_meeting_details(async_client: AsyncClient, admin_token_fixture: str, db_client, test_client_token: dict):
    """Test admin can retrieve detailed meeting information."""
    headers = {"Authorization": f"Bearer {admin_token_fixture}"}
    # Create a meeting
    client_headers = {"Authorization": f"Bearer {test_client_token['access_token']}"}
    meeting_data = {"title": "Admin Detail Meeting", "description": "Admin test", "scheduledTime": (datetime.now(timezone.utc) + timedelta(days=8)).isoformat(), "duration": 30, "meetingType": "audio"}
    with patch('backend.routers.meetings.EmailService.send_meeting_confirmation'):
        create_response = await async_client.post("/api/meetings/create", json=meeting_data, headers=client_headers)
    meeting_id = create_response.json()["meetingId"]

    response = await async_client.get(f"/api/admin/meetings/{meeting_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["meetingId"] == meeting_id
    assert response.json()["title"] == "Admin Detail Meeting"

@pytest.mark.asyncio
async def test_admin_update_meeting(async_client: AsyncClient, admin_token_fixture: str, db_client, test_client_token: dict):
    """Test admin can update meeting information."""
    headers = {"Authorization": f"Bearer {admin_token_fixture}"}
    # Create a meeting
    client_headers = {"Authorization": f"Bearer {test_client_token['access_token']}"}
    meeting_data = {"title": "Admin Update Meeting", "description": "Admin test", "scheduledTime": (datetime.now(timezone.utc) + timedelta(days=9)).isoformat(), "duration": 60, "meetingType": "video"}
    with patch('backend.routers.meetings.EmailService.send_meeting_confirmation'):
        create_response = await async_client.post("/api/meetings/create", json=meeting_data, headers=client_headers)
    meeting_id = create_response.json()["meetingId"]

    update_data = {"title": "Admin Updated Title", "status": "completed"}
    response = await async_client.patch(f"/api/admin/meetings/{meeting_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["success"] is True
    
    meeting_in_db = db_client.meetings.find_one({"meetingId": meeting_id})
    assert meeting_in_db["title"] == "Admin Updated Title"
    assert meeting_in_db["status"] == "completed"

@pytest.mark.asyncio
async def test_admin_delete_meeting(async_client: AsyncClient, admin_token_fixture: str, db_client, test_client_token: dict):
    """Test admin can force delete a meeting."""
    headers = {"Authorization": f"Bearer {admin_token_fixture}"}
    # Create a meeting
    client_headers = {"Authorization": f"Bearer {test_client_token['access_token']}"}
    meeting_data = {"title": "Admin Delete Meeting", "description": "Admin test", "scheduledTime": (datetime.now(timezone.utc) + timedelta(days=10)).isoformat(), "duration": 30, "meetingType": "audio"}
    with patch('backend.routers.meetings.EmailService.send_meeting_confirmation'):
        create_response = await async_client.post("/api/meetings/create", json=meeting_data, headers=client_headers)
    meeting_id = create_response.json()["meetingId"]

    response = await async_client.delete(f"/api/admin/meetings/{meeting_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["success"] is True
    
    meeting_in_db = db_client.meetings.find_one({"meetingId": meeting_id})
    assert meeting_in_db is None