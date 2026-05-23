# ============================================================
# PATH: app/main.py
# ============================================================
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db.database import connect_to_mongo, close_mongo_connection
from app.api import farmer

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Khởi động cùng FastAPI
    await connect_to_mongo()
    yield
    # Tắt cùng FastAPI
    await close_mongo_connection()

app = FastAPI(
    title="Durian Smart Core Enterprise", 
    description="Hệ thống lõi Traceability Đa chữ ký",
    version="2.0",
    lifespan=lifespan
)

# Nhúng Router của Nông dân vào hệ thống
app.include_router(farmer.router)

@app.get("/")
def read_root():
    return {"message": "Durian Smart Core đang hoạt động trên GPU Server!"}