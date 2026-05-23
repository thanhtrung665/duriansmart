# ============================================================
# PATH: scripts/init_mongo_indexes.py
# DURIAN SMART - DATABASE INDEX OPTIMIZATION
# ============================================================
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def create_indexes():
    print("⏳ Đang thiết lập cấu trúc Index cho MongoDB...")
    client = AsyncIOMotorClient(os.getenv("MONGODB_URL"))
    db = client[os.getenv("DATABASE_NAME", "durian_smart_db")]
    
    # 1. Index Unique cho batch_id (Bảo vệ cốt lõi, không cho phép trùng lô)
    await db.batches.create_index("batch_id", unique=True)
    
    # 2. Index cho các trường Phân quyền (RBAC) để load Dashboard cực nhanh
    await db.batches.create_index("farmer_id")
    await db.batches.create_index("enterprise_id")
    await db.batches.create_index("lab_id")  # Thêm Index cho Phòng Lab
    
    # 3. Index cho Máy trạng thái (State Machine)
    await db.batches.create_index("current_state")
    
    # 4. Index Truy xuất nguồn gốc sâu (Deep Field Index)
    # Rất quan trọng khi truy vấn: "Tìm tất cả sầu riêng thuộc mã vùng trồng VN-TG-01"
    await db.batches.create_index("farmer_profile.farm_code_puc")
    
    print("✅ Đã cập nhật & tạo Index thành công! Tốc độ truy vấn Database đã được tối ưu cho 120 ngày.")
    client.close()

if __name__ == "__main__":
    asyncio.run(create_indexes())