import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_client(async_client: AsyncClient, admin_token_fixture: str, db_client):
    """Test creating a new client via admin endpoint."""
    headers = {"Authorization": f"Bearer {admin_token_fixture}"}
    client_data = {
        "firstName": "New",
        "lastName": "Client",
        "email": "newclient@example.com",
        "phone": "1112223344",
        "country": "Testlandia",
        "caseType": "Divorce"
    }
    response = await async_client.post("/api/admin/clients/create", json=client_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "clientNumber" in response.json()
    
    client_in_db = db_client.clients.find_one({"email": client_data["email"]})
    assert client_in_db is not None
    assert client_in_db["firstName"] == client_data["firstName"]

@pytest.mark.asyncio
async def test_get_client_details(async_client: AsyncClient, admin_token_fixture: str, test_client_token: dict):
    """Test retrieving client details by client number via admin endpoint."""
    headers = {"Authorization": f"Bearer {admin_token_fixture}"}
    client_number = test_client_token["client_number"]
    response = await async_client.get(f"/api/admin/clients/{client_number}", headers=headers)
    assert response.status_code == 200
    assert response.json()["client"]["clientNumber"] == client_number
    assert response.json()["client"]["email"] == test_client_token["email"]

@pytest.mark.asyncio
async def test_get_client_details_not_found(async_client: AsyncClient, admin_token_fixture: str):
    """Test retrieving details for a non-existent client."""
    headers = {"Authorization": f"Bearer {admin_token_fixture}"}
    response = await async_client.get("/api/admin/clients/NONEXISTENT123", headers=headers)
    assert response.status_code == 404
    assert "Client not found" in response.json()["detail"]

@pytest.mark.asyncio
async def test_validate_client_number_exists(async_client: AsyncClient, admin_token_fixture: str, test_client_token: dict):
    """Test validating an existing client number."""
    headers = {"Authorization": f"Bearer {admin_token_fixture}"}
    client_number = test_client_token["client_number"]
    response = await async_client.get(f"/api/clients/{client_number}/validate", headers=headers)
    assert response.status_code == 200
    assert response.json()["valid"] is True
    assert response.json()["client"]["clientNumber"] == client_number

@pytest.mark.asyncio
async def test_validate_client_number_non_existent(async_client: AsyncClient, admin_token_fixture: str):
    """Test validating a non-existent client number."""
    headers = {"Authorization": f"Bearer {admin_token_fixture}"}
    response = await async_client.get("/api/clients/INVALIDNUM/validate", headers=headers)
    assert response.status_code == 200
    assert response.json()["valid"] is False
    assert response.json()["client"] is None