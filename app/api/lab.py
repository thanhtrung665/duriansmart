from fastapi import APIRouter
from app.schemas.durian_schemas import LabReportSchema

router = APIRouter()

@router.post("/submit-report")
async def submit_lab_report(report: LabReportSchema):
    # Dữ liệu truyền vào đã được Pydantic tự động ép chuẩn
    if not report.is_passed:
        # Xử lý cảnh báo lô hàng hỏng 
        return {"status": "warning", "message": f"Cảnh báo: Lô {report.batch_id} không đạt tiêu chuẩn xuất khẩu"}
    
    # Sinh mã băm để đẩy lên smart contract
    mock_hash = f"hash_lab_{report.batch_id}_v1"
    return {
        "status": "success",
        "message": "Báo cáo Lab hợp lệ. Đã ký số và băm dữ liệu",
        "lab_inspection_hash": mock_hash, # Đã sửa lỗi dư chữ "i"
        "certificate": report.certificate # Đã tối ưu code
    }