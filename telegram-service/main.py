import os
import asyncio
import qrcode
import io
import base64
import logging
from typing import Dict
from fastapi import FastAPI, BackgroundTasks, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from telethon import TelegramClient
from telethon.sessions import StringSession
import requests
from datetime import datetime

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TelegramService")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shared Directory
SHARED_DIR = "/tmp/forensics_uploads"
os.makedirs(SHARED_DIR, exist_ok=True)

# Main Backend URL (Docker network)
BACKEND_URL = "http://backend:8001/api/forensics/analyze-internal"

# Telegram API Credentials (Replace with your own in production)
# These are public test credentials, ideally move to .env
API_ID = int(os.getenv("TELEGRAM_API_ID", "6")) 
API_HASH = os.getenv("TELEGRAM_API_HASH", "eb06d4abfb49dc3eeb1aeb98ae0f581e")

# Active Sessions Store
class SessionData:
    def __init__(self, client, client_number):
        self.client = client
        self.client_number = client_number
        self.qr_url = None
        self.status = "initializing" # initializing, qr_ready, connected, extracting, completed, failed

sessions: Dict[str, SessionData] = {}

@app.post("/session/start")
async def start_session(data: dict = Body(...), background_tasks: BackgroundTasks = None):
    client_number = data.get("client_number")
    session_id = f"tg_{client_number}_{int(datetime.utcnow().timestamp())}"
    
    logger.info(f"Starting Telegram session: {session_id}")
    
    # Initialize Telethon Client with a temporary session
    client = TelegramClient(StringSession(), API_ID, API_HASH)
    await client.connect()
    
    sessions[session_id] = SessionData(client, client_number)
    
    # Start QR Login process in background
    background_tasks.add_task(handle_qr_login, session_id)
    
    return {"success": True, "sessionId": session_id}

@app.get("/session/{session_id}/status")
async def get_status(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    return {
        "status": session.status,
        "qr": session.qr_url
    }

async def handle_qr_login(session_id: str):
    session = sessions[session_id]
    client = session.client
    
    try:
        if not await client.is_user_authorized():
            qr_login = await client.qr_login()
            
            # Convert QR URL to Base64 Image
            img = qrcode.make(qr_login.url)
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            session.qr_url = f"data:image/png;base64,{img_str}"
            session.status = "qr_ready"
            logger.info(f"QR Code ready for {session_id}")
            
            # Wait for login
            try:
                await qr_login.wait(timeout=120) # 2 minutes to scan
                session.status = "connected"
                session.qr_url = None
                logger.info(f"User logged in: {session_id}")
                
                # Start Extraction
                await extract_data(session_id)
                
            except asyncio.TimeoutError:
                session.status = "failed"
                logger.error("QR Scan timeout")
                await client.disconnect()
        else:
            session.status = "connected"
            await extract_data(session_id)
            
    except Exception as e:
        logger.error(f"Login error: {e}")
        session.status = "failed"
        await client.disconnect()

async def extract_data(session_id: str):
    session = sessions[session_id]
    client = session.client
    session.status = "extracting"
    
    try:
        logger.info(f"Extracting data for {session_id}...")
        
        full_transcript = "--- TELEGRAM FORENSIC EXPORT ---
"
        full_transcript += f"Date: {datetime.utcnow()}
"
        full_transcript += f"Case: {session.client_number}

"
        
        # Iterate over dialogs (chats)
        dialog_count = 0
        async for dialog in client.iter_dialogs(limit=50):
            dialog_count += 1
            chat_name = dialog.name
            full_transcript += f"\n{'='*30}\nCHAT: {chat_name} (ID: {dialog.id})\n{'='*30}\n"
            
            # Fetch last 100 messages
            async for message in client.iter_messages(dialog, limit=100):
                sender = "ME" if message.out else (await message.get_sender()).first_name or "Other"
                date_str = message.date.strftime("%Y-%m-%d %H:%M:%S")
                text = message.text or "[Media/Sticker]"
                
                full_transcript += f"[{date_str}] {sender}: {text}\n"
        
        # Save to file
        filename = f"TELEGRAM_AUTO_{session.client_number}_{int(datetime.utcnow().timestamp())}.txt"
        file_path = os.path.join(SHARED_DIR, filename)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(full_transcript)
            
        logger.info(f"Data saved to {file_path}")
        
        # Notify Backend
        try:
            requests.post(BACKEND_URL, json={
                "file_path": file_path,
                "client_number": session.client_number,
                "source": "telegram_automation"
            })
            session.status = "completed"
        except Exception as e:
            logger.error(f"Failed to notify backend: {e}")
            session.status = "completed_error"
            
    except Exception as e:
        logger.error(f"Extraction error: {e}")
        session.status = "failed"
    finally:
        await client.disconnect()
        # cleanup session after delay
        # del sessions[session_id] 
