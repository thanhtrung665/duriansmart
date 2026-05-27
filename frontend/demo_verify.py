# ============================================================
# PATH: frontend/verify_app.py - DURIAN SMART VERIFIER
# ============================================================
import streamlit as st
import time

st.set_page_config(page_title="Durian Smart | Verify", page_icon="🔍", layout="wide")

# Mock Database (Dữ liệu giả lập)
MOCK_DB = {
    "BATCH-001": {
        "status": "Đã kiểm định",
        "origin": "Vùng trồng Đắk Lắk (PUC-01)",
        "lab": "Phòng Lab GACC HCM",
        "result": "Đạt chuẩn xuất khẩu",
        "hash": "0x8a8634798b53a480ec9d2bf22b736cc32b2af23ef2c6a8cea02f603ab7946781",
        "timestamp": "2026-05-27 09:30:15"
    },
    "BATCH-004": {
        "status": "Đã kiểm định",
        "origin": "Vùng trồng Tiền Giang (PUC-02)",
        "lab": "Phòng Lab GACC HCM",
        "result": "CẢNH BÁO: Không đạt chuẩn",
        "hash": "0xdf6607e75ea144116f977f524d6ccaf3fc9c60be28e679c482bd5286291149cb",
        "timestamp": "2026-05-26 14:15:00"
    }
}

# CSS Dark Mode Web3
st.markdown("""
<style>
    .stApp { background-color: #0B1120; color: white; }
    .search-box { padding: 40px; text-align: center; }
    .result-card { background: #1E293B; border: 1px solid #334155; border-radius: 16px; padding: 30px; margin-top: 20px; animation: fadeIn 0.5s; }
    .badge-success { background: #064E3B; color: #34D399; padding: 5px 10px; border-radius: 4px; font-weight: bold; }
    .badge-danger { background: #7F1D1D; color: #F87171; padding: 5px 10px; border-radius: 4px; font-weight: bold; }
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
</style>
""", unsafe_allow_html=True)

st.title("🔍 Xác Thực Chứng Chỉ Sầu Riêng")
st.markdown("<p style='color:#94A3B8;'>Nhập Mã lô (Batch ID) để kiểm tra tính xác thực trên Blockchain Cardano.</p>", unsafe_allow_html=True)

# Input
batch_input = st.text_input("Nhập mã lô hàng...", placeholder="VD: BATCH-001")
search_btn = st.button("Tra cứu chứng chỉ")

if search_btn:
    if not batch_input:
        st.warning("Vui lòng nhập mã lô hàng!")
    else:
        with st.spinner("Đang truy vấn sổ cái Blockchain..."):
            time.sleep(1.5) # Giả lập delay mạng
            
            if batch_input in MOCK_DB:
                data = MOCK_DB[batch_input]
                
                # Hiển thị giao diện kết quả
                st.markdown(f"""
                <div class="result-card">
                    <h3 style="color:#38BDF8;">LÔ HÀNG: {batch_input}</h3>
                    <p><strong>Nguồn gốc:</strong> {data['origin']}</p>
                    <p><strong>Cơ quan kiểm định:</strong> {data['lab']}</p>
                    <p><strong>Kết quả:</strong> <span class="{'badge-success' if 'Đạt' in data['result'] else 'badge-danger'}">{data['result']}</span></p>
                    <hr style="border-color:#334155;">
                    <p style="font-size:0.8rem; color:#64748B;"><strong>Blockchain Transaction Hash:</strong><br>{data['hash']}</p>
                    <p style="font-size:0.8rem; color:#64748B;"><strong>Thời gian ghi nhận:</strong> {data['timestamp']}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error("❌ Không tìm thấy thông tin trên Blockchain.")

# Footer demo
st.markdown("<br><br><p style='text-align:center; color:#475569;'>Powered by Durian Smart Blockchain Node</p>", unsafe_allow_html=True)