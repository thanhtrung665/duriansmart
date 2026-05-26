# ============================================================
# PATH: app/api/lab.py
# DURIAN SMART - API CƠ QUAN KIỂM ĐỊNH (LABORATORY)
# ============================================================
import hashlib
import json
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException

# Giả định import Repository từ kiến trúc Database của bạn
from app.db.repository import BatchRepository

router = APIRouter(prefix="/lab", tags=["Cơ Quan Kiểm Định"])

def get_repo():
    return BatchRepository()

# ==========================================
# 1. SCHEMAS (Cấu trúc dữ liệu đầu vào)
# ==========================================
class LabCertificateCreate(BaseModel):
    batch_id: str
    test_date: str
    technician_id: str
    cadimi_level: str
    vang_o_result: str
    bvtv_result: str
    final_result: str  # "Đạt" hoặc "Không đạt"

# ==========================================
# 2. ENDPOINTS XỬ LÝ NGHIỆP VỤ
# ==========================================
@router.post("/{batch_id}/certificate")
async def issue_certificate(
    batch_id: str,
    payload: LabCertificateCreate,
    repo: BatchRepository = Depends(get_repo)
):
    """
    [INSPECTING -> EXPORTABLE / REJECTED] Cơ quan kiểm định trả kết quả và lưu mã băm.
    """
    # 1. Lấy dữ liệu lô hàng hiện tại để kiểm tra tính hợp lệ của luồng (Workflow)
    batch_record = await repo.collection.find_one({"batch_id": batch_id})
    
    if not batch_record:
        raise HTTPException(status_code=404, detail="Không tìm thấy lô hàng.")
        
    # Đảm bảo lô hàng đang ở đúng trạng thái chờ kiểm định
    if batch_record.get("current_state") != "INSPECTING":
        raise HTTPException(
            status_code=400, 
            detail=f"Lô hàng đang ở trạng thái {batch_record.get('current_state')}, chưa sẵn sàng để kiểm định."
        )

    # 2. Chuyển đổi dữ liệu và băm bằng chuẩn Standard JSON
    payload_dict = payload.model_dump()
    json_str = json.dumps(payload_dict, sort_keys=True)
    lab_hash = hashlib.sha256(json_str.encode('utf-8')).hexdigest()

    # 3. Xác định trạng thái tiếp theo của máy trạng thái (State Machine)
    next_state = "EXPORTABLE" if payload.final_result == "Đạt" else "REJECTED"

    # 4. Cập nhật Database
    try:
        await repo.collection.update_one(
            {"batch_id": batch_id},
            {
                "$set": {
                    "current_state": next_state,
                    "lab_data": payload_dict,
                    "lab_hash": lab_hash
                }
            }
        )
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Lỗi khi cập nhật Database: {str(e)}")

    return {
        "status": "success",
        "message": f"Đã cấp chứng nhận thành công. Lô {batch_id} đã chuyển sang trạng thái {next_state}.",
        "lab_hash": lab_hash
    }

@router.get("/pending-batches")
async def get_pending_batches(repo: BatchRepository = Depends(get_repo)):
    """
    Lấy danh sách các lô hàng đang chờ kiểm định (Trạng thái: INSPECTING).
    Phục vụ cho việc hiển thị lên bảng dữ liệu của trang Quản lý Lab.
    """
    cursor = repo.collection.find({"current_state": "INSPECTING"})
    batches = await cursor.to_list(length=100)
    
    # Format lại ID object của MongoDB để tránh lỗi JSON serializable
    for batch in batches:
        batch["_id"] = str(batch["_id"])
        
    return {
        "status": "success",
        "data": batches
    }