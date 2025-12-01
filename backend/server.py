from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter
from starlette.middleware.cors import CORSMiddleware
import os
from motor.motor_asyncio import AsyncIOMotorClient

from .routers import auth, clients, documents, consent, chat, cases, payment, forensics, meetings, admin, emails, health, requests, public
from . import db

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown events."""
    mongo_url = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
    db_name = os.environ.get("DB_NAME", "safechild")
    
    db.client = AsyncIOMotorClient(mongo_url)
    db.db = db.client[db_name]
    
    print("--- MongoDB connection established ---")
    
    yield
    
    db.client.close()
    print("--- MongoDB connection closed ---")

# Create the main app with the lifespan manager
app = FastAPI(title="SafeChild Law Firm API", lifespan=lifespan)

# Create a router (prefix handled by gateway)
api_router = APIRouter()

# Include routers
api_router.include_router(auth.router)
api_router.include_router(clients.router)
api_router.include_router(documents.router)
api_router.include_router(consent.router)
api_router.include_router(chat.router)
api_router.include_router(cases.router)
api_router.include_router(payment.router)
api_router.include_router(forensics.router)
api_router.include_router(meetings.router)
api_router.include_router(admin.router)
api_router.include_router(emails.router)
api_router.include_router(requests.router)
api_router.include_router(public.router)
app.include_router(health.router) # Health check does not need /api prefix

# Include the router in the main app
app.include_router(api_router)

# DEBUG: Print all registered routes
for route in app.routes:
    if hasattr(route, "path"):
        print(f"Route: {route.path} [{route.methods}]")

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    # SECURITY: Default to localhost only. In production, set CORS_ORIGINS env var.
    allow_origins=os.environ.get('CORS_ORIGINS', 'http://localhost,https://localhost').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)