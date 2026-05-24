# ============================================================
# PATH: app/main.py
# DURIAN SMART - GATEWAY API (Bản hoàn chỉnh 4 Cổng)
# ============================================================
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Nạp module kết nối MongoDB
from app.db.database import connect_to_mongo, close_mongo_connection

# Nạp trọn bộ 4 Router (Microservices) của hệ thống
from app.api import farmer, enterprise, lab, public

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Khởi động cùng hệ thống: Mở đường ống xuống Database
    await connect_to_mongo()
    yield
    # Tắt cùng hệ thống: Đóng van Database an toàn
    await close_mongo_connection()

# Khởi tạo Trái tim của hệ thống
app = FastAPI(
    title="Durian Smart Core Enterprise", 
    description="Hệ thống lõi Traceability Đa chữ ký ứng dụng AI & Blockchain",
    version="2.0",
    lifespan=lifespan
)

# BẬT LÁ CHẮN CORS (Bắt buộc để 4 App Streamlit có thể gọi chéo API vào cổng 8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Mở cửa cho mọi IP trong quá trình Demo/Chấm thi
    allow_credentials=True,
    allow_methods=["*"],  # Cho phép tất cả các lệnh GET, POST, PUT, DELETE
    allow_headers=["*"],
)

# Đấu nối 4 Đường ống dữ liệu vào Cổng API chính
app.include_router(farmer.router)
app.include_router(enterprise.router)
app.include_router(lab.router)
app.include_router(public.router) # Mảnh ghép cuối cùng: Truy xuất cho Khách hàng

@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "Durian Smart GPU Server đang hoạt động! Hệ sinh thái 4 cổng API đã sẵn sàng."
    }