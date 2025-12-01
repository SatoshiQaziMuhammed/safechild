from fastapi import APIRouter, HTTPException, Depends, Body, UploadFile, File, BackgroundTasks
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
import uuid
from pathlib import Path

from .. import get_db
from ..auth import get_current_admin # Admin check
from ..models import EvidenceRequest
from backend.routers.forensics import run_forensic_analysis_task
from backend.security_service import security_service

router = APIRouter(prefix="/requests", tags=["Evidence Requests"])

@router.post("/create")
async def create_evidence_request(
    data: dict = Body(...),
    current_user: dict = Depends(get_current_admin), # Only admins/lawyers
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Lawyer creates a magic link request for a client.
    Data: { "clientNumber": "123", "types": ["photos", "whatsapp"] }
    """
    # Generate a unique, secure token (URL-safe)
    token = uuid.uuid4().hex 
    
    request = {
        "id": str(uuid.uuid4()),
        "token": token,
        "clientNumber": data.get("clientNumber"),
        "lawyerId": str(current_user.get("_id", "admin")),
        "requestedTypes": data.get("types", ["any"]),
        "status": "pending",
        "expiresAt": datetime.utcnow() + timedelta(days=7), # Valid for 7 days
        "createdAt": datetime.utcnow()
    }
    
    await db.evidence_requests.insert_one(request)
    
    # Return the full magic link (in a real app, from config)
    return {
        "success": True,
        "magic_link": f"/upload-request/{token}",
        "token": token
    }

@router.get("/{token}")
async def get_request_details(
    token: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Public endpoint for the client to see what is requested.
    No login required, Token is the key.
    """
    req = await db.evidence_requests.find_one({"token": token})
    if not req:
        raise HTTPException(status_code=404, detail="Invalid or expired link.")
        
    if req["expiresAt"] < datetime.utcnow():
        raise HTTPException(status_code=410, detail="This link has expired.")
        
    # Get client name for personalization
    client = await db.clients.find_one({"clientNumber": req["clientNumber"]})
    client_name = f"{client.get('firstName', '')} {client.get('lastName', '')}" if client else "Valued Client"
    
    return {
        "clientName": client_name,
        "requestedTypes": req["requestedTypes"],
        "status": req["status"]
    }

@router.post("/{token}/upload")
async def upload_requested_evidence(
    token: str,
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Public upload endpoint secure by Token.
    """
    req = await db.evidence_requests.find_one({"token": token})
    if not req:
        raise HTTPException(status_code=404, detail="Invalid link.")
    
    # Process the file using the existing forensic logic
    # Reuse code from forensics.py logic effectively
    
    case_id = f"REQ_{req['clientNumber']}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    
    upload_dir = Path("/tmp/forensics_uploads")
    upload_dir.mkdir(exist_ok=True, parents=True)
    
    file_path = upload_dir / f"{case_id}_{file.filename}.enc"
    
    content = await file.read()
    file_size = len(content)
    
    # Encrypt
    encryption_result = security_service.encrypt_file(content)
    with open(file_path, "wb") as buffer:
        buffer.write(encryption_result['encrypted_data'])
        
    encryption_metadata = {k: v for k, v in encryption_result.items() if k != 'encrypted_data'}
    
    # Determine analysis type based on extension
    file_ext = Path(file.filename).suffix.lower()
    forensic_extensions = ['.db', '.tar', '.gz', '.tgz', '.ab', '.zip']
    analysis_type = "forensic_parsing" if file_ext in forensic_extensions else "direct_evidence"

    # Chain of Custody
    coc_event = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow(),
        "actor": f"Client (via Magic Link): {req['clientNumber']}",
        "action": "EVIDENCE_UPLOAD_MAGIC_LINK",
        "details": f"File uploaded via requested link. Token: {token[:8]}...",
        "hashAtEvent": None
    }
    
    analysis_record = {
        "case_id": case_id,
        "client_number": req["clientNumber"],
        "request_token": token, # Link back to request
        "status": "processing",
        "analysis_type": analysis_type,
        "uploaded_file": str(file_path),
        "file_name": file.filename,
        "file_size": file_size,
        "encryption_metadata": encryption_metadata,
        "chain_of_custody": [coc_event],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    await db.forensic_analyses.insert_one(analysis_record)
    
    # Get client info for email
    client = await db.clients.find_one({"clientNumber": req["clientNumber"]})
    client_info = {
        "clientNumber": req["clientNumber"],
        "email": client.get("email") if client else "",
        "firstName": client.get("firstName", "") if client else "",
        "lastName": client.get("lastName", "") if client else ""
    }

    background_tasks.add_task(
        run_forensic_analysis_task,
        file_path,
        encryption_metadata,
        case_id,
        client_info,
        db
    )
    
    return {"success": True, "message": "File uploaded successfully."}
