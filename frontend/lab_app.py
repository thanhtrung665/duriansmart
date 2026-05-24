#### 2. File `frontend/lab_app.py` (Giao diện Phòng Lab)

import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Lab Certification Portal")

st.title("🔬 Durian Smart - Lab Portal")
st.warning("Khu vực dành riêng cho Nhân viên Kiểm định")

with st.form("lab_form"):
    batch_id = st.text_input("Batch ID cần kiểm định", value="BATCH-001")
    lab_id = st.text_input("Mã nhân viên Lab", value="LAB-QUATEST3")
    cert_code = st.text_input("Mã chứng thư số", value="CERT-2024-99")
    cadimi = st.slider("Hàm lượng Cadimi (mg/kg)", 0.0, 0.2, 0.02)
    is_passed = st.checkbox("Đạt chuẩn xuất khẩu GACC?", value=True)
    
    if st.form_submit_button("Ký duyệt Chứng thư"):
        payload = {
            "certificate_code": cert_code,
            "cadimi_level": cadimi,
            "vang_o_status": "Không phát hiện",
            "is_passed": is_passed
        }
        res = requests.post(f"{API_URL}/lab/{batch_id}/certify?lab_id={lab_id}", json=payload)
        if res.status_code == 200:
            st.success("Đã cấp chứng thư thành công!")
