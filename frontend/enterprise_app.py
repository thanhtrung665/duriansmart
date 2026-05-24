import streamlit as st
import requests
import pandas as pd

API_URL = "http://localhost:8000" # Đổi sang IP Server nếu chạy remote

st.set_page_config(page_title="Enterprise Dashboard", layout="wide")

st.title("🚜 Durian Smart - Enterprise Portal")
st.sidebar.header("Quản lý Lô hàng")

# 1. Xem danh sách lô hàng
if st.sidebar.button("Lấy danh sách lô hàng"):
    # Giả lập gọi API lấy dữ liệu từ MongoDB
    st.info("Đang tải dữ liệu từ Blockchain & MongoDB...")
    # st.write(requests.get(f"{API_URL}/batches").json())

# 2. Form Bàn giao (Takeover)
st.subheader("📦 Bàn giao & Đóng gói")
with st.form("takeover_form"):
    batch_id = st.text_input("Mã lô hàng (Batch ID)", value="BATCH-001")
    ent_id = st.text_input("Mã doanh nghiệp", value="ENT-VINAGREEN")
    weight = st.number_input("Tổng khối lượng (kg)", min_value=0.0)
    boxes = st.number_input("Số thùng", min_value=0)
    
    if st.form_submit_button("Xác nhận Bàn giao"):
        payload = {
            "total_boxes": boxes,
            "total_weight_kg": weight,
            "packaging_date": "2024-05-24"
        }
        res = requests.post(f"{API_URL}/enterprise/{batch_id}/takeover?enterprise_id={ent_id}", json=payload)
        if res.status_code == 200:
            st.success(f"Đã bàn giao! Mã băm: {res.json()['enterprise_hash']}")

# 3. Nút bấm Đúc Blockchain (Chỉ hiện khi Lab đã xong)
st.subheader("⛓️ Thực thi Đa chữ ký On-chain")
if st.button("🚀 ĐÚC MÃ QR BLOCKCHAIN"):
    res = requests.post(f"{API_URL}/enterprise/{batch_id}/mint-export-qr")
    if res.status_code == 200:
        st.balloons()
        st.success("Giao dịch thành công!")
        st.write(f"Link Cardano Scan: {res.json()['explorer_url']}")
