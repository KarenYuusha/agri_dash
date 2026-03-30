import streamlit as st
import pandas as pd
import plotly.express as px


def show_climate_page():
    st.title("🌤️ Phân tích Khí hậu Đa biến (NASA POWER)")
    st.markdown(
        "Khám phá mối liên hệ giữa các chỉ số khí tượng và điều kiện môi trường.")

    @st.cache_data
    def load_climate_data():
        try:
            df = pd.read_csv("raw_data/nasa_power_daily.csv")
            df['Date'] = pd.to_datetime(
                df['Date'].astype(str), format='%Y%m%d')
            df['Year'] = df['Date'].dt.year
            df['Month'] = df['Date'].dt.month
            df['Province'] = df['Province'].str.strip()
            numeric_cols = ["T2M", "RH2M", "T2M_MAX", "T2M_MIN",
                            "CLOUD_AMT", "PRECTOTCORR", "GWETPROF", "CLRSKY_SFC_SW_DWN"]
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            return df
        except Exception as e:
            st.error(f"Lỗi tải dữ liệu: {e}")
            return None

    df_cli = load_climate_data()

    if df_cli is not None:
        param_info = {
            "T2M": "Nhiệt độ (2m)",
            "T2M_MAX": "Nhiệt độ Max",
            "T2M_MIN": "Nhiệt độ Min",
            "RH2M": "Độ ẩm (%)",
            "PRECTOTCORR": "Lượng mưa",
            "GWETPROF": "Độ ẩm đất",
            "CLOUD_AMT": "Lượng mây",
            "CLRSKY_SFC_SW_DWN": "Bức xạ mặt trời"
        }

        with st.sidebar:
            st.header("📍 Cấu hình")
            sel_prov = st.selectbox("Chọn tỉnh thành:", sorted(
                df_cli['Province'].unique()), key="c_prov")

            min_y, max_y = int(df_cli['Year'].min()), int(df_cli['Year'].max())
            yr_range = st.slider("Khoảng năm:", min_y, max_y,
                                 (min_y, max_y), key="c_yrs")

            sel_params = st.multiselect(
                "Chọn các tham số phân tích:",
                options=list(param_info.keys()),
                default=list(param_info.keys())[:6],  # Default first 6
                format_func=lambda x: f"{x} - {param_info[x]}"
            )

        # Apply Filters
        df_f = df_cli[
            (df_cli['Province'] == sel_prov) &
            (df_cli['Year'].between(yr_range[0], yr_range[1]))
        ]

        if df_f.empty:
            st.warning("Không tìm thấy dữ liệu.")
        elif len(sel_params) < 2:
            st.info("Vui lòng chọn ít nhất 2 tham số để xem ma trận tương quan.")
        else:
            # Monthly Average)
            st.subheader(f"Xu hướng biến thiên tại {sel_prov}")
            df_m = df_f.groupby(['Year', 'Month'])[
                sel_params].mean().reset_index()
            df_m['Date_Display'] = pd.to_datetime(
                df_m[['Year', 'Month']].assign(DAY=1)[['Year', 'Month', 'DAY']])

            fig_trend = px.line(df_m, x='Date_Display', y=sel_params,
                                title="Trung bình hàng tháng",
                                labels={"value": "Giá trị", "Date_Display": "Thời gian", "variable": "Chỉ số"})
            st.plotly_chart(fig_trend, use_container_width=True)

            st.markdown("---")

            # Correlation Matrix (The Heatmap)
            st.subheader("Ma trận Tương quan")
            st.markdown("""
            Biểu đồ này thể hiện mối liên hệ giữa **tất cả** các yếu tố khí hậu được chọn. 
            - **1.0 (Xanh đậm):** Tương quan thuận hoàn hảo (cùng tăng/giảm).
            - **-1.0 (Đỏ đậm):** Tương quan nghịch hoàn hảo (cái này tăng thì cái kia giảm).
            """)

            # Calculate Pearson Correlation
            corr_matrix = df_f[sel_params].corr()

            fig_corr = px.imshow(
                corr_matrix,
                text_auto=".2f",  # Show values with 2 decimal places
                aspect="auto",
                # Red-Blue scale (Red is negative, Blue is positive)
                color_continuous_scale='RdBu_r',
                range_color=[-1, 1],
                labels=dict(color="Hệ số tương quan"),
                title=f"Mối liên hệ giữa các yếu tố khí hậu tại {sel_prov}"
            )
            st.plotly_chart(fig_corr, use_container_width=True)

            st.markdown("---")
            with st.expander("💡 Giải thích kết quả tương quan"):
                st.write("""
                - **Lượng mưa (PRECTOTCORR) & Độ ẩm đất (GWETPROF):** Thường có tương quan thuận cao (> 0.7).
                - **Lượng mây (CLOUD_AMT) & Bức xạ (CLRSKY...):** Thường có tương quan nghịch mạnh (< -0.6).
                - **Nhiệt độ (T2M) & Độ ẩm (RH2M):** Thường có mối liên hệ mật thiết tùy theo khu vực và mùa.
                """)
                st.dataframe(df_f[sel_params].describe().T,
                             use_container_width=True)
