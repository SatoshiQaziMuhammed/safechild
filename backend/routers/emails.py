from fastapi import APIRouter, HTTPException
from typing import Optional
from ..email_service import EmailService
import logging

router = APIRouter(prefix="/emails", tags=["Email Notifications"])
logger = logging.getLogger(__name__)

@router.post("/meeting-confirmation")
def send_meeting_confirmation_email(
    recipient_email: str,
    recipient_name: str,
    meeting_title: str,
    meeting_date: str,
    meeting_time: str,
    meeting_url: Optional[str] = None,
    meeting_id: Optional[str] = None
):
    """Send meeting confirmation email (internal endpoint)."""
    try:
        result = EmailService.send_meeting_confirmation(
            recipient_email=recipient_email,
            recipient_name=recipient_name,
            meeting_title=meeting_title,
            meeting_date=meeting_date,
            meeting_time=meeting_time,
            meeting_url=meeting_url,
            meeting_id=meeting_id
        )
        
        if result["success"]:
            return {"success": True, "message": "Email sent successfully", "email_id": result.get("email_id")}
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to send email"))
    
    except Exception as e:
        logger.error(f"Error sending meeting confirmation email: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/forensic-complete")
def send_forensic_complete_email(
    recipient_email: str,
    recipient_name: str,
    case_id: str,
    file_name: str,
    statistics: Optional[dict] = None
):
    """Send forensic analysis complete email (internal endpoint)."""
    try:
        result = EmailService.send_forensic_analysis_complete(
            recipient_email=recipient_email,
            recipient_name=recipient_name,
            case_id=case_id,
            file_name=file_name,
            statistics=statistics
        )
        
        if result["success"]:
            return {"success": True, "message": "Email sent successfully", "email_id": result.get("email_id")}
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to send email"))
    
    except Exception as e:
        logger.error(f"Error sending forensic complete email: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/document-uploaded")
def send_document_uploaded_email(
    recipient_email: str,
    recipient_name: str,
    document_name: str,
    document_number: str,
    uploaded_at: str
):
    """Send document uploaded email (internal endpoint)."""
    try:
        result = EmailService.send_document_uploaded(
            recipient_email=recipient_email,
            recipient_name=recipient_name,
            document_name=document_name,
            document_number=document_number,
            uploaded_at=uploaded_at
        )
        
        if result["success"]:
            return {"success": True, "message": "Email sent successfully", "email_id": result.get("email_id")}
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to send email"))
    
    except Exception as e:
        logger.error(f"Error sending document uploaded email: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/welcome")
def send_welcome_email(
    recipient_email: str,
    recipient_name: str,
    client_number: str
):
    """Send welcome email to new clients (internal endpoint)."""
    try:
        result = EmailService.send_welcome_email(
            recipient_email=recipient_email,
            recipient_name=recipient_name,
            client_number=client_number
        )
        
        if result["success"]:
            return {"success": True, "message": "Email sent successfully", "email_id": result.get("email_id")}
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to send email"))
    
    except Exception as e:
        logger.error(f"Error sending welcome email: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
