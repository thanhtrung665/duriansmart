# ============================================================
# PATH: app/db/database.py
# DURIAN SMART - MONGODB ASYNC CONNECTION LOGIC
# ============================================================
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME", "kimochi")

class Database:
    client: AsyncIOMotorClient = None
    db = None

db_instance = Database()

async def connect_to_mongo():
    """Hàm mở kết nối khi FastAPI khởi động"""
    if not MONGODB_URL:
        print("⚠️ CẢNH BÁO: Chưa tìm thấy MONGODB_URL trong file .env")
        return
        
    print("⏳ Đang kết nối tới MongoDB Atlas...")
    db_instance.client = AsyncIOMotorClient(MONGODB_URL)
    db_instance.db = db_instance.client[DATABASE_NAME]
    print("✅ Đã kết nối MongoDB thành công!")

async def close_mongo_connection():
    """Hàm ngắt kết nối an toàn khi tắt server"""
    if db_instance.client:
        db_instance.client.close()
        print("🔌 Đã đóng kết nối MongoDB.")

def get_database():
    """Dependency Injection để các file Router gọi Database"""
    return db_instance.db