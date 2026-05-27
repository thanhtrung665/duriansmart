# ============================================================
# PATH: frontend/lab_app.py
# DURIAN SMART - CƠ QUAN KIỂM ĐỊNH (HOÀN THIỆN WEB3 & UI CHUẨN)
# ============================================================
import streamlit as st
import base64
import os
import time
import requests

# Địa chỉ Máy chủ Backend FastAPI
API_BASE_URL = "https://durian-smart-backend.onrender.com"

st.set_page_config(page_title="Durian Smart | Lab", page_icon="🔬", layout="wide", initial_sidebar_state="expanded")

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
AVATAR_LINK = get_base64_of_bin_file("frontend/images/coquankiemdinh.jpg") 
FORM_BG_IMAGE = get_base64_of_bin_file("frontend/images/bg_garden.jpg")

# Database Ảo cho Lab (UI State)
if "lab_batches" not in st.session_state:
    st.session_state.lab_batches = [
        {"id": "BATCH-001", "cadimi": "0.02 mg/kg", "vang_o": "Không phát hiện", "thuoc_bvtv": "Đạt chuẩn", "result": "Đạt", "status": "Đã Trả kết quả", "css": "badge-done"},
        {"id": "BATCH-002", "cadimi": "Chờ xét nghiệm", "vang_o": "Chờ xét nghiệm", "thuoc_bvtv": "Chờ xét nghiệm", "result": "Đang xử lý", "status": "Đang kiểm định", "css": "badge-inspect"},
        {"id": "BATCH-003", "cadimi": "Chờ lấy mẫu", "vang_o": "Chờ lấy mẫu", "thuoc_bvtv": "Chờ lấy mẫu", "result": "Chờ xử lý", "status": "Đang giao nhận", "css": "badge-delivery"},
        {"id": "BATCH-004", "cadimi": "0.08 mg/kg", "vang_o": "Phát hiện vết", "thuoc_bvtv": "Vượt ngưỡng", "result": "Không đạt", "status": "Đã kiểm định", "css": "badge-failed"}
    ]

if "page" not in st.session_state: st.session_state.page = "manage"
# State cho khối Web3 Success
if "mint_success" not in st.session_state: st.session_state.mint_success = False
if "minted_data" not in st.session_state: st.session_state.minted_data = {}

# ==========================================
# [GLOBAL CSS - SIDEBAR SÁNG & ĐỒNG BỘ]
# ==========================================
st.markdown(f"""
<style>
    header, [data-testid="stHeader"] {{ visibility: hidden; }}
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] {{ font-family: 'Plus Jakarta Sans', sans-serif; }}

    .stApp {{ background-color: #F8FAFC; }}

    /* Sidebar Light Style - Chữ màu tối nổi bật trên nền trắng */
    [data-testid="stSidebar"] {{ background: #FFFFFF !important; border-right: 1px solid #E2E8F0; }}
    [data-testid="stSidebar"] * {{ color: #1E293B !important; }} 
    .sidebar-profile {{ display: flex; align-items: center; gap: 15px; padding: 10px 0 20px 0; border-bottom: 1px solid #E2E8F0; margin-bottom: 20px; }}
    .sidebar-profile img {{ width: 50px; height: 50px; border-radius: 14px; object-fit: cover; border: 2px solid #38BDF8; }}
    .sidebar-profile span {{ font-weight: 800; font-size: 1.1rem; color: #0F172A !important; }}
    
    div[data-testid="stVerticalBlock"] > div.stButton > button {{ background: transparent; color: #475569 !important; border: none; border-radius: 10px; font-weight: 700; text-align: left; justify-content: flex-start; padding: 10px 15px; width: 100%; transition: all 0.3s; }}
    div[data-testid="stVerticalBlock"] > div.stButton > button:hover {{ background: #EFF6FF !important; color: #0369A1 !important; }}
    
    .top-right-logo {{ position: fixed; top: 15px; right: 30px; display: flex; align-items: center; gap: 12px; z-index: 99999; }}
    .top-right-logo img {{ width: 45px; height: 45px; border-radius: 50%; box-shadow: 0 4px 15px rgba(0,0,0,0.1);}}
    .top-right-logo span {{ font-weight: 800; color: #1E293B; font-size: 1.1rem; line-height: 1.2;}}
</style>
""", unsafe_allow_html=True)

st.markdown(f'<div class="top-right-logo"><img src="{LOGO_LINK}"><span id="logo-text">Durian<br>Smart</span></div>', unsafe_allow_html=True)

# ==========================================
# [SIDEBAR MENU]
# ==========================================
with st.sidebar:
    st.markdown(f'<div class="sidebar-profile"><img src="{AVATAR_LINK}"><span>LAB GACC HCM</span></div>', unsafe_allow_html=True)
    st.write("---")
    if st.button("📊 Dữ liệu mẫu kiểm định", use_container_width=True): 
        st.session_state.page = "manage"
        st.session_state.mint_success = False
        st.rerun()
    if st.button("🛡️ Cấp chứng nhận số", use_container_width=True): 
        st.session_state.page = "cert"
        st.session_state.mint_success = False
        st.rerun()
    if st.button("📋 Báo cáo chi tiết", use_container_width=True): 
        st.session_state.page = "report"
        st.rerun()
    st.write("---")
    st.button("⚙️ Hệ thống LIMS", disabled=True, use_container_width=True)
    st.button("Đăng xuất", use_container_width=True)

# ==========================================
# [ROUTING & PAGES]
# ==========================================

# ------------------------------------------
# PAGE 1: DỮ LIỆU MẪU KIỂM ĐỊNH SINH HÓA
# ------------------------------------------
if st.session_state.page == "manage":
    st.markdown("""
    <style>
        .page-title { color: #0F172A; font-weight: 900; font-size: 2.2rem; text-transform: uppercase; margin-bottom: 30px; letter-spacing: -0.5px;}
        .table-header { font-weight: 800; color: #1E293B; border-bottom: 2px solid #0F172A; padding-bottom: 12px; margin-bottom: 15px; font-size: 0.95rem; text-align: center; text-transform: uppercase;}
        .table-row { align-items: center; border-bottom: 1px solid #F1F5F9; padding: 18px 0; text-align: center; color: #475569; font-weight: 600; font-size: 0.95rem;}
        
        .res-pass { color: #16A34A; font-weight: 800; }
        .res-fail { color: #DC2626; font-weight: 800; }
        .res-wait { color: #94A3B8; font-style: italic; }
        
        .status-badge { padding: 8px 15px; border-radius: 50px; font-weight: 700; font-size: 0.85rem; display: inline-block; text-align: center; width: 90%; border: 1px solid transparent;}
        .badge-done { background: #DCFCE7; color: #166534; border-color: #BBF7D0;}
        .badge-inspect { background: #FEF08A; color: #854D0E; border-color: #FDE047;}
        .badge-delivery { background: #E0F2FE; color: #0369A1; border-color: #BAE6FD;}
        .badge-failed { background: #E9D5FF; color: #5B21B6; border-color: #D8B4FE;}
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="page-title">Dữ liệu mẫu kiểm định sinh hóa</div>', unsafe_allow_html=True)
    
    # Không dùng thẻ div trắng thừa thãi, render trực tiếp columns
    h_cols = st.columns([1, 1.2, 1.2, 1.2, 1, 1.5])
    headers = ["Mã Lô", "Độc tố Cadimi", "Chất Vàng O", "Dư lượng BVTV", "Kết quả", "Trạng thái"]
    for i, col in enumerate(h_cols):
        col.markdown(f'<div class="table-header">{headers[i]}</div>', unsafe_allow_html=True)
    
    for batch in st.session_state.lab_batches:
        cols = st.columns([1, 1.2, 1.2, 1.2, 1, 1.5])
        cols[0].markdown(f'<div class="table-row" style="color:#0F172A; font-weight:800;">{batch["id"]}</div>', unsafe_allow_html=True)
        cols[1].markdown(f'<div class="table-row">{batch["cadimi"]}</div>', unsafe_allow_html=True)
        cols[2].markdown(f'<div class="table-row">{batch["vang_o"]}</div>', unsafe_allow_html=True)
        cols[3].markdown(f'<div class="table-row">{batch["thuoc_bvtv"]}</div>', unsafe_allow_html=True)
        
        # Format kết quả
        res = batch["result"]
        res_css = "res-pass" if res == "Đạt" else "res-fail" if res == "Không đạt" else "res-wait"
        cols[4].markdown(f'<div class="table-row {res_css}">{res}</div>', unsafe_allow_html=True)
        
        # Format trạng thái
        cols[5].markdown(f'<div style="text-align:center; padding: 12px 0;"><span class="status-badge {batch.get("css", "badge-delivery")}">{batch["status"]}</span></div>', unsafe_allow_html=True)

# ------------------------------------------
# PAGE 2: CẤP CHỨNG NHẬN SỐ (WEB3 DARK MODE STYLE)
# ------------------------------------------
elif st.session_state.page == "cert":
    st.markdown(f"""
    <style>
        /* Ẩn Sidebar */
        [data-testid="stSidebar"], [data-testid="collapsedControl"] {{ display: none !important; }}
        
        /* Cấu hình ảnh nền chìm & Dark Overlay */
        .stApp {{ background-image: url('{FORM_BG_IMAGE}'); background-size: cover; background-position: center; background-attachment: fixed; }}
        .stApp::before {{ content: ""; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(15, 23, 42, 0.8); backdrop-filter: blur(8px); z-index: 0; }}
        .main {{ z-index: 1; }}

        /* Cấu hình khối Form Web3 */
        [data-testid="stForm"] {{ background: #0B1120 !important; border-radius: 16px !important; padding: 40px !important; border: 1px solid #1E293B !important; box-shadow: 0 25px 50px rgba(0,0,0,0.8) !important; }}
        [data-testid="stForm"] label p {{ color: #94A3B8 !important; font-weight: 700; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; }}
        [data-testid="stForm"] [data-baseweb="checkbox"] label {{ color: #38BDF8 !important; font-style: italic; }}
        
        /* Input Dark Mode */
        div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {{ background: #1E293B !important; border-radius: 8px !important; border: 1px solid #334155 !important; }}
        input, select {{ color: white !important; font-weight: 600 !important; font-family: monospace; }}
        
        /* Nút Submit */
        [data-testid="stFormSubmitButton"] {{ display: flex; justify-content: center; margin-top: 30px; }}
        [data-testid="stFormSubmitButton"] > button {{ background: #2563EB !important; color: white !important; font-weight: 800; font-size: 1.1rem; border-radius: 8px; padding: 12px 60px; border: none; transition: all 0.3s ease; width: 100%; max-width: 400px;}}
        [data-testid="stFormSubmitButton"] > button:hover {{ background: #1D4ED8 !important; transform: translateY(-2px); box-shadow: 0 10px 20px rgba(37, 99, 235, 0.4); }}
        
        /* Nút Quay Lại */
        .btn-back-yellow > button {{ background: transparent !important; color: #38BDF8 !important; font-size: 2.5rem !important; font-weight: 900 !important; border: none !important; padding: 0 !important; }}
        .btn-back-yellow > button:hover {{ color: white !important; }}

        /* KHỐI THÀNH CÔNG WEB3 */
        .web3-success-box {{ background-color: #064E3B; border: 1px solid #10B981; border-radius: 12px; padding: 25px; margin-top: 25px; animation: fadeIn 0.5s; }}
        .web3-success-header {{ color: #34D399; font-weight: 800; text-align: center; margin-bottom: 20px; font-size: 1.1rem; display: flex; justify-content: center; align-items: center; gap: 10px; }}
        .web3-row {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(16, 185, 129, 0.2); padding: 15px 0; font-family: monospace; color: #A7F3D0; font-size: 0.9rem; }}
        .web3-label {{ color: #6EE7B7; font-weight: bold; letter-spacing: 1px; }}
        .web3-hash {{ word-break: break-all; text-align: right; max-width: 70%; }}
        .web3-footer {{ text-align: center; color: #6EE7B7; font-size: 0.8rem; margin-top: 15px; font-style: italic; opacity: 0.8; }}
        @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(-10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="btn-back-yellow">', unsafe_allow_html=True)
    if st.button("↩", key="back_from_lab"): 
        st.session_state.page = "manage"
        st.session_state.mint_success = False
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Căn giữa Form
    _, col_form, _ = st.columns([1.5, 6, 1.5])
    
    with col_form:
        st.markdown(f"""
        <div style="text-align:center; margin-bottom: 30px; margin-top: -30px;">
            <div style="display:inline-flex; align-items:center; justify-content:center; width:60px; height:60px; background: rgba(56, 189, 248, 0.1); border-radius: 50%; margin-bottom:15px; border: 1px solid rgba(56,189,248,0.3);">
                <span style="font-size: 1.8rem; color: #38BDF8;">⬡</span>
            </div>
            <h2 style="color:white; font-weight:800; text-transform:uppercase; margin:0; letter-spacing: 2px;">Cấp Chứng Chỉ Mới</h2>
            <p style="color:#94A3B8; margin-top:5px; font-size: 0.95rem;">Tạo và lưu chứng nhận kiểm định sinh hóa bất biến trên Cardano Blockchain.</p>
        </div>
        """, unsafe_allow_html=True)

        with st.form("lab_cert_form", clear_on_submit=False):
            r1c1, r1c2 = st.columns(2)
            with r1c1: batch_id = st.text_input("Mã Lô Sầu Riêng*")
            with r1c2: test_date_input = st.date_input("Ngày phân tích*")

            r2c1, r2c2, r2c3 = st.columns(3)
            with r2c1: val_cadimi = st.text_input("Độc tố Cadimi (mg/kg)*", placeholder="VD: 0.02")
            with r2c2: val_vango = st.selectbox("Xét nghiệm Vàng O*", ["Không phát hiện", "Phát hiện vết", "Vượt ngưỡng"])
            with r2c3: val_bvtv = st.selectbox("Dư lượng thuốc BVTV*", ["Đạt chuẩn (< 0.01%)", "Vượt ngưỡng an toàn"])

            final_result = st.selectbox("KẾT LUẬN CHUNG*", ["Đạt", "Không đạt"])
            
            # Khung Note Web3
            st.markdown("""
            <div style="background: #1E293B; border-radius: 8px; border: 1px solid #334155; padding: 15px; margin-top: 15px; margin-bottom: 20px;">
                <p style="color: #64748B; font-family: monospace; font-size: 0.85rem; margin:0; line-height: 1.5;">
                    // Nội dung chứng chỉ, JSON metadata của GACC, và các chỉ số sinh hóa sẽ được tự động đóng gói.<br>
                    // Dữ liệu sẽ được hash tự động trước khi ký điện tử và đúc NFT On-chain...
                </p>
            </div>
            """, unsafe_allow_html=True)

            agreement = st.checkbox("Tôi đồng ý cấp chứng nhận và kích hoạt Smart Contract.")
            
            if st.form_submit_button("✧ Phát hành Chứng Chỉ"):
                if not batch_id or not agreement:
                    st.error("⚠️ Vui lòng điền đủ Mã lô và xác nhận cấp chứng nhận.")
                else:
                    with st.spinner("Đang kết nối Cardano Node... Xử lý giao dịch..."):
                        payload = {
                            "batch_id": batch_id,
                            "test_date": str(test_date_input),
                            "technician_id": "TECH-SYSTEM",
                            "cadimi_level": val_cadimi if val_cadimi else "0.01",
                            "vang_o_result": val_vango,
                            "bvtv_result": val_bvtv,
                            "final_result": final_result
                        }
                        
                        try:
                            # Tích hợp gọi API
                            response = requests.post(f"{API_BASE_URL}/lab/{batch_id}/certificate", json=payload)
                            if response.status_code == 200:
                                data = response.json()
                                # Kích hoạt State để hiện khối thông báo xanh
                                st.session_state.mint_success = True
                                st.session_state.minted_data = {
                                    "batch": batch_id,
                                    "hash": data.get("lab_hash", f"0x{os.urandom(32).hex()}")
                                }
                                
                                # Cập nhật danh sách lô hàng trên UI
                                found = False
                                for b in st.session_state.lab_batches:
                                    if b["id"] == batch_id:
                                        b["cadimi"] = (val_cadimi + " mg/kg") if val_cadimi else "0.01 mg/kg"
                                        b["vang_o"] = val_vango
                                        b["thuoc_bvtv"] = val_bvtv
                                        b["result"] = "Đạt" if "Đạt" in final_result and "Không" not in final_result else "Không đạt"
                                        b["status"] = "Đã Trả kết quả"
                                        b["css"] = "badge-done"
                                        found = True
                                        
                                if not found:
                                    st.toast("✅ Đã ghi nhận thành công dưới Database, dù không có sẵn trong danh sách hiển thị.")
                            else:
                                st.error(f"⚠️ Lỗi từ hệ thống: {response.json().get('detail', 'Lỗi không xác định')}")
                        except requests.exceptions.ConnectionError:
                            st.error("🔌 Không thể kết nối đến Máy chủ Backend. Vui lòng kiểm tra Uvicorn!")

        # HIỂN THỊ KHỐI THÀNH CÔNG KIỂU WEB3 NẾU ĐÃ MINT
        if st.session_state.mint_success:
            st.markdown(f"""
            <div class="web3-success-box">
                <div class="web3-success-header">✓ Chứng chỉ đã được ghi lên Blockchain</div>
                <div class="web3-row">
                    <span class="web3-label">CREDENTIAL ID</span>
                    <span class="web3-hash">{st.session_state.minted_data.get('batch')}</span>
                </div>
                <div class="web3-row">
                    <span class="web3-label">HASH</span>
                    <span class="web3-hash">{st.session_state.minted_data.get('hash')}</span>
                </div>
                <div class="web3-footer">Lưu lại Credential ID để xác thực sau này.</div>
            </div>
            """, unsafe_allow_html=True)

# ------------------------------------------
# PAGE 3: BÁO CÁO CHI TIẾT
# ------------------------------------------
elif st.session_state.page == "report":
    st.title("📋 Báo cáo kiểm định chi tiết")
    st.info("Khu vực truy xuất hồ sơ PDF và biểu đồ phân tích thành phần hóa học của từng lô hàng theo thời gian thực.")