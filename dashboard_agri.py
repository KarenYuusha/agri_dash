import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np


# Schema requirements
REQUIRED_COLUMNS = {
    'year',
    'month',
    'sector',
    'geo_level',
    'attribute',
    'commodity',
    'location_name',
    'value',
    'unit'
}


# Format utilities
def get_display_unit(unit):
    unit_map = {
        '1000_ha': 'ha',
        'ha': 'ha',
        '1000_ton': 'ton',
        'ton': 'ton',
        '1000_usd': 'USD',
        'million_usd': 'USD',
        'usd': 'USD',
        'million_vnd': 'VND',
        '1000_m3': 'm3',
        'million_trees': 'trees',
        'percent': '%'
    }
    return unit_map.get(unit, unit)


def format_value(value, unit, unit_category):
    if pd.isna(value):
        return "-"

    display_unit = get_display_unit(unit)

    # Ratio (percent)
    if unit_category == "Ratio":
        return f"{value:,.2f}%"

    abs_val = abs(value)

    if abs_val >= 1_000_000_000:
        scaled = value / 1_000_000_000
        suffix = "B"
    elif abs_val >= 1_000_000:
        scaled = value / 1_000_000
        suffix = "M"
    elif abs_val >= 1_000:
        scaled = value / 1_000
        suffix = "K"
    else:
        scaled = value
        suffix = ""

    if unit_category == "Currency":
        if display_unit == "USD":
            return f"${scaled:,.2f}{suffix}"
        elif display_unit == "VND":
            return f"{scaled:,.2f}{suffix} VND"
        else:
            return f"{scaled:,.2f}{suffix}"

    return f"{scaled:,.2f}{suffix} {display_unit}"


def clean_metric_label(attribute, unit):
    return f"{attribute} ({get_display_unit(unit)})"

# Data loading


@st.cache_data
def load_data(uploaded_file=None):

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_csv('./data/luong_thuc.csv')

    missing_cols = REQUIRED_COLUMNS - set(df.columns)
    if missing_cols:
        raise ValueError(
            f"Missing required columns: {', '.join(sorted(missing_cols))}"
        )

    df['unit'] = df['unit'].astype(str).str.strip().str.lower()

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

    # Metric identifier
    df['metric_id'] = (
        df['sector'].astype(str) + " | " +
        df['attribute'].astype(str) + " | " +
        df['unit'].astype(str)
    )

    return df

# Main app


def show():
    st.title("🌾 Agriculture Yearly Report")
    st.markdown("Dimension-safe agricultural analytics dashboard")

    st.sidebar.header("Filters")

    uploaded_csv = st.sidebar.file_uploader("Upload CSV", type=["csv"])

    try:
        df = load_data(uploaded_csv)
    except Exception as e:
        st.error(f"❌ {e}")
        st.stop()

    # Sector Filter
    selected_sector = st.sidebar.selectbox(
        "Sector",
        sorted(df['sector'].dropna().unique())
    )

    df_sector = df[df['sector'] == selected_sector]

    # Geographic Level
    selected_geo = st.sidebar.selectbox(
        "Geographic Level",
        sorted(df_sector['geo_level'].dropna().unique())
    )

    df_geo = df_sector[df_sector['geo_level'] == selected_geo]

    # Attribute Filter
    attributes = sorted(df_geo['attribute'].dropna().unique())
    selected_attrs = st.sidebar.multiselect(
        "Attributes",
        attributes,
        default=attributes[:1],
    )

    if not selected_attrs:
        st.warning("Select at least one attribute.")
        return

    filtered_df = df_geo[df_geo['attribute'].isin(selected_attrs)].copy()
    # Commodity Filter
    commodities = sorted(
        filtered_df['commodity'].dropna().unique()
    )

    selected_commodities = st.sidebar.multiselect(
        "Commodities",
        commodities,
        default=commodities,
    )

    commodity_mode = st.sidebar.radio(
        "Commodity Mode",
        ["Aggregate", "Split"],
        horizontal=True,
    )

    if selected_commodities and set(selected_commodities) != set(commodities):
        filtered_df = filtered_df[filtered_df['commodity'].isin(
            selected_commodities)]

    if filtered_df.empty:
        st.info("No data available.")
        return

    # KPI seciton
    metric_groups = filtered_df.groupby('metric_id')

    cols = st.columns(len(metric_groups))

    for i, (metric_id, group) in enumerate(metric_groups):

        total_value = group['normalized_value'].sum()

        unit = group['unit'].iloc[0]
        category = group['unit_category'].iloc[0]
        attribute = group['attribute'].iloc[0]

        label = clean_metric_label(attribute, unit)

        formatted_value = format_value(total_value, unit, category)

        cols[i].metric(
            label,
            formatted_value
        )
    # Trend Analysis
    st.subheader("Trend Analysis")

    show_annotations = st.toggle("Show Min/Max Annotations", value=True)

    group_cols = ['date', 'metric_id']

    if commodity_mode == "Split":
        group_cols.append('commodity')

    ts = (
        filtered_df
        .groupby(group_cols)['normalized_value']
        .sum()
        .reset_index()
    )

    if commodity_mode == "Split":
        ts['series'] = ts['metric_id'] + " | " + ts['commodity']
    else:
        ts['series'] = ts['metric_id']

    unique_metrics = ts['series'].unique()

    if len(unique_metrics) == 2:
        fig = px.line()

        for idx, series in enumerate(unique_metrics):
            sub = ts[ts['series'] == series]

            fig.add_scatter(
                x=sub['date'],
                y=sub['normalized_value'],
                mode='lines',
                name=series,
                yaxis='y1' if idx == 0 else 'y2'
            )

        fig.update_layout(
            yaxis=dict(title=unique_metrics[0]),
            yaxis2=dict(
                title=unique_metrics[1],
                overlaying='y',
                side='right'
            ),
            hovermode="x unified"
        )

    else:
        fig = px.line(
            ts,
            x='date',
            y='normalized_value',
            color='series',
            title="Value Over Time"
        )
        fig.update_layout(hovermode="x unified")

    # Annotations for highest/lowest per series
    if show_annotations:
        for series in unique_metrics:
            sub = ts[ts['series'] == series].dropna(
                subset=['normalized_value'])
            if sub.empty:
                continue

            max_row = sub.loc[sub['normalized_value'].idxmax()]
            min_row = sub.loc[sub['normalized_value'].idxmin()]

            for row, label, color in [
                (max_row, "▲ Max", "green"),
                (min_row, "▼ Min", "red")
            ]:
                fig.add_annotation(
                    x=row['date'],
                    y=row['normalized_value'],
                    text=f"{label}<br>{row['normalized_value']:,.0f}",
                    showarrow=True,
                    arrowhead=2,
                    arrowcolor=color,
                    font=dict(color=color, size=11),
                    bgcolor="white",
                    bordercolor=color,
                    borderwidth=1,
                    borderpad=3,
                    ax=0,
                    ay=-40
                )

    st.plotly_chart(fig, width='stretch')

    # Pie chart on the left, top location bar chart on the right
    show_pie = len(selected_commodities) > 1
    show_locations = filtered_df['location_name'].nunique() > 1

    if show_pie or show_locations:
        left, right = st.columns(2)

        if show_pie:
            with left:
                st.subheader("Commodity Composition")

                pie_data = (
                    filtered_df
                    .groupby('commodity')['normalized_value']
                    .sum()
                    .reset_index()
                )

                fig_pie = px.pie(
                    pie_data,
                    names='commodity',
                    values='normalized_value',
                    title=f"Share of {', '.join(selected_attrs)}",
                    hole=0.4
                )
                fig_pie.update_traces(
                    textposition='inside',
                    textinfo='percent+label'
                )
                st.plotly_chart(fig_pie, use_container_width=True)

        if show_locations:
            with right:
                st.subheader("Top 10 Locations")

                location_data = (
                    filtered_df
                    .groupby(['location_name', 'attribute'])['normalized_value']
                    .sum()
                    .reset_index()
                )

                top10 = (
                    location_data
                    .groupby('location_name')['normalized_value']
                    .sum()
                    .nlargest(10)
                    .index
                )

                location_data = location_data[location_data['location_name'].isin(
                    top10)]

                order = (
                    location_data
                    .groupby('location_name')['normalized_value']
                    .sum()
                    .sort_values(ascending=False)
                    .index.tolist()
                )

                location_data = location_data.sort_values(
                    'normalized_value', ascending=True)

                fig_loc = px.bar(
                    location_data,
                    x='normalized_value',
                    y='location_name',
                    orientation='h',
                    color='attribute' if len(selected_attrs) > 1 else None,
                    barmode='group',
                    category_orders={'location_name': order[::-1]}
                )
                fig_loc.update_layout(
                    yaxis_title=None,
                    xaxis_title=None,
                    margin=dict(l=0, r=0, t=30, b=0)
                )
                st.plotly_chart(fig_loc, use_container_width=True)

    # Monthly bar chart
    st.subheader("Seasonality")

    group_cols = ['month', 'metric_id']

    if commodity_mode == "Split":
        group_cols.append('commodity')

    seasonal = (
        filtered_df
        .groupby(group_cols)['normalized_value']
        .sum()
        .reset_index()
    )

    if commodity_mode == "Split":
        seasonal['series'] = seasonal['metric_id'] + \
            " | " + seasonal['commodity']
    else:
        seasonal['series'] = seasonal['metric_id']

    fig2 = px.bar(
        seasonal,
        x='month',
        y='normalized_value',
        color='series',
        barmode='group'
    )
    st.plotly_chart(fig2, width='stretch')

    # Show raw data
    with st.expander("📋 View Raw Data"):
        st.dataframe(
            filtered_df[
                [
                    'year', 'month', 'sector', 'attribute',
                    'commodity', 'location_name',
                    'value', 'unit', 'normalized_value'
                ]
            ].head(100),
            width='stretch'
        )
