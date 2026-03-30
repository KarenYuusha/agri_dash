import streamlit as st
import pandas as pd
import pydeck as pdk


def show_geography_page():
    st.title("🌐 Bản đồ 3D Nông nghiệp Việt Nam")

    @st.cache_data
    def load_geo_data():
        try:
            df = pd.read_csv("demo_data/agri_data.csv")
            coords = pd.read_csv("raw_data/cities_latlon.csv")

            # Clean and match strings
            df['Province'] = df['Province'].astype(str).str.strip()
            coords['Province'] = coords['Province'].astype(str).str.strip()

            # Filter for Province level only
            df_prov = df[df['Level'] == 'Province'].copy()

            # Merge coordinates
            merged = pd.merge(df_prov, coords, on='Province', how='inner')
            merged['Value'] = pd.to_numeric(
                merged['Value'], errors='coerce').fillna(0)

            return merged
        except Exception as e:
            st.error(f"Lỗi tải dữ liệu: {e}")
            return None

    df_geo = load_geo_data()

    if df_geo is not None:
        c1, c2, c3 = st.columns(3)
        with c1:
            sel_year = st.selectbox("Chọn Năm", sorted(
                df_geo['Year'].unique(), reverse=True), key="geo_year")
        with c2:
            sel_attr = st.selectbox("Chọn Chỉ số", sorted(
                df_geo['Attribute'].unique()), key="geo_attr")
        with c3:
            all_comms = sorted(df_geo['Commodity'].unique())
            sel_comms = st.multiselect("Chọn Nông sản (có thể chọn nhiều)", all_comms, default=[
                                       all_comms[0]], key="geo_comm")

        if not sel_comms:
            st.warning("Vui lòng chọn ít nhất một loại nông sản.")
        else:
            mask = (df_geo['Year'] == sel_year) & \
                   (df_geo['Attribute'] == sel_attr) & \
                   (df_geo['Commodity'].isin(sel_comms))

            filtered_df = df_geo[mask]

            map_data = filtered_df.groupby(['Province', 'Latitude', 'Longitude', 'Unit']).agg({
                'Value': 'sum'
            }).reset_index()

            if map_data.empty:
                st.info("Không tìm thấy dữ liệu cho lựa chọn này.")
            else:
                # Calculate 3D height (Elevation)
                max_val = map_data['Value'].max()
                # Scale: adjust 200000 to make columns taller or shorter
                map_data['elevation'] = map_data['Value'] / \
                    (max_val if max_val > 0 else 1) * 200000

                # 3D map
                view_state = pdk.ViewState(
                    latitude=15.8, longitude=108.0, zoom=5, pitch=45, bearing=0
                )

                layer = pdk.Layer(
                    "ColumnLayer",
                    data=map_data,
                    get_position=["Longitude", "Latitude"],
                    get_elevation="elevation",
                    radius=18000,  # Column width
                    get_fill_color="[255, 100, 0, 180]",  # Orange
                    pickable=True,
                    auto_highlight=True,
                )

                st.pydeck_chart(pdk.Deck(
                    layers=[layer],
                    initial_view_state=view_state,
                    map_style="dark",
                    tooltip={
                        "text": "{Province}\nTổng {Attribute}: {Value} {Unit}"
                    }
                ))

                # Top List
                st.write(f"### Chi tiết Top tỉnh có {sel_attr} cao nhất")
                st.dataframe(map_data.nlargest(10, 'Value')[
                             ['Province', 'Value', 'Unit']], use_container_width=True)
