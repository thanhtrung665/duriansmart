# ============================================================
# PATH: frontend/farmer_app.py
# ============================================================
import streamlit as st
import requests
from audio_recorder_streamlit import audio_recorder
import io

API_URL = "http://localhost:8000" # URL của lõi FastAPI

st.set_page_config(page_title="Farmer Portal", layout="centered")

st.title("🚜 Durian Smart - Cổng Nông Dân")
st.markdown("Hệ thống Nhật ký Canh tác bằng Giọng nói AI")

tab1, tab2 = st.tabs(["🌱 Khởi tạo Vụ mùa (Ngày 1)", "🎤 Ghi âm Nhật ký (Hàng ngày)"])

# ---------------------------------------------------------
# TAB 1: KHỞI TẠO LÔ HÀNG
# ---------------------------------------------------------
with tab1:
    st.subheader("Đăng ký mã vùng trồng")
    with st.form("init_batch_form"):
        batch_id = st.text_input("Mã Lô Sầu Riêng", value="BATCH-001")
        farmer_id = st.text_input("Mã định danh Nông dân", value="FARMER-TG-09")
        farmer_name = st.text_input("Tên chủ vườn", value="Nguyễn Văn A")
        farm_code = st.text_input("Mã vùng trồng (PUC)", value="VN-TG-01")
        variety = st.selectbox("Giống Sầu Riêng", ["Ri6", "Monthong", "Musang King"])
        
        if st.form_submit_button("Lưu Hồ Sơ Khởi Tạo"):
            payload = {
                "batch_id": batch_id,
                "farmer_id": farmer_id,
                "farmer_name": farmer_name,
                "farm_code_puc": farm_code,
                "durian_variety": variety
            }
            # Gọi API FastAPI (Lưu ý: farmer.py đang dùng Form, nên ta gửi dưới dạng data)
            res = requests.post(f"{API_URL}/farmer/init-batch", data=payload)
            if res.status_code == 200:
                st.success(f"Khởi tạo thành công lô hàng: {batch_id}")
            else:
                st.error(f"Lỗi: {res.json()['detail']}")

# ---------------------------------------------------------
# TAB 2: GHI ÂM NHẬT KÝ VỚI AI WHISPER
# ---------------------------------------------------------
with tab2:
    st.subheader("Cập nhật công việc hàng ngày")
    
    col1, col2 = st.columns(2)
    with col1:
        log_batch_id = st.text_input("Xác nhận Mã Lô", value="BATCH-001", key="log_batch")
    with col2:
        day_num = st.number_input("Ngày canh tác thứ", min_value=1, max_value=120, value=1)

    st.markdown("**Bấm vào biểu tượng Micro để nói:**")
    
    # Widget ghi âm (trả về dữ liệu dạng bytes)
    audio_bytes = audio_recorder(text="Đang nghe...", recording_color="#ef4444", neutral_color="#11CAA0")

    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")
        
        if st.button("🚀 Phân tích AI & Lưu Blockchain"):
            with st.spinner("Con chip GPU GTX 1660 Super đang bóc băng..."):
                # Đóng gói file âm thanh gửi đi
                files = {"audio_file": ("voice_log.wav", io.BytesIO(audio_bytes), "audio/wav")}
                data = {"day_number": day_num}
                
                res = requests.post(
                    f"{API_URL}/farmer/{log_batch_id}/upload-voice-log", 
                    data=data, 
                    files=files
                )
                
                if res.status_code == 200:
                    result = res.json()
                    st.success("Lưu nhật ký thành công!")
                    
                    # Hiển thị kết quả bóc băng
                    st.info(f"**📝 AI nghe được:** {result['recognized_text']}")
                    
                    # Đổi màu hiển thị dựa trên trạng thái hóa chất
                    if "CẢNH BÁO" in result['ai_evaluation']:
                        st.error(f"**⚠️ Cảnh báo GACC:** {result['ai_evaluation']}")
                    else:
                        st.success(f"**✅ Đánh giá GACC:** {result['ai_evaluation']}")
                        
                    st.caption(f"⛓️ Mã băm hiện tại: {result['current_farmer_hash']}")
                else:
                    st.error("Có lỗi xảy ra khi gọi AI Server!")