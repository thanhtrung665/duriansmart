# ============================================================
# PATH: app/api/farmer.py
# DURIAN SMART - NÔNG DÂN API (Bản cập nhật UUID Đa tiến trình)
# ============================================================
import os
import shutil
import uuid
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from app.db.repository import BatchRepository
from app.schemas.rbac_schemas import DurianBatchDocument, FarmerInfo, DailyLogItem
from app.services.ai_oracle import ai_engine

router = APIRouter(prefix="/farmer", tags=["Nông Dân"])

# Dependency Injection cho Repository
def get_repo():
    return BatchRepository()

@router.post("/init-batch")
async def init_durian_batch(
    batch_id: str = Form(...),
    farmer_id: str = Form(...),
    farmer_name: str = Form(...),
    farm_code_puc: str = Form(...),
    durian_variety: str = Form(...),
    repo: BatchRepository = Depends(get_repo)
):
    """[Ngày 1] Khởi tạo vùng trồng và bắt đầu vụ mùa mới"""
    new_batch = DurianBatchDocument(
        batch_id=batch_id,
        farmer_id=farmer_id,
        farmer_profile=FarmerInfo(
            farmer_name=farmer_name,
            farmer_age=45, # Tạm fix, có thể truyền từ Form nếu muốn mở rộng
            farm_code_puc=farm_code_puc,
            gps_location={"lat": 10.7626, "long": 106.6601},
            farm_area_m2=5000.0,
            durian_variety=durian_variety
        )
    )
    
    saved_id = await repo.create_new_batch(new_batch)
    return {"status": "success", "message": "Đã khởi tạo lô hàng", "batch_id": saved_id}

@router.post("/{batch_id}/upload-voice-log")
async def submit_voice_log(
    batch_id: str,
    day_number: int = Form(...),
    audio_file: UploadFile = File(...),
    repo: BatchRepository = Depends(get_repo)
):
    """[Ngày 2 -> 120] Thu âm báo cáo hàng ngày (Hỗ trợ đa tiến trình)"""
    # Sinh tên file tạm thời độc nhất vô nhị (tránh xung đột đa tiến trình)
    temp_filename = f"temp_{uuid.uuid4().hex}_{audio_file.filename}"
    
    with open(temp_filename, "wb") as buffer:
        shutil.copyfileobj(audio_file.file, buffer)
        
    try:
        # GPU Whisper bóc băng (Không quan tâm là .wav hay .m4a)
        transcribed_text = ai_engine.transcribe_audio(temp_filename)
        ai_status = ai_engine.analyze_log_content(transcribed_text)
        
        # Đóng gói thành DailyLogItem và lưu vào mảng Database
        log_item = DailyLogItem(
            day_number=day_number,
            voice_log_text=transcribed_text,
            ai_analysis_status=ai_status
        )
        new_hash = await repo.append_daily_log(batch_id, log_item)
        
    finally:
        # Xóa file rác cực kỳ an toàn
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

    return {
        "status": "success", 
        "day": day_number,
        "recognized_text": transcribed_text,
        "ai_evaluation": ai_status,
        "current_farmer_hash": new_hash
    }