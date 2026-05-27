# ============================================================
# PATH: frontend/verify_app.py
# DURIAN SMART - FULL VERIFICATION MODULE
# ============================================================
import streamlit as st
import os

st.set_page_config(page_title="Durian Smart | Xác thực Lô hàng", page_icon="🔍", layout="centered")

# --- MOCK DATABASE (Dữ liệu đầy đủ) ---
MOCK_DATABASE = {
    "BATCH-001": {
        "image_path": "frontend/images/durian.jpg", 
        "farmer": {
            "name": "Nguyễn Văn A", 
            "code": "F-ND-001",
            "address": "Xã Ea Knuếc, Krông Pắk, Đắk Lắk", 
            "variety": "Ri6",
            "diary": "Lịch bón phân hữu cơ: 15/03/2026. Tưới: Hệ thống tự động hàng ngày.",
            "date": "2026-05-15"
        },
        "enterprise": {
            "name": "CTY XNK X", 
            "pkg_code": "PKG-XNK-001",
            "date": "2026-05-20", 
            "method": "Đóng gói chân không, dán tem QR"
        },
        "lab": {
            "name": "Phòng Lab GACC HCM", 
            "code": "LAB-GACC-HCM",
            "date": "2026-05-25", 
            "cadimi": "0.02 mg/kg", 
            "vang_o": "Không phát hiện", 
            "pesticide": "Đạt chuẩn (<0.01%)",
            "result": "Đạt"
        },
        "blockchain": {
            "id": "0x8a8634798b53a480ec9d2bf22b736cc32b2af23ef2c6a8cea02f603ab7946781", 
            "hash": "0xdf6607e75ea144116f977f524d6ccaf3fc9c60be28e679c482bd5286291149cb"
        }
    }
}

# --- CSS STYLING ---
st.markdown("""
<style>
    .stApp { background-color: #F8FAFC; }
    .header-box { text-align: center; padding: 20px; background: white; border-radius: 20px; box-shadow: 0 5px 15px rgba(0,0,0,0.05); margin-bottom: 20px; }
    .status-card { background: #16A34A; color: white; padding: 15px; border-radius: 12px; text-align: center; font-weight: 400; margin-bottom: 20px; }
    .info-section { background: #F1F5F9; padding: 15px; border-radius: 12px; border-left: 5px solid #16A34A; margin-bottom: 10px; }
    .label { color: #64748B; font-weight: 600; font-size: 0.7rem; text-transform: uppercase; margin-bottom: 2px; }
    .value { color: #1E293B; font-weight: 700; font-size: 0.9rem; margin-bottom: 12px; }
</style>
""", unsafe_allow_html=True)

# --- LOGIC XÁC THỰC ---
params = st.query_params
batch_id = params.get("id")

if not batch_id:
    batch_id = st.text_input("Nhập mã lô hàng để tra cứu (VD: BATCH-001):")

if batch_id:
    if batch_id in MOCK_DATABASE:
        data = MOCK_DATABASE[batch_id]
        
        st.markdown(f'<div class="header-box"><h2>LÔ HÀNG: {batch_id}</h2></div>', unsafe_allow_html=True)
        
        # Ảnh sản phẩm
        img_path = data["image_path"]
        if os.path.exists(img_path):
            st.image(img_path, caption=f"Hình ảnh thực tế lô {batch_id}", width=200)
        
        st.markdown('<div class="status-card">✓ SẢN PHẨM CHÍNH HÃNG - ĐÃ ĐƯỢC CHỨNG NHẬN</div>', unsafe_allow_html=True)

        # 1. Nông dân & Canh tác (Bổ sung: Mã nông dân, Địa chỉ, Giống, Nhật ký)
        with st.expander("👨‍🌾 Nông dân & Canh tác", expanded=True):
            st.markdown(f"""
            <div class="info-section">
                <p class="label">Nông dân / Mã số</p><p class="value">{data['farmer']['name']} ({data['farmer']['code']})</p>
                <p class="label">Địa chỉ vườn</p><p class="value">{data['farmer']['address']}</p>
                <p class="label">Giống sầu riêng</p><p class="value">{data['farmer']['variety']}</p>
                <p class="label">Nhật ký canh tác</p><p class="value">{data['farmer']['diary']}</p>
            </div>
            """, unsafe_allow_html=True)

        # 2. Doanh nghiệp & Đóng gói (Bổ sung: Tên công ty, Mã đóng gói)
        with st.expander("🏭 Doanh nghiệp & Đóng gói"):
            st.markdown(f"""
            <div class="info-section">
                <p class="label">Tên Công ty</p><p class="value">{data['enterprise']['name']}</p>
                <p class="label">Mã cơ sở đóng gói</p><p class="value">{data['enterprise']['pkg_code']}</p>
                <p class="label">Ngày đóng gói</p><p class="value">{data['enterprise']['date']}</p>
            </div>
            """, unsafe_allow_html=True)

        # 3. Kiểm định (Bổ sung: Mã phòng lab, Cadimi, Vàng O, BVTV)
        with st.expander("🧪 Kết quả kiểm định phòng Lab"):
            st.markdown(f"""
            <div class="info-section" style="border-left-color: #DC2626;">
                <p class="label">Đơn vị kiểm định (Mã)</p><p class="value">{data['lab']['name']} ({data['lab']['code']})</p>
                <p class="label">Kết quả kiểm định</p>
                <p class="value">Cadimi: {data['lab']['cadimi']} | Vàng O: {data['lab']['vang_o']}</p>
                <p class="label">Dư lượng thuốc trừ sâu</p><p class="value">{data['lab']['pesticide']}</p>
                <p class="label">Kết luận chung</p><p class="value" style="color:#16A34A; font-size:1rem;">{data['lab']['result']}</p>
            </div>
            """, unsafe_allow_html=True)

        # 4. Blockchain
        st.markdown("---")
        st.markdown("### 🔗 Blockchain Verification")
        st.info(f"Credential ID: {data['blockchain']['id'][:30]}...")
    else:
        st.error("❌ Không tìm thấy thông tin lô hàng.")
