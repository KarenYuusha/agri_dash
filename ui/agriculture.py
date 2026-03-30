import streamlit as st
import pandas as pd
import plotly.express as px

def show_agriculture_page():
    st.title("📊 Phân tích số liệu nông nghiệp")

    @st.cache_data
    def load_data():
        df = pd.read_csv("demo_data/agri_data.csv")
        for col in ['Province', 'Attribute', 'Commodity', 'Level']:
            df[col] = df[col].astype(str).str.strip()
        df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
        return df

    try:
        df = load_data()
    except FileNotFoundError:
        st.error("Không tìm thấy file agri_data.csv!")
        return

    tab1, tab2 = st.tabs(["Tổng quan", "Phân tích Chuyên sâu"])

    # --- TAB 1: TỔNG QUAN ---
    with tab1:
        # Bộ lọc hàng đầu
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            lev_map = {"Toàn quốc": "National", "Vùng": "Regional", "Tỉnh": "Province"}
            s_lev_label = st.selectbox("Cấp độ", list(lev_map.keys()), key="q_lev")
            s_lev_val = lev_map[s_lev_label]
        with c2:
            reg_opts = sorted(df[df['Level'] == s_lev_val]['Province'].unique())
            s_reg = st.selectbox("Địa phương", reg_opts, key="q_reg")
        with c3:
            yr_opts = sorted(df['Year'].unique(), reverse=True)
            s_yr = st.selectbox("Năm", yr_opts, key="q_yr")
        with c4:
            comm_opts = sorted(df['Commodity'].unique())
            s_comm = st.selectbox("Nông sản (để xem Metric)", comm_opts, key="q_comm")

        # 1. Metrics Row
        st.markdown("---")
        m_df = df[(df['Province'] == s_reg) & (df['Year'] == s_yr) & (df['Commodity'] == s_comm)]
        
        def get_m(attr): return m_df[m_df['Attribute'].str.contains(attr, case=False, na=False)]['Value'].sum()
        
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric(f"Sản lượng {s_comm}", f"{get_m('Sản lượng'):,.1f} tấn")
        col_m2.metric(f"Diện tích {s_comm}", f"{get_m('Diện tích'):,.1f} ha")
        col_m3.metric(f"Năng suất {s_comm}", f"{get_m('Năng suất'):,.2f}")

        # 2. Charts Row (Comparing all Commodities for the selected location)
        st.subheader(f"Cơ cấu nông nghiệp tại {s_reg} ({s_yr})")
        chart_attr = st.selectbox("Chọn chỉ số so sánh biểu đồ:", sorted(df['Attribute'].unique()), key="q_chart_attr")
        
        plot_df_q = df[(df['Province'] == s_reg) & (df['Year'] == s_yr) & (df['Attribute'] == chart_attr)]
        
        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            fig_bar = px.bar(plot_df_q, x='Commodity', y='Value', color='Commodity', text_auto='.2s',
                             title=f"Phân bố {chart_attr} theo loại cây trồng")
            st.plotly_chart(fig_bar, use_container_width=True)
        with chart_col2:
            fig_pie = px.pie(plot_df_q, values='Value', names='Commodity', hole=0.4,
                             title=f"Tỷ trọng {chart_attr}")
            st.plotly_chart(fig_pie, use_container_width=True)

    # --- TAB 2: CHUYÊN SÂU ---
    with tab2:
        st.header("Xu hướng & So sánh đa chiều")
        
        with st.container(border=True):
            comp_map = {"Địa phương": "Province", "Nông sản": "Commodity"}
            c_sel = st.radio("**So sánh theo (Màu sắc biểu đồ):**", list(comp_map.keys()), horizontal=True, key="t_comp")
            color_col = comp_map[c_sel]

        f1, f2, f3 = st.columns(3)
        with f1:
            t_lev_map = {"Toàn quốc": "National", "Vùng": "Regional", "Tỉnh": "Province"}
            t_lev_val = t_lev_map[st.selectbox("Cấp độ lọc:", list(t_lev_map.keys()), key="t_lev")]
            t_space_opts = sorted(df[df['Level'] == t_lev_val]['Province'].unique())
            t_spaces = st.multiselect("Chọn địa phương:", t_space_opts, default=t_space_opts[:3], key="t_spaces")
        with f2:
            t_comms = st.multiselect("Chọn loại nông sản:", sorted(df['Commodity'].unique()), default=df['Commodity'].unique()[:3], key="t_comms")
        with f3:
            t_attr = st.selectbox("Chọn chỉ số:", sorted(df['Attribute'].unique()), key="t_attr")
            t_yrs = st.slider("Khoảng năm:", int(df['Year'].min()), int(df['Year'].max()), (2008, 2023), key="t_yrs")

        # Filtering
        df_t = df[(df['Year'].between(t_yrs[0], t_yrs[1])) & (df['Level'] == t_lev_val) & (df['Attribute'] == t_attr)]
        if t_spaces: df_t = df_t[df_t['Province'].isin(t_spaces)]
        if t_comms: df_t = df_t[df_t['Commodity'].isin(t_comms)]

        if df_t.empty:
            st.warning("Không có dữ liệu!")
        else:
            # Grouping
            df_plot = df_t.groupby(['Year', color_col])['Value'].sum().reset_index()

            # Plot 1: Line Chart (Trend)
            st.plotly_chart(px.line(df_plot, x='Year', y='Value', color=color_col, markers=True, title=f"Xu hướng {t_attr} qua các năm"), use_container_width=True)

            # Plot 2 & 3: Heatmap & Stacked Bar
            st.markdown("---")
            col_a, col_b = st.columns(2)
            with col_a:
                st.subheader(f"Tương quan Diện tích & Sản lượng")
                # We need both Area and Production for a Bubble Chart
                # This filter gets both attributes for the selected locations/crops
                bubble_df = df[(df['Year'].between(t_yrs[0], t_yrs[1])) & 
                               (df['Level'] == t_lev_val) & 
                               (df['Province'].isin(t_spaces)) &
                               (df['Commodity'].isin(t_comms))]
                
                # Pivot to get Attributes as columns
                bubble_pivot = bubble_df.pivot_table(
                    index=['Year', 'Province', 'Commodity'], 
                    columns='Attribute', 
                    values='Value'
                ).reset_index()

                # Check if we have the right columns for the scatter
                if 'Diện tích' in bubble_pivot.columns and 'Sản lượng' in bubble_pivot.columns:
                    fig_scatter = px.scatter(
                        bubble_pivot, 
                        x='Diện tích', 
                        y='Sản lượng',
                        size='Sản lượng', 
                        color=color_col,
                        hover_name='Province',
                        animation_frame='Year', # Adds a play button to see changes over time
                        title="Tương quan Sản lượng vs Diện tích (Bubble Chart)"
                    )
                    st.plotly_chart(fig_scatter, use_container_width=True)
                else:
                    st.info("Cần có dữ liệu 'Diện tích' và 'Sản lượng' để hiển thị biểu đồ bong bóng.")

            with col_b:
                st.subheader(f"Biểu đồ Miền {t_attr}")
                # Area chart shows the total volume and how each part contributes
                fig_area = px.area(
                    df_plot, 
                    x='Year', 
                    y='Value', 
                    color=color_col,
                    title=f"Đóng góp của các {c_sel} vào tổng {t_attr}",
                    line_group=color_col
                )
                st.plotly_chart(fig_area, use_container_width=True)