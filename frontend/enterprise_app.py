# ============================================================
# PATH: frontend/enterprise_app.py
# DURIAN SMART - ENTERPRISE MODULE (TÍCH HỢP API BACKEND & XUẤT QR)
# ============================================================
import streamlit as st
import base64
import os
import time
import requests

# Địa chỉ Máy chủ Backend FastAPI
API_BASE_URL = "http://localhost:8000"

st.set_page_config(page_title="Durian Smart | Enterprise", layout="wide")

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

# Database Ảo (Mock State) để hiển thị UI
if "batches_data" not in st.session_state:
    st.session_state.batches_data = [
        {"id": "BATCH-001", "puc": "PUC-01", "farmer": "ND-001", "qty": "10 Tấn", "status": "Đang kiểm định", "qr_ready": False},
        {"id": "BATCH-002", "puc": "PUC-02", "farmer": "ND-002", "qty": "15 Tấn", "status": "Sẵn sàng xuất", "qr_ready": True},
        {"id": "BATCH-003", "puc": "PUC-03", "farmer": "ND-003", "qty": "10 Tấn", "status": "Đóng gói", "qr_ready": False},
        {"id": "BATCH-004", "puc": "PUC-01", "farmer": "ND-001", "qty": "8 Tấn", "status": "Bị trả về", "qr_ready": False},
        {"id": "BATCH-005", "puc": "PUC-04", "farmer": "ND-005", "qty": "12 Tấn", "status": "Bị tiêu hủy", "qr_ready": False}
    ]

if "page" not in st.session_state: st.session_state.page = "dashboard"
if "selected_qr_batch" not in st.session_state: st.session_state.selected_qr_batch = ""

# ==========================================
# [HỆ THỐNG CSS]
# ==========================================
st.markdown(f"""
<style>
    .stApp {{ background-color: #F8FAFC; }}
    header, [data-testid="stHeader"] {{ visibility: hidden; }}
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] {{ font-family: 'Plus Jakarta Sans', sans-serif; }}

    [data-testid="stSidebar"] {{ background: #164B31 !important; }}
    [data-testid="stSidebar"] * {{ color: white !important; }}
    .sidebar-profile {{ display: flex; align-items: center; gap: 15px; padding: 10px 0 20px 0; border-bottom: 1px solid rgba(255,255,255,0.2); margin-bottom: 20px; }}
    .sidebar-profile img {{ width: 50px; height: 50px; border-radius: 14px; object-fit: cover; border: 2px solid #FACC15; }}
    
    .top-right-logo {{ position: fixed; top: 15px; right: 30px; display: flex; align-items: center; gap: 12px; z-index: 99999; }}
    .top-right-logo img {{ width: 45px; height: 45px; border-radius: 50%; box-shadow: 0 4px 15px rgba(250, 204, 21, 0.4);}}
    .top-right-logo span {{ font-weight: 800; color: #164B31; font-size: 1.1rem; line-height: 1.2;}}

    .stat-card {{ background: linear-gradient(135deg, #114B32 0%, #166534 100%); padding: 20px; border-radius: 16px; color: white; box-shadow: 0 10px 15px rgba(0,0,0,0.1); }}
    .stat-value {{ font-size: 1.8rem; font-weight: 800; margin-top: 5px; color: #FACC15; }}

    .bg-garden {{ position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: -1; background-image: url('{BG_IMAGE}'); background-size: cover; background-position: center; opacity: 0.15; filter: blur(5px); pointer-events: none; }}
    
    [data-testid="stForm"] {{ background: rgba(22, 75, 49, 0.95); backdrop-filter: blur(12px); border-radius: 24px; padding: 40px 50px; border: 1px solid rgba(255,255,255,0.15); box-shadow: 0 25px 50px rgba(0,0,0,0.3); margin-top: 20px; }}
    [data-testid="stForm"] label, [data-testid="stForm"] p {{ color: white !important; font-weight: 600; font-size: 0.95rem; }}
    [data-testid="stForm"] [data-baseweb="checkbox"] label {{ color: #FACC15 !important; font-style: italic; }}
    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {{ border-radius: 50px !important; background: white !important; padding: 2px 15px; border: none !important; }}
    
    [data-testid="stFormSubmitButton"] {{ display: flex; justify-content: center; margin-top: 20px; }}
    [data-testid="stFormSubmitButton"] > button {{ background: #FFFFFF; color: #114B32 !important; font-weight: 800; font-size: 1.1rem; border-radius: 50px; padding: 10px 40px; border: none; box-shadow: 0 8px 20px rgba(0,0,0,0.2); transition: all 0.3s ease; }}
    [data-testid="stFormSubmitButton"] > button:hover {{ background: #FACC15; transform: translateY(-2px); }}
    
    .back-btn > button {{ background: transparent; color: #114B32; font-weight: 800; font-size: 1.2rem; border: none; padding-left: 0; }}
    .back-btn > button:hover {{ color: #FACC15; background: transparent; }}

    .status-badge {{ padding: 6px 12px; border-radius: 50px; font-weight: 700; font-size: 0.85rem; display: inline-block; text-align: center; width: 100%; }}
    .badge-ready {{ background: #A3A02C; color: white; }}
    .badge-inspect {{ background: #FDE047; color: #854D0E; }}
    .badge-pack {{ background: #FDBA74; color: #9A3412; }}
    .badge-return {{ background: #EF4444; color: white; }}
    .badge-destroy {{ background: #7F1D1D; color: white; }}
    
    div[data-testid="stButton"] > button[disabled] {{ background-color: #EF4444 !important; color: white !important; border: none !important; opacity: 0.9 !important; border-radius: 50px; font-weight: 800; }}
    div[data-testid="stButton"] > button:not([disabled]).btn-qr {{ background-color: #A3A02C !important; color: white !important; border: none !important; border-radius: 50px; font-weight: 800; transition: 0.3s; }}
    div[data-testid="stButton"] > button:not([disabled]).btn-qr:hover {{ background-color: #166534 !important; box-shadow: 0 5px 15px rgba(22,101,52,0.4); transform: scale(1.05); }}
    
    .table-header {{ font-weight: 800; color: #164B31; border-bottom: 2px solid #164B31; padding-bottom: 10px; margin-bottom: 15px; font-size: 1rem; text-align: center; }}
    .table-row {{ align-items: center; border-bottom: 1px solid #E2E8F0; padding: 12px 0; text-align: center; color: #334155; font-weight: 600; }}
</style>
""", unsafe_allow_html=True)

st.markdown(f'<div class="top-right-logo"><img src="{LOGO_LINK}"><span id="logo-text">Durian<br>Smart</span></div>', unsafe_allow_html=True)

# ==========================================
# [SIDEBAR]
# ==========================================
with st.sidebar:
    st.markdown(f'<div class="sidebar-profile"><img src="{AVATAR_LINK}"><span>CTY XNK X</span></div>', unsafe_allow_html=True)
    st.write("---")
    if st.button("🏠 Màn hình chính", use_container_width=True): st.session_state.page = "dashboard"; st.rerun()
    if st.button("📦 Báo cáo đóng gói", use_container_width=True): st.session_state.page = "packing"; st.rerun()
    if st.button("🛡️ Yêu cầu kiểm định", use_container_width=True): st.session_state.page = "cert"; st.rerun()
    if st.button("📋 Thông tin lô hàng", use_container_width=True): st.session_state.page = "batches"; st.rerun()
    st.button("💰 Đối tác thu mua", disabled=True, use_container_width=True)
    st.write("---")
    st.button("⚙️ Cài đặt", disabled=True, use_container_width=True)
    st.button("💬 Góp ý phản hồi", disabled=True, use_container_width=True)
    st.button("❓ Giúp đỡ", disabled=True, use_container_width=True)
    st.button("Đăng xuất")


# ==========================================
# [ROUTING & PAGES]
# ==========================================

# --- 1. DASHBOARD ---
if st.session_state.page == "dashboard":
    st.title("🏭 Tổng quan Doanh nghiệp Xuất khẩu")
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown('<div class="stat-card">Sản lượng thu mua<div class="stat-value">423.5 Tấn</div></div>', unsafe_allow_html=True)
    c2.markdown('<div class="stat-card">Số Lô Xuất Khẩu<div class="stat-value">200 Lô</div></div>', unsafe_allow_html=True)
    c3.markdown('<div class="stat-card">Tổng Doanh Thu<div class="stat-value">$ 51.250</div></div>', unsafe_allow_html=True)
    c4.markdown('<div class="stat-card">Số Lô Chờ Kiểm Định<div class="stat-value">50 Lô</div></div>', unsafe_allow_html=True)

    st.write("---")
    g1, g2 = st.columns([2, 1])
    with g1:
        st.subheader("Sản lượng thu mua và xuất khẩu (Tấn)")
        st.bar_chart({"Thu mua": [78, 60, 45, 30], "Xuất khẩu": [65, 50, 35, 25]})
    with g2:
        st.subheader("Lối tắt chức năng")
        if st.button("📦 Gửi Báo Cáo Đóng Gói", use_container_width=True): st.session_state.page = "packing"; st.rerun()
        if st.button("🛡️ Gửi Yêu Cầu Kiểm Định", use_container_width=True): st.session_state.page = "cert"; st.rerun()
        if st.button("📋 Truy xuất Dữ liệu Lô hàng", use_container_width=True): st.session_state.page = "batches"; st.rerun()


# --- 2. BÁO CÁO XỬ LÝ VÀ ĐÓNG GÓI ---
elif st.session_state.page == "packing":
    st.markdown('<style>.stApp { background-color: #164B31 !important; } #logo-text{color: white !important;}</style>', unsafe_allow_html=True)
    st.markdown('<div class="bg-garden"></div>', unsafe_allow_html=True)
    st.markdown('<div class="back-btn">', unsafe_allow_html=True)
    if st.button("⬅️ Quay lại", key="b_pack"): st.session_state.page = "dashboard"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("""<div style="text-align:center; margin-bottom: 20px;"><img src="https://cdn-icons-png.flaticon.com/512/8649/8649595.png" width="60"><h2 style="color:white; font-weight:800; text-transform:uppercase;">Báo cáo xử lý và đóng gói</h2></div>""", unsafe_allow_html=True)

    with st.form("packing_report_form", clear_on_submit=False):
        r1c1, r1c2, r1c3 = st.columns(3)
        with r1c1: ent_name = st.text_input("Tên Doanh Nghiệp (PHC)*", placeholder="CTY XNK X")
        with r1c2: fac_code = st.text_input("Mã Cơ Sở Đóng Gói (PHC)*")
        with r1c3: batch_id = st.text_input("Mã Lô Sầu Riêng*")

        r2c1, r2c2, r2c3 = st.columns(3)
        with r2c1: emp_id = st.text_input("Mã Nhân viên báo cáo*")
        with r2c2: emp_name = st.text_input("Họ & Tên Nhân Viên")
        with r2c3: proc_date = st.date_input("Ngày xử lý, đóng gói*")

        r3c1, r3c2 = st.columns([2, 1])
        with r3c1: method = st.text_input("Phương pháp xử lý, đóng gói*")
        with r3c2: uploaded_file = st.file_uploader("File Báo Cáo Đóng Gói", type=["pdf", "jpg"])
            
        st.write("") 
        agreement = st.checkbox("Tôi xin cam đoan tất cả thông tin trên là đúng sự thật.")
        
        if st.form_submit_button("Cập nhật báo cáo"):
            if not batch_id or not agreement:
                st.error("⚠️ Vui lòng điền mã lô và cam đoan.")
            else:
                with st.spinner("Đang gọi API và ghi băm báo cáo lên Smart Contract..."):
                    # Đóng gói dữ liệu gửi API
                    payload = {
                        "enterprise_name": ent_name,
                        "facility_code": fac_code,
                        "batch_id": batch_id,
                        "employee_id": emp_id,
                        "employee_name": emp_name,
                        "processing_date": str(proc_date),
                        "processing_method": method
                    }
                    try:
                        # Bắn API POST xuống FastAPI Backend
                        response = requests.post(f"{API_BASE_URL}/enterprise/{batch_id}/packaging-report", json=payload)
                        if response.status_code == 200:
                            data = response.json()
                            st.success(f"🎉 {data['message']}")
                            st.info(f"🔗 Enterprise Hash (Chuẩn JSON): {data.get('enterprise_hash')}")
                            # Cập nhật Local UI State để thấy hiệu ứng ngay
                            for b in st.session_state.batches_data:
                                if b["id"] == batch_id: b["status"] = "Đóng gói"
                        else:
                            st.error(f"⚠️ Lỗi từ hệ thống: {response.json().get('detail', 'Lỗi không xác định')}")
                    except requests.exceptions.ConnectionError:
                        st.error("🔌 Không thể kết nối đến Máy chủ Backend. Vui lòng kiểm tra Uvicorn!")


# --- 3. YÊU CẦU KIỂM ĐỊNH CẤP CHỨNG CHỈ ---
elif st.session_state.page == "cert":
    st.markdown('<style>.stApp { background-color: #164B31 !important; } #logo-text{color: white !important;}</style>', unsafe_allow_html=True)
    st.markdown('<div class="bg-garden"></div>', unsafe_allow_html=True)
    st.markdown('<div class="back-btn">', unsafe_allow_html=True)
    if st.button("⬅️ Quay lại", key="b_cert"): st.session_state.page = "dashboard"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("""<div style="text-align:center; margin-bottom: 20px;"><img src="https://cdn-icons-png.flaticon.com/512/8649/8649595.png" width="60"><h2 style="color:white; font-weight:800; text-transform:uppercase;">Yêu cầu kiểm định & Cấp chứng chỉ số</h2></div>""", unsafe_allow_html=True)

    with st.form("cert_request_form", clear_on_submit=False):
        r1c1, r1c2, r1c3 = st.columns(3)
        with r1c1: ent_name_req = st.text_input("Tên Doanh Nghiệp (PHC)*", placeholder="CTY XNK X", key="cert_ent")
        with r1c2: fac_code_req = st.text_input("Mã Cơ Sở Đóng Gói (PHC)*", key="cert_fac")
        with r1c3: lab_code = st.text_input("Mã Cơ Quan Kiểm Định*", placeholder="VD: LAB-GACC-HCM")

        r2c1, r2c2, r2c3 = st.columns(3)
        with r2c1: req_batch = st.text_input("Mã Lô Sầu Riêng*", key="cert_batch")
        with r2c2: puc_code = st.text_input("Mã Vùng (PUC)*")
        with r2c3: variety = st.selectbox("Giống Sầu Riêng*", ["Ri6", "Monthong"])

        r3c1, r3c2, _ = st.columns(3)
        with r3c1: sample_date = st.date_input("Ngày gửi mẫu*")
        with r3c2: category = st.selectbox("Danh mục kiểm định*", ["Kiểm dịch thực vật & Dư lượng thuốc BVTV"])

        st.write("") 
        agreement = st.checkbox("Tôi đồng ý chia sẻ dữ liệu về Lô hàng phục vụ quá trình kiểm định")
        
        if st.form_submit_button("Nộp yêu cầu"):
            if not req_batch or not agreement:
                st.error("⚠️ Vui lòng điền mã lô và cam đoan.")
            else:
                with st.spinner("Đang chuyển tiếp yêu cầu API đến Cơ quan kiểm định..."):
                    payload = {
                        "enterprise_name": ent_name_req,
                        "facility_code": fac_code_req,
                        "lab_code": lab_code,
                        "batch_id": req_batch,
                        "puc_code": puc_code,
                        "variety": variety,
                        "sample_date": str(sample_date),
                        "test_category": category
                    }
                    try:
                        response = requests.post(f"{API_BASE_URL}/enterprise/{req_batch}/cert-request", json=payload)
                        if response.status_code == 200:
                            data = response.json()
                            st.success(f"🎉 {data['message']}")
                            for b in st.session_state.batches_data:
                                if b["id"] == req_batch: b["status"] = "Đang kiểm định"
                        else:
                            st.error(f"⚠️ Lỗi: {response.json().get('detail', 'Lỗi không xác định')}")
                    except requests.exceptions.ConnectionError:
                        st.error("🔌 Lỗi kết nối Backend. Vui lòng đảm bảo server Uvicorn đang chạy.")


# --- 4. THÔNG TIN LÔ HÀNG ---
elif st.session_state.page == "batches":
    st.markdown('<div class="back-btn">', unsafe_allow_html=True)
    if st.button("⬅️ Quay lại", key="b_batch"): st.session_state.page = "dashboard"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<h2 style="color:#164B31; font-weight:800; text-transform:uppercase; margin-bottom: 20px;">Dữ liệu lô hàng thu mua và xuất khẩu</h2>', unsafe_allow_html=True)
    
    st.markdown('<div style="background: white; border-radius: 12px; padding: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.05);">', unsafe_allow_html=True)
    h_cols = st.columns([1.2, 1, 1, 1, 1.2, 1.5, 1.2])
    headers = ["Mã Lô hàng", "Mã vùng(PUC)", "Mã Nông dân", "Sản lượng", "Nhật ký canh tác", "Trạng thái", "Xuất QR-Code"]
    for i, col in enumerate(h_cols):
        col.markdown(f'<div class="table-header">{headers[i]}</div>', unsafe_allow_html=True)
    
    for i, batch in enumerate(st.session_state.batches_data):
        cols = st.columns([1.2, 1, 1, 1, 1.2, 1.5, 1.2])
        cols[0].markdown(f'<div class="table-row">{batch["id"]}</div>', unsafe_allow_html=True)
        cols[1].markdown(f'<div class="table-row">{batch["puc"]}</div>', unsafe_allow_html=True)
        cols[2].markdown(f'<div class="table-row">{batch["farmer"]}</div>', unsafe_allow_html=True)
        cols[3].markdown(f'<div class="table-row">{batch["qty"]}</div>', unsafe_allow_html=True)
        cols[4].markdown(f'<div class="table-row" style="color:#164B31; cursor:pointer;">Truy cập</div>', unsafe_allow_html=True)
        
        status = batch["status"]
        if status == "Sẵn sàng xuất": css_class = "badge-ready"
        elif status == "Đang kiểm định": css_class = "badge-inspect"
        elif status == "Đóng gói": css_class = "badge-pack"
        elif status == "Bị trả về": css_class = "badge-return"
        else: css_class = "badge-destroy"
        
        cols[5].markdown(f'<div class="table-row"><span class="status-badge {css_class}">{status}</span></div>', unsafe_allow_html=True)
        
        with cols[6]:
            if batch["qr_ready"] or status == "Sẵn sàng xuất":
                st.markdown('<div class="btn-qr">', unsafe_allow_html=True)
                if st.button("Xuất mã", key=f"qr_on_{i}", use_container_width=True):
                    with st.spinner("Đang gọi Smart Contract và đúc NFT Blockchain..."):
                        try:
                            # Kích hoạt On-chain API (Single-Signature)
                            res = requests.post(f"{API_BASE_URL}/enterprise/{batch['id']}/mint-export-qr")
                            if res.status_code == 200:
                                st.session_state.selected_qr_batch = batch['id']
                                st.session_state.page = "qr_view"
                                st.rerun()
                            else:
                                st.error(f"⚠️ Lỗi Blockchain: {res.json().get('detail')}")
                        except Exception as e:
                            st.error("🔌 Lỗi kết nối Backend Uvicorn.")
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.button("Xuất mã", key=f"qr_off_{i}", disabled=True, use_container_width=True)
                
    st.markdown('</div>', unsafe_allow_html=True)


# --- 5. GIAO DIỆN XUẤT QR CODE (SEED-TO-SACK) ---
elif st.session_state.page == "qr_view":
    batch_id = st.session_state.selected_qr_batch
    
    # CSS Custom cho trang QR
    st.markdown("""
    <style>
        .stApp { background-color: #164B31 !important; }
        #logo-text { color: white !important; }
        .back-icon { color: #FACC15 !important; font-size: 2rem; font-weight: 800; border: none; background: transparent;}
        .back-icon:hover { color: white !important; }
        
        .qr-export-btn > button {
            background-color: white !important;
            color: #164B31 !important;
            font-weight: 800;
            font-size: 1.1rem;
            padding: 10px 40px;
            border-radius: 50px;
            border: none;
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
            transition: all 0.3s;
        }
        .qr-export-btn > button:hover {
            transform: scale(1.05);
            background-color: #FACC15 !important;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="bg-garden"></div>', unsafe_allow_html=True)
    
    # Nút Back mũi tên vàng góc trái
    if st.button("⬅️", key="b_qr_back", type="secondary", use_container_width=False):
        st.session_state.page = "batches"
        st.rerun()

    # Layout chính giữa trang
    st.markdown(f"""
    <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; margin-top: -30px;">
        <div style="text-align: center; margin-bottom: 20px;">
            <img src="{LOGO_LINK}" width="50" style="margin-bottom: 5px;">
            <div style="color: white; font-weight: 800; font-size: 1.2rem; line-height: 1.1;">Durian<br>Smart</div>
        </div>
        
        <h2 style="color:white; font-weight:800; font-size: 2rem; text-transform:uppercase; text-align: center; margin-bottom: 40px;">
            XUẤT MÃ QR-CODE TRUY XUẤT NGUỒN GỐC
        </h2>
        
        <div style="position: relative; width: 350px; height: 350px; display: flex; flex-direction: column; align-items: center;">
            <div style="background: #FACC15; width: 160px; height: 160px; border-radius: 50%; border: 8px solid white; display: flex; align-items: center; justify-content: center; position: absolute; top: -50px; z-index: 3; box-shadow: 0 10px 20px rgba(0,0,0,0.2);">
                <span style="font-size: 5rem;">🍈</span>
            </div>
            
            <div style="background: #A3A02C; color: white; padding: 5px 30px; font-weight: 800; font-size: 0.9rem; text-transform: uppercase; border-radius: 4px; position: absolute; top: 90px; z-index: 4; box-shadow: 0 4px 10px rgba(0,0,0,0.2);">
                Certified Compliant
            </div>
            
            <div style="background: white; border-radius: 20px; width: 100%; height: 280px; position: absolute; bottom: 0; display: flex; align-items: flex-end; justify-content: center; padding-bottom: 30px; box-shadow: 0 15px 40px rgba(0,0,0,0.3);">
                <img src="https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=https://duriansmart.vn/verify/{batch_id}" width="180">
            </div>
        </div>
    </div>
    <br>
    """, unsafe_allow_html=True)
    
    # Nút Xuất và hiển thị JSON
    st.markdown('<div class="qr-export-btn" style="display:flex; justify-content:center; margin-top: 20px;">', unsafe_allow_html=True)
    if st.button("Xuất mã QR-CODE"):
        # Gom toàn bộ dữ liệu Seed-to-Sack vào JSON
        seed_to_sack_data = {
            "batch_metadata": { "batch_id": batch_id, "puc_code": "PUC-01", "variety": "Ri6", "yield": "10 Tấn" },
            "farmer_data": { "name": "Hồ Thanh Trung", "farm_address": "Tiền Giang", "daily_logs": ["Bón phân X", "Tưới nước", "Phun thuốc"] },
            "enterprise_data": { "name": "CTY XNK X", "facility": "VN-PHC-123", "packing_method": "Rửa ozone, đóng thùng lạnh", "employee": "NV-099" },
            "lab_data": { "lab_name": "LAB-GACC-HCM", "test_date": "2026-06-01", "result": "Đạt tiêu chuẩn kiểm dịch thực vật", "cert_hash": f"0x{os.urandom(16).hex()}" },
            "smart_contract": { "network": "Cardano Preprod", "tx_hash": f"0x{os.urandom(16).hex()}", "status": "LOCKED" }
        }
        st.toast(f"Đã xuất thành công gói dữ liệu chuẩn GACC cho {batch_id}!")
        with st.expander("📄 Dữ liệu JSON Seed-to-Sack đính kèm mã QR", expanded=True):
            st.json(seed_to_sack_data)
    st.markdown('</div>', unsafe_allow_html=True)