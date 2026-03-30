import streamlit as st


def show_homepage():
    st.title("🌾 Dashboard nông nghiệp Việt Nam")

    st.markdown("""
    ### Dashboard phân tích dữ liệu nông nghiệp Việt Nam (2008-2023)
    Hệ thống phân tích dữ liệu của **63 tỉnh thành**, bao gồm **8 loại nông sản**:
    *Lúa, ngô, khoai lang, sắn, lạc, mía, chè, cam và quýt.*
    
    ---
    #### Các chức năng chính:
    1. **Phân tích nông nghiệp**: Biểu đồ phân bố và so sánh xu hướng.
    2. **Phân tích địa lý**: Bản đồ 3D theo các vùng miền.
    3. **Phân tích khí hậu**: Xu hướng khí hậu và mối tương quan.
    4. **Phân tích thổ nhưỡng**: Phân bố đặc tính đất đai.
    5. **Dự đoán**: Dự báo năng suất và gợi ý cây trồng phù hợp.
    """)
