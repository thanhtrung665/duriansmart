import httpx
import os
from dotenv import load_dotenv

# Nạp cấu hình file .env
load_dotenv()

class KaggleAIClient:
    def __init__(self):
        # Lấy url ngrok từ cấu hình hệ thống
        self.base_url = os.getenv("KAGGLE_AI_URL")
        if not self.base_url:
            raise ValueError("Lỗi chưa cấu hình")
    async def forward_audio_to_oracle(self, file_bytes: bytes, file_name: str) -> dict:
        timeout = httpx.Timeout(60.0, connect=10.0)
        async with httpx.AsyncClient(base_url=self.base_url, timeout=timeout) as client:
            files = {"audio": (file_name, file_bytes, "audio/wav")}
            try:
                print(f"Đang truyền file qua NGROK lên kaggle")
                response = await client.post("/v1/analyze-audio", files=files)
                if response.status_code == 200:
                    print("Kết nối thành công! Đã nhận dữ liệu Standard Json từ AI Oracle")
                    return response.json()
                else:
                    return {
                        "error": f"Lỗi hệ thống Kaggle trả về mã HTTP {response.status_code}",
                        "detail": response.text
                    }
            except httpx.RequestError as exc:
                return {
                    "error": "Không thể kết nối tới NGROK",
                    "detail": f"Vui lòng kiểm tra Kaggle, cụ thể {exc}"
                }