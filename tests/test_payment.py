import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock
from datetime import datetime

@pytest.mark.skip(reason="Payment functionality will be addressed after the core project is production-ready.")
@pytest.mark.asyncio
async def test_create_checkout_session_success(async_client: AsyncClient, test_client_token: dict, db_client):
    """Test successful creation of a Stripe checkout session."""
    headers = {"Authorization": f"Bearer {test_client_token['access_token']}"}
    request_data = {"origin_url": "http://localhost:3000/success"}
    
    with patch('backend.routers.payment.create_consultation_checkout', new_callable=AsyncMock) as mock_create_checkout:
        mock_create_checkout.return_value = {
            "success": True,
            "url": "http://stripe.checkout.url/123",
            "session_id": "cs_test_123",
            "amount": 1000,
            "currency": "eur"
        }
        
        response = await async_client.post("/api/payment/create-checkout", json=request_data, headers=headers)
        assert response.status_code == 200
        assert response.json()["url"] == "http://stripe.checkout.url/123"
        assert response.json()["session_id"] == "cs_test_123"
        mock_create_checkout.assert_called_once_with(
            client_number=test_client_token["client_number"],
            client_email=test_client_token["email"],
            origin_url=request_data["origin_url"],
            package_id="consultation"
        )
        
        # Verify payment transaction record in DB
        transaction_in_db = db_client.payment_transactions.find_one({"session_id": "cs_test_123"})
        assert transaction_in_db is not None
        assert transaction_in_db["payment_status"] == "pending"

@pytest.mark.skip(reason="Payment functionality will be addressed after the core project is production-ready.")
@pytest.mark.asyncio
async def test_create_checkout_session_failure(async_client: AsyncClient, test_client_token: dict):
    """Test failure in creating a Stripe checkout session."""
    headers = {"Authorization": f"Bearer {test_client_token['access_token']}"}
    request_data = {"origin_url": "http://localhost:3000/success"}
    
    with patch('backend.routers.payment.create_consultation_checkout', new_callable=AsyncMock) as mock_create_checkout:
        mock_create_checkout.return_value = {"success": False, "error": "Stripe error"}
        
        response = await async_client.post("/api/payment/create-checkout", json=request_data, headers=headers)
        assert response.status_code == 400
        assert "Stripe error" in response.json()["detail"]
        
@pytest.mark.skip(reason="Payment functionality will be addressed after the core project is production-ready.")
@pytest.mark.asyncio
async def test_check_checkout_status_paid(async_client: AsyncClient, test_client_token: dict, db_client):
    """Test checking a paid checkout session status."""
    headers = {"Authorization": f"Bearer {test_client_token['access_token']}"}
    session_id = "cs_test_paid_123"
    
    # Simulate an initiated payment transaction
    db_client.payment_transactions.insert_one({
        "session_id": session_id,
        "client_number": test_client_token["client_number"],
        "payment_status": "initiated",
        "status": "initiated",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    })
    
    with patch('backend.routers.payment.get_checkout_status', new_callable=AsyncMock) as mock_get_status:
        mock_get_status.return_value = {
            "success": True,
            "status": "complete",
            "payment_status": "paid",
            "amount_total": 1000,
            "currency": "eur"
        }
        
        response = await async_client.get(f"/api/payment/checkout/status/{session_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["payment_status"] == "paid"
        
        # Verify DB update
        transaction_in_db = db_client.payment_transactions.find_one({"session_id": session_id})
        assert transaction_in_db["payment_status"] == "paid"
        assert transaction_in_db["completed_at"] is not None

@pytest.mark.skip(reason="Payment functionality will be addressed after the core project is production-ready.")
@pytest.mark.asyncio
async def test_check_checkout_status_pending(async_client: AsyncClient, test_client_token: dict, db_client):
    """Test checking a pending checkout session status."""
    headers = {"Authorization": f"Bearer {test_client_token['access_token']}"}
    session_id = "cs_test_pending_456"
    
    db_client.payment_transactions.insert_one({
        "session_id": session_id,
        "client_number": test_client_token["client_number"],
        "payment_status": "initiated",
        "status": "initiated",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    })
    
    with patch('backend.routers.payment.get_checkout_status', new_callable=AsyncMock) as mock_get_status:
        mock_get_status.return_value = {
            "success": True,
            "status": "open",
            "payment_status": "unpaid",
            "amount_total": 1000,
            "currency": "eur"
        }
        
        response = await async_client.get(f"/api/payment/checkout/status/{session_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["payment_status"] == "unpaid"

@pytest.mark.skip(reason="Payment functionality will be addressed after the core project is production-ready.")
@pytest.mark.asyncio
async def test_stripe_webhook_payment_succeeded(async_client: AsyncClient, db_client):
    """Test Stripe webhook for payment_succeeded event."""
    session_id = "cs_webhook_success_789"
    
    # Simulate an initiated payment transaction
    db_client.payment_transactions.insert_one({
        "session_id": session_id,
        "client_number": "TESTWEBHOOK1",
        "payment_status": "initiated",
        "status": "initiated",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    })
    
    mock_payload = b'{"id": "evt_123", "type": "checkout.session.completed", "data": {"object": {"id": "cs_webhook_success_789", "payment_status": "paid"}}}'
    mock_signature = "t=1678886400,v1=fake_signature"
    
    with patch('backend.routers.payment.handle_webhook', new_callable=AsyncMock) as mock_handle_webhook:
        mock_handle_webhook.return_value = {
            "success": True,
            "session_id": session_id,
            "payment_status": "paid",
            "event_type": "checkout.session.completed"
        }
        
        response = await async_client.post("/api/payment/webhook", content=mock_payload, headers={"Stripe-Signature": mock_signature})
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        
        # Verify DB update
        transaction_in_db = db_client.payment_transactions.find_one({"session_id": session_id})
        assert transaction_in_db["payment_status"] == "paid"
        assert transaction_in_db["webhook_received"] is True
        assert transaction_in_db["webhook_event_type"] == "checkout.session.completed"

@pytest.mark.skip(reason="Payment functionality will be addressed after the core project is production-ready.")
@pytest.mark.asyncio
async def test_stripe_webhook_invalid_signature(async_client: AsyncClient):
    """Test Stripe webhook with invalid signature."""
    mock_payload = b'{"id": "evt_123", "type": "checkout.session.completed", "data": {"object": {"id": "cs_invalid_789", "payment_status": "paid"}}}'
    mock_signature = "t=1678886400,v1=invalid_signature"
    
    with patch('backend.routers.payment.handle_webhook', new_callable=AsyncMock) as mock_handle_webhook:
        mock_handle_webhook.return_value = {"success": False, "error": "Invalid signature"}
        
        response = await async_client.post("/api/payment/webhook", content=mock_payload, headers={"Stripe-Signature": mock_signature})
        assert response.status_code == 400
        assert "Invalid signature" in response.json()["detail"]