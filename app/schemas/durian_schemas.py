# ============================================================
# PATH: app/schemas/durian_schemas.py
# DURIAN SMART - STANDARD JSON SCHEMAS (PYDANTIC V2)
# ============================================================

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, Any, Optional
from pycardano import PlutusData
from dataclasses import dataclass


# --- SUB-MODELS HỖ TRỢ ---
class GPSLocation(BaseModel):
    latitude: float = Field(..., description="Vĩ độ của vùng trồng PUC", examples=[10.4083])
    longitude: float = Field(..., description="Kinh độ của vùng trồng PUC", examples=[106.7783])
    
# --- 1. TẦNG NÔNG DÂN (ZALO MINI APP) ---
class FarmerInputSchema(BaseModel):
    puc_code: str = Field(..., description="Mã vùng trồng sầu riêng được GACC cấp phép", examples=["PUC-TG-001"])
    durian_variety: str = Field(..., description="Chủng loại sầu riêng (Ri6 hoặc Monthong)", examples=["Ri6", "Monthong"])
    gps: GPSLocation = Field(..., description="Tọa độ GPS thực địa tại thời điểm báo cáo")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Thời gian ghi nhận báo cáo")
    audio_file_name: str = Field(..., description="Tên file âm thanh giọng nói nhận từ Zalo Mini App từ nông dân", examples=["report_20260518.wav"])
    
    # Văn bản trả về sau xử lý
    raw_text_extracted: Optional[str] = Field(None, description="Văn bản trích xuất từ giọng nói nông dân")
    # Kết quả đối soát RAG của AI Oracle 
    ai_oracle_compliant: Optional[bool] = Field(None, description="Trạng thái hợp lệ theo nghị định của GACC")

# --- 2. TẦNG DOANH NGHIỆP XỬ LÝ (ENTERPRISE APP) ---
# Di chuyển schema này lên trước Lab để đúng với Flow thực tế: Nông dân -> Doanh nghiệp -> Lab
class EnterpriseProcessingSchema(BaseModel):
    phc_code: str = Field(..., description="Mã cơ sở đóng gói xuất khẩu", examples=["PHC-001"])
    batch_id: str = Field(..., description="Mã định danh lô hàng", examples=["BATCH-2026-005"])
    weight_tons: float = Field(..., description="Sản lượng thực tế lô hàng (Tấn)", examples=[10.5])
    air_pressure_clean_psi: float = Field(..., description="Áp suất khí nén xử lý rệp sáp (đơn vị PSI)", examples=[120.0])
    total_boxes: int = Field(..., description="Tổng số lượng thùng carton đóng gói xuất khẩu", examples=[925])
    temporary_label_affixed: bool = Field(..., description="Xác nhận đã dán nhãn tạm định danh cho từng thùng", examples=[True])
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Thời gian hoàn tất quy trình đóng gói và ghi nhận báo cáo")

# --- 3. TẦNG PHÒNG KIỂM ĐỊNH (LAB PORTAL) ---
class LabReportSchema(BaseModel):
    batch_id: str = Field(..., description="Mã số định danh lô hàng sầu riêng thu mua", examples=["BATCH-2026-005"])
    lab_test_id: str = Field(..., description="Mã số cơ quan kiểm định", examples=["LAB-001"])
    technician_id: str = Field(..., description="Mã số kỹ thuật viên thực hiện kiểm định", examples=["TECH-123"])
    cadmium_level_ppm: float = Field(..., description="Nồng độ kim loại nặng Cadimi phát hiện (đơn vị ppm)", examples=[0.02])
    golden_o_status: bool = Field(..., description="Trạng thái nhiễm chất cấm Vàng O (True nếu phát hiện, False nếu không)", examples=[False])
    pesticide_residue_compliant: bool = Field(..., description="Trạng thái dư lượng thuốc trừ sâu", examples=[True])
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Thời gian ký báo cáo kiểm định")
    is_passed: bool = Field(..., description="Kết quả phân loại tổng thể kiểm định (Pass/Fail)", examples=[True])
    certificate: Optional[str] = Field(None, description="Mã số chứng thư kiểm định được cấp bởi cơ quan kiểm định nếu kết quả Pass")

# --- 4. TẦNG BLOCKCHAIN PAYLOAD (BẰNG CHỨNG HASH ON-CHAIN) ---
class BlockchainPayloadSchema(BaseModel):
    batch_id: str = Field(..., description="Mã lô hàng bảo chứng chặng cuối")
    farmer_cultivation_hash: str = Field(..., description="Mã băm SHA-256 nhật ký canh tác của nông dân")
    enterprise_processing_hash: str = Field(..., description="Mã băm SHA-256 quy trình đóng gói, xử lý")
    lab_inspection_hash: str = Field(..., description="Mã băm SHA-256 kết quả xét nghiệm phòng Lab")
    lab_certificate: str = Field(..., description="Mã số chứng thư kiểm định được cấp bởi cơ quan kiểm định")
    mint_authorized_by: str = Field(..., description="Mã ví Cardano (Public Key Hash) của doanh nghiệp xin cấp quyền xuất QR")
"""class BlockchainPayloadSchema(BaseModel):
    batch_id: str = Field(..., description="Mã số định danh lô hàng sầu riêng thu mua", examples=["BATCH-2026-005"])
    puc_code: str = Field(..., description="Mã vùng trồng sầu riêng được GACC cấp phép", examples=["PUC-TG-001"])
    durian_variety: str = Field(..., description="Chủng loại sầu riêng (Ri6 hoặc Monthong)", examples=["Ri6", "Monthong"])
    gps: GPSLocation = Field(..., description="Tọa độ GPS thực địa tại thời điểm báo cáo")
    lab_test_id: str = Field(..., description="Mã số cơ quan kiểm định", examples=["LAB-001"])
    cadmium_level_ppm: float = Field(..., description="Nồng độ kim loại nặng Cadimi phát hiện (đơn vị ppm)", examples=[0.02])
    golden_0_status: bool =Field(..., description="Trạng thái nhiễm chất cấm Vàng O (True nếu phát hiện, False nếu không)", examples=[False])
    pesticide_residue_compliant: bool = Field(..., description="Trạng thái dư lượng thuốc trừ sâu", examples=[False])
    is_passed: bool = Field(..., description="Kết quả phân loại tổng thể kiểm định (Pass/Fail)", examples=[True])
    weight_tons: float = Field(..., description="Sản lượng thực tế lô hàng (Tấn)", examples=[10.5])
    air_pressure_clean_psi: float = Field(..., description="Áp suất khí nén xử lý rệp sáp (đơn vị PSI)", examples=[120.0])
    total_boxes: int = Field(..., description="Tổng số lượng thùng cartone đóng gói xuất khẩu ", examples=[925])"""

# 5 -- Kết nối ON-CHAIN 
# Ánh xạ 1:1 kiểu DurianDatum bên mã nguồn Aiken
@dataclass
class OnChainDurianDatum(PlutusData):
    CONSTR_ID = 0
    farmer_cultivation_hash: bytes
    lab_inspection_hash: bytes
    enterprise_process_hash: bytes
    authorized_enterprise: bytes
