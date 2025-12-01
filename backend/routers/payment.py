from fastapi import APIRouter, HTTPException, Depends, Body
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
import uuid

from .. import get_db
from ..auth import get_current_client

router = APIRouter(prefix="/payment", tags=["Payment"])

@router.post("/process-mock")
async def process_mock_payment(
    data: dict = Body(...),
    current_client: dict = Depends(get_current_client),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    MOCK Payment Endpoint for Production Testing.
    Simulates a successful payment transaction.
    """
    case_id = data.get("case_id")
    if not case_id:
        raise HTTPException(status_code=400, detail="Case ID is required")

    # Verify case exists and belongs to client
    case = await db.forensic_analyses.find_one({
        "case_id": case_id,
        "client_number": current_client["clientNumber"]
    })

    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    # Generate a fake transaction ID
    transaction_id = f"TXN_MOCK_{uuid.uuid4().hex[:12].upper()}"
    amount = 99.00 # Mock amount

    payment_record = {
        "transaction_id": transaction_id,
        "case_id": case_id,
        "client_number": current_client["clientNumber"],
        "amount": amount,
        "currency": "EUR",
        "status": "completed",
        "provider": "MOCK_GATEWAY",
        "created_at": datetime.utcnow()
    }

    # Save payment record
    await db.payments.insert_one(payment_record)

    # Update case with payment info (optional, if logic requires it)
    await db.forensic_analyses.update_one(
        {"case_id": case_id},
        {"$set": {"payment_status": "paid", "transaction_id": transaction_id}}
    )

    return {
        "success": True,
        "message": "Payment processed successfully (MOCK)",
        "transaction_id": transaction_id,
        "amount": amount,
        "status": "completed"
    }

@router.get("/history")
async def get_payment_history(
    current_client: dict = Depends(get_current_client),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get payment history for the client"""
    payments = await db.payments.find(
        {"client_number": current_client["clientNumber"]},
        {"_id": 0}
    ).sort("created_at", -1).to_list(length=100)

    return payments