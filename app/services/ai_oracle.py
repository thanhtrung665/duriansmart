# ============================================================
# PATH: app/services/ai_oracle.py
# DURIAN SMART - AI ORACLE (WHISPER GPU)
# ============================================================
import torch
import whisper
import os

class AIOracle:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"⏳ Đang nạp mô hình Whisper lên {self.device.upper()}...")
        # Dùng bản 'small' cho tốc độ realtime, có thể nâng lên 'medium' nếu muốn chính xác hơn
        self.model = whisper.load_model("small", device=self.device)
        print("✅ Động cơ AI Whisper đã sẵn sàng!")

    def transcribe_audio(self, file_path: str) -> str:
        """Nhận file âm thanh, trả về văn bản tiếng Việt"""
        result = self.model.transcribe(file_path, language="vi")
        return result["text"].strip()

    def analyze_log_content(self, text: str) -> str:
        """
        RAG Đối soát giả lập: Phân tích nội dung xem có vi phạm hóa chất không.
        (Bản thương mại sẽ nối với mô hình LLM/Knowledge Graph ở đây)
        """
        text_lower = text.lower()
        banned_chemicals = ["thuốc diệt cỏ", "cadimi", "vàng ô", "chất kích thích"]
        
        for toxic in banned_chemicals:
            if toxic in text_lower:
                return f"CẢNH BÁO: Phát hiện từ khóa '{toxic}' vi phạm chuẩn GACC!"
                
        return "Hợp lệ (Đạt chuẩn GACC)"

# Khởi tạo Singleton để load model 1 lần duy nhất
ai_engine = AIOracle()