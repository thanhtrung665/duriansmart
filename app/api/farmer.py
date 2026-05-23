# ============================================================
# PATH: app/api/farmer.py
# ============================================================
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.schemas.durian_schemas import FarmerInputSchema
from app.services.kaggle_client import KaggleAIClient
import json

router = APIRouter()
kaggle_client = KaggleAIClient()

@router.post("/submit-log")
async def submit_cultivation_log(
    payload: str = Form(..., description="Chuỗi JSON của FarmerInputSchema"),
    audio_file: UploadFile = File(..., description="File ghi âm nhật ký (.m4a/.wav)")
):
    try:
        # Giải mã và xác thực cấu trúc dữ liệu thô nhận tử Zalo App
        try:
            data_dict = json.payloads(payload)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Trường payload không phải là chuỗi JSON hợp lệ")
        
        validated_data = FarmerInputSchema(**data_dict)
        
        # Bước 2: Tạm lập giả định (Mock) luồng đẩy sang Kaggle (Sẽ code ở Phần 4 & 5)
        print(f"Đã nhận file audio: {audio_file.filename} từ vùng trồng: {validated_data.puc_code}")
        # Đọc dữ liệu nhị phân của file âm thanh bất đồng bộ 
        audio_bytes = await audio_file.read()
        if not audio_bytes:
            raise HTTPException(status_code=400, detail="File âm thanh rỗng hoặc bị lỗi")
        
        # Đẩy file lên Kaggle xử lý
        ai_response = await kaggle_client.forward_audio_to_oracle(
            file_bytes=audio_bytes,
            file_name=audio_file.filename
        )
        # Kiểm tra lỗi AI Oracle Kaggle 
        if "error" in ai_response:
            raise HTTPException(
                status_code=500,
                detail=f"Lỗi xử lý tại AI Oracle (Kaggle): {ai_response['error']}. Chi tiết: {ai_response.get('detail', '')}"
            )
        # Trích xuất kết quả phân tích bồi đắp vào Schema để làm giàu dữ liệu
        validated_data.raw_text_extracted = ai_response.get("raw_text_extracted")
        validated_data.ai_oracle_compliant = ai_response.get("ai_oracle_compliant")
        
        # Phản hồi cấu trúc dữ liệu Standard JSON hoàn chỉnh về 
        return {
            "status": "success",
            "message": "AI Oracle đã đối soát xong nhật ký thực địa vùng trồng",
            "blockchain_ready_data": validated_data.model_dump()
        }
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý hệ thống chặng Backend: {str(e)}")