"""
Simple Agricultural Data Dashboard using Streamlit
Quick and easy single-page dashboard

Requirements:
    pip install streamlit plotly pandas

To run:
    streamlit run streamlit_simple.py
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Page config
st.set_page_config(page_title="Agricultural Dashboard",
                   page_icon="🌾", layout="wide")

# Load data


@st.cache_data
def load_data():
    df = pd.read_csv('./actual_data/luong_thuc.csv')

    # Normalize values
    def normalize_value(row):
        value, unit = row['value'], row['unit']
        if pd.isna(value) or pd.isna(unit):
            return np.nan
        multipliers = {
            '1000_ha': 1000, 'ha': 1,
            '1000_USD': 1000, 'million_USD': 1_000_000, 'USD': 1,
            '1000_ton': 1000, 'ton': 1
        }
        return value * multipliers.get(unit, 1)

    df['normalized_value'] = df.apply(normalize_value, axis=1)
    df['date'] = pd.to_datetime(df['year'].astype(
        str) + '-' + df['month'].astype(str).str.zfill(2) + '-01')
    return df


df = load_data()

# Title
st.title('🌾 Agricultural Data Dashboard')

# Sidebar
st.sidebar.header('Filters')
attributes = sorted([x for x in df['attribute'].unique() if pd.notna(x)])
selected_attr = st.sidebar.selectbox('Select Attribute', attributes)

# Filter data
filtered_df = df[df['attribute'] == selected_attr]

# Metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric('Total Value', f"{filtered_df['normalized_value'].sum():,.0f}")
with col2:
    st.metric('Average Value',
              f"{filtered_df['normalized_value'].mean():,.0f}")
with col3:
    st.metric('Total Records', f"{len(filtered_df):,}")

st.divider()

# Visualizations
col1, col2 = st.columns([2, 1])

with col1:
    # Time series
    ts = filtered_df.groupby('date')['normalized_value'].sum().reset_index()
    fig1 = px.line(ts, x='date', y='normalized_value',
                   title=f'{selected_attr} Over Time',
                   labels={'normalized_value': 'Value', 'date': 'Date'})
    fig1.update_traces(line_color='#3498db', line_width=3)
    st.plotly_chart(fig1, width='stretch')

with col2:
    # Pie chart
    commodity_data = filtered_df[filtered_df['commodity'].notna()]
    if len(commodity_data) > 0:
        top_comm = commodity_data.groupby(
            'commodity')['normalized_value'].sum().nlargest(8)
        fig2 = px.pie(values=top_comm.values, names=top_comm.index,
                      title='Top 8 Commodities', hole=0.4)
        st.plotly_chart(fig2, width='stretch')

# Row 2
col1, col2 = st.columns(2)

with col1:
    # Regional bar chart
    regional = filtered_df[
        (filtered_df['location_name'].notna()) &
        (filtered_df['location_name'] != 'cả nước')
    ]
    if len(regional) > 0:
        top_regions = regional.groupby('location_name')[
            'normalized_value'].sum().nlargest(10).sort_values()
        fig3 = px.bar(x=top_regions.values, y=top_regions.index,
                      orientation='h', title='Top 10 Regions')
        fig3.update_traces(marker_color='#2ecc71')
        st.plotly_chart(fig3, width='stretch')

with col2:
    # Seasonal pattern
    seasonal = filtered_df.groupby(
        'month')['normalized_value'].sum().reset_index()
    fig4 = px.bar(seasonal, x='month', y='normalized_value',
                  title='Seasonal Pattern')
    fig4.update_traces(marker_color='#e74c3c')
    fig4.update_xaxes(tickmode='array', tickvals=list(range(1, 13)),
                      ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    st.plotly_chart(fig4, width='stretch')

# Data table
with st.expander('📋 View Data Table'):
    st.dataframe(filtered_df[['year', 'month', 'attribute', 'commodity',
                              'location_name', 'value', 'unit', 'normalized_value']].head(50),
                 width='stretch')
