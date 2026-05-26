# ============================================================
# PATH: frontend/lab_app.py
# DURIAN SMART - CƠ QUAN KIỂM ĐỊNH (TÍCH HỢP API BACKEND)
# ============================================================
import streamlit as st
import base64
import os
import time
import requests

# Địa chỉ Máy chủ Backend FastAPI
API_BASE_URL = "http://localhost:8000"

st.set_page_config(page_title="Durian Smart | Lab", layout="wide")

# ==========================================
# [ASSETS & STATE SETUP]
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
AVATAR_LINK = get_base64_of_bin_file("frontend/images/70.jpg") 
BG_IMAGE = get_base64_of_bin_file("frontend/images/Screenshot 2026-05-25 185450.png")

# Database Ảo cho Lab (UI State)
if "lab_batches" not in st.session_state:
    st.session_state.lab_batches = [
        {"id": "BATCH-001", "cadimi": "0.02 mg/kg", "vang_o": "Không phát hiện", "thuoc_bvtv": "Đạt chuẩn", "result": "Đạt", "status": "Đã Trả kết quả"},
        {"id": "BATCH-002", "cadimi": "Chờ xét nghiệm", "vang_o": "Chờ xét nghiệm", "thuoc_bvtv": "Chờ xét nghiệm", "result": "Đang xử lý", "status": "Đang kiểm định"},
        {"id": "BATCH-003", "cadimi": "Chờ lấy mẫu", "vang_o": "Chờ lấy mẫu", "thuoc_bvtv": "Chờ lấy mẫu", "result": "Chờ xử lý", "status": "Đang giao nhận"},
        {"id": "BATCH-004", "cadimi": "0.08 mg/kg", "vang_o": "Phát hiện vết", "thuoc_bvtv": "Vượt ngưỡng", "result": "Không đạt", "status": "Đã kiểm định"}
    ]

if "page" not in st.session_state: st.session_state.page = "manage"

# ==========================================
# [HỆ THỐNG CSS]
# ==========================================
st.markdown(f"""
<style>
    .stApp {{ background-color: #F8FAFC; }}
    header, [data-testid="stHeader"] {{ visibility: hidden; }}
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] {{ font-family: 'Plus Jakarta Sans', sans-serif; }}

    [data-testid="stSidebar"] {{ background: #0F172A !important; }}
    [data-testid="stSidebar"] * {{ color: white !important; }}
    .sidebar-profile {{ display: flex; align-items: center; gap: 15px; padding: 10px 0 20px 0; border-bottom: 1px solid rgba(255,255,255,0.2); margin-bottom: 20px; }}
    .sidebar-profile img {{ width: 50px; height: 50px; border-radius: 14px; object-fit: cover; border: 2px solid #38BDF8; background: white; padding: 2px; }}
    
    .top-right-logo {{ position: fixed; top: 15px; right: 30px; display: flex; align-items: center; gap: 12px; z-index: 99999; }}
    .top-right-logo img {{ width: 45px; height: 45px; border-radius: 50%; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);}}
    .top-right-logo span {{ font-weight: 800; color: #0F172A; font-size: 1.1rem; line-height: 1.2;}}

    .bg-garden {{ position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: -1; background-image: url('{BG_IMAGE}'); background-size: cover; background-position: center; opacity: 0.1; filter: grayscale(80%) blur(4px); pointer-events: none; }}
    
    [data-testid="stForm"] {{ background: rgba(15, 23, 42, 0.95); backdrop-filter: blur(12px); border-radius: 24px; padding: 40px 50px; border: 1px solid rgba(255,255,255,0.15); box-shadow: 0 25px 50px rgba(0,0,0,0.3); margin-top: 20px; }}
    [data-testid="stForm"] label, [data-testid="stForm"] p {{ color: white !important; font-weight: 600; font-size: 0.95rem; }}
    [data-testid="stForm"] [data-baseweb="checkbox"] label {{ color: #38BDF8 !important; font-style: italic; }}
    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {{ border-radius: 12px !important; background: white !important; padding: 2px 15px; border: none !important; }}
    
    [data-testid="stFormSubmitButton"] {{ display: flex; justify-content: center; margin-top: 20px; }}
    [data-testid="stFormSubmitButton"] > button {{ background: #38BDF8; color: #0F172A !important; font-weight: 800; font-size: 1.1rem; border-radius: 50px; padding: 10px 40px; border: none; box-shadow: 0 8px 20px rgba(56, 189, 248, 0.3); transition: all 0.3s ease; }}
    [data-testid="stFormSubmitButton"] > button:hover {{ transform: translateY(-2px); box-shadow: 0 12px 25px rgba(56, 189, 248, 0.5); }}

    .table-header {{ font-weight: 800; color: #0F172A; border-bottom: 2px solid #0F172A; padding-bottom: 10px; margin-bottom: 15px; font-size: 0.9rem; text-align: center; text-transform: uppercase; }}
    .table-row {{ align-items: center; border-bottom: 1px solid #E2E8F0; padding: 12px 0; text-align: center; color: #334155; font-weight: 600; font-size: 0.9rem; }}
    
    .status-badge {{ padding: 6px 12px; border-radius: 50px; font-weight: 700; font-size: 0.8rem; display: inline-block; text-align: center; width: 100%; }}
    
    .s-giaonhan {{ background: #E0F2FE; color: #0369A1; border: 1px solid #0369A1; }}
    .s-kiemdinh {{ background: #FEF08A; color: #854D0E; border: 1px solid #854D0E; }}
    .s-dakiemdinh {{ background: #DDD6FE; color: #5B21B6; border: 1px solid #5B21B6; }}
    .s-datrakq {{ background: #DCFCE7; color: #166534; border: 1px solid #166534; }}
    
    .r-dat {{ color: #166534; font-weight: 800; }}
    .r-khongdat {{ color: #991B1B; font-weight: 800; }}
    .r-dangxuly {{ color: #64748B; font-style: italic; font-weight: 500; }}
</style>
""", unsafe_allow_html=True)

st.markdown(f'<div class="top-right-logo"><img src="{LOGO_LINK}"><span id="logo-text">Durian<br>Smart</span></div>', unsafe_allow_html=True)

# ==========================================
# [SIDEBAR]
# ==========================================
with st.sidebar:
    st.markdown(f'<div class="sidebar-profile"><img src="{AVATAR_LINK}"><span>LAB GACC HCM</span></div>', unsafe_allow_html=True)
    st.write("---")
    if st.button("📊 Quản lý lô hàng", use_container_width=True): st.session_state.page = "manage"; st.rerun()
    if st.button("🛡️ Cấp chứng nhận số", use_container_width=True): st.session_state.page = "cert"; st.rerun()
    if st.button("📋 Báo cáo chi tiết", use_container_width=True): st.session_state.page = "report"; st.rerun()
    st.write("---")
    st.button("⚙️ Hệ thống LIMS", disabled=True, use_container_width=True)
    st.button("Đăng xuất")


# ==========================================
# [ROUTING & PAGES]
# ==========================================

# --- 1. QUẢN LÝ LÔ HÀNG KIỂM ĐỊNH ---
if st.session_state.page == "manage":
    st.markdown('<h2 style="color:#0F172A; font-weight:800; text-transform:uppercase; margin-bottom: 20px;">Dữ liệu mẫu kiểm định sinh hóa</h2>', unsafe_allow_html=True)
    
    st.markdown('<div style="background: white; border-radius: 12px; padding: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.05);">', unsafe_allow_html=True)
    h_cols = st.columns([1, 1.2, 1.2, 1.2, 1, 1.5])
    headers = ["Mã Lô", "Độc tố Cadimi", "Chất Vàng O", "Dư lượng BVTV", "Kết quả", "Trạng thái"]
    for i, col in enumerate(h_cols):
        col.markdown(f'<div class="table-header">{headers[i]}</div>', unsafe_allow_html=True)
    
    for batch in st.session_state.lab_batches:
        cols = st.columns([1, 1.2, 1.2, 1.2, 1, 1.5])
        cols[0].markdown(f'<div class="table-row">{batch["id"]}</div>', unsafe_allow_html=True)
        cols[1].markdown(f'<div class="table-row">{batch["cadimi"]}</div>', unsafe_allow_html=True)
        cols[2].markdown(f'<div class="table-row">{batch["vang_o"]}</div>', unsafe_allow_html=True)
        cols[3].markdown(f'<div class="table-row">{batch["thuoc_bvtv"]}</div>', unsafe_allow_html=True)
        
        # Style cho Kết quả
        res = batch["result"]
        res_class = "r-dat" if res == "Đạt" else "r-khongdat" if res == "Không đạt" else "r-dangxuly"
        cols[4].markdown(f'<div class="table-row {res_class}">{res}</div>', unsafe_allow_html=True)
        
        # Style cho Trạng thái
        status = batch["status"]
        if status == "Đang giao nhận": css_class = "s-giaonhan"
        elif status == "Đang kiểm định": css_class = "s-kiemdinh"
        elif status == "Đã kiểm định": css_class = "s-dakiemdinh"
        else: css_class = "s-datrakq"
        
        cols[5].markdown(f'<div class="table-row"><span class="status-badge {css_class}">{status}</span></div>', unsafe_allow_html=True)
                
    st.markdown('</div>', unsafe_allow_html=True)


# --- 2. CẤP CHỨNG NHẬN SỐ ---
elif st.session_state.page == "cert":
    st.markdown('<style>.stApp { background-color: #0F172A !important; } #logo-text{color: white !important;}</style>', unsafe_allow_html=True)
    st.markdown('<div class="bg-garden"></div>', unsafe_allow_html=True)
    
    st.markdown("""<div style="text-align:center; margin-bottom: 20px; margin-top: 20px;"><img src="https://cdn-icons-png.flaticon.com/512/8649/8649595.png" width="60" style="filter: hue-rotate(180deg);"><h2 style="color:white; font-weight:800; text-transform:uppercase;">Khai báo kết quả & Cấp chứng nhận số</h2></div>""", unsafe_allow_html=True)

    with st.form("lab_cert_form", clear_on_submit=False):
        st.markdown('<h4 style="color: #38BDF8;">1. Thông tin mẫu</h4>', unsafe_allow_html=True)
        r1c1, r1c2, r1c3 = st.columns(3)
        with r1c1: batch_id = st.text_input("Mã Lô Sầu Riêng cần cấp*")
        with r1c2: test_date_input = st.date_input("Ngày phân tích*")
        with r1c3: tech_id = st.text_input("Mã Kỹ thuật viên*")

        st.markdown('<h4 style="color: #38BDF8; margin-top: 15px;">2. Chỉ số Sinh hóa (GACC Standard)</h4>', unsafe_allow_html=True)
        r2c1, r2c2, r2c3 = st.columns(3)
        with r2c1: val_cadimi = st.text_input("Chỉ số Cadimi (mg/kg)*", placeholder="VD: 0.02")
        with r2c2: val_vango = st.selectbox("Xét nghiệm Vàng O*", ["Không phát hiện", "Phát hiện vết", "Vượt ngưỡng"])
        with r2c3: val_bvtv = st.selectbox("Dư lượng thuốc BVTV*", ["Đạt chuẩn (< 0.01%)", "Vượt ngưỡng an toàn"])

        r3c1, r3c2 = st.columns([1, 2])
        with r3c1: final_result = st.selectbox("Kết luận chung*", ["Đạt", "Không đạt"])
        with r3c2: st.file_uploader("Đính kèm bản Scan Báo cáo (PDF)", type=["pdf"])
            
        st.write("") 
        agreement = st.checkbox("Tôi xác nhận kết quả kiểm định chính xác và ký số bằng Private Key của cơ quan.")
        
        if st.form_submit_button("Cấp Chứng Nhận & Ký Số"):
            if not batch_id or not tech_id or not agreement:
                st.error("⚠️ Vui lòng điền đủ Mã lô, Mã Kỹ thuật viên và tick chọn xác nhận chữ ký số.")
            else:
                with st.spinner(f"Đang gọi API mã hóa kết quả và lưu vào hệ thống cho lô {batch_id}..."):
                    # 1. Chuẩn bị payload chuẩn JSON
                    payload = {
                        "batch_id": batch_id,
                        "test_date": str(test_date_input),
                        "technician_id": tech_id,
                        "cadimi_level": val_cadimi if val_cadimi else "0.01",
                        "vang_o_result": val_vango,
                        "bvtv_result": val_bvtv,
                        "final_result": final_result
                    }
                    
                    # 2. Gọi API đến FastAPI Backend
                    try:
                        response = requests.post(f"{API_BASE_URL}/lab/{batch_id}/certificate", json=payload)
                        if response.status_code == 200:
                            data = response.json()
                            st.success(f"🎉 {data['message']}")
                            st.info(f"🔑 Chữ ký số Lab-Hash (Chuẩn JSON): {data.get('lab_hash')}")
                            
                            # 3. Cập nhật Local UI State để thấy hiệu ứng cập nhật bảng ngay
                            found = False
                            for b in st.session_state.lab_batches:
                                if b["id"] == batch_id:
                                    b["cadimi"] = (val_cadimi + " mg/kg") if val_cadimi else "0.01 mg/kg"
                                    b["vang_o"] = val_vango
                                    b["thuoc_bvtv"] = val_bvtv
                                    b["result"] = final_result
                                    b["status"] = "Đã Trả kết quả"
                                    found = True
                            
                            if not found:
                                st.warning("Ghi chú: Lô này không có trong danh sách hiển thị giả lập trên UI, nhưng API đã ghi nhận thành công dưới Database!")
                                
                        else:
                            st.error(f"⚠️ Lỗi từ hệ thống: {response.json().get('detail', 'Lỗi không xác định')}")
                    except requests.exceptions.ConnectionError:
                        st.error("🔌 Không thể kết nối đến Máy chủ Backend. Vui lòng kiểm tra Uvicorn!")


# --- 3. BÁO CÁO CHI TIẾT ---
elif st.session_state.page == "report":
    st.title("📋 Báo cáo kiểm định chi tiết")
    st.info("Khu vực truy xuất hồ sơ PDF và biểu đồ phân tích thành phần hóa học của từng lô hàng theo thời gian thực.")