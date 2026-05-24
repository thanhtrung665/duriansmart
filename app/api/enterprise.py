# ============================================================
# PATH: app/api/enterprise.py
# ============================================================
import hashlib
import json
from fastapi import APIRouter, Depends, HTTPException
from app.db.repository import BatchRepository
from app.schemas.rbac_schemas import EnterprisePayload
from app.services.cardano_client import CardanoMultiSigService

router = APIRouter(prefix="/enterprise", tags=["Doanh Nghiệp"])
cardano_service = CardanoMultiSigService()

def get_repo():
    return BatchRepository()

@router.post("/{batch_id}/takeover")
async def process_and_takeover_batch(
    batch_id: str,
    enterprise_id: str,
    payload: EnterprisePayload,
    repo: BatchRepository = Depends(get_repo)
):
    """
    [HARVESTED] Doanh nghiệp ký nhận lô hàng và đẩy báo cáo đóng gói.
    """
    # 1. Chuẩn hóa Standard JSON để băm dữ liệu
    payload_dict = payload.model_dump()
    
    # Sử dụng sort_keys=True để đảm bảo thứ tự JSON không đổi khi sinh mã Hash
    json_str = json.dumps(payload_dict, sort_keys=True)
    enterprise_hash = hashlib.sha256(json_str.encode('utf-8')).hexdigest()

    # 2. Đẩy xuống Repository để thực hiện luồng State Machine an toàn
    await repo.enterprise_takeover(
        batch_id=batch_id, 
        enterprise_id=enterprise_id, 
        processing_data=payload_dict, 
        ent_hash=enterprise_hash
    )

    return {
        "status": "success",
        "message": f"Bàn giao thành công. Lô hàng {batch_id} đã chuyển sang trạng thái HARVESTED.",
        "enterprise_hash": enterprise_hash
    }
@router.post("/{batch_id}/mint-export-qr")
async def mint_qr_blockchain(
    batch_id: str,
    repo: BatchRepository = Depends(get_repo)
):
    """
    [EXPORTABLE -> MINTED] Kích hoạt hợp đồng Đa chữ ký và trả về mã QR truy xuất.
    """
    # 1. Kiểm tra trạng thái lô hàng từ Database
    batch_record = await repo.collection.find_one({"batch_id": batch_id})
    if not batch_record:
        raise HTTPException(status_code=404, detail="Không tìm thấy lô hàng.")
        
    if batch_record.get("current_state") != "EXPORTABLE":
        raise HTTPException(status_code=400, detail="Lô hàng chưa đủ điều kiện (Chưa có chứng thư Lab).")

    # 2. Rút trích 3 Mã băm (Giữ nguyên kiến trúc chuẩn JSON)
    farmer_hash = batch_record.get("farmer_hash")
    ent_hash = batch_record.get("enterprise_hash")
    lab_hash = batch_record.get("lab_hash")

    # 3. Kích hoạt On-chain Multi-sig
    try:
        tx_hash = cardano_service.mint_export_qr_onchain(
            batch_id=batch_id,
            farmer_hash=farmer_hash,
            ent_hash=ent_hash,
            lab_hash=lab_hash
        )
        
        # 4. Lưu lại TxHash vào Database
        explorer_url = f"https://preprod.cardanoscan.io/transaction/{tx_hash}"
        await repo.collection.update_one(
            {"batch_id": batch_id},
            {"$set": {
                "is_minted_onchain": True,
                "transaction_hash": tx_hash
            }}
        )
        
        return {
            "status": "success",
            "message": "Đúc Blockchain thành công. Hệ thống đã khóa vĩnh viễn dữ liệu.",
            "explorer_url": explorer_url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi Blockchain: {str(e)}")