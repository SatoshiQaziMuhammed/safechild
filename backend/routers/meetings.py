from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

from .. import get_db
from ..models import MeetingCreate
from ..auth import get_current_client
from ..email_service import EmailService
import logging
import os

router = APIRouter(prefix="/meetings", tags=["Video Meetings"])
logger = logging.getLogger(__name__)

class MeetingStatusUpdate(BaseModel):
    status: str

@router.post("/create")
async def create_meeting(
    meeting_data: MeetingCreate,
    current_client: dict = Depends(get_current_client),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create a video meeting/consultation"""
    try:
        meeting_id = f"MTG_{current_client['clientNumber']}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        room_name = f"safechild-{current_client['clientNumber']}-{datetime.utcnow().strftime('%Y%m%d%H%M')}"
        
        frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
        meeting_url = f"{frontend_url}/video-call?room={room_name}"
        
        meeting_record = {
            "meetingId": meeting_id,
            "clientNumber": current_client["clientNumber"],
            "clientEmail": current_client["email"],
            "title": meeting_data.title,
            "description": meeting_data.description,
            "roomName": room_name,
            "meetingUrl": meeting_url,
            "scheduledTime": meeting_data.scheduledTime,
            "duration": meeting_data.duration,
            "meetingType": meeting_data.meetingType,
            "status": "scheduled",
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        
        await db.meetings.insert_one(meeting_record)
        
        try:
            scheduled_date = ""
            scheduled_time = ""
            if meeting_data.scheduledTime:
                scheduled_date = meeting_data.scheduledTime.strftime('%d.%m.%Y')
                scheduled_time = meeting_data.scheduledTime.strftime('%H:%M') + " Uhr"
            else:
                scheduled_date = datetime.utcnow().strftime('%d.%m.%Y')
                scheduled_time = "Nach Vereinbarung"
            
            EmailService.send_meeting_confirmation(
                recipient_email=current_client["email"],
                recipient_name=f"{current_client.get('firstName', '')} {current_client.get('lastName', '')}".strip() or "Kunde",
                meeting_title=meeting_data.title,
                meeting_date=scheduled_date,
                meeting_time=scheduled_time,
                meeting_url=meeting_url,
                meeting_id=meeting_id
            )
            logger.info(f"Meeting confirmation email sent to {current_client['email']}")
        except Exception as e:
            logger.error(f"Failed to send meeting confirmation email: {str(e)}")
        
        return {
            "success": True,
            "meetingId": meeting_id,
            "roomName": room_name,
            "meetingUrl": meeting_url,
            "message": "Meeting created successfully"
        }
        
    except Exception as e:
        print(f"[API] Error creating meeting: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/my-meetings")
async def get_my_meetings(
    current_client: dict = Depends(get_current_client),
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Get all meetings for current client
    """
    try:
        query = {"clientNumber": current_client["clientNumber"]}
        
        if status:
            query["status"] = status
        
        meetings = await db.meetings.find(
            query,
            {"_id": 0}
        ).sort("createdAt", -1).skip(skip).limit(limit).to_list(length=None)
        
        return {
            "total": len(meetings),
            "meetings": meetings
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{meeting_id}")
async def get_meeting_details(
    meeting_id: str,
    current_client: dict = Depends(get_current_client),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Get meeting details
    """
    try:
        meeting = await db.meetings.find_one({
            "meetingId": meeting_id,
            "clientNumber": current_client["clientNumber"]
        }, {"_id": 0})
        
        if not meeting:
            raise HTTPException(status_code=404, detail="Meeting not found")
        
        return meeting
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{meeting_id}/status")
async def update_meeting_status(
    meeting_id: str,
    status_update: MeetingStatusUpdate,
    current_client: dict = Depends(get_current_client),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Update meeting status
    """
    try:
        valid_statuses = ["scheduled", "in_progress", "completed", "cancelled"]
        if status_update.status not in valid_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )
        
        meeting = await db.meetings.find_one({
            "meetingId": meeting_id,
            "clientNumber": current_client["clientNumber"]
        })
        
        if not meeting:
            raise HTTPException(status_code=404, detail="Meeting not found")
        
        update_data = {
            "status": status_update.status,
            "updatedAt": datetime.utcnow()
        }
        
        if status_update.status == "in_progress" and not meeting.get("startedAt"):
            update_data["startedAt"] = datetime.utcnow()
        elif status_update.status == "completed" and not meeting.get("endedAt"):
            update_data["endedAt"] = datetime.utcnow()
        
        await db.meetings.update_one(
            {"meetingId": meeting_id},
            {"$set": update_data}
        )
        
        return {"success": True, "message": "Meeting status updated"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{meeting_id}")
async def delete_meeting(
    meeting_id: str,
    current_client: dict = Depends(get_current_client),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Delete/cancel a meeting"""
    try:
        meeting = await db.meetings.find_one({
            "meetingId": meeting_id,
            "clientNumber": current_client["clientNumber"]
        })
        
        if not meeting:
            raise HTTPException(status_code=404, detail="Meeting not found")
        
        if meeting["status"] == "in_progress":
            raise HTTPException(
                status_code=400,
                detail="Cannot delete meeting that is in progress"
            )
        
        await db.meetings.delete_one({"meetingId": meeting_id})
        
        return {"success": True, "message": "Meeting deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))