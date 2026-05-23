from fastapi import FastAPI
from app.api import farmer, lab, enterprise
from contextlib import asynccontextmanager
from app.db.database import connect_to_mongo, close_mongo_connection

# Khởi tạo ứng dụng FasstAPI với Metadata chuẩn chỉnh
app = FastAPI(
    title="Durian Smart MVP",
    description="Hệ thống Durian Smart - Truy xuất nguồn gốc minh bạch sầu riêng cho người Việt",
    version="1.0.0"
)

# Đăng ký các Router phân quyền
app.include_router(farmer.router, prefix="/api/v1/farmer", tags=["Phân hệ Nông dân (Zalo Mini App)"])
app.include_router(enterprise.router, prefix="/api/v1/enterprise", tags=["Phân hệ Doanh nghiệp XNK"])
app.include_router(lab.router, prefix="/api/v1/lab", tags=["Phân hệ phòng Lab"])

@app.get("/")
async def root_health_check():
    return {"status": "success", "message": "Durian Smart is running Smoothly!"}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Khởi động cùng FastAPI
    await connect_to_mongo()
    yield
    # Tắt cùng FastAPI
    await close_mongo_connection()

app = FastAPI(title="Durian Smart Core", lifespan=lifespan)