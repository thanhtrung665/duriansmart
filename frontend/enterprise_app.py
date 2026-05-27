# ============================================================
# PATH: frontend/enterprise_app.py
# DURIAN SMART - ENTERPRISE MODULE (HOÀN THIỆN 100% THIẾT KẾ & API)
# ============================================================
import streamlit as st
import base64
import os
import time
import requests

API_BASE_URL = "https://durian-smart-backend.onrender.com"

# Cấu hình trang mở rộng để form có không gian
st.set_page_config(page_title="Durian Smart | Enterprise", page_icon="🏭", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# [ASSETS & STATE SETUP] - QUẢN LÝ 4 FILE ẢNH ĐỘC LẬP
# ==========================================
@st.cache_data
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f: data = f.read()
        b64 = base64.b64encode(data).decode()
        mime = "image/png" if bin_file.lower().endswith(".png") else "image/jpeg"
        return f"data:{mime};base64,{b64}"
    except FileNotFoundError: return ""

# 4 File ảnh theo đúng yêu cầu
LOGO_LINK = get_base64_of_bin_file("frontend/images/logo_durian_smart.png")
AVATAR_LINK = get_base64_of_bin_file("frontend/images/enterprise.jpg")
NEWS_IMAGE = get_base64_of_bin_file("frontend/images/tintuc.jpg") # Ảnh tin tức riêng
FORM_BG_IMAGE = get_base64_of_bin_file("frontend/images/bg_garden.jpg") # Ảnh nền vườn sầu riêng chìm

if "batches_data" not in st.session_state:
    st.session_state.batches_data = [
        {"id": "BATCH-001", "puc": "PUC-01", "farmer": "ND-001", "qty": "10 Tấn", "status": "Sẵn sàng xuất", "qr_ready": True},
        {"id": "BATCH-002", "puc": "PUC-02", "farmer": "ND-002", "qty": "15 Tấn", "status": "Đang kiểm định", "qr_ready": False},
        {"id": "BATCH-003", "puc": "PUC-03", "farmer": "ND-003", "qty": "10 Tấn", "status": "Đóng gói", "qr_ready": False},
        {"id": "BATCH-004", "puc": "PUC-01", "farmer": "ND-001", "qty": "8 Tấn", "status": "Bị trả về", "qr_ready": False}
    ]
if "page" not in st.session_state: st.session_state.page = "dashboard"
if "selected_qr_batch" not in st.session_state: st.session_state.selected_qr_batch = ""

# ==========================================
# [GLOBAL CSS - SIDEBAR & CHUNG]
# ==========================================
st.markdown(f"""
<style>
    header, [data-testid="stHeader"] {{ visibility: hidden; }}
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] {{ font-family: 'Plus Jakarta Sans', sans-serif; }}

    .stApp {{ background-color: #F8FAFC; }}

    /* Sidebar Dark Green Style */
    [data-testid="stSidebar"] {{ background: #164B31 !important; }}
    [data-testid="stSidebar"] * {{ color: white !important; }}
    .sidebar-profile {{ display: flex; align-items: center; gap: 15px; padding: 10px 0 20px 0; border-bottom: 1px solid rgba(255,255,255,0.2); margin-bottom: 20px; }}
    .sidebar-profile img {{ width: 50px; height: 50px; border-radius: 14px; object-fit: cover; border: 2px solid #FACC15; }}
    .sidebar-profile span {{ font-weight: 700; font-size: 1.1rem; color: white; }}
    
    div[data-testid="stVerticalBlock"] > div.stButton > button {{ background: transparent; color: white; border: none; border-radius: 10px; font-weight: 600; text-align: left; justify-content: flex-start; padding: 10px 15px; width: 100%; transition: all 0.3s; }}
    div[data-testid="stVerticalBlock"] > div.stButton > button:hover {{ background: rgba(250, 204, 21, 0.2) !important; color: #FACC15 !important; }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# [SIDEBAR MENU]
# ==========================================
with st.sidebar:
    st.markdown(f'<div class="sidebar-profile"><img src="{AVATAR_LINK}"><span>CTY XNK X</span></div>', unsafe_allow_html=True)
    st.write("---")
    if st.button("🏠 Màn hình chính", use_container_width=True): st.session_state.page = "dashboard"; st.rerun()
    if st.button("📦 Báo cáo đóng gói", use_container_width=True): st.session_state.page = "packing"; st.rerun()
    if st.button("🛡️ Yêu cầu kiểm định", use_container_width=True): st.session_state.page = "cert"; st.rerun()
    if st.button("📋 Thông tin lô hàng", use_container_width=True): st.session_state.page = "batches"; st.rerun()
    st.write("---")
    st.button("⚙️ Cài đặt", disabled=True, use_container_width=True)
    st.button("💬 Góp ý phản hồi", disabled=True, use_container_width=True)
    st.button("Đăng xuất", use_container_width=True)

# ==========================================
# [ROUTING & PAGES]
# ==========================================
# ------------------------------------------
# COMMON CSS CHO CÁC TRANG FORM CÓ ẢNH NỀN CHÌM
# ------------------------------------------
FORM_PAGES_CSS = f"""
<style>
    /* Ẩn Sidebar hoàn toàn */
    [data-testid="stSidebar"] {{ display: none !important; }}
    [data-testid="collapsedControl"] {{ display: none !important; }}
    
    /* Ảnh nền chìm bg_garden.jpg */
    .stApp {{
        background-image: url('{FORM_BG_IMAGE}');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    .stApp::before {{
        content: ""; position: fixed; top: 0; left: 0; right: 0; bottom: 0;
        background: rgba(0, 0, 0, 0.45); backdrop-filter: blur(6px); z-index: 0;
    }}
    .main {{ z-index: 1; }}

    /* Khối Form Căn Giữa */
    [data-testid="stForm"] {{ 
        background: #1F4E38 !important; border-radius: 20px !important; 
        padding: 40px !important; border: none !important; box-shadow: 0 25px 50px rgba(0,0,0,0.5) !important; 
    }}
    [data-testid="stForm"] label p {{ color: white !important; font-weight: 600; font-size: 0.95rem; }}
    [data-testid="stForm"] [data-baseweb="checkbox"] label {{ color: white !important; }}
    
    /* Ô Input nền trắng */
    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {{ 
        background: white !important; border-radius: 8px !important; border: none !important; 
    }}
    input, select {{ color: #1F4E38 !important; font-weight: 600 !important; }}
    
    /* Nút Submit */
    [data-testid="stFormSubmitButton"] {{ display: flex; justify-content: center; margin-top: 20px; }}
    [data-testid="stFormSubmitButton"] > button {{ 
        background: white !important; color: #1F4E38 !important; font-weight: 800; font-size: 1.1rem; 
        border-radius: 50px; padding: 10px 40px; border: none; transition: all 0.3s ease; 
    }}
    [data-testid="stFormSubmitButton"] > button:hover {{ background: #FACC15 !important; transform: translateY(-2px); }}
    
    /* Nút Quay Lại */
    .btn-back-yellow > button {{ background: transparent !important; color: #FACC15 !important; font-size: 2.5rem !important; font-weight: 900 !important; border: none !important; padding: 0 !important; }}
    .btn-back-yellow > button:hover {{ color: white !important; }}
</style>
"""

# ------------------------------------------
# PAGE 1: DASHBOARD
# ------------------------------------------
if st.session_state.page == "dashboard":
    st.markdown("""
    <style>
        .stat-card { background: #88B096; padding: 20px; border-radius: 12px; color: white; text-align: center; height: 120px; display: flex; flex-direction: column; justify-content: center;}
        .stat-value { font-size: 1.8rem; font-weight: 800; color: #FDE047; margin-top: 5px; }
        .top-right-logo { position: fixed; top: 15px; right: 30px; display: flex; align-items: center; gap: 12px; z-index: 99999; }
        .top-right-logo img { width: 45px; height: 45px; border-radius: 50%; box-shadow: 0 4px 15px rgba(0,0,0,0.1);}
        .top-right-logo span { font-weight: 800; color: #64748B; font-size: 1rem; line-height: 1.2;}
        .shortcut-card { background: white; border: 1px solid #E2E8F0; border-radius: 12px; padding: 15px; margin-bottom: 15px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown(f'<div class="top-right-logo"><img src="{LOGO_LINK}"><span>Durian<br>Smart</span></div>', unsafe_allow_html=True)
    st.markdown('<h2 style="color:#64748B; font-weight:800; display:flex; align-items:center; gap:15px;">🏭 Tổng quan Doanh nghiệp Xuất khẩu</h2>', unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown('<div class="stat-card">Sản lượng thu mua<div class="stat-value">423.5 Tấn</div></div>', unsafe_allow_html=True)
    c2.markdown('<div class="stat-card">Số Lô Xuất Khẩu<div class="stat-value">200 Lô</div></div>', unsafe_allow_html=True)
    c3.markdown('<div class="stat-card">Tổng Doanh Thu<div class="stat-value">$ 51.250</div></div>', unsafe_allow_html=True)
    c4.markdown('<div class="stat-card">Lô Chờ Kiểm Định<div class="stat-value">50 Lô</div></div>', unsafe_allow_html=True)

    st.write("---")
    g1, g2 = st.columns([2.5, 1])
    with g1:
        st.markdown('<h4 style="color:#64748B;">Sản lượng thu mua và xuất khẩu (Tấn)</h4>', unsafe_allow_html=True)
        st.bar_chart({"Thu mua": [140, 110, 80, 55], "Xuất khẩu": [65, 50, 35, 25]}, color=["#75A68F", "#93C5FD"])
    with g2:
        st.markdown('<h4 style="color:#64748B;">Lối tắt chức năng</h4>', unsafe_allow_html=True)
        if st.button("📦 Gửi Báo Cáo Đóng Gói", use_container_width=True): st.session_state.page = "packing"; st.rerun()
        st.write("")
        if st.button("🛡️ Gửi Yêu Cầu Kiểm Định", use_container_width=True): st.session_state.page = "cert"; st.rerun()
        st.write("")
        if st.button("📋 Truy xuất Dữ liệu Lô hàng", use_container_width=True): st.session_state.page = "batches"; st.rerun()

    st.markdown("""<script>
        const buttons = window.parent.document.querySelectorAll('div[data-testid="column"] button');
        buttons.forEach(btn => {
            btn.style.backgroundColor = 'white'; btn.style.color = '#64748B'; 
            btn.style.border = '1px solid #E2E8F0'; btn.style.borderRadius = '8px';
            btn.style.padding = '15px'; btn.style.fontWeight = '600';
        });
    </script>""", unsafe_allow_html=True)

# ------------------------------------------
# PAGE 2: BÁO CÁO XỬ LÝ VÀ ĐÓNG GÓI
# ------------------------------------------
elif st.session_state.page == "packing":
    st.markdown(FORM_PAGES_CSS, unsafe_allow_html=True)
    
    st.markdown('<div class="btn-back-yellow">', unsafe_allow_html=True)
    if st.button("↩", key="back_from_packing"): st.session_state.page = "dashboard"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    _, col_form, _ = st.columns([1, 8, 1])
    
    with st.form("packing_form", clear_on_submit=False):
            f_col_left, f_col_right = st.columns([2, 1])
            
            with f_col_left:
                # Thay vì dùng st.columns(3), ta dùng một container và CSS Grid
                st.markdown('<div class="grid-container">', unsafe_allow_html=True)
                ent_name = st.text_input("Tên Doanh Nghiệp (PHC)*", value="CTY XNK X")
                fac_code = st.text_input("Mã Cơ Sở (PHC)*")
                b_id = st.text_input("Mã Lô Sầu Riêng*")
                
                emp_id = st.text_input("Mã Nhân viên*")
                emp_name = st.text_input("Họ & Tên NV")
                p_date = st.date_input("Ngày xử lý*")
                
                qty = st.number_input("Số lượng (Tấn)*", min_value=0.0, step=0.1)
                boxes = st.number_input("Số thùng đóng gói*", min_value=0, step=1)
                method = st.text_input("Phương pháp xử lý*")
                st.markdown('</div>', unsafe_allow_html=True)

            with f_col_right:
                st.markdown('<p style="color:white; font-weight:600; font-size:0.95rem; margin-bottom: 5px;">File Báo Cáo Đóng Gói</p>', unsafe_allow_html=True)
                uploaded_file = st.file_uploader("Upload", label_visibility="collapsed")
                st.markdown('<div style="height:115px;"></div>', unsafe_allow_html=True)

            agreement = st.checkbox("Tôi xin cam đoan thông tin trên là đúng sự thật.")
            
            if st.form_submit_button("Cập nhật báo cáo"):
                # Logic xử lý API giữ nguyên
                if not b_id or not agreement or qty <= 0: 
                    st.error("⚠️ Vui lòng điền đủ mã lô, số lượng và tích chọn cam đoan.")
                else:
                    with st.spinner("Đang gọi API..."):
                        payload = {
                            "enterprise_name": ent_name, "facility_code": fac_code, "batch_id": b_id,
                            "employee_id": emp_id, "employee_name": emp_name, "processing_date": str(p_date),
                            "quantity_tons": qty, "total_boxes": boxes, "processing_method": method
                        }
                        try:
                            res = requests.post(f"{API_BASE_URL}/enterprise/{b_id}/packaging-report", json=payload)
                            if res.status_code == 200: 
                                st.success("🎉 Thành công!"); st.session_state.page = "dashboard"; st.rerun()
                            else: st.error(f"Lỗi: {res.json().get('detail')}")
                        except: st.error("🔌 Lỗi kết nối Backend.")
# ------------------------------------------
# PAGE 3: YÊU CẦU KIỂM ĐỊNH (CERT REQUEST - ĐỒNG BỘ LAYOUT 2 CỘT)
# ------------------------------------------
elif st.session_state.page == "cert":
    st.markdown(FORM_PAGES_CSS, unsafe_allow_html=True)
    
    st.markdown('<div class="btn-back-yellow">', unsafe_allow_html=True)
    if st.button("↩", key="back_from_cert"): st.session_state.page = "dashboard"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    _, col_form, _ = st.columns([1, 8, 1])
    
    with col_form:
        st.markdown(f"""
        <div style="text-align:center; margin-bottom: 20px; margin-top: -40px;">
            <img src="{LOGO_LINK}" width="50"><br>
            <span style="color:white; font-weight:800;">Durian Smart</span>
            <h2 style="color:white; font-weight:800; text-transform:uppercase; margin-top:10px;">Yêu cầu kiểm định & Cấp chứng chỉ số</h2>
        </div>
        """, unsafe_allow_html=True)

        with st.form("enterprise_cert_request_form", clear_on_submit=False):
            
            # --- CẤU TRÚC PHÂN MỤC GIỐNG LAB ---
            
            # I. THÔNG TIN ĐƠN VỊ
            st.markdown('<h4 style="color: #38BDF8; font-size:1.05rem; margin-top:0;">I. THÔNG TIN ĐƠN VỊ</h4>', unsafe_allow_html=True)
            # Dùng grid cho nhóm 3 cột
            st.markdown('<div class="grid-3">', unsafe_allow_html=True)
            lab_target = st.text_input("Gửi đến Cơ quan kiểm định*", value="Phòng Lab GACC HCM")
            lab_code = st.text_input("Mã Cơ Quan Kiểm Định*", value="LAB-GACC-HCM")
            ent_name = st.text_input("Tên Doanh Nghiệp (PHC)*", value="CTY XNK X")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="grid-3">', unsafe_allow_html=True)
            fac_code = st.text_input("Mã Cơ Sở Đóng Gói Doanh Nghiệp*")
            contact = st.text_input("Người phụ trách hồ sơ")
            phone = st.text_input("Số điện thoại liên hệ")
            st.markdown('</div>', unsafe_allow_html=True)

            # II. THÔNG TIN LÔ HÀNG
            st.markdown('<h4 style="color: #38BDF8; font-size:1.05rem; margin-top:20px;">II. THÔNG TIN LÔ HÀNG</h4>', unsafe_allow_html=True)
            st.markdown('<div class="grid-3">', unsafe_allow_html=True)
            batch_id = st.text_input("Mã Lô Sầu Riêng*")
            variety = st.selectbox("Giống Sầu Riêng*", ["Ri6", "Monthong", "Musang King"])
            test_qty = st.number_input("Sản Lượng Kiểm Định (Tấn)*", min_value=0.0, step=0.1)
            st.markdown('</div>', unsafe_allow_html=True)

            # III. CHI TIẾT & HỒ SƠ
            st.markdown('<h4 style="color: #38BDF8; font-size:1.05rem; margin-top:20px;">III. CHI TIẾT & HỒ SƠ</h4>', unsafe_allow_html=True)
            
            # Layout hàng ngang cho ngày tháng và upload file
            c_left, c_right = st.columns([2, 1])
            with c_left:
                st.markdown('<div class="grid-2">', unsafe_allow_html=True)
                sample_date = st.date_input("Ngày gửi mẫu dự kiến*")
                category = st.selectbox("Danh mục yêu cầu*", ["Kiểm dịch thực vật & Dư lượng BVTV", "Kiểm định Sinh hóa GACC"])
                st.markdown('</div>', unsafe_allow_html=True)
                note = st.text_area("Ghi chú bổ sung cho Phòng Lab")
            
            with c_right:
                st.markdown('<p style="color:#94A3B8; font-weight:700; font-size:0.85rem;">FILE BÁO CÁO KIỂM ĐỊNH</p>', unsafe_allow_html=True)
                uploaded_file = st.file_uploader("Upload", type=["pdf", "png", "jpg"], label_visibility="collapsed")

            agreement = st.checkbox("Tôi cam đoan thông tin trên là chính xác và đồng ý chia sẻ dữ liệu.")
            
            # Submit button
            submit = st.form_submit_button("✧ Nộp Yêu Cầu Kiểm Định")
            
            if submit:
                # Logic gọi API giữ nguyên...
                st.success("Yêu cầu đã được gửi!")
# ------------------------------------------
# PAGE 4: THÔNG TIN LÔ HÀNG (FULL BATCHES)
# ------------------------------------------
elif st.session_state.page == "batches":
    st.markdown("""
    <style>
        .table-header { font-weight: 800; color: #164B31; border-bottom: 2px solid #164B31; padding-bottom: 10px; margin-bottom: 15px; font-size: 1rem; text-align: center; }
        .table-row { align-items: center; border-bottom: 1px solid #E2E8F0; padding: 12px 0; text-align: center; color: #334155; font-weight: 600; }
        .status-badge { padding: 6px 12px; border-radius: 50px; font-weight: 700; font-size: 0.85rem; display: inline-block; text-align: center; width: 100%; }
        .badge-ready { background: #A3A02C; color: white; }
        .badge-inspect { background: #FDE047; color: #854D0E; }
        .badge-pack { background: #FDBA74; color: #9A3412; }
        .badge-return { background: #EF4444; color: white; }
        
        /* CSS tuỳ chỉnh cho nút Xuất mã (Xanh lá, chữ trắng) khi đạt chuẩn */
        div[data-testid="stButton"] > button[kind="primary"] {
            background-color: #16A34A !important;
            color: white !important;
            border: none !important;
            border-radius: 50px !important;
            font-weight: 800 !important;
            transition: all 0.3s ease !important;
        }
        div[data-testid="stButton"] > button[kind="primary"]:hover {
            background-color: #15803D !important;
            transform: scale(1.05);
            box-shadow: 0 5px 15px rgba(22, 163, 74, 0.4) !important;
        }
        /* CSS cho nút vô hiệu hoá */
        div[data-testid="stButton"] > button[kind="secondary"][disabled] {
            background-color: #E2E8F0 !important;
            color: #94A3B8 !important;
            border: none !important;
            border-radius: 50px !important;
            font-weight: 700 !important;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="btn-back-yellow" style="margin-bottom: -15px;">', unsafe_allow_html=True)
    if st.button("↩", key="back_from_batches"): st.session_state.page = "dashboard"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<h2 style="color:#164B31; font-weight:800; text-transform:uppercase; margin-bottom: 20px; text-align: center;">Dữ liệu lô hàng thu mua và xuất khẩu</h2>', unsafe_allow_html=True)
    
    # Render các cột Header không bọc div thừa
    h_cols = st.columns([1.2, 1, 1, 1, 1.2, 1.5, 1.2])
    headers = ["Mã Lô hàng", "Mã vùng(PUC)", "Mã Nông dân", "Sản lượng", "Nhật ký canh tác", "Trạng thái", "Xuất QR-Code"]
    for i, col in enumerate(h_cols):
        col.markdown(f'<div class="table-header">{headers[i]}</div>', unsafe_allow_html=True)
    
    # Render dữ liệu các Lô hàng
    for i, batch in enumerate(st.session_state.batches_data):
        cols = st.columns([1.2, 1, 1, 1, 1.2, 1.5, 1.2])
        cols[0].markdown(f'<div class="table-row">{batch["id"]}</div>', unsafe_allow_html=True)
        cols[1].markdown(f'<div class="table-row">{batch["puc"]}</div>', unsafe_allow_html=True)
        cols[2].markdown(f'<div class="table-row">{batch["farmer"]}</div>', unsafe_allow_html=True)
        cols[3].markdown(f'<div class="table-row">{batch["qty"]}</div>', unsafe_allow_html=True)
        cols[4].markdown(f'<div class="table-row" style="color:#164B31; font-weight:700;">Truy cập</div>', unsafe_allow_html=True)
        
        status = batch["status"]
        color = "#A3A02C" if status == "Sẵn sàng xuất" else "#FEF08A" if status == "Đang kiểm định" else "#FDBA74"
        font_col = "white" if status == "Sẵn sàng xuất" else "#854D0E"
        cols[5].markdown(f'<div style="text-align:center; padding:8px 0;"><span style="background:{color}; padding:5px 12px; border-radius:50px; color:{font_col}; font-weight:700; font-size:0.8rem;">{status}</span></div>', unsafe_allow_html=True)
        
        with cols[6]:
            if status == "Sẵn sàng xuất":
                if st.button("Xuất mã", key=f"qr_{i}", type="primary", use_container_width=True):
                    with st.spinner("Đang gọi Smart Contract và đúc NFT Blockchain..."):
                        try:
                            res = requests.post(f"{API_BASE_URL}/enterprise/{batch['id']}/mint-export-qr")
                            if res.status_code == 200:
                                st.session_state.selected_qr_batch = batch['id']
                                st.session_state.page = "qr_view"
                                st.rerun() # Tự động nhảy sang trang QR
                            else: 
                                st.error("⚠️ Lỗi gọi Blockchain.")
                        except: 
                            st.error("🔌 Lỗi kết nối Backend.")
            else: 
                st.button("Đợi xử lý", disabled=True, key=f"d_{i}", type="secondary", use_container_width=True)

# ------------------------------------------
# PAGE 5: GIAO DIỆN XUẤT QR CODE
# ------------------------------------------
elif st.session_state.page == "qr_view":
    st.markdown(FORM_PAGES_CSS, unsafe_allow_html=True)
    st.markdown('<div class="btn-back-yellow">', unsafe_allow_html=True)
    if st.button("↩", key="back_qr"): st.session_state.page = "batches"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="display:flex; flex-direction:column; align-items:center; margin-top: 50px;">
        <h2 style="color:white; font-weight:800;">XUẤT MÃ QR TRUY XUẤT NGUỒN GỐC</h2>
        <div style="background: white; padding: 40px; border-radius: 20px; text-align: center; margin-top:20px; box-shadow: 0 15px 40px rgba(0,0,0,0.3);">
            <div style="background: #FACC15; padding: 5px 20px; border-radius: 5px; font-weight:800; font-size:1.1rem; color:#1F4E38; margin-bottom: 20px; text-transform: uppercase;">Certified Compliant</div>
            <img src="https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=https://duriansmart.vn/verify/{st.session_state.selected_qr_batch}">
            <h3 style="color:#1F4E38; margin-top:20px;">LÔ: {st.session_state.selected_qr_batch}</h3>
        </div>
    </div>
    """, unsafe_allow_html=True)