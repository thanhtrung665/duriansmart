# ============================================================
# PATH: frontend/verify_app.py
# DURIAN SMART - PUBLIC QR VERIFICATION MODULE (LOCAL IMAGE)
# ============================================================
import streamlit as st
import os

st.set_page_config(page_title="Durian Smart | Xác thực", page_icon="🔍", layout="centered")

# --- MOCK DATABASE ---
# Lưu ý: Đảm bảo đường dẫn này khớp với cây thư mục của bạn
MOCK_DATABASE = {
    "BATCH-001": {
        "image_path": "frontend/images/durian.jpg", 
        "farmer": {"name": "Nguyễn Văn A", "puc": "PUC-01", "farm": "Vườn sầu riêng Ri6 - Đắk Lắk", "date": "2026-05-15"},
        "enterprise": {"name": "CTY XNK X", "factory": "F-001", "date": "2026-05-20", "method": "Đóng gói chân không"},
        "lab": {"lab_name": "Phòng Lab GACC HCM", "date": "2026-05-25", "cadimi": "0.02 mg/kg", "result": "Đạt"},
        "blockchain": {"id": "0x8a8634798b53a480ec9d2bf22b736cc32b2af23ef2c6a8cea02f603ab7946781", "hash": "0xdf6607e75ea144116f977f524d6ccaf3fc9c60be28e679c482bd5286291149cb"}
    }
}

# --- CSS STYLING ---
st.markdown("""
<style>
    .stApp { background-color: #F8FAFC; }
    .header-box { text-align: center; padding: 20px; background: white; border-radius: 20px; box-shadow: 0 5px 15px rgba(0,0,0,0.05); margin-bottom: 20px; }
    .status-card { background: #16A34A; color: white; padding: 15px; border-radius: 12px; text-align: center; font-weight: 800; margin-bottom: 20px; }
    .info-section { background: white; padding: 15px; border-radius: 12px; border-left: 5px solid #16A34A; margin-bottom: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.02); }
    .label { color: #64748B; font-weight: 600; font-size: 0.75rem; text-transform: uppercase; }
    .value { color: #1E293B; font-weight: 700; font-size: 0.95rem; margin-bottom: 8px; }
</style>
""", unsafe_allow_html=True)

# --- LOGIC XÁC THỰC ---
params = st.query_params
batch_id = params.get("id")

if not batch_id:
    batch_id = st.text_input("Nhập Batch ID để demo (VD: BATCH-001):")

if batch_id:
    if batch_id in MOCK_DATABASE:
        data = MOCK_DATABASE[batch_id]
        
        # 1. Header
        st.markdown(f'<div class="header-box"><h2>LÔ HÀNG: {batch_id}</h2></div>', unsafe_allow_html=True)
        
        # 2. Xử lý hiển thị ảnh cục bộ
        img_path = data["image_path"]
        if os.path.exists(img_path):
            # ĐÃ XÓA THAM SỐ GÂY LỖI: use_container_width
            st.image(img_path, caption=f"Hình ảnh thực tế lô {batch_id}")
        else:
            st.warning(f"⚠️ Ảnh mẫu chưa tìm thấy tại đường dẫn: {img_path}")
        
        # 3. Status xác thực
        st.markdown('<div class="status-card">✓ SẢN PHẨM CHÍNH HÃNG - ĐÃ ĐƯỢC CHỨNG NHẬN</div>', unsafe_allow_html=True)

        # 4. Thông tin chi tiết
        with st.expander("👨‍🌾 Nông dân & Canh tác", expanded=True):
            st.markdown(f'<div class="info-section"><p class="label">Nông dân</p><p class="value">{data["farmer"]["name"]}</p><p class="label">Mã vùng</p><p class="value">{data["farmer"]["puc"]}</p></div>', unsafe_allow_html=True)

        with st.expander("🏭 Doanh nghiệp & Đóng gói"):
            st.markdown(f'<div class="info-section"><p class="label">Doanh nghiệp</p><p class="value">{data["enterprise"]["name"]}</p><p class="label">Phương pháp</p><p class="value">{data["enterprise"]["method"]}</p></div>', unsafe_allow_html=True)

        with st.expander("🧪 Kết quả kiểm định"):
            st.markdown(f'<div class="info-section" style="border-left-color: #DC2626;"><p class="label">Phòng Lab</p><p class="value">{data["lab"]["lab_name"]}</p><p class="label">Kết quả</p><p class="value" style="color:#16A34A;">{data["lab"]["result"]}</p></div>', unsafe_allow_html=True)

        # 5. Blockchain
        st.markdown("---")
        st.markdown("### 🔗 Blockchain Verification")
        st.info(f"ID: {data['blockchain']['id'][:20]}...")
    else:
        st.error("❌ Không tìm thấy thông tin lô hàng.")
