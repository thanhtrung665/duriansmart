# ============================================================
# PATH: frontend/verify_app.py
# DURIAN SMART - TRANG XÁC THỰC NGUỒN GỐC (MOBILE FIRST)
# ============================================================
import streamlit as st
import base64
import requests

API_BASE_URL = "https://durian-smart-backend.onrender.com"

st.set_page_config(
    page_title="Xác thực | Durian Smart", 
    page_icon="🍈", 
    layout="centered", 
    initial_sidebar_state="collapsed"
)

# ==========================================
# [ASSETS SETUP]
# ==========================================
@st.cache_data
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f: data = f.read()
        b64 = base64.b64encode(data).decode()
        mime = "image/png" if bin_file.lower().endswith(".png") else "image/jpeg"
        return f"data:{mime};base64,{b64}"
    except FileNotFoundError: return ""

LOGO_LINK = get_base64_of_bin_file("frontend/images/logo_durian_smart.png")

# ==========================================
# [HỆ THỐNG CSS ĐẶC CHẾ CHO MOBILE]
# ==========================================
st.markdown(f"""
<style>
    /* Ép giao diện thành form Mobile (Max width 480px) */
    .stApp {{ background-color: #F1F5F9; }}
    .main {{ max-width: 480px; margin: 0 auto; background: white; box-shadow: 0 0 20px rgba(0,0,0,0.05); min-height: 100vh; padding-bottom: 50px; }}
    header, [data-testid="stHeader"] {{ visibility: hidden; }}
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;700;800&display=swap');
    html, body, [class*="css"] {{ font-family: 'Plus Jakarta Sans', sans-serif; }}

    /* Khung Header Ứng dụng */
    .app-header {{ display: flex; justify-content: center; align-items: center; padding: 15px; border-bottom: 1px solid #F1F5F9; background: white; }}
    .app-header img {{ width: 40px; margin-right: 10px; }}
    .app-header h3 {{ margin: 0; color: #164B31; font-weight: 800; font-size: 1.2rem; }}

    /* Khung Sản phẩm */
    .product-hero {{ padding: 20px; text-align: center; background: linear-gradient(135deg, #114B32 0%, #166534 100%); color: white; }}
    .batch-title {{ font-size: 1.5rem; font-weight: 800; margin-bottom: 5px; }}
    .verified-badge {{ background: #FACC15; color: #854D0E; padding: 4px 12px; border-radius: 50px; font-weight: 700; font-size: 0.85rem; display: inline-block; margin-top: 10px; }}

    /* Card Dữ liệu từng Giai đoạn */
    .timeline-card {{ background: white; border: 1px solid #E2E8F0; border-radius: 12px; margin: 15px; padding: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.02); }}
    .card-header {{ display: flex; align-items: center; border-bottom: 1px solid #F1F5F9; padding-bottom: 10px; margin-bottom: 10px; }}
    .card-header .icon {{ background: #DCFCE7; width: 35px; height: 35px; border-radius: 8px; display: flex; justify-content: center; align-items: center; font-size: 1.2rem; margin-right: 12px; }}
    .card-header .title {{ font-weight: 800; color: #0F172A; font-size: 1rem; }}
    
    .data-row {{ display: flex; justify-content: space-between; padding: 8px 0; }}
    .data-label {{ color: #64748B; font-size: 0.85rem; font-weight: 500; }}
    .data-value {{ color: #0F172A; font-size: 0.9rem; font-weight: 700; text-align: right; max-width: 60%; word-wrap: break-word; }}
    
    /* Box Blockchain (Quan trọng) */
    .blockchain-box {{ background: #F8FAFC; border: 1px dashed #38BDF8; border-radius: 8px; padding: 10px; margin-top: 10px; }}
    .hash-text {{ font-family: monospace; font-size: 0.75rem; color: #0369A1; word-break: break-all; }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# [LOGIC LẤY DỮ LIỆU TỪ URL PARAMETER]
# ==========================================
# Lấy mã lô hàng từ URL (VD: http://localhost:8501/?batch_id=BATCH-002)
if "batch_id" in st.query_params:
    target_batch = st.query_params["batch_id"]
else:
    target_batch = None

# Giao diện Header chung
st.markdown(f"""
<div class="app-header">
    <img src="{LOGO_LINK}">
    <h3>Durian Smart Trace</h3>
</div>
""", unsafe_allow_html=True)

if not target_batch:
    st.warning("⚠️ Không tìm thấy mã lô hàng (batch_id). Vui lòng quét mã QR hợp lệ.")
    st.stop()

# Gọi API để lấy dữ liệu thực tế
with st.spinner("Đang truy xuất Blockchain..."):
    try:
        response = requests.get(f"{API_BASE_URL}/verify/{target_batch}")
        if response.status_code == 200:
            batch_data = response.json()["data"]
        else:
            st.error("❌ Dữ liệu lô hàng không tồn tại hoặc chưa được đồng bộ.")
            st.stop()
    except Exception as e:
        st.error("🔌 Lỗi kết nối đến máy chủ hệ thống.")
        st.stop()

# ==========================================
# [HIỂN THỊ DỮ LIỆU - MOBILE UI]
# ==========================================

# 1. Hero Section (Tổng quan sản phẩm)
st.markdown(f"""
<div class="product-hero">
    <div style="font-size: 3rem; margin-bottom: 10px;">🍈</div>
    <div class="batch-title">Sầu riêng Ri6 Xuất Khẩu</div>
    <div style="font-size: 0.9rem; opacity: 0.9;">Mã lô: {batch_data.get('batch_id')}</div>
    <div class="verified-badge">✓ CHỨNG NHẬN TRUY XUẤT BLOCKCHAIN</div>
</div>
""", unsafe_allow_html=True)

# 2. Khối BLOCKCHAIN CERTIFICATE (Giống màn hình giữa của JAPFA)
tx_hash = batch_data.get("transaction_hash", "Chưa đúc lên chuỗi")
st.markdown(f"""
<div class="timeline-card">
    <div class="card-header">
        <div class="icon">⛓️</div>
        <div class="title">Chứng thực Cardano Blockchain</div>
    </div>
    <div class="data-row"><span class="data-label">Mạng lưới</span><span class="data-value">Cardano Preprod</span></div>
    <div class="data-row"><span class="data-label">Trạng thái</span><span class="data-value" style="color:#166534;">{'Đã khóa (Locked)' if batch_data.get('is_minted_onchain') else 'Đang chờ xử lý'}</span></div>
    <div class="blockchain-box">
        <div class="data-label" style="margin-bottom: 5px;">Transaction Hash (TxID):</div>
        <div class="hash-text">{tx_hash}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# 3. Giai đoạn 1: NÔNG TRẠI (Seed)
st.markdown(f"""
<div class="timeline-card">
    <div class="card-header">
        <div class="icon">🧑‍🌾</div>
        <div class="title">1. Nhật ký Canh tác & Thu hoạch</div>
    </div>
    <div class="data-row"><span class="data-label">Mã Vùng Trồng (PUC)</span><span class="data-value">{batch_data.get('puc_code', 'N/A')}</span></div>
    <div class="data-row"><span class="data-label">Mã Nông Dân</span><span class="data-value">{batch_data.get('farmer_id', 'N/A')}</span></div>
    <div class="data-row"><span class="data-label">Sản lượng khai báo</span><span class="data-value">{batch_data.get('yield', 'N/A')}</span></div>
    <div class="blockchain-box">
        <div class="data-label" style="margin-bottom: 5px;">Data Hash:</div>
        <div class="hash-text">{batch_data.get('farmer_hash', 'N/A')}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# 4. Giai đoạn 2: DOANH NGHIỆP (Processing)
ent_data = batch_data.get("enterprise_data", {})
if ent_data:
    st.markdown(f"""
    <div class="timeline-card">
        <div class="card-header">
            <div class="icon">🏭</div>
            <div class="title">2. Xử lý & Đóng gói</div>
        </div>
        <div class="data-row"><span class="data-label">Cơ sở đóng gói (PHC)</span><span class="data-value">{ent_data.get('facility_code', 'N/A')}</span></div>
        <div class="data-row"><span class="data-label">Ngày xử lý</span><span class="data-value">{ent_data.get('processing_date', 'N/A')}</span></div>
        <div class="data-row"><span class="data-label">Phương pháp</span><span class="data-value">{ent_data.get('processing_method', 'N/A')}</span></div>
        <div class="blockchain-box">
            <div class="data-label" style="margin-bottom: 5px;">Data Hash:</div>
            <div class="hash-text">{batch_data.get('enterprise_hash', 'N/A')}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# 5. Giai đoạn 3: KIỂM ĐỊNH (Lab)
lab_data = batch_data.get("lab_data", {})
if lab_data:
    result_color = "#166534" if lab_data.get('final_result') == "Đạt" else "#991B1B"
    st.markdown(f"""
    <div class="timeline-card">
        <div class="card-header">
            <div class="icon">🔬</div>
            <div class="title">3. Chứng nhận Chất lượng (GACC)</div>
        </div>
        <div class="data-row"><span class="data-label">Độc tố Cadimi</span><span class="data-value">{lab_data.get('cadimi_level', 'N/A')} mg/kg</span></div>
        <div class="data-row"><span class="data-label">Chất Vàng O</span><span class="data-value">{lab_data.get('vang_o_result', 'N/A')}</span></div>
        <div class="data-row"><span class="data-label">Dư lượng BVTV</span><span class="data-value">{lab_data.get('bvtv_result', 'N/A')}</span></div>
        <div class="data-row"><span class="data-label">KẾT LUẬN CUỐI</span><span class="data-value" style="color: {result_color}; font-size: 1rem;">{lab_data.get('final_result', 'N/A')}</span></div>
        <div class="blockchain-box">
            <div class="data-label" style="margin-bottom: 5px;">Data Hash:</div>
            <div class="hash-text">{batch_data.get('lab_hash', 'N/A')}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="timeline-card">
        <div class="card-header">
            <div class="icon" style="background:#F1F5F9; color:#94A3B8;">⏳</div>
            <div class="title" style="color:#94A3B8;">3. Chứng nhận Chất lượng</div>
        </div>
        <div style="text-align: center; color: #64748B; font-size: 0.9rem; padding: 10px 0;">Lô hàng đang chờ xử lý kiểm định...</div>
    </div>
    """, unsafe_allow_html=True)