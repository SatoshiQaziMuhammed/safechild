import pytest
from httpx import AsyncClient
from unittest.mock import patch

@pytest.mark.asyncio
async def test_send_message_success_client(async_client: AsyncClient, db_client, test_client_token: dict):
    """Test successful sending of a chat message by a client with email notification."""
    chat_data = {
        "sessionId": "chat_session_001",
        "sender": "client",
        "clientNumber": test_client_token["client_number"],
        "message": "Hello, I need assistance."
    }
    headers = {"Authorization": f"Bearer {test_client_token['access_token']}"}
    
    with patch('backend.routers.chat.EmailService.send_email') as mock_send_email:
        response = await async_client.post("/api/chat/message", json=chat_data, headers=headers)
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert "messageId" in response.json()
        mock_send_email.assert_called_once() # Verify admin email was attempted to be sent
    
    msg_in_db = await db_client.chat_messages.find_one({"sessionId": chat_data["sessionId"]})
    assert msg_in_db is not None
    assert msg_in_db["message"] == chat_data["message"]

@pytest.mark.asyncio
async def test_send_message_success_bot(async_client: AsyncClient, db_client):
    """Test successful sending of a chat message by the bot (no email notification)."""
    chat_data = {
        "sessionId": "chat_session_002",
        "sender": "bot",
        "clientNumber": "BOT001",
        "message": "How can I help you?"
    }
    # No authentication needed for bot messages as they are internal, or should be handled by an internal token system
    with patch('backend.routers.chat.EmailService.send_email') as mock_send_email:
        response = await async_client.post("/api/chat/message", json=chat_data)
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert "messageId" in response.json()
        mock_send_email.assert_not_called() # No email for bot messages
    
    msg_in_db = await db_client.chat_messages.find_one({"sessionId": chat_data["sessionId"]})
    assert msg_in_db is not None
    assert msg_in_db["message"] == chat_data["message"]

@pytest.mark.asyncio
async def test_get_chat_history_success(async_client: AsyncClient, db_client, test_client_token: dict):
    """Test retrieving chat history for an existing session."""
    session_id = "chat_session_003"
    # Send a couple of messages for history
    chat_data_1 = {
        "sessionId": session_id,
        "sender": "client",
        "clientNumber": test_client_token["client_number"],
        "message": "First message."
    }
    chat_data_2 = {
        "sessionId": session_id,
        "sender": "bot",
        "clientNumber": test_client_token["client_number"],
        "message": "Second message."
    }
    headers = {"Authorization": f"Bearer {test_client_token['access_token']}"}
    await async_client.post("/api/chat/message", json=chat_data_1, headers=headers)
    await async_client.post("/api/chat/message", json=chat_data_2, headers=headers)
    
    response = await async_client.get(f"/api/chat/{session_id}", headers=headers)
    assert response.status_code == 200
    assert "messages" in response.json()
    assert len(response.json()["messages"]) == 2
    assert response.json()["messages"][0]["message"] == "First message."
    assert response.json()["messages"][1]["message"] == "Second message."

@pytest.mark.asyncio
async def test_get_chat_history_empty(async_client: AsyncClient, test_client_token: dict):
    """Test retrieving chat history for a non-existent session."""
    headers = {"Authorization": f"Bearer {test_client_token['access_token']}"}
    response = await async_client.get("/api/chat/nonexistent_chat_session", headers=headers)
    assert response.status_code == 200
    assert "messages" in response.json()
    assert len(response.json()["messages"]) == 0

@pytest.mark.asyncio
async def test_get_chat_history_unauthorized(async_client: AsyncClient):
    """Test retrieving chat history without authentication."""
    response = await async_client.get("/api/chat/some_session_id")
    assert response.status_code == 401
    assert "Could not validate credentials" in response.json()["detail"]
