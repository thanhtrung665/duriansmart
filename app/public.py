# ============================================================
# PATH: app/api/public.py
# DURIAN SMART - PUBLIC TRACEABILITY API
# ============================================================
from fastapi import APIRouter, Depends, HTTPException
from app.db.repository import BatchRepository

router = APIRouter(prefix="/public", tags=["Tra cứu Công khai"])

def get_repo():
    return BatchRepository()

@router.get("/trace/{batch_id}")
async def get_traceability_info(
    batch_id: str,
    repo: BatchRepository = Depends(get_repo)
):
    """
    Cổng tra cứu minh bạch cho Người tiêu dùng.
    Truy xuất toàn bộ lịch sử 120 ngày sinh trưởng, chứng nhận Lab và mã băm Cardano.
    """
    try:
        # Hàm fetch_batch_evolution trả về dict chuẩn Standard JSON
        data = await repo.fetch_batch_evolution(batch_id)
        return {"status": "success", "data": data}
    except Exception as e:
        raise HTTPException(status_code=404, detail="Không tìm thấy thông tin mã QR này!")
