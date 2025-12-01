import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_landmark_cases_success(async_client: AsyncClient, db_client):
    """Test retrieving all landmark cases."""
    # Assuming conftest.py seeds some landmark cases
    response = await async_client.get("/api/cases/landmark")
    assert response.status_code == 200
    assert "cases" in response.json()
    assert len(response.json()["cases"]) > 0  # Should have seeded cases

@pytest.mark.asyncio
async def test_get_landmark_case_by_number_success(async_client: AsyncClient, db_client):
    """Test retrieving a specific landmark case by its number."""
    # Assuming conftest.py seeds with caseNumber: LC2023001
    case_number = "LC2023001"
    response = await async_client.get(f"/api/cases/landmark/{case_number}")
    assert response.status_code == 200
    assert response.json()["caseNumber"] == case_number

@pytest.mark.asyncio
async def test_get_landmark_case_by_number_not_found(async_client: AsyncClient):
    """Test retrieving a non-existent landmark case."""
    response = await async_client.get("/api/cases/landmark/NONEXISTENTLC")
    assert response.status_code == 404
    assert "Case not found" in response.json()["detail"]
