import pytest
from httpx import AsyncClient
from unittest.mock import patch
import os
from pathlib import Path

@pytest.fixture
def mock_file_content():
    """Provides dummy file content for uploads."""
    return b"This is a test document content."

@pytest.fixture
def mock_document_file(tmp_path, mock_file_content):
    """Creates a temporary mock document file for testing uploads."""
    file_path = tmp_path / "test_document.txt"
    file_path.write_bytes(mock_file_content)
    return file_path

@pytest.mark.asyncio
async def test_upload_my_document_success(async_client: AsyncClient, test_client_token: dict, mock_document_file: Path, db_client):
    """Test successful document upload by an authenticated client."""
    headers = {"Authorization": f"Bearer {test_client_token['access_token']}"}
    files = {"file": ("test_document.txt", mock_document_file.open("rb"), "text/plain")}
    
    with patch('backend.routers.documents.EmailService.send_document_uploaded') as mock_send_email:
        response = await async_client.post("/api/documents/portal/upload", files=files, headers=headers)
    
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "documentNumber" in response.json()
    assert response.json()["fileName"] == "test_document.txt"
    mock_send_email.assert_called_once() # Verify email was attempted to be sent
    
    # Verify document exists in DB
    doc_in_db = db_client.documents.find_one({"fileName": "test_document.txt"})
    assert doc_in_db is not None
    assert doc_in_db["clientNumber"] == test_client_token["client_number"]

@pytest.mark.asyncio
async def test_upload_my_document_unauthorized(async_client: AsyncClient, mock_document_file: Path):
    """Test document upload by an unauthenticated client."""
    files = {"file": ("test_document.txt", mock_document_file.open("rb"), "text/plain")}
    response = await async_client.post("/api/documents/upload", files=files)
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]

@pytest.mark.asyncio
async def test_upload_my_document_unsupported_type(async_client: AsyncClient, test_client_token: dict, tmp_path, mock_file_content):
    """Test document upload with an unsupported file type."""
    headers = {"Authorization": f"Bearer {test_client_token['access_token']}"}
    unsupported_file = tmp_path / "unsupported.exe"
    unsupported_file.write_bytes(mock_file_content)
    files = {"file": ("unsupported.exe", unsupported_file.open("rb"), "application/octet-stream")}
    response = await async_client.post("/api/documents/portal/upload", files=files, headers=headers)
    assert response.status_code == 400
    assert "File type not allowed" in response.json()["detail"]

@pytest.mark.asyncio
async def test_upload_my_document_too_large(async_client: AsyncClient, test_client_token: dict, tmp_path):
    """Test document upload with a file exceeding the size limit."""
    headers = {"Authorization": f"Bearer {test_client_token['access_token']}"}
    large_file = tmp_path / "large_file.txt"
    large_file.write_bytes(b"A" * (10 * 1024 * 1024 + 1)) # 10MB + 1 byte
    files = {"file": ("large_file.txt", large_file.open("rb"), "text/plain")}
    response = await async_client.post("/api/documents/portal/upload", files=files, headers=headers)
    assert response.status_code == 400
    assert "File size exceeds 10MB limit" in response.json()["detail"]

@pytest.mark.asyncio
async def test_get_my_documents(async_client: AsyncClient, test_client_token: dict, mock_document_file: Path, db_client):
    """Test retrieving documents for the authenticated client."""
    headers = {"Authorization": f"Bearer {test_client_token['access_token']}"}
    
    # Upload a document first
    files = {"file": ("doc_for_listing.txt", mock_document_file.open("rb"), "text/plain")}
    await async_client.post("/api/documents/portal/upload", files=files, headers=headers)
            
    response = await async_client.get("/api/documents/portal/my-documents", headers=headers)
    assert response.status_code == 200
    assert "documents" in response.json()
    assert len(response.json()["documents"]) >= 1
    assert any(d["fileName"] == "doc_for_listing.txt" for d in response.json()["documents"])

@pytest.mark.asyncio
async def test_download_document_success(async_client: AsyncClient, test_client_token: dict, mock_document_file: Path, db_client, mock_file_content):
    """Test successful document download."""
    headers = {"Authorization": f"Bearer {test_client_token['access_token']}"}
    files = {"file": ("download_test.txt", mock_document_file.open("rb"), "text/plain")}
    upload_response = await async_client.post("/api/documents/portal/upload", files=files, headers=headers)
    assert upload_response.status_code == 200
    doc_number = upload_response.json()["documentNumber"]
    
    response = await async_client.get(f"/api/documents/{doc_number}/download", headers=headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/octet-stream"
    assert response.headers["content-disposition"] == f"attachment; filename=\"download_test.txt\""
    assert response.content == mock_file_content

@pytest.mark.asyncio
async def test_download_document_not_found(async_client: AsyncClient, test_client_token: dict):
    """Test downloading a non-existent document."""
    headers = {"Authorization": f"Bearer {test_client_token['access_token']}"}
    response = await async_client.get(f"/api/documents/NONEXISTENTDOC/download", headers=headers)
    assert response.status_code == 404
    assert "Document not found" in response.json()["detail"]