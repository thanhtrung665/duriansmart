# ============================================================
# PATH: frontend/consumer_app.py
# DURIAN SMART - CONSUMER TRACEABILITY PORTAL
# ============================================================
import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Durian Traceability", page_icon="🍈", layout="centered")

# CSS tinh chỉnh cho giao diện Mobile-friendly
st.markdown("""
    <style>
    .main-title { color: #11CAA0; text-align: center; font-size: 2.5rem; font-weight: 700;}
    .sub-title { color: #64748b; text-align: center; font-size: 1.1rem; margin-bottom: 30px;}
    .hash-box { background-color: #f1f5f9; padding: 15px; border-radius: 8px; word-break: break-all; font-family: monospace; color: #0f172a;}
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">🍈 DURIAN SMART</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Minh bạch Hành trình - Trọn vẹn Niềm tin</p>', unsafe_allow_html=True)

# Thanh tìm kiếm thay cho thao tác Quét QR
search_query = st.text_input("🔍 Nhập mã truy xuất trên tem (VD: BATCH-001):")

if st.button("Tra cứu Nguồn gốc", use_container_width=True) and search_query:
    with st.spinner("Đang truy xuất dữ liệu từ Mạng lưới Blockchain..."):
        res = requests.get(f"{API_URL}/public/trace/{search_query}")
        
        if res.status_code == 200:
            batch_data = res.json()["data"]
            farmer_info = batch_data.get("farmer_profile", {})
            
            # --- 1. TỔNG QUAN SẢN PHẨM ---
            st.success("✅ Chứng nhận Sản phẩm Chính hãng")
            st.subheader(f"Sầu riêng {farmer_info.get('durian_variety', 'Đặc sản')} - Hạng Premium")
            
            col1, col2 = st.columns(2)
            col1.metric("Nông dân", farmer_info.get("farmer_name", "N/A"))
            col2.metric("Mã vùng trồng", farmer_info.get("farm_code_puc", "N/A"))
            
            st.divider()

            # --- 2. NHẬT KÝ CANH TÁC (120 NGÀY) ---
            st.subheader("🌱 Hành trình 120 ngày canh tác")
            daily_logs = batch_data.get("daily_logs", [])
            
            if not daily_logs:
                st.info("Chưa có nhật ký nào được ghi nhận.")
            else:
                # Dùng Expander để hiển thị mảng nhật ký Standard JSON một cách gọn gàng
                for log in reversed(daily_logs): # Hiển thị ngày mới nhất lên đầu
                    with st.expander(f"Ngày {log['day_number']} - Phân tích AI: {log['ai_analysis_status']}"):
                        st.write(f"**Giọng nói Nông dân:** {log['voice_log_text']}")
                        st.caption(f"Thời gian ghi nhận: {log['date_recorded']}")
            
            st.divider()

            # --- 3. KIỂM ĐỊNH CHẤT LƯỢNG (PHÒNG LAB) ---
            st.subheader("🔬 Chứng nhận Chất lượng Độc lập")
            lab_data = batch_data.get("lab_certificate", {})
            if lab_data and lab_data.get("is_passed"):
                st.success(f"**ĐẠT CHUẨN XUẤT KHẨU GACC** (Mã: {lab_data.get('certificate_code')})")
                st.write(f"- Hàm lượng Cadimi: {lab_data.get('cadimi_level')} mg/kg (An toàn)")
                st.write(f"- Dư lượng Vàng Ô: {lab_data.get('vang_o_status')}")
            else:
                st.warning("Lô hàng đang trong quá trình kiểm định.")

            st.divider()

            # --- 4. XÁC THỰC BLOCKCHAIN (ON-CHAIN) ---
            st.subheader("⛓️ Xác thực Blockchain Cardano")
            if batch_data.get("is_minted_onchain"):
                st.info("Lô hàng đã được khóa dữ liệu vĩnh viễn trên Cardano thông qua Hợp đồng Đa chữ ký.")
                
                st.markdown("**Mã băm Nhật ký Nông dân:**")
                st.markdown(f'<div class="hash-box">{batch_data.get("farmer_hash")}</div>', unsafe_allow_html=True)
                
                st.markdown("**Mã băm Chứng nhận Lab:**")
                st.markdown(f'<div class="hash-box">{batch_data.get("lab_hash")}</div>', unsafe_allow_html=True)
                
                tx_hash = batch_data.get("transaction_hash")
                st.markdown(f"[👉 Bấm vào đây để kiểm tra Giao dịch gốc trên CardanoScan](https://preprod.cardanoscan.io/transaction/{tx_hash})")
            else:
                st.info("Lô hàng đang chờ đúc mã On-chain.")

        else:
            st.error("Không tìm thấy dữ liệu! Vui lòng kiểm tra lại mã QR hoặc mã lô hàng.")