# ============================================================
# PATH: app/api/farmer.py
# DURIAN SMART - API NÔNG DÂN (FARMER)
# ============================================================
import hashlib
import json
from typing import List
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from app.db.repository import BatchRepository

router = APIRouter(prefix="/farmer", tags=["Nông Dân"])

def get_repo():
    return BatchRepository()

# ==========================================
# SCHEMAS (Cấu trúc dữ liệu đầu vào)
# ==========================================
class FarmingLog(BaseModel):
    date: str
    activity: str

class BatchCreate(BaseModel):
    batch_id: str
    puc_code: str
    farmer_id: str
    farmer_name: str
    farm_location: str
    variety: str
    yield_amount: str
    daily_logs: List[FarmingLog]

# ==========================================
# ENDPOINTS
# ==========================================
@router.post("/create-batch")
async def create_harvest_batch(
    payload: BatchCreate, 
    repo: BatchRepository = Depends(get_repo)
):
    """
    [START -> HARVESTED] Nông dân khởi tạo lô hàng, khai báo nhật ký canh tác và tạo băm gốc.
    """
    # 1. Kiểm tra xem lô hàng đã tồn tại chưa
    existing_batch = await repo.collection.find_one({"batch_id": payload.batch_id})
    if existing_batch:
        raise HTTPException(status_code=400, detail=f"Mã lô {payload.batch_id} đã tồn tại trong hệ thống!")

    # 2. Băm dữ liệu Nông dân (Standard JSON)
    payload_dict = payload.model_dump()
    json_str = json.dumps(payload_dict, sort_keys=True)
    farmer_hash = hashlib.sha256(json_str.encode('utf-8')).hexdigest()

    # 3. Tạo Document mới để lưu vào MongoDB
    batch_doc = {
        "batch_id": payload.batch_id,
        "puc_code": payload.puc_code,
        "farmer_id": payload.farmer_id,
        "variety": payload.variety,
        "yield": payload.yield_amount,
        "farmer_data": payload_dict,
        "farmer_hash": farmer_hash,
        "current_state": "HARVESTED", # Trạng thái đầu tiên: Đã thu hoạch, chờ DN nhận
        "is_minted_onchain": False
    }

    # 4. Ghi xuống Database
    try:
        await repo.collection.insert_one(batch_doc)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi Database: {str(e)}")

    return {
        "status": "success",
        "message": f"Khai báo lô hàng {payload.batch_id} thành công!",
        "farmer_hash": farmer_hash
    }