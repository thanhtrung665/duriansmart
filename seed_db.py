# PATH: seed_db.py
import asyncio
from app.db.repository import BatchRepository

async def main():
    print("🔄 Đang kết nối tới MongoDB Atlas Cluster 'kimochi'...")
    repo = BatchRepository()
    
    # Gửi lệnh Ping để kiểm tra kết nối mạng
    try:
        await repo.client.admin.command('ping')
        print("✅ Ping thành công! Đã kết nối với MongoDB Atlas.")
    except Exception as e:
        print(f"❌ Lỗi kết nối Database: {e}")
        return

    print("🌱 Đang khởi tạo dữ liệu mẫu (Seed Data)...")
    await repo.seed_mock_data()
    
    print("📊 Dữ liệu hiện có trong Database:")
    cursor = repo.collection.find({})
    batches = await cursor.to_list(length=10)
    for b in batches:
        print(f"   - Mã lô: {b.get('batch_id')} | Trạng thái: {b.get('current_state')}")

if __name__ == "__main__":
    asyncio.run(main())