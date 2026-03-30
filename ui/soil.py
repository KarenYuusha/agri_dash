import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def show_soil_page():
    st.title("🌱 Phân tích Đặc tính Đất & Lớp phủ (Soil & Landcover)")
    st.markdown("Phân tích các chỉ số lý hóa của đất và hiện trạng sử dụng đất tại các tỉnh thành.")

    @st.cache_data
    def load_soil_data():
        try:
            # File của bạn: raw_data/soil_data.csv
            df = pd.read_csv("raw_data/soil_data.csv")
            # Làm sạch dữ liệu
            df['Province'] = df['Province'].str.strip()
            # Map mã Landcover sang tên hiển thị
            lc_map = {
                10: "Rừng (Trees)", 20: "Cây bụi (Shrubland)", 30: "Trảng cỏ (Grassland)",
                40: "Đất trồng trọt (Cropland)", 50: "Đô thị (Built-up)", 
                80: "Mặt nước (Water)", 90: "Đất ngập nước (Wetland)"
            }
            df['Landcover_Name'] = df['Landcover'].map(lc_map)
            return df
        except Exception as e:
            st.error(f"Lỗi tải dữ liệu đất: {e}")
            return None

    df_soil = load_soil_data()

    if df_soil is not None:
        # --- BỘ LỌC TỈNH THÀNH ---
        sel_provinces = st.multiselect(
            "Chọn các tỉnh để so sánh:", 
            options=sorted(df_soil['Province'].unique()),
            default=sorted(df_soil['Province'].unique())[:5],
            key="s_provs"
        )

        df_s = df_soil[df_soil['Province'].isin(sel_provinces)]

        if df_s.empty:
            st.warning("Vui lòng chọn ít nhất một tỉnh.")
        else:
            # --- 1. BIỂU ĐỒ RADAR: SO SÁNH THÀNH PHẦN ĐẤT ---
            st.subheader("Cấu trúc Đất & Độ phì nhiêu")
            st.info("Biểu đồ Radar giúp so sánh đa chỉ tiêu (Sét, Cát, pH, Hữu cơ) giữa các tỉnh.")
            
            fig_radar = go.Figure()
            categories = ['Soil_ph', 'Soil_soc', 'Soil_clay', 'Soil_sand', 'Ndvi_mean']

            # Create a copy for normalization so we don't ruin the raw data
            df_norm = df_s.copy()

            for cat in categories:
                # Scale each column from 0 to 1
                c_min = df_soil[cat].min()
                c_max = df_soil[cat].max()
                if c_max > c_min:
                    df_norm[cat] = (df_s[cat] - c_min) / (c_max - c_min)

            fig_radar = go.Figure()

            for prov in sel_provinces:
                prov_row = df_norm[df_norm['Province'] == prov]
                if not prov_row.empty:
                    fig_radar.add_trace(go.Scatterpolar(
                        r=[prov_row[c].iloc[0] for c in categories],
                        theta=['pH (Acidity)', 'SOC (Organic)', 'Clay', 'Sand', 'NDVI (Greenness)'],
                        fill='toself',
                        name=prov
                    ))

            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                title="So sánh Đặc tính Đất"
            )
            st.plotly_chart(fig_radar, use_container_width=True)

            # --- 2. BIỂU ĐỒ PHÂN BỔ LOẠI ĐẤT (TERNARY PLOT) ---
            st.markdown("---")
            c1, c2 = st.columns(2)
            
            with c1:
                st.subheader("Thành phần Cơ giới Đất")
                # Ternary plot rất phổ biến trong thổ nhưỡng để phân loại đất (Sét-Cát-Thịt)
                # Vì dữ liệu bạn có Clay và Sand, chúng ta giả định phần còn lại là Silt (Thịt)
                df_s['Soil_silt'] = 100 - df_s['Soil_clay'] - df_s['Soil_sand']
                
                fig_ternary = px.scatter_ternary(
                    df_s, a="Soil_clay", b="Soil_sand", c="Soil_silt",
                    color="Province", size="Soil_soc",
                    hover_name="Province",
                    title="Tam giác thành phần cơ giới đất (Kích thước = Độ hữu cơ SOC)"
                )
                st.plotly_chart(fig_ternary, use_container_width=True)

            with c2:
                st.subheader("Hiện trạng Lớp phủ (Landcover)")
                fig_sun = px.sunburst(
                    df_s, path=['Landcover_Name', 'Province'], values='Ndvi_mean',
                    color='Ndvi_mean', color_continuous_scale='RdYlGn',
                    title="Phân bố Lớp phủ & Chỉ số Xanh (NDVI)"
                )
                st.plotly_chart(fig_sun, use_container_width=True)

            # --- 3. TƯƠNG QUAN ĐỘ CAO & NDVI ---
            st.markdown("---")
            st.subheader("⛰️ Ảnh hưởng của Độ cao (Elevation) đến Sức khỏe Thực vật (NDVI)")
            fig_elev = px.scatter(
                df_soil, x="Elevation", y="Ndvi_mean", 
                color="Landcover_Name", size="Soil_soc",
                hover_data=['Province'],
                title="Mối quan hệ Độ cao - NDVI trên toàn bộ 63 tỉnh"
            )
            st.plotly_chart(fig_elev, use_container_width=True)

            with st.expander("📊 Chi tiết dữ liệu Thổ nhưỡng"):
                st.dataframe(df_s, use_container_width=True)