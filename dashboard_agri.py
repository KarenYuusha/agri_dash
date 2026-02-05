import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# unit constrain mapping
UNIT_CATEGORIES = {
    '1000_ha': 'Area', 'ha': 'Area',
    '1000_ton': 'Mass', 'ton': 'Mass',
    '1000_USD': 'Currency', 'million_USD': 'Currency', 'USD': 'Currency', 'million_VND': 'Currency',
    '1000_m3': 'Volume',
    'million_trees': 'Count',
    'percent': 'Ratio'
}

@st.cache_data
def load_data():
    df = pd.read_csv('./data/luong_thuc.csv')

    def normalize_value(row):
        value, unit = row['value'], row['unit']
        if pd.isna(value) or pd.isna(unit):
            return np.nan
        multipliers = {
            '1000_ha': 1000, 'ha': 1,
            '1000_USD': 1000, 'million_USD': 1_000_000, 'USD': 1,
            'million_VND': 1, # Treat as base unit for VND, distinct from USD 
            '1000_ton': 1000, 'ton': 1,
            '1000_m3': 1000,
            'million_trees': 1_000_000,
            'percent': 1
        }
        return value * multipliers.get(unit, 1)

    df['normalized_value'] = df.apply(normalize_value, axis=1)
    df['unit_category'] = df['unit'].map(UNIT_CATEGORIES).fillna('Other')
    
    df['date'] = pd.to_datetime(df['year'].astype(
        str) + '-' + df['month'].astype(str).str.zfill(2) + '-01')
    return df


def show():
    df = load_data()

    st.title('🌾 Agriculture Yearly Report')
    st.markdown("Analysis of agricultural production, area, and trade values.")

    st.sidebar.header('Agriculture Filters')

    # Geographic Level Filter
    geo_levels = sorted([x for x in df['geo_level'].dropna().unique()])
    default_geo = 'National' if 'National' in geo_levels else geo_levels[0]
    selected_geo = st.sidebar.selectbox('Geographic Level', geo_levels, index=geo_levels.index(default_geo) if default_geo in geo_levels else 0)

    # Filter by Geo Level first
    df_geo = df[df['geo_level'] == selected_geo]

    # ensure attributes are valid strings
    attributes = sorted([x for x in df_geo['attribute'].unique() if pd.notna(x)])
    selected_attrs = st.sidebar.multiselect('Select Attributes', attributes, default=[
                                            attributes[0]] if attributes else None)

    if not selected_attrs:
        st.warning("Please select at least one attribute.")
        return
        
    # Check Unit Consistency
    selected_units = df_geo[df_geo['attribute'].isin(selected_attrs)]['unit_category'].unique()
    if len(selected_units) > 1:
        st.error(f"⚠️ Unit Mismatch! You selected attributes with incompatible units: {', '.join(selected_units)}. Please select attributes with the same unit category (e.g., all Area, or all Mass).")
        return

    filtered_df = df_geo[df_geo['attribute'].isin(selected_attrs)]

    # Metrics (Aggregate over all selected)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric('Total Value (Selected)',
                  f"{filtered_df['normalized_value'].sum():,.0f}")
    with col2:
        st.metric('Avg Annual Value',
                  f"{filtered_df.groupby('year')['normalized_value'].sum().mean():,.0f}")
    with col3:
        st.metric('Records', f"{len(filtered_df):,}")

    st.divider()


    # 1. Main Trend Line (Multi-attribute support)
    st.subheader(f"Trend Analysis: {', '.join(selected_attrs)}")

    # Aggregate by date and attribute
    ts = filtered_df.groupby(['date', 'attribute'])[
        'normalized_value'].sum().reset_index()

    fig1 = px.line(ts, x='date', y='normalized_value', color='attribute',
                   title='Value Over Time by Attribute',
                   labels={'normalized_value': 'Normalized Value', 'date': 'Date'})
    fig1.update_traces(line_width=3)
    fig1.update_layout(hovermode="x unified")
    st.plotly_chart(fig1, use_container_width=True)

    col_charts_1, col_charts_2 = st.columns(2)

    with col_charts_1:
        # 2. Commodity Breakdown (Pie)
        st.subheader("Commodity Share")
        commodity_data = filtered_df[filtered_df['commodity'].notna()]
        if len(commodity_data) > 0:
            top_comm = commodity_data.groupby(
                'commodity')['normalized_value'].sum().nlargest(10)
            fig2 = px.pie(values=top_comm.values, names=top_comm.index,
                          title='Top 10 Commodities (All Selected Attributes)', hole=0.4)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No commodity data available for selection.")

    with col_charts_2:
        # 3. Regional Comparison
        st.subheader("Regional Leaders")
        regional = filtered_df[
            (filtered_df['location_name'].notna()) &
            (filtered_df['location_name'] != 'cả nước')
        ]
        if len(regional) > 0:
            top_regions = regional.groupby('location_name')[
                'normalized_value'].sum().nlargest(10).sort_values()
            fig3 = px.bar(x=top_regions.values, y=top_regions.index,
                          orientation='h', title='Top 10 Locations')
            fig3.update_traces(marker_color='#2ecc71')
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("No regional data available.")

    # 4. Seasonal / Monthly Pattern
    st.subheader("Seasonality")
    seasonal = filtered_df.groupby(['month', 'attribute'])[
        'normalized_value'].sum().reset_index()
    fig4 = px.bar(seasonal, x='month', y='normalized_value', color='attribute',
                  title='Seasonal Pattern (Aggregated)', barmode='group')
    fig4.update_xaxes(tickmode='array', tickvals=list(range(1, 13)),
                      ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    st.plotly_chart(fig4, use_container_width=True)

    # Data table
    with st.expander('📋 View Raw Data'):
        st.dataframe(filtered_df[['year', 'month', 'attribute', 'commodity',
                                  'location_name', 'value', 'unit', 'normalized_value']].head(100),
                     use_container_width=True)
