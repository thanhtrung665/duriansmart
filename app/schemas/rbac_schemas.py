# ============================================================
# PATH: app/schemas/rbac_schemas.py
# DURIAN SMART - RBAC & STATE MACHINE MODELS (STANDARD JSON)
# ============================================================
from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone

# -----------------------------------------
# 1. Định nghĩa Phân quyền & Trạng thái
# -----------------------------------------
class UserRole(str, Enum):
    FARMER = "FARMER"
    ENTERPRISE = "ENTERPRISE"
    LAB = "LAB"

class BatchState(str, Enum):
    PLANTED = "PLANTED"         
    HARVESTED = "HARVESTED"     
    TESTING = "TESTING"         
    EXPORTABLE = "EXPORTABLE"   

# -----------------------------------------
# 2. Cấu trúc Nhật ký Hàng ngày
# -----------------------------------------
class DailyLogItem(BaseModel):
    day_number: int              # Ngày thứ bao nhiêu trong chu kỳ 120 ngày
    date_recorded: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    voice_log_text: str          # Văn bản AI bóc băng
    ai_analysis_status: str      # AI đánh giá (vd: Đạt chuẩn GACC, Cảnh báo hóa chất)

# -----------------------------------------
# 3. Schema Dữ liệu Đầu vào (Payload)
# -----------------------------------------
class FarmerInfo(BaseModel):
    farmer_name: str
    farmer_age: int
    farm_code_puc: str           # Mã vùng trồng được cấp
    gps_location: Dict[str, float] # {"lat": 10.7626, "long": 106.6601}
    farm_area_m2: float          # Diện tích (m2)
    durian_variety: str          # Giống sầu riêng (Ri6, Monthong...)

class EnterprisePayload(BaseModel):
    total_boxes: int
    total_weight_kg: float
    packaging_date: str

class LabPayload(BaseModel):
    certificate_code: str
    cadimi_level: float
    vang_o_status: str
    is_passed: bool

# -----------------------------------------
# 4. TRÁI TIM HỆ THỐNG: MÔ HÌNH LƯU TRỮ CHUẨN MONGODB
# -----------------------------------------
class DurianBatchDocument(BaseModel):
    batch_id: str
    current_state: BatchState = BatchState.PLANTED
    
    # Định danh cơ bản
    farmer_id: str
    enterprise_id: Optional[str] = None
    lab_id: Optional[str] = None
    
    # Khối Dữ liệu Nông dân (Đã nâng cấp)
    farmer_profile: Optional[FarmerInfo] = None
    daily_logs: List[DailyLogItem] = Field(default_factory=list) # Mảng chứa đủ 120 ngày
    
    # Khối Dữ liệu Doanh nghiệp & Lab
    enterprise_processing: Optional[Dict[str, Any]] = Field(default_factory=dict)
    lab_certificate: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    # 3 Mã băm (Hash) On-chain
    farmer_hash: str = ""
    enterprise_hash: str = ""
    lab_hash: str = ""
    
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())