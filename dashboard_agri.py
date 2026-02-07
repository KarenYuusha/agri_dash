import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

# normalize unit


@st.cache_data
def load_data(uploaded_file=None):
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_csv('./data/luong_thuc.csv')

    df['unit'] = (
        df['unit']
        .astype(str)
        .str.strip()
        .str.lower()
        .replace({
            'hectare': 'ha',
            'hectares': 'ha',
            '1000 ha': '1000_ha',
            '1,000 ha': '1000_ha',
            'us$': 'usd',
            'million usd': 'million_usd',
            '1000 usd': '1000_usd'
        })
    )

    multipliers = {
        '1000_ha': 1000, 'ha': 1,
        '1000_ton': 1000, 'ton': 1,
        '1000_usd': 1000, 'million_usd': 1_000_000, 'usd': 1,
        'million_vnd': 1,
        '1000_m3': 1000,
        'million_trees': 1_000_000,
        'percent': 1
    }

    df['normalized_value'] = df.apply(
        lambda r: r['value'] * multipliers.get(r['unit'], np.nan)
        if pd.notna(r['value']) else np.nan,
        axis=1
    )

    UNIT_CATEGORIES = {
        '1000_ha': 'Area', 'ha': 'Area',
        '1000_ton': 'Mass', 'ton': 'Mass',
        '1000_usd': 'Currency', 'million_usd': 'Currency',
        'usd': 'Currency', 'million_vnd': 'Currency',
        '1000_m3': 'Volume',
        'million_trees': 'Count',
        'percent': 'Ratio'
    }

    df['unit_category'] = df['unit'].map(UNIT_CATEGORIES)

    df['date'] = pd.to_datetime(
        df['year'].astype(str) + '-' +
        df['month'].astype(str).str.zfill(2) + '-01'
    )

    return df


def show():
    st.title('🌾 Agriculture Yearly Report')
    st.markdown("Analysis of agricultural production, area, and trade values.")

    st.sidebar.header("Agriculture Filters")

    uploaded_csv = st.sidebar.file_uploader(
        "Upload CSV data",
        type=["csv"]
    )

    if uploaded_csv is not None:
        st.sidebar.success(f"Using uploaded file: {uploaded_csv.name}")

    df = load_data(uploaded_csv)

    geo_levels = sorted(df['geo_level'].dropna().unique())
    selected_geo = st.sidebar.selectbox("Geographic Level", geo_levels)

    df_geo = df[df['geo_level'] == selected_geo]

    attributes = sorted(df_geo['attribute'].dropna().unique())
    selected_attrs = st.sidebar.multiselect(
        "Attributes",
        attributes,
        default=[attributes[0]] if attributes else []
    )

    if not selected_attrs:
        st.warning("Please select at least one attribute.")
        return

    # unit consistency check
    unit_categories = (
        df_geo[df_geo['attribute'].isin(selected_attrs)]
        ['unit_category']
        .dropna()
        .unique()
    )

    if len(unit_categories) > 1:
        st.error(
            f"⚠️ Unit mismatch across attributes: {', '.join(unit_categories)}"
        )
        return

    # commodity filter
    commodities = sorted(
        df_geo[df_geo['attribute'].isin(selected_attrs)]
        ['commodity']
        .dropna()
        .unique()
    )

    selected_commodities = st.sidebar.multiselect(
        "Commodities",
        commodities,
        default=commodities
    )

    commodity_mode = st.sidebar.radio(
        "Commodity Mode",
        ["Aggregate", "Split"],
        horizontal=True
    )

    filtered_df = df_geo[
        (df_geo['attribute'].isin(selected_attrs)) &
        (df_geo['commodity'].isin(selected_commodities))
    ].copy()

    if filtered_df.empty:
        st.info("No data for current selection.")
        return

    c1, c2, c3 = st.columns(3)

    c1.metric("Total Value", f"{filtered_df['normalized_value'].sum():,.0f}")
    c2.metric(
        "Avg Annual Value",
        f"{filtered_df.groupby('year')['normalized_value'].sum().mean():,.0f}"
    )
    c3.metric("Records", f"{len(filtered_df):,}")

    st.divider()

    st.subheader("Trend Analysis")

    if commodity_mode == "Aggregate":
        ts = (
            filtered_df
            .groupby(['date', 'attribute'])['normalized_value']
            .sum()
            .reset_index()
        )
        ts['series'] = ts['attribute']

    else:
        ts = (
            filtered_df
            .groupby(['date', 'attribute', 'commodity'])['normalized_value']
            .sum()
            .reset_index()
        )

        if len(selected_attrs) == 1:
            ts['series'] = ts['commodity']
        else:
            ts['series'] = ts['attribute'] + ' | ' + ts['commodity']

    fig1 = px.line(
        ts,
        x='date',
        y='normalized_value',
        color='series',
        title='Value Over Time',
        labels={'normalized_value': 'Normalized Value', 'date': 'Date'}
    )

    fig1.update_traces(line_width=3)
    fig1.update_layout(
        hovermode="x unified",
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.35,
            xanchor='center',
            x=0.5
        )
    )

    st.plotly_chart(fig1, use_container_width=True)
