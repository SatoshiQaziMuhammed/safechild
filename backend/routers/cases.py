from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from .. import get_db
from ..models import LandmarkCase

router = APIRouter(prefix="/cases", tags=["Landmark Cases"])

@router.get("/landmark")
async def get_landmark_cases(db: AsyncIOMotorDatabase = Depends(get_db)):
    """Get all landmark cases"""
    cases = await db.landmark_cases.find({}, {"_id": 0}).to_list(length=None)
    return {"cases": cases}

@router.get("/landmark/{case_number}")
async def get_landmark_case(case_number: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Get specific landmark case"""
    case = await db.landmark_cases.find_one({"caseNumber": case_number}, {"_id": 0})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case
