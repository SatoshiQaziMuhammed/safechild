from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..models import Client, ClientRegister, ClientLogin, Token
from ..auth import get_password_hash, verify_password, create_access_token, get_current_client
from ..email_service import EmailService
from ..utils import generate_client_number
from .. import get_db
import logging

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = logging.getLogger(__name__)

@router.post("/register", response_model=Token)
async def register_client(client_data: ClientRegister, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Register a new client with login credentials"""
    try:
        existing_client = await db.clients.find_one({"email": client_data.email})
        if existing_client:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        client_number = generate_client_number()
        hashed_password = get_password_hash(client_data.password)
        
        new_client = Client(
            clientNumber=client_number,
            firstName=client_data.firstName,
            lastName=client_data.lastName,
            email=client_data.email,
            phone=client_data.phone,
            country=client_data.country,
            caseType=client_data.caseType,
            hashedPassword=hashed_password,
            role="client",
            status="active"
        )
        
        await db.clients.insert_one(new_client.model_dump())
        
        try:
            EmailService.send_welcome_email(
                recipient_email=client_data.email,
                recipient_name=f"{client_data.firstName} {client_data.lastName}",
                client_number=client_number
            )
            logger.info(f"Welcome email sent to {client_data.email}")
        except Exception as e:
            logger.error(f"Failed to send welcome email: {str(e)}")
        
        access_token = create_access_token(
            data={"sub": client_number, "email": client_data.email, "role": "client"}
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            clientNumber=client_number,
            email=client_data.email,
            firstName=client_data.firstName,
            lastName=client_data.lastName
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login", response_model=Token)
async def login_client(credentials: ClientLogin, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Login with email and password"""
    try:
        client = await db.clients.find_one({"email": credentials.email})
        
        if not client or not client.get("hashedPassword"):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        if not verify_password(credentials.password, client["hashedPassword"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        access_token = create_access_token(
            data={
                "sub": client["clientNumber"], 
                "email": client["email"],
                "role": client.get("role", "client")
            }
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            clientNumber=client["clientNumber"],
            email=client["email"],
            firstName=client["firstName"],
            lastName=client["lastName"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/me")
async def get_current_user_info(current_client: dict = Depends(get_current_client), db: AsyncIOMotorDatabase = Depends(get_db)):
    """Get current authenticated client info"""
    try:
        client = await db.clients.find_one(
            {"clientNumber": current_client["clientNumber"]},
            {"_id": 0, "hashedPassword": 0}
        )
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        return client
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
