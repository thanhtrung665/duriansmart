# ============================================================
# PATH: app/api/enterprise.py
# DURIAN SMART - ENTERPRISE ROUTER WITH REAL ON-CHAIN LOGIC
# ============================================================
from fastapi import APIRouter, HTTPException, Header
from app.schemas.durian_schemas import EnterpriseProcessingSchema, BlockchainPayloadSchema
from app.services.cardano_client import CardanoService

router = APIRouter()

# Khởi tạo dịch vụ Cardano
cardano_service = CardanoService()

@router.post("/upload-processing-report")
async def upload_phc_report(report: EnterpriseProcessingSchema):
    # Logic xử lý lưu báo cáo đóng gói (Giữ nguyên)
    import hashlib
    mock_hash = hashlib.sha256(report.model_dump_json().encode()).hexdigest()
    return {
        "status": "success", 
        "message": "Báo cáo xử lý đóng gói đã được lưu.",
        "enterprise_processing_hash": mock_hash
    }

@router.post("/mint-export-qr")
async def mint_export_qr(
    payload: BlockchainPayloadSchema,
    enterprise_wallet_signature: str = Header(..., description="Chữ ký ví Cardano của doanh nghiệp")
):
    # 1. KIỂM TRA BẢO MẬT & TÍNH TOÀN VẸN
    # So sánh ví gọi API có khớp với ví Doanh nghiệp đang quản lý hệ thống hay không
    expected_pubkey_hash = cardano_service.vk.hash().to_primitive().hex()
    
    if payload.mint_authorized_by != expected_pubkey_hash:
        raise HTTPException(status_code=403, detail="LỖI BẢO MẬT: Ví của bạn không có quyền đúc QR cho lô hàng này!")
        
    if not payload.farmer_cultivation_hash or not payload.lab_inspection_hash or not payload.enterprise_processing_hash:
        raise HTTPException(status_code=400, detail="LỖI LOGIC: Thiếu bằng chứng bất biến. Không thể kích hoạt Smart Contract.")
    
    try:
        # 2. THỰC THI GIAO DỊCH ON-CHAIN THỰC TẾ
        print("⏳ Đang đóng gói Datum và gửi lên Cardano Preprod Testnet...")
        tx_hash = cardano_service.mint_export_qr_onchain(
            batch_id=payload.batch_id,
            farmer_hash=payload.farmer_cultivation_hash,
            lab_hash=payload.lab_inspection_hash,
            phc_hash=payload.enterprise_processing_hash
        )
        
        # 3. TRẢ VỀ LINK QR TRUY XUẤT
        explorer_link = f"https://preprod.cardanoscan.io/transaction/{tx_hash}"
        
        return {
            "status": "success",
            "message": f"Giao dịch THÀNH CÔNG! Lô hàng {payload.batch_id} đã được bảo chứng On-chain.",
            "transaction_hash": tx_hash,
            "qr_code_url": explorer_link
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi ghi sổ cái Cardano: {str(e)}")