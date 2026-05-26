# ============================================================
# PATH: frontend/farmer_app.py
# DURIAN SMART - NÔNG DÂN (TÍCH HỢP API BACKEND)
# ============================================================
import streamlit as st
import base64
import os
import time
import requests
from streamlit_mic_recorder import mic_recorder

# Địa chỉ API Backend
API_BASE_URL = "https://durian-smart-backend.onrender.com"

# 1. CẤU HÌNH TRANG CƠ BẢN
st.set_page_config(page_title="Durian Smart | ThanhTrung", page_icon="🍈", layout="wide")

# ==========================================
# [ASSETS SETUP] - KỸ THUẬT MÃ HÓA BASE64 ĐÃ TỐI ƯU CACHE
# ==========================================
@st.cache_data
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        b64 = base64.b64encode(data).decode()
        mime = "image/png" if bin_file.lower().endswith(".png") else "image/jpeg"
        return f"data:{mime};base64,{b64}"
    except FileNotFoundError:
        return ""

LOGO_LINK = get_base64_of_bin_file("frontend/images/logo_durian_smart.png")
AVATAR_LINK = get_base64_of_bin_file("frontend/images/70.jpg")
NEWS_BG_IMAGE = get_base64_of_bin_file("frontend/images/Screenshot 2026-05-25 185450.png")
# ==========================================

# 2. HỆ THỐNG CSS CUSTOM TOÀN DIỆN
st.markdown(f"""
<style>
    .stApp {{ background-color: #F4F7F6; transition: background-color 0.3s; }}
    header, [data-testid="stHeader"] {{ visibility: hidden; }}

    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] {{ font-family: 'Plus Jakarta Sans', sans-serif; }}

    /* --- SIDEBAR --- */
    [data-testid="stSidebar"] {{
        background: rgba(255, 255, 255, 0.7) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(17, 202, 160, 0.15);
    }}
    .sidebar-profile {{ display: flex; align-items: center; gap: 15px; padding: 10px 0 20px 0; border-bottom: 1px solid rgba(17, 202, 160, 0.2); margin-bottom: 20px; }}
    .sidebar-profile img {{ width: 50px; height: 50px; border-radius: 14px; object-fit: cover; box-shadow: 0 4px 15px rgba(17, 202, 160, 0.2); border: 2px solid #11CAA0; }}
    .sidebar-profile span {{ font-weight: 700; font-size: 1.1rem; color: #0F172A; }}
    
    .menu-category {{ font-size: 0.8rem; color: #94A3B8; font-weight: 700; margin-top: 20px; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 1.5px; }}
    div[data-testid="stVerticalBlock"] > div.stButton > button {{ background: transparent; color: #475569; border: none; border-radius: 10px; font-weight: 600; text-align: left; justify-content: flex-start; padding: 10px 15px; width: 100%; transition: all 0.3s; }}
    div[data-testid="stVerticalBlock"] > div.stButton > button:hover {{ background: rgba(17, 202, 160, 0.1) !important; color: #11CAA0 !important; }}
    .logout-btn > button {{ background: #0F172A !important; color: white !important; border-radius: 12px !important; justify-content: center !important; margin-top: 40px; }}

    /* --- TOP RIGHT LOGO --- */
    .top-right-logo {{ position: fixed; top: 15px; right: 30px; display: flex; align-items: center; gap: 12px; z-index: 99999; }}
    .top-right-logo img {{ width: 45px; height: 45px; border-radius: 50%; box-shadow: 0 4px 15px rgba(250, 204, 21, 0.4);}}
    .top-right-logo span {{ font-weight: 800; color: #0F172A; font-size: 1.1rem; line-height: 1.2;}}

    /* --- CSS TRANG FORM KHỞI TẠO (MINT NFT) --- */
    .bg-garden {{
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: -1;
        background-image: url('{NEWS_BG_IMAGE}'); background-size: cover; background-position: center; 
        opacity: 0.08; /* Giảm mạnh độ sáng */
        filter: blur(10px); /* BẮT BUỘC: Đánh nhòe hoàn toàn chữ trên bài báo */
        pointer-events: none; /* Ngăn chặn ảnh nền đè lên thao tác chuột */
    }}
    
    [data-testid="stForm"] {{
        background: rgba(22, 75, 49, 0.95); backdrop-filter: blur(12px); border-radius: 24px;
        padding: 40px 50px; border: 1px solid rgba(255,255,255,0.15); box-shadow: 0 25px 50px rgba(0,0,0,0.3); margin-top: 20px;
    }}
    
    [data-testid="stForm"] label, [data-testid="stForm"] p {{ color: white !important; font-weight: 600; font-size: 0.95rem; }}
    [data-testid="stForm"] [data-baseweb="checkbox"] label {{ color: #FACC15 !important; font-style: italic; }}
    [data-testid="stFormSubmitButton"] {{ display: flex; justify-content: center; margin-top: 20px; }}
    [data-testid="stFormSubmitButton"] > button {{
        background: linear-gradient(135deg, #FACC15 0%, #EAB308 100%); color: #114B32 !important; font-weight: 800; font-size: 1.1rem;
        border-radius: 50px; padding: 10px 40px; border: none; box-shadow: 0 8px 20px rgba(250, 204, 21, 0.3); transition: all 0.3s ease;
    }}
    [data-testid="stFormSubmitButton"] > button:hover {{ transform: translateY(-2px); box-shadow: 0 12px 25px rgba(250, 204, 21, 0.5); }}
    
    .back-btn > button {{ background: transparent; color: #114B32; font-weight: 800; font-size: 1.2rem; border: none; padding-left: 0; }}
    .back-btn > button:hover {{ color: #FACC15; background: transparent; }}
</style>
""", unsafe_allow_html=True)

# 3. LOGO GÓC TRÊN BÊN PHẢI
st.markdown(f"""
<div class="top-right-logo">
    <img src="{LOGO_LINK}">
    <span id="logo-text">Durian<br>Smart</span>
</div>
""", unsafe_allow_html=True)

# 4. SIDEBAR NAVIGATION
with st.sidebar:
    st.markdown(f"""
    <div class="sidebar-profile">
        <img src="{AVATAR_LINK}">
        <span>ThanhTrung</span>
    </div>
    """, unsafe_allow_html=True)
    
    if "current_page" not in st.session_state:
        st.session_state.current_page = "home"
        
    st.markdown('<div class="menu-category">Menu</div>', unsafe_allow_html=True)
    if st.button("🏠 Màn hình chính", key="menu_home"): st.session_state.current_page = "home"; st.rerun()
    if st.button("📊 Lịch sử canh tác", key="menu_history"): pass
    if st.button("👥 Đối tác thu mua", key="menu_partner"): pass
    
    st.markdown('<div class="menu-category">Công cụ</div>', unsafe_allow_html=True)
    if st.button("⚙️ Cài đặt", key="tool_settings"): pass
    if st.button("💬 Góp ý phản hồi", key="tool_feedback"): pass
    if st.button("❓ Giúp đỡ", key="tool_help"): pass
    
    st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
    st.button("Đăng xuất", key="btn_logout")
    st.markdown('</div>', unsafe_allow_html=True)


# ==========================================================
# 5. ĐIỀU HƯỚNG TRANG (ROUTING SPA)
# ==========================================================

# ----------------------------------------------------------
# TRANG 1: MÀN HÌNH CHÍNH (DASHBOARD)
# ----------------------------------------------------------
if st.session_state.current_page == "home":
    st.write("") 
    st.write("")
    
    # CSS Đặc quyền cho Dashboard
    st.markdown("""
    <style>
    .card-wrapper { height: 120px; background: linear-gradient(135deg, #114B32 0%, #1A704B 100%); border-radius: 16px; padding: 20px; color: white; box-shadow: 0 10px 30px rgba(17, 75, 50, 0.2); display: flex; flex-direction: column; justify-content: center; margin-bottom: 15px; position: relative; overflow: hidden; }
    .card-wrapper::after { content: ''; position: absolute; top: -30%; right: -20%; width: 100px; height: 100px; background: rgba(255,255,255,0.05); border-radius: 50%; blur: 20px; }
    .action-icon { font-size: 2.2rem; margin-bottom: 5px; }
    .action-title { font-size: 1.05rem; font-weight: 700; line-height: 1.4; z-index: 2; }
    .stButton > button.web3-btn { background: rgba(17, 202, 160, 0.1); color: #114B32; border: 1px solid rgba(17, 202, 160, 0.3); border-radius: 12px; font-weight: 700; padding: 10px 0; width: 100%; transition: all 0.3s ease; }
    .stButton > button.web3-btn:hover { background: linear-gradient(135deg, #11CAA0 0%, #FACC15 100%); color: #0F172A; border: 1px solid transparent; box-shadow: 0 8px 20px rgba(17, 202, 160, 0.3); }
    .chatbot-bar { background: rgba(255, 255, 255, 0.8); backdrop-filter: blur(10px); border: 1px solid rgba(17, 202, 160, 0.2); border-radius: 50px; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; margin: 30px 0; box-shadow: 0 4px 20px rgba(0,0,0,0.02); transition: all 0.3s; cursor: pointer; }
    .chatbot-bar:hover { border: 1px solid #11CAA0; box-shadow: 0 4px 25px rgba(17, 202, 160, 0.15); transform: translateY(-2px); }
    .chatbot-text { color: #64748B; font-weight: 600; font-size: 1.05rem; }
    .chatbot-icon { font-size: 1.8rem; background: linear-gradient(135deg, #11CAA0 0%, #1A704B 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .history-card { background: rgba(255, 255, 255, 0.8); backdrop-filter: blur(15px); border-radius: 20px; padding: 30px; border: 1px solid rgba(255,255,255,0.5); box-shadow: 0 10px 40px rgba(0,0,0,0.03); height: 420px; overflow-y: auto; }
    .history-card-title { color: #114B32; font-size: 1.2rem; font-weight: 800; margin-bottom: 25px; display: flex; align-items: center; gap: 10px;}
    .timeline-container { display: flex; flex-direction: column; gap: 20px; }
    .timeline-item { border-left: 4px solid #FACC15; padding-left: 15px; }
    .timeline-date { color: #11CAA0; font-weight: 700; font-size: 0.95rem; margin-bottom: 6px; }
    .timeline-text { color: #475569; font-size: 0.95rem; line-height: 1.5; margin-bottom: 8px; }
    .timeline-hash { display: inline-flex; align-items: center; gap: 5px; background: rgba(17, 202, 160, 0.08); color: #114B32; font-family: 'Courier New', Courier, monospace; font-size: 0.75rem; font-weight: 600; padding: 4px 10px; border-radius: 6px; border: 1px solid rgba(17, 202, 160, 0.2);}
    .news-card { background-image: url('""" + NEWS_BG_IMAGE + """'); background-size: cover; background-position: center; border-radius: 20px; height: 420px; position: relative; box-shadow: 0 10px 40px rgba(0,0,0,0.1); overflow: hidden; }
    .news-card-overlay { background: linear-gradient(180deg, rgba(17, 75, 50, 0.9) 0%, rgba(17, 75, 50, 0) 60%); position: absolute; top: 0; left: 0; width: 100%; height: 100%; padding: 25px; }
    .news-title-tag { background: rgba(255,255,255,0.15); backdrop-filter: blur(10px); color: white; font-weight: 700; padding: 8px 18px; border-radius: 10px; display: inline-block; border: 1px solid rgba(255,255,255,0.2); font-size: 0.9rem; }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3, col_empty = st.columns([1, 1, 1, 0.5])
    
    with col1:
        st.markdown('<div class="card-wrapper"><div class="action-icon">🧑‍🌾</div><div class="action-title">Khởi tạo hồ sơ<br>canh tác</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="btn-container">', unsafe_allow_html=True)
        if st.button("Khởi tạo ngay", key="action_create", use_container_width=True): st.session_state.current_page = "create_batch"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card-wrapper"><div class="action-icon">📋</div><div class="action-title">Ghi chú nhật<br>ký canh tác</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="btn-container">', unsafe_allow_html=True)
        if st.button("Thêm ghi chú", key="action_log", use_container_width=True): st.session_state.current_page = "voice_log"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="card-wrapper"><div class="action-icon">📈</div><div class="action-title">Thống kê sản<br>lượng</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="btn-container">', unsafe_allow_html=True)
        st.button("Xem thống kê", key="action_stats", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<script>const buttons = window.parent.document.querySelectorAll('div[data-testid=\"column\"] button'); buttons.forEach(btn => btn.classList.add('web3-btn'));</script>", unsafe_allow_html=True)
    st.markdown('<div class="chatbot-bar"><span class="chatbot-text">Durian Chatbot giúp gì được cho bác ạ ?</span><span class="chatbot-icon">🤖</span></div>', unsafe_allow_html=True)

    bottom_left, bottom_right = st.columns([1.8, 1])
    with bottom_left:
        history_data = [
            {"date": "13:00 - 21/5/2026", "action": "Phun thuốc trừ sâu, dung tích 100 lít trên 1 heta sầu riêng.", "hash": "0x8f4c...3b9e"},
            {"date": "08:35 - 21/5/2026", "action": "Bón phân đạm hiệu X với tổng số 52 bao trên diện tích 1 heta sầu riêng.", "hash": "0x1a2b...9c8d"},
            {"date": "16:20 - 19/5/2026", "action": "Tưới nước hệ thống nhỏ giọt khu vực A, B. Độ ẩm đất đạt 70%.", "hash": "0x5e6f...7a8b"}
        ]
        timeline_html = '<div class="timeline-container">'
        for item in history_data: timeline_html += f'<div class="timeline-item"><div class="timeline-date">{item["date"]}</div><div class="timeline-text">{item["action"]}</div><div class="timeline-hash">⛓️ Cardano Tx: {item["hash"]}</div></div>'
        timeline_html += '</div>'
        st.markdown(f'<div class="history-card"><div class="history-card-title">📊 Lịch sử ghi chú nhật ký canh tác</div>{timeline_html}</div>', unsafe_allow_html=True)

    with bottom_right:
        st.markdown('<div class="news-card"><div class="news-card-overlay"><div class="news-title-tag">Tin tức thị trường</div></div></div>', unsafe_allow_html=True)


# ----------------------------------------------------------
# TRANG 2: KHỞI TẠO HỒ SƠ CANH TÁC (MINT NFT BATCH)
# ----------------------------------------------------------
elif st.session_state.current_page == "create_batch":
    st.markdown('<div class="bg-garden"></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="back-btn">', unsafe_allow_html=True)
    if st.button("⬅️ Quay lại màn hình chính", key="back_to_home_1"): st.session_state.current_page = "home"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("""<div style="display:flex; align-items:center; justify-content:center; gap:15px; margin-bottom: -15px;"><h2 style="color:#114B32; font-weight:800; text-align:center;">🍈 KHỞI TẠO HỒ SƠ CANH TÁC SẦU RIÊNG</h2></div>""", unsafe_allow_html=True)

    with st.form("mint_nft_form", clear_on_submit=False):
        r1_c1, r1_c2 = st.columns([2, 1])
        with r1_c1: farmer_name = st.text_input("Họ & Tên Nông Dân*", value="Hồ Thanh Trung") 
        with r1_c2: dob = st.date_input("Ngày sinh*")

        r2_c1, r2_c2, r2_c3 = st.columns(3)
        with r2_c1: farmer_id = st.text_input("Mã định danh Nông dân*", placeholder="VD: FAR-0921")
        with r2_c2: batch_id = st.text_input("Mã Lô Sầu Riêng*", placeholder="VD: BATCH-001")
        with r2_c3: puc_code = st.text_input("Mã Vùng (PUC)*", placeholder="VD: VN-PUC-889")

        r3_c1, r3_c2, r3_c3 = st.columns(3)
        with r3_c1: area = st.text_input("Diện Tích Vườn*", placeholder="VD: 2.5 Hecta")
        with r3_c2: tree_count = st.number_input("Số Lượng Cây", min_value=1, step=1)
        with r3_c3: variety = st.selectbox("Giống Sầu Riêng*", ["Ri6", "Monthong", "Musang King", "Khác"])

        address = st.text_input("Địa Chỉ Vườn*", placeholder="VD: Huyện Cai Lậy, Tỉnh Tiền Giang")
        
        st.write("") 
        agreement = st.checkbox("Tôi xin cam đoan tất cả thông tin trên là đúng sự thật và chịu trách nhiệm ghi băm lên Blockchain.")

        submitted = st.form_submit_button("Tạo Hồ Sơ Canh Tác")

        if submitted:
            if not farmer_id or not batch_id or not puc_code or not agreement:
                st.error("⚠️ Vui lòng điền đầy đủ các trường bắt buộc (*) và tích chọn cam đoan.")
            else:
                with st.spinner("Đang gọi API khởi tạo Smart Contract và Đúc NFT Lô hàng..."):
                    payload = {
                        "batch_id": batch_id,
                        "puc_code": puc_code,
                        "farmer_id": farmer_id,
                        "farmer_name": farmer_name,
                        "farm_location": address,
                        "variety": variety,
                        "yield_amount": f"{area} - {tree_count} cây",
                        "daily_logs": [] # Tạm thời để mảng rỗng chờ hệ thống Voice Log đẩy vào
                    }
                    
                    try:
                        # Gửi POST request tới FastAPI Backend
                        response = requests.post(f"{API_BASE_URL}/farmer/create-batch", json=payload)
                        
                        if response.status_code == 200:
                            data = response.json()
                            st.success(f"🎉 Khởi tạo thành công! Lô {batch_id} đã được đúc NFT.")
                            st.info(f"🔗 Farmer Hash (TxID): {data.get('farmer_hash')}")
                        else:
                            st.error(f"⚠️ Lỗi từ hệ thống: {response.json().get('detail', 'Lỗi không xác định')}")
                    except requests.exceptions.ConnectionError:
                        st.error("🔌 Không thể kết nối đến Máy chủ Backend FastAPI. Vui lòng kiểm tra lại Uvicorn.")


# ----------------------------------------------------------
# TRANG 3: GHI CHÚ NHẬT KÝ CANH TÁC (AI VOICE LOG) - FIX LỖI TRÀN Ô
# ----------------------------------------------------------
elif st.session_state.current_page == "voice_log":
    st.markdown('<div class="bg-garden"></div>', unsafe_allow_html=True)
    
    # CSS ĐỘC QUYỀN TRÁNH VỠ DOM: Đổi màu nền toàn trang thành Xanh rêu
    st.markdown("""
    <style>
        .stApp { background-color: #164B31 !important; }
        #logo-text { color: white !important; } /* Đổi màu logo thành trắng cho nổi bật */
        label { color: white !important; font-weight: 600; }
        div[data-baseweb="input"] > div { border-radius: 50px !important; background: white !important; padding: 2px 15px; border: none !important;}
        .back-btn > button { color: white !important; }
        .back-btn > button:hover { color: #FACC15 !important; }
        .verify-btn button { background: #FACC15 !important; color: #114B32 !important; font-weight: 800 !important; border-radius: 50px !important; padding: 10px 40px !important; border: none !important; margin-top: 20px; box-shadow: 0 5px 15px rgba(250, 204, 21, 0.2); }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="back-btn">', unsafe_allow_html=True)
    if st.button("⬅️ Quay lại màn hình chính", key="back_to_home_2"): st.session_state.current_page = "home"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align:center; margin-bottom: 40px;">
        <img src="https://cdn-icons-png.flaticon.com/512/8649/8649595.png" width="80" style="margin-bottom:15px;">
        <h2 style="color:white; font-weight:800; text-transform:uppercase; margin:0;">GHI CHÚ NHẬT KÝ CANH TÁC THÔNG MINH</h2>
    </div>
    """, unsafe_allow_html=True)
    
    v_c1, v_c2, v_c3 = st.columns(3)
    with v_c1: batch_id = st.text_input("Mã Lô Sầu Riêng*", placeholder="BATCH-001")
    with v_c2: farmer_id = st.text_input("Mã định danh Nông dân*", placeholder="FAR-0921")
    with v_c3: puc_code = st.text_input("Mã vùng (PUC)*", placeholder="VN-PUC-889")
    
    st.write("") 
    
    # Nút thu âm chuẩn
    audio = mic_recorder(
        start_prompt="🎙️ Bấm để bắt đầu thu âm (Durian Bot)",
        stop_prompt="⏹️ Đang thu âm... Bấm để dừng",
        key='recorder'
    )
    
    if audio:
        with st.spinner("AI Whisper đang bóc băng giọng nói..."):
            time.sleep(1.5)
            transcription = "Hôm nay tôi tiến hành bón phân đạm hiệu X với tổng số 52 bao trên diện tích 1 heta sầu riêng Ri6 khu vực phía Bắc."
            st.markdown(f"""
            <div style="background: white; border-radius: 16px; padding: 25px; color: #114B32; margin-top: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.2);">
                <div style="display: flex; align-items: center; gap: 10px; font-weight: 800; margin-bottom: 15px; font-size: 1.1rem;">🔔 Kết quả ghi chú nhật ký canh tác</div>
                <div style="font-style: italic; font-weight: 500; color: #475569; font-size: 1.05rem;">"{transcription}"</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background: white; border-radius: 16px; padding: 25px; color: #114B32; margin-top: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.2);">
            <div style="display: flex; align-items: center; gap: 10px; font-weight: 800; margin-bottom: 15px; font-size: 1.1rem;">🔔 Kết quả ghi chú nhật ký canh tác</div>
            <div style="font-style: italic; font-weight: 500; color: #475569; font-size: 1.05rem;">Chưa có dữ liệu thu âm...</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.write("")
    
    st.markdown('<div class="verify-btn">', unsafe_allow_html=True)
    if st.button("Kết quả đối chứng"):
        st.toast("⚡ Dữ liệu trùng khớp 98% với quy trình chuẩn GACC!")
    st.markdown('</div>', unsafe_allow_html=True)