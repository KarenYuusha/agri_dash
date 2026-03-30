import streamlit as st
from ui.homepage import show_homepage
from ui.agriculture import show_agriculture_page
from ui.geography import show_geography_page
from ui.climate import show_climate_page
from ui.soil import show_soil_page

# Page Config
st.set_page_config(page_title="AgriData Vietnam", layout="wide")

# Sidebar Navigation
st.sidebar.title("Menu Điều Hướng")
page = st.sidebar.radio(
    "Chọn chức năng:",
    ["Trang chủ", "Phân tích nông nghiệp", "Phân tích địa lý", 
     "Phân tích khí hậu", "Phân tích thổ nhưỡng", "Dự đoán"]
)

# Routing Logic
if page == "Trang chủ":
    show_homepage()
elif page == "Phân tích nông nghiệp":
    show_agriculture_page() 
elif page == 'Phân tích địa lý':
    show_geography_page()
elif page == 'Phân tích khí hậu':
    show_climate_page()
elif page == 'Phân tích thổ nhưỡng':
    show_soil_page()
else:
    st.title(f"📊 {page}")
    st.write("To be continued")