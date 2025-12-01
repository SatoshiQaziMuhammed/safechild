from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional

class Database:
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None

db = Database()

def get_db() -> AsyncIOMotorDatabase:
    """Dependency to get the database session."""
    if db.db is None:
        raise RuntimeError("Database connection has not been established.")
    return db.db
