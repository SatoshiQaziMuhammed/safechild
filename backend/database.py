import os
from motor.motor_asyncio import AsyncIOMotorClient

# Production'da bu adres environment variable'dan gelir.
# Yoksa varsayılan olarak localhost'a bağlanır.
MONGO_URL = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "safechild_db"

client = None
db = None

def get_db():
    return db

print(f"🔌 Veritabanı yapılandırması yüklendi: {DB_NAME} (Bağlantı başlatılmadı)")