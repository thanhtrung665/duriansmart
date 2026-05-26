# ============================================================
# PATH: app/api/public.py
# DURIAN SMART - PUBLIC VERIFICATION API
# ============================================================
from fastapi import APIRouter, Depends, HTTPException
from app.db.repository import BatchRepository

router = APIRouter(prefix="/verify", tags=["Truy xuất nguồn gốc"])

def get_repo():
    return BatchRepository()

@router.get("/{batch_id}")
async def get_batch_traceability(batch_id: str, repo: BatchRepository = Depends(get_repo)):
    """
    Lấy toàn bộ lịch sử Seed-to-Sack của một lô hàng để hiển thị cho người tiêu dùng.
    """
    batch = await repo.get_by_id(batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="Không tìm thấy dữ liệu truy xuất cho mã lô này.")
    
    # Loại bỏ object _id của MongoDB trước khi trả về JSON
    batch.pop("_id", None)
    
    return {
        "status": "success",
        "data": batch
    }