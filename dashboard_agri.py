import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

# =========================
# Schema definition
# =========================
REQUIRED_COLUMNS = {
    'year',
    'month',
    'geo_level',
    'attribute',
    'commodity',
    'location_name',
    'value',
    'unit'
}

# =========================
# Data loading & validation
# =========================


@st.cache_data
def load_data(uploaded_file=None):
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_csv('./data/luong_thuc.csv')

    # ---- schema validation ----
    missing_cols = REQUIRED_COLUMNS - set(df.columns)
    if missing_cols:
        raise ValueError(
            f"Missing required columns: {', '.join(sorted(missing_cols))}"
        )

    # ---- normalize unit ----
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
        df['month'].astype(str).str.zfill(2) + '-01',
        errors='coerce'
    )

    return df

# =========================
# Main app
# =========================


def show():
    st.title('🌾 Agriculture Yearly Report')
    st.markdown("Analysis of agricultural production, area, and trade values.")

    st.sidebar.header("Agriculture Filters")

    # ---- CSV upload ----
    uploaded_csv = st.sidebar.file_uploader(
        "Upload CSV data",
        type=["csv"]
    )

    try:
        df = load_data(uploaded_csv)
        if uploaded_csv is not None:
            st.sidebar.success(f"Using uploaded file: {uploaded_csv.name}")
    except Exception as e:
        st.error(f"❌ Data validation error: {e}")
        st.stop()

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

    # ---- unit consistency check ----
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

    # ---- commodity filter ----
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
        ts['series'] = (
            ts['commodity']
            if len(selected_attrs) == 1
            else ts['attribute'] + ' | ' + ts['commodity']
        )

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

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Commodity Share")
        commodity_data = filtered_df[filtered_df['commodity'].notna()]
        if not commodity_data.empty:
            top_comm = (
                commodity_data
                .groupby('commodity')['normalized_value']
                .sum()
                .nlargest(10)
            )
            st.plotly_chart(
                px.pie(
                    values=top_comm.values,
                    names=top_comm.index,
                    title='Top 10 Commodities',
                    hole=0.4
                ),
                use_container_width=True
            )

    with col2:
        st.subheader("Regional Leaders")
        regional = filtered_df[
            (filtered_df['location_name'].notna()) &
            (filtered_df['location_name'] != 'cả nước')
        ]
        if not regional.empty:
            top_regions = (
                regional
                .groupby('location_name')['normalized_value']
                .sum()
                .nlargest(10)
                .sort_values()
            )
            st.plotly_chart(
                px.bar(
                    x=top_regions.values,
                    y=top_regions.index,
                    orientation='h',
                    title='Top 10 Locations'
                ),
                use_container_width=True
            )

    st.subheader("Seasonality")
    seasonal = (
        filtered_df
        .groupby(['month', 'attribute'])['normalized_value']
        .sum()
        .reset_index()
    )

    fig4 = px.bar(
        seasonal,
        x='month',
        y='normalized_value',
        color='attribute',
        barmode='group',
        title='Seasonal Pattern'
    )

    fig4.update_xaxes(
        tickmode='array',
        tickvals=list(range(1, 13)),
        ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    )

    st.plotly_chart(fig4, use_container_width=True)

    with st.expander("📋 View Raw Data"):
        st.dataframe(
            filtered_df[
                [
                    'year', 'month', 'attribute', 'commodity',
                    'location_name', 'value', 'unit', 'normalized_value'
                ]
            ].head(100),
            use_container_width=True
        )
