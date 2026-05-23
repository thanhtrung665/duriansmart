import streamlit as st
import requests
import time

# Cấu hình trang
st.set_page_config(page_title="Durian Smart Protal", page_icon="🍈", layout="wide")
st.title("🍈 DURIAN SMART - HỆ THỐNG BẢO CHỨNG SẦU RIÊNG XUẤT KHẨU")

# Tạo 2 Tabs: Một cho daonh nghiệp, Một cho Hải quan (Người dùng cuối)
tab1, tab2 = st.tabs(["🏢 Cổng Doanh Nghiệp (Mint QR)", "🔍 Cổng Truy Xuất Người Tiêu Dùng"])
with tab1:
    st.header("Danh sách Lô hàng chờ xuất khẩu")
    st.info("Lô hàng BATCH-2026-005 đã nhận đủ dữ liệu từ Nông dân và Phòng Lab")
    
    col1, col2, col3 = st.columns(3)
    col1.success("✅ Nông dân: Hợp lệ (AI Oracle duyệt)")
    col2.success("✅ Phòng Lab: Hợp lệ")
    col3.warning("⏳ Vựa đóng gói: Chờ xác nhận")
    st.markdown("---")
    st.subheader("Hoàn tất thủ tục On-chain")
    
    # Form giả lập dữ liệu Vựa và Mint QR
    with st.form("mint_form"):
        st.write('Xác nhận thông số đóng gói lô hàng BATCH-2026-005')
        weight = st.number_input("Sản lượng (Tấn)", value=18.5)
        boxes = st.number_input("Số thùng carton", value=925)
        