from fastapi import APIRouter, Depends, HTTPException, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from .. import get_db
from ..models import Consent, ConsentCreate

router = APIRouter(prefix="/consent", tags=["Consent Management"])

@router.post("")
async def log_consent(consent_data: ConsentCreate, request: Request, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Log user consent"""
    try:
        ip_address = request.client.host
        
        consent_dict = consent_data.model_dump()
        consent_dict['ipAddress'] = ip_address
        
        consent = Consent.model_validate(consent_dict)
        
        await db.consents.insert_one(consent.model_dump())
        
        return {
            "success": True,
            "consentId": str(consent.id),
            "timestamp": consent.timestamp
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}")
async def get_consent(session_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Get consent details for a session"""
    consent = await db.consents.find_one({"sessionId": session_id}, {"_id": 0})
    if not consent:
        raise HTTPException(status_code=404, detail="Consent not found")
    return consent
