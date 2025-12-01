from fastapi import APIRouter, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from .. import get_db
from ..models import Client, ClientCreate
from ..utils import generate_client_number

router = APIRouter(prefix="/clients", tags=["Client Management"])

@router.post("")
async def create_client(client_data: ClientCreate, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Create a new client and generate client number"""
    try:
        client_number = generate_client_number()
        
        existing = await db.clients.find_one({"clientNumber": client_number})
        while existing:
            client_number = generate_client_number()
            existing = await db.clients.find_one({"clientNumber": client_number})
        
        client = Client(
            clientNumber=client_number,
            **client_data.model_dump()
        )
        
        await db.clients.insert_one(client.model_dump())
        
        return {
            "success": True,
            "clientNumber": client_number,
            "message": "Client registered successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{client_number}")
async def get_client(client_number: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Get client details by client number"""
    client = await db.clients.find_one({"clientNumber": client_number}, {"_id": 0})
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

@router.get("/{client_number}/validate")
async def validate_client_number(client_number: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Validate if client number exists"""
    client = await db.clients.find_one({"clientNumber": client_number}, {"_id": 0})
    return {
        "valid": client is not None,
        "client": client if client else None
    }
