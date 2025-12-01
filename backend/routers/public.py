from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
from pathlib import Path
from .. import get_db

router = APIRouter(prefix="/public", tags=["Public Access"])

@router.get("/reports/{token}")
async def get_shared_report(
    token: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    # Find token
    share_link = await db.shared_reports.find_one({"token": token})
    if not share_link:
        raise HTTPException(status_code=404, detail="Invalid link")
        
    if share_link.get("isRevoked", False):
        raise HTTPException(status_code=410, detail="Link has been revoked")
        
    if share_link["expiresAt"] < datetime.utcnow():
        raise HTTPException(status_code=410, detail="Link has expired")
        
    # Get case
    case = await db.forensic_analyses.find_one({"case_id": share_link["caseId"]})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    # Get report path
    report_path = case.get("report_pdf") or case.get("report_txt")
    if not report_path or not Path(report_path).exists():
        raise HTTPException(status_code=404, detail="Report file not found on server")
        
    filename = Path(report_path).name
    media_type = "application/pdf" if filename.endswith(".pdf") else "text/plain"
    
    return FileResponse(report_path, media_type=media_type, filename=filename)
