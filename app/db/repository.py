# ============================================================
# PATH: app/db/repository.py
# DURIAN SMART - DATABASE REPOSITORY (STATE MACHINE MANAGEMENT)
# ============================================================
import os
import certifi
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import HTTPException
from dotenv import load_dotenv

# Nạp các biến từ file .env
load_dotenv()

class BatchRepository:
    def __init__(self):
        self.mongo_uri = os.getenv("MONGODB_URL")
        self.db_name = os.getenv("DATABASE_NAME", "kimochi")
        
        if not self.mongo_uri:
            raise ValueError("⚠️ Chưa cấu hình MONGODB_URL trong file .env")
            
        # Thêm tham số tlsCAFile=certifi.where() để giải quyết triệt để lỗi SSL Handshake
        self.client = AsyncIOMotorClient(
            self.mongo_uri, 
            tlsCAFile=certifi.where()
        )
        self.db = self.client[self.db_name]
        self.collection = self.db["batches"]
        
    async def get_by_id(self, batch_id: str) -> dict:
        """
        Tìm kiếm lô hàng dựa trên mã lô (batch_id).
        """
        batch = await self.collection.find_one({"batch_id": batch_id})
        if batch:
            batch["_id"] = str(batch["_id"])
        return batch

    async def enterprise_takeover(
        self, 
        batch_id: str, 
        enterprise_id: str, 
        processing_data: dict, 
        ent_hash: str
    ):
        """
        [WORKFLOW] Doanh nghiệp ký nhận bàn giao lô hàng và cập nhật báo cáo đóng gói.
        Chuyển trạng thái lô hàng sang PROCESSING.
        """
        # Kiểm tra sự tồn tại và trạng thái hiện tại của lô hàng trước khi xử lý
        batch = await self.collection.find_one({"batch_id": batch_id})
        if not batch:
            raise HTTPException(status_code=404, detail=f"Không tìm thấy lô hàng {batch_id} để bàn giao.")

        # Định hình luồng dữ liệu an toàn (State Machine Guard)
        # Cho phép tiếp nhận từ trạng thái gốc ban đầu (VD: CREATED hoặc HARVESTED)
        allowed_states = ["CREATED", "HARVESTED", "PROCESSING"]
        if batch.get("current_state") not in allowed_states:
            raise HTTPException(
                status_code=400, 
                detail=f"Lô sầu riêng đang ở trạng thái {batch.get('current_state')}, không thể thực hiện xử lý đóng gói."
            )

        # Tiến hành cập nhật khối dữ liệu chuẩn JSON và chuyển trạng thái
        result = await self.collection.update_one(
            {"batch_id": batch_id},
            {
                "$set": {
                    "enterprise_id": enterprise_id,
                    "enterprise_data": processing_data,
                    "enterprise_hash": ent_hash,
                    "current_state": "PROCESSING"  # Đang xử lý, đóng gói
                }
            }
        )
        return result.modified_count > 0

    async def seed_mock_data(self):
        """
        Hàm hỗ trợ khởi tạo dữ liệu mẫu (Mock Data Seed) để phục vụ quá trình chạy thử nghiệm 
        và đồng bộ trạng thái chính xác giữa các module Frontend (Farmer, Enterprise, Lab).
        """
        count = await self.collection.count_documents({})
        if count == 0:
            mock_batches = [
                {
                    "batch_id": "BATCH-001",
                    "puc_code": "PUC-01",
                    "farmer_id": "ND-001",
                    "yield": "10 Tấn",
                    "farmer_hash": "a1b2c3d4e5f6g7h8",
                    "current_state": "INSPECTING", # Đang kiểm định, chờ Lab duyệt
                    "is_minted_onchain": False
                },
                {
                    "batch_id": "BATCH-002",
                    "puc_code": "PUC-02",
                    "farmer_id": "ND-002",
                    "yield": "15 Tấn",
                    "farmer_hash": "b2c3d4e5f6g7h8i9",
                    "enterprise_hash": "e8f7g6h5i4j3k2l1",
                    "current_state": "EXPORTABLE", # Đã có chứng thư Lab, sẵn sàng xuất QR
                    "is_minted_onchain": False
                },
                {
                    "batch_id": "BATCH-003",
                    "puc_code": "PUC-03",
                    "farmer_id": "ND-003",
                    "yield": "10 Tấn",
                    "farmer_hash": "c3d4e5f6g7h8i9j0",
                    "current_state": "HARVESTED", # Nông dân vừa thu hoạch bàn giao
                    "is_minted_onchain": False
                }
            ]
            await self.collection.insert_many(mock_batches)
            print("🚀 [SEED] Đã khởi tạo thành công dữ liệu mẫu cho hệ thống.")