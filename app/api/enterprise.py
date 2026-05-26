# ============================================================
# PATH: app/api/enterprise.py
# ============================================================
import hashlib
import json
import os
from typing import Optional, List
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException

# Giả định bạn đã có các module này
from app.db.repository import BatchRepository
from app.services.cardano_client import CardanoMVPService 

router = APIRouter(prefix="/enterprise", tags=["Doanh Nghiệp"])
cardano_service = CardanoMVPService()

def get_repo():
    return BatchRepository()

# ==========================================
# 1. SCHEMAS (Cấu trúc dữ liệu đầu vào)
# ==========================================
class PackagingReportCreate(BaseModel):
    enterprise_name: str
    facility_code: str
    batch_id: str
    employee_id: str
    employee_name: Optional[str] = None
    processing_date: str
    processing_method: str

class CertRequestCreate(BaseModel):
    enterprise_name: str
    facility_code: str
    lab_code: str
    batch_id: str
    puc_code: str
    variety: str
    sample_date: str
    test_category: str

# ==========================================
# 2. ENDPOINTS QUẢN LÝ LÔ HÀNG (DASHBOARD)
# ==========================================
@router.get("/dashboard-stats")
async def get_dashboard_stats(repo: BatchRepository = Depends(get_repo)):
    """
    Lấy dữ liệu thống kê tổng quan cho Dashboard Doanh nghiệp.
    (Sử dụng các câu lệnh Count/Aggregate từ Database)
    """
    # TODO: Thay thế bằng query thực tế từ MongoDB/PostgreSQL
    return {
        "total_volume_tons": 423.5,
        "total_batches_exported": 200,
        "total_revenue_usd": 51250,
        "pending_inspection_batches": 50
    }

@router.get("/batches")
async def get_enterprise_batches(repo: BatchRepository = Depends(get_repo)):
    """
    Lấy danh sách lô hàng để hiển thị lên bảng dữ liệu (Kèm trạng thái thực).
    """
    # TODO: Fetch từ DB. Đây là dữ liệu trả về mẫu để Frontend khớp logic.
    return {
        "status": "success",
        "data": [
            {"id": "BATCH-001", "puc": "PUC-01", "farmer": "ND-001", "qty": "10 Tấn", "status": "Đang kiểm định", "qr_ready": False},
            {"id": "BATCH-002", "puc": "PUC-02", "farmer": "ND-002", "qty": "15 Tấn", "status": "Sẵn sàng xuất", "qr_ready": True}
        ]
    }

# ==========================================
# 3. ENDPOINTS XỬ LÝ NGHIỆP VỤ (WORKFLOW)
# ==========================================
@router.post("/{batch_id}/packaging-report")
async def submit_packaging_report(
    batch_id: str,
    payload: PackagingReportCreate,
    repo: BatchRepository = Depends(get_repo)
):
    """
    [HARVESTED -> PROCESSING] Doanh nghiệp gửi báo cáo đóng gói và sinh mã Hash.
    """
    payload_dict = payload.model_dump()
    
    # Ép chuẩn Standard JSON (Không dùng JSONL) để băm dữ liệu
    json_str = json.dumps(payload_dict, sort_keys=True)
    enterprise_hash = hashlib.sha256(json_str.encode('utf-8')).hexdigest()

    # Lưu xuống DB và chuyển trạng thái
    await repo.enterprise_takeover(
        batch_id=batch_id, 
        enterprise_id=payload.enterprise_name, 
        processing_data=payload_dict, 
        ent_hash=enterprise_hash
    )

    return {
        "status": "success",
        "message": f"Báo cáo đóng gói hoàn tất. Lô hàng {batch_id} đã chuyển sang trạng thái Đóng gói.",
        "enterprise_hash": enterprise_hash
    }

@router.post("/{batch_id}/cert-request")
async def request_certification(
    batch_id: str,
    payload: CertRequestCreate,
    repo: BatchRepository = Depends(get_repo)
):
    """
    [PROCESSING -> INSPECTING] Gửi yêu cầu kiểm định đến Lab.
    """
    # 1. Lưu thông tin yêu cầu kiểm định vào lô hàng
    request_data = payload.model_dump()
    
    # 2. Update DB: Đổi trạng thái lô hàng thành "INSPECTING" (Đang kiểm định)
    # await repo.collection.update_one(
    #     {"batch_id": batch_id},
    #     {"$set": {"current_state": "INSPECTING", "cert_request_data": request_data}}
    # )

    return {
        "status": "success",
        "message": f"Đã gửi yêu cầu kiểm định cho lô {batch_id} đến Lab {payload.lab_code}."
    }

@router.post("/{batch_id}/mint-export-qr")
async def mint_qr_blockchain(
    batch_id: str,
    repo: BatchRepository = Depends(get_repo)
):
    """
    [EXPORTABLE -> MINTED] Kích hoạt hợp đồng Single-Signature MVP và trả về mã QR.
    """
    # 1. Kiểm tra trạng thái lô hàng
    batch_record = await repo.collection.find_one({"batch_id": batch_id})
    if not batch_record:
        raise HTTPException(status_code=404, detail="Không tìm thấy lô hàng.")
        
    if batch_record.get("current_state") != "EXPORTABLE":
        raise HTTPException(status_code=400, detail="Lô hàng chưa có chứng nhận từ Lab.")

    # 2. Sử dụng 1 mã băm duy nhất cho Single-Signature MVP
    ent_hash = batch_record.get("enterprise_hash")

    # 3. Đúc Blockchain
    try:
        tx_hash = cardano_service.mint_export_qr_single_sig(
            batch_id=batch_id,
            signer_hash=ent_hash
        )
        
        # 4. Lưu TxHash
        explorer_url = f"https://preprod.cardanoscan.io/transaction/{tx_hash}"
        await repo.collection.update_one(
            {"batch_id": batch_id},
            {"$set": {"is_minted_onchain": True, "transaction_hash": tx_hash, "current_state": "MINTED"}}
        )
        
        return {
            "status": "success",
            "message": "Hệ thống đã khóa vĩnh viễn dữ liệu với 1 chữ ký số.",
            "explorer_url": explorer_url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi Blockchain: {str(e)}")