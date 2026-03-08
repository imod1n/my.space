from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
import logging

load_dotenv()

logger = logging.getLogger(__name__)

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "kommunalka")

client: AsyncIOMotorClient = None
db = None


async def connect_db():
    global client, db
    try:
        client = AsyncIOMotorClient(MONGO_URL)
        db = client[DB_NAME]
        await client.admin.command("ping")
        print(f"✅ MongoDB connected: {DB_NAME}")   # ← временно
        await db.payments.create_index("date")
        await db.payments.create_index("category")
        await db.payments.create_index("period")    # ← добавьте индекс для period
    except Exception as e:
        print(f"❌ MongoDB error: {e}")              # ← временно
        raise


async def close_db():
    global client
    if client:
        client.close()
        logger.info("MongoDB соединение закрыто")


def get_collection(name: str = "payments"):
    return db[name]
