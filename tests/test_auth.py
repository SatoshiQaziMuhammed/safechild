import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_client_success(async_client: AsyncClient, db_client):
    """Test successful client registration."""
    register_data = {
        "firstName": "Test",
        "lastName": "User",
        "email": "testregister@example.com",
        "password": "TestPass123!",
        "phone": "1234567890",
        "country": "Testland",
        "caseType": "General"
    }
    response = await async_client.post("/api/auth/register", json=register_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "clientNumber" in response.json()
    assert response.json()["email"] == register_data["email"]
    
    # Verify client exists in DB
    client_in_db = db_client.clients.find_one({"email": register_data["email"]})
    assert client_in_db is not None
    assert client_in_db["firstName"] == register_data["firstName"]

@pytest.mark.asyncio
async def test_register_client_duplicate_email(async_client: AsyncClient, db_client):
    """Test registration with a duplicate email."""
    register_data = {
        "firstName": "Duplicate",
        "lastName": "User",
        "email": "duplicate@example.com",
        "password": "TestPass123!",
        "phone": "1234567890",
        "country": "Testland",
        "caseType": "General"
    }
    await async_client.post("/api/auth/register", json=register_data)
    response = await async_client.post("/api/auth/register", json=register_data)
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

@pytest.mark.asyncio
async def test_login_client_success(async_client: AsyncClient, db_client):
    """Test successful client login."""
    register_data = {
        "firstName": "Login",
        "lastName": "User",
        "email": "testlogin@example.com",
        "password": "LoginPass123!",
        "phone": "1234567890",
        "country": "Testland",
        "caseType": "General"
    }
    await async_client.post("/api/auth/register", json=register_data)
    
    login_data = {
        "email": register_data["email"],
        "password": register_data["password"]
    }
    response = await async_client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["email"] == register_data["email"]

@pytest.mark.asyncio
async def test_login_client_invalid_credentials(async_client: AsyncClient):
    """Test client login with invalid credentials."""
    login_data = {
        "email": "nonexistent@example.com",
        "password": "wrongpass"
    }
    response = await async_client.post("/api/auth/login", json=login_data)
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]

@pytest.mark.asyncio
async def test_get_current_user_info_success(async_client: AsyncClient, test_client_token: dict):
    """Test retrieving current authenticated user info."""
    headers = {"Authorization": f"Bearer {test_client_token['access_token']}"}
    response = await async_client.get("/api/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["clientNumber"] == test_client_token["client_number"]
    assert response.json()["email"] == test_client_token["email"]

@pytest.mark.asyncio
async def test_get_current_user_info_unauthorized(async_client: AsyncClient):
    """Test retrieving current user info without authentication."""
    response = await async_client.get("/api/auth/me")
    assert response.status_code == 403
    assert "Not authenticated" in response.json()["detail"]
