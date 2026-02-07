import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np


@st.cache_data
def load_data():
    df = pd.read_csv('./data/nasa_power_daily.csv')
    # Parse date: YYYYMMDD (int) -> datetime
    df['date_parsed'] = pd.to_datetime(df['Date'].astype(str), format='%Y%m%d')
    return df


def show():
    df = load_data()

    st.title('🛰️ NASA Sensor Data (Daily)')
    st.markdown("Daily weather observations from NASA POWER.")

    # Sidebar
    st.sidebar.header('Sensor Filters')

    provinces = sorted(df['Province'].unique())
    selected_province = st.sidebar.selectbox('Select Province', provinces)

    # Date Range
    min_date = df['date_parsed'].min().date()
    max_date = df['date_parsed'].max().date()

    start_date, end_date = st.sidebar.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    # Filter
    mask = (
        (df['Province'] == selected_province) &
        (df['date_parsed'].dt.date >= start_date) &
        (df['date_parsed'].dt.date <= end_date)
    )
    filtered_df = df[mask].sort_values('date_parsed')

    if filtered_df.empty:
        st.warning("No data found for the selected filters.")
        return

    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Avg Temp (T2M)", f"{filtered_df['T2M'].mean():.1f} °C")
    with col2:
        st.metric("Max Temp", f"{filtered_df['T2M_MAX'].max():.1f} °C")
    with col3:
        st.metric("Total Rainfall",
                  f"{filtered_df['PRECTOTCORR'].sum():.1f} mm")
    with col4:
        st.metric("Avg Humidity", f"{filtered_df['RH2M'].mean():.1f} %")

    st.divider()

    # 1. Temperature Timeline
    st.subheader("Temperature Trends")
    fig_temp = go.Figure()
    fig_temp.add_trace(go.Scatter(x=filtered_df['date_parsed'], y=filtered_df['T2M_MAX'],
                                  name='Max Temp', line=dict(color='#e74c3c', width=1)))
    fig_temp.add_trace(go.Scatter(x=filtered_df['date_parsed'], y=filtered_df['T2M_MIN'],
                                  name='Min Temp', line=dict(color='#3498db', width=1)))
    fig_temp.add_trace(go.Scatter(x=filtered_df['date_parsed'], y=filtered_df['T2M'],
                                  name='Avg Temp', line=dict(color='#2ecc71', width=2)))
    fig_temp.update_layout(
        title='Daily Temperature Range', hovermode='x unified')
    st.plotly_chart(fig_temp, width='stretch')

    # 2. Rainfall and Humidity
    st.subheader("Rainfall & Humidity")
    fig_rh = go.Figure()

    # Bar for Rain (Left Axis)
    fig_rh.add_trace(go.Bar(x=filtered_df['date_parsed'], y=filtered_df['PRECTOTCORR'],
                            name='Rainfall (mm)', marker_color='#3498db', opacity=0.6))

    # Line for Humidity (Right Axis)
    fig_rh.add_trace(go.Scatter(x=filtered_df['date_parsed'], y=filtered_df['RH2M'],
                                name='Humidity (%)', line=dict(color='#f1c40f', width=2),
                                yaxis='y2'))

    fig_rh.update_layout(
        title='Rainfall vs Humidity',
        yaxis=dict(title='Rainfall (mm)'),
        yaxis2=dict(title='Humidity (%)', overlaying='y', side='right'),
        hovermode='x unified'
    )
    st.plotly_chart(fig_rh, width='stretch')

    # 3. Correlation Heatmap
    st.subheader("Weather Correlation")
    cols_corr = ['T2M', 'RH2M', 'PRECTOTCORR', 'GWETPROF', 'CLOUD_AMT']
    corr = filtered_df[cols_corr].corr()
    fig_corr = px.imshow(corr, text_auto=True, color_continuous_scale='RdBu_r',
                         title='Correlation Matrix')
    st.plotly_chart(fig_corr, width='stretch')

    # 4. Station Map
    st.subheader("Station Location")
    location_df = filtered_df[['Latitude', 'Longitude',
                               'Province']].drop_duplicates().head(1)

    st.map(location_df, latitude='Latitude', longitude='Longitude', zoom=5)

    with st.expander("View Data"):
        st.dataframe(filtered_df)
