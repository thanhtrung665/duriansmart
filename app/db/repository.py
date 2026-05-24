# ============================================================
# PATH: app/db/repository.py
# DURIAN SMART - DATABASE REPOSITORY LAYER (STANDARD JSON)
# ============================================================
import hashlib
import json
from app.db.database import get_database
from app.schemas.rbac_schemas import DurianBatchDocument, BatchState, DailyLogItem
from fastapi import HTTPException

class BatchRepository:
    def __init__(self):
        self.db = get_database()
        if self.db is None:
            raise Exception("Database chưa được khởi tạo! Hãy kiểm tra lại kết nối Motor.")
        self.collection = self.db["batches"]

    async def create_new_batch(self, batch_document: DurianBatchDocument):
        """
        [Giai đoạn 1 - PLANTED] 
        Nông dân khởi tạo lô hàng sầu riêng mới cùng thông tin vùng trồng (PUC, GPS).
        Chặn tuyệt đối hành vi ghi đè nếu trùng batch_id.
        """
        existing = await self.collection.find_one({"batch_id": batch_document.batch_id})
        if existing:
            raise HTTPException(
                status_code=400, 
                detail=f"Mã lô hàng '{batch_document.batch_id}' đã tồn tại. Không thể khởi tạo lại!"
            )
        
        # Lưu trữ theo định dạng Standard JSON thuần túy
        await self.collection.insert_one(batch_document.model_dump())
        return batch_document.batch_id

    async def append_daily_log(self, batch_id: str, log_item: DailyLogItem):
        """
        [Ghi nhật ký 120 ngày]
        Bổ sung nhật ký canh tác mới vào mảng daily_logs mà không ảnh hưởng dữ liệu cũ.
        Sau đó tự động tái tính toán mã băm farmer_hash để bảo vệ tính bất biến.
        """
        # 1. Đẩy log mới vào mảng bằng toán tử $push
        result = await self.collection.update_one(
            {
                "batch_id": batch_id,
                "current_state": BatchState.PLANTED.value
            },
            {
                "$push": {"daily_logs": log_item.model_dump()},
                "$set": {"updated_at": log_item.date_recorded}
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=404, 
                detail="Lô hàng không tồn tại hoặc đã được bàn giao cho Doanh nghiệp, chặn sửa đổi nhật ký!"
            )

        # 2. Đọc lại toàn bộ mảng nhật ký để tính toán mã băm lũy kế (Cumulative Hash)
        record = await self.collection.find_one({"batch_id": batch_id})
        logs_list = record.get("daily_logs", [])
        
        # Chuẩn hóa chuỗi JSON ổn định (sort_keys=True) để mã băm không bị lệch khi chạy lại
        logs_json_str = json.dumps(logs_list, sort_keys=True)
        new_farmer_hash = hashlib.sha256(logs_json_str.encode('utf-8')).hexdigest()

        # 3. Cập nhật mã băm mới nhất vào tài liệu
        await self.collection.update_one(
            {"batch_id": batch_id},
            {"$set": {"farmer_hash": new_farmer_hash}}
        )
        
        return new_farmer_hash

    async def enterprise_takeover(self, batch_id: str, enterprise_id: str, processing_data: dict, ent_hash: str):
        """
        [Giai đoạn 2 - HARVESTED]
        Doanh nghiệp ký nhận bàn giao lô hàng và nạp dữ liệu xử lý đóng gói thương mại.
        Chuyển trạng thái máy từ PLANTED sang HARVESTED.
        """
        result = await self.collection.update_one(
            {
                "batch_id": batch_id, 
                "current_state": BatchState.PLANTED.value
            },
            {"$set": {
                "enterprise_id": enterprise_id,
                "current_state": BatchState.HARVESTED.value,
                "enterprise_processing": processing_data,
                "enterprise_hash": ent_hash,
                "updated_at": processing_data.get("packaging_date")
            }}
        )
        if result.modified_count == 0:
            raise HTTPException(
                status_code=400, 
                detail="Bàn giao thất bại. Lô hàng chưa sẵn sàng hoặc đã nằm trong chuỗi xử lý khác."
            )
        return True

    async def lab_certification(self, batch_id: str, lab_id: str, certificate_data: dict, lab_hash: str):
        """
        [Giai đoạn 3 & 4 - TESTING & EXPORTABLE]
        Phòng kiểm định nạp chứng thư số độc lập (Cadimi, Vàng O).
        Kích hoạt trạng thái EXPORTABLE - Đủ điều kiện đa chữ ký để On-chain.
        """
        result = await self.collection.update_one(
            {
                "batch_id": batch_id,
                "current_state": BatchState.HARVESTED.value # Lô hàng đã đóng gói mới được kiểm nghiệm
            },
            {"$set": {
                "lab_id": lab_id,
                "current_state": BatchState.EXPORTABLE.value,
                "lab_certificate": certificate_data,
                "lab_hash": lab_hash,
                "updated_at": certificate_data.get("timestamp")
            }}
        )
        if result.modified_count == 0:
            raise HTTPException(
                status_code=400, 
                detail="Cấp chứng chỉ thất bại. Kiểm tra lại trạng thái hiện tại của lô hàng."
            )
        return True

    async def fetch_batch_evolution(self, batch_id: str) -> dict:
        """
        [Truy xuất chuỗi hành trình]
        Phục vụ cổng tra cứu QR-Code: Trả về toàn bộ lịch sử 120 ngày canh tác, 
        thông tin doanh nghiệp và chứng nhận của Phòng Lab dưới dạng Standard JSON.
        """
        record = await self.collection.find_one({"batch_id": batch_id}, {"_id": 0})
        if not record:
            raise HTTPException(status_code=404, detail="Không tìm thấy mã QR sầu riêng này trên hệ thống!")
        return record