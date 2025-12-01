import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock
from pathlib import Path
import os
from datetime import datetime

@pytest.mark.asyncio
async def test_start_forensic_analysis_success(async_client: AsyncClient, test_client_token: dict, mock_forensic_file: Path, db_client):
    """Test successful initiation of forensic analysis."""
    headers = {"Authorization": f"Bearer {test_client_token['access_token']}"}
    files = {"backup_file": ("mock_forensic.db", mock_forensic_file.open("rb"), "application/x-sqlite3")}
    
    with patch('backend.routers.forensics.SafeChildForensicsEngine.analyze_android_backup', new_callable=AsyncMock) as mock_analyze:
        mock_analyze.return_value = {"success": True, "report_txt": "/tmp/test_report.txt"}
        with patch('backend.routers.forensics.EmailService.send_forensic_analysis_complete') as mock_send_email:
            response = await async_client.post("/api/forensics/analyze", files=files, headers=headers)
            assert response.status_code == 200
            assert response.json()["success"] is True
            assert "case_id" in response.json()
            assert response.json()["message"] == "Forensic analysis started. You will be notified when complete."
            
            case_id = response.json()["case_id"]
            analysis_record = db_client.forensic_analyses.find_one({"case_id": case_id})
            assert analysis_record is not None
            assert analysis_record["status"] == "processing"
            mock_analyze.assert_called_once() # The background task would call this
            mock_send_email.assert_not_called() # Email is sent after completion, not initiation

@pytest.mark.asyncio
async def test_start_forensic_analysis_unsupported_file_type(async_client: AsyncClient, test_client_token: dict, tmp_path):
    """Test forensic analysis with an unsupported file type."""
    headers = {"Authorization": f"Bearer {test_client_token['access_token']}"}
    unsupported_file = tmp_path / "unsupported.txt"
    unsupported_file.write_text("plain text")
    files = {"backup_file": ("unsupported.txt", unsupported_file.open("rb"), "text/plain")}
    
    response = await async_client.post("/api/forensics/analyze", files=files, headers=headers)
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]

@pytest.mark.asyncio
async def test_get_forensic_status_processing(async_client: AsyncClient, test_client_token: dict, db_client):
    """Test retrieving status of a processing forensic analysis."""
    headers = {"Authorization": f"Bearer {test_client_token['access_token']}"}
    case_id = "CASE_TEST1_PROCESSING"
    db_client.forensic_analyses.insert_one({
        "case_id": case_id,
        "client_number": test_client_token["client_number"],
        "status": "processing",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "uploaded_file": "/tmp/mock_file.db",
        "file_name": "mock_file.db"
    })
    
    response = await async_client.get(f"/api/forensics/status/{case_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "processing"
    assert response.json()["case_id"] == case_id

@pytest.mark.asyncio
async def test_get_forensic_status_completed(async_client: AsyncClient, test_client_token: dict, db_client):
    """Test retrieving status of a completed forensic analysis."""
    headers = {"Authorization": f"Bearer {test_client_token['access_token']}"}
    case_id = "CASE_TEST2_COMPLETED"
    db_client.forensic_analyses.insert_one({
        "case_id": case_id,
        "client_number": test_client_token["client_number"],
        "status": "completed",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "completed_at": datetime.utcnow(),
        "report_txt": "/tmp/completed_report.txt",
        "file_name": "completed_file.db",
        "statistics": {"total_entries": 100}
    })
    
    response = await async_client.get(f"/api/forensics/status/{case_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    assert "statistics" in response.json()
    assert response.json()["statistics"]["total_entries"] == 100

@pytest.mark.asyncio
async def test_download_forensic_report_success(async_client: AsyncClient, test_client_token: dict, db_client, tmp_path):
    """Test successful download of a forensic report."""
    headers = {"Authorization": f"Bearer {test_client_token['access_token']}"}
    case_id = "CASE_REPORT_DOWNLOAD"
    report_file_path = tmp_path / f"{case_id}.txt"
    report_file_path.write_text("This is a forensic report content.")
    
    db_client.forensic_analyses.insert_one({
        "case_id": case_id,
        "client_number": test_client_token["client_number"],
        "status": "completed",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "completed_at": datetime.utcnow(),
        "report_txt": str(report_file_path),
        "file_name": "source.db"
    })
    
    response = await async_client.get(f"/api/forensics/report/{case_id}?format=txt", headers=headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/plain"
    assert response.headers["content-disposition"] == f"attachment; filename=\"SafeChild_Report_{case_id}.txt\""
    assert response.content.decode() == "This is a forensic report content."

@pytest.mark.asyncio
async def test_download_forensic_report_not_completed(async_client: AsyncClient, test_client_token: dict, db_client):
    """Test downloading a report for a case that is not completed."""
    headers = {"Authorization": f"Bearer {test_client_token['access_token']}"}
    case_id = "CASE_REPORT_PENDING"
    db_client.forensic_analyses.insert_one({
        "case_id": case_id,
        "client_number": test_client_token["client_number"],
        "status": "processing",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "uploaded_file": "/tmp/mock.db",
        "file_name": "mock.db"
    })
    
    response = await async_client.get(f"/api/forensics/report/{case_id}?format=txt", headers=headers)
    assert response.status_code == 400
    assert "Analysis not completed yet" in response.json()["detail"]

@pytest.mark.asyncio
async def test_get_my_forensic_cases(async_client: AsyncClient, test_client_token: dict, db_client):
    """Test retrieving all forensic cases for the authenticated client."""
    headers = {"Authorization": f"Bearer {test_client_token['access_token']}"}
    # Assume some cases are created by other tests or fixtures
    response = await async_client.get("/api/forensics/my-cases", headers=headers)
    assert response.status_code == 200
    assert "cases" in response.json()
    assert "total" in response.json()

@pytest.mark.asyncio
async def test_delete_forensic_case_success(async_client: AsyncClient, test_client_token: dict, db_client, tmp_path):
    """Test successful deletion of a completed forensic case and its files."""
    headers = {"Authorization": f"Bearer {test_client_token['access_token']}"}
    case_id = "CASE_DELETE_SUCCESS"
    mock_uploaded_file = tmp_path / "uploaded_to_delete.db"
    mock_uploaded_file.write_text("uploaded content")
    mock_report_file = tmp_path / "report_to_delete.txt"
    mock_report_file.write_text("report content")

    db_client.forensic_analyses.insert_one({
        "case_id": case_id,
        "client_number": test_client_token["client_number"],
        "status": "completed",
        "created_at": datetime.utcnow(),
        "uploaded_file": str(mock_uploaded_file),
        "report_txt": str(mock_report_file),
        "file_name": "to_delete.db"
    })
    
    assert mock_uploaded_file.exists()
    assert mock_report_file.exists()

    response = await async_client.delete(f"/api/forensics/case/{case_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["message"] == "Case deleted successfully"

    case_in_db = db_client.forensic_analyses.find_one({"case_id": case_id})
    assert case_in_db is None
    assert not mock_uploaded_file.exists()
    assert not mock_report_file.exists()

@pytest.mark.asyncio
async def test_delete_forensic_case_processing(async_client: AsyncClient, test_client_token: dict, db_client):
    """Test attempting to delete a forensic case while it is processing."""
    headers = {"Authorization": f"Bearer {test_client_token['access_token']}"}
    case_id = "CASE_DELETE_PROCESSING"
    db_client.forensic_analyses.insert_one({
        "case_id": case_id,
        "client_number": test_client_token["client_number"],
        "status": "processing",
        "created_at": datetime.utcnow(),
        "uploaded_file": "/tmp/processing.db",
        "file_name": "processing.db"
    })
    
    response = await async_client.delete(f"/api/forensics/case/{case_id}", headers=headers)
    assert response.status_code == 400
    assert "Cannot delete case while processing" in response.json()["detail"]

