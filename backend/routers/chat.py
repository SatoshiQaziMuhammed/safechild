# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from .. import get_db
from ..models import ChatMessage, ChatMessageCreate
from ..email_service import EmailService
import logging
import os

router = APIRouter(prefix="/chat", tags=["Chat Management"])
logger = logging.getLogger(__name__)

@router.post("/message")
async def send_message(message_data: ChatMessageCreate, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Send a chat message"""
    try:
        message = ChatMessage.model_validate(message_data)
        await db.chat_messages.insert_one(message.model_dump())
        
        if message_data.sender == 'client':
            try:
                session_messages = await db.chat_messages.find(
                    {"sessionId": message_data.sessionId}
                ).sort("timestamp", 1).to_list(length=50)
                
                message_history = ""
                for msg in session_messages[-5:]:
                    sender_label = "Kunde" if msg.get("sender") == "client" else "Bot"
                    message_history += f"{sender_label}: {msg.get('message', '')}\n"
                
                # Simplified email content to avoid encoding issues
                email_html = f"""
                <html>
                <body>
                    <h1>Neue Chat-Nachricht</h1>
                    <p><strong>Session ID:</strong> {message_data.sessionId}</p>
                    <p><strong>Neue Nachricht:</strong></p>
                    <p>{message_data.message}</p>
                    <hr>
                    <p><strong>Letzte Nachrichten:</strong></p>
                    <pre>{message_history}</pre>
                    <hr>
                    <p><strong>AKTION ERFORDERLICH:</strong> Ein Kunde wartet auf Antwort.</p>
                </body>
                </html>
                """

                EmailService.send_email(
                    to=["info@safechild.mom"], 
                    subject=f"Neue Chat-Nachricht - Session {message_data.sessionId[:8]}",
                    html=email_html
                )
                logger.info(f"Chat notification email sent to admin for session {message_data.sessionId}")
            except Exception as e:
                logger.error(f"Failed to send chat notification email: {str(e)}")
        
        return {
            "success": True,
            "messageId": str(message.id),
            "timestamp": message.timestamp
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}")
async def get_chat_history(session_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Get chat history for a session"""
    messages = await db.chat_messages.find({"sessionId": session_id}).sort("timestamp", 1).to_list(length=None)
    return {"messages": messages}
