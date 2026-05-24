# ============================================================
# PATH: app/api/lab.py
# ============================================================
import hashlib
import json
from fastapi import APIRouter, Depends, HTTPException
from app.db.repository import BatchRepository
from app.schemas.rbac_schemas import LabPayload

router = APIRouter(prefix="/lab", tags=["Phòng Kiểm Định"])

def get_repo():
    return BatchRepository()

@router.post("/{batch_id}/certify")
async def lab_certification(
    batch_id: str,
    lab_id: str,
    payload: LabPayload,
    repo: BatchRepository = Depends(get_repo)
):
    """
    [EXPORTABLE] Cấp chứng thư số cho lô hàng.
    """
    if not payload.is_passed:
        raise HTTPException(
            status_code=400, 
            detail="Mẫu sầu riêng không đạt chuẩn. Từ chối cấp chứng thư xuất khẩu!"
        )

    # 1. Chuẩn hóa và băm dữ liệu chứng thư
    payload_dict = payload.model_dump()
    json_str = json.dumps(payload_dict, sort_keys=True)
    lab_hash = hashlib.sha256(json_str.encode('utf-8')).hexdigest()

    # 2. Cập nhật State Machine
    await repo.lab_certification(
        batch_id=batch_id,
        lab_id=lab_id,
        certificate_data=payload_dict,
        lab_hash=lab_hash
    )

    return {
        "status": "success",
        "message": f"Đã cấp chứng thư {payload.certificate_code}. Lô hàng SẴN SÀNG ĐÚC BLOCKCHAIN.",
        "lab_hash": lab_hash
    }