import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np


@st.cache_data
def load_data():
    df = pd.read_excel('data/disaster-in-vietnam_1900-to-2024.xlsx')
    return df


def show():
    df = load_data()

    st.title('🌪️ Vietnam Disaster History (1900-2024)')
    st.markdown("Historical overview of natural disasters in Vietnam.")

    # Sidebar Filters
    st.sidebar.header('Disaster Filters')

    min_year = int(df['Start Year'].min())
    max_year = int(df['Start Year'].max())

    selected_years = st.sidebar.slider(
        "Select Year Range", min_year, max_year, (1990, max_year))

    types = sorted([x for x in df['Disaster Type'].unique() if pd.notna(x)])
    selected_types = st.sidebar.multiselect(
        "Select Disaster Types", types, default=types)

    if not selected_types:
        st.warning("Please select at least one disaster type.")
        return

    # Filter
    filtered_df = df[
        (df['Start Year'].between(selected_years[0], selected_years[1])) &
        (df['Disaster Type'].isin(selected_types))
    ]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Events", f"{len(filtered_df):,}")
    with col2:
        st.metric("Total Deaths", f"{filtered_df['Total Deaths'].sum():,.0f}")
    with col3:
        # 'Total Damage ('000 US$)' column
        damage = filtered_df["Total Damage ('000 US$)"].sum()
        st.metric("Total Damage (Est.)", f"${damage:,.0f} k")

    st.divider()

    # Visualizations

    # 1. Timeline
    st.subheader(
        f"Disaster Frequency ({selected_years[0]}-{selected_years[1]})")
    yearly_counts = filtered_df.groupby(
        'Start Year').size().reset_index(name='Count')
    fig1 = px.bar(yearly_counts, x='Start Year', y='Count',
                  title='Number of Disasters per Year')
    fig1.update_traces(marker_color='#e74c3c')
    st.plotly_chart(fig1, use_container_width=True)

    col_charts_1, col_charts_2 = st.columns(2)

    with col_charts_1:
        # 2. Distribution by Type
        st.subheader("Disaster Types")
        type_counts = filtered_df['Disaster Type'].value_counts()
        fig2 = px.pie(values=type_counts.values, names=type_counts.index,
                      title='Distribution by Type', hole=0.4)
        st.plotly_chart(fig2, use_container_width=True)

    with col_charts_2:
        # 3. Impact (Deaths)
        st.subheader("Human Impact")
        # Top 10 deadliest events
        deadliest = filtered_df.nlargest(10, 'Total Deaths')[
            ['Event Name', 'Disaster Type', 'Start Year', 'Total Deaths']]
        # Fill NaN Event Name with Type + Year
        deadliest['Event Name'] = deadliest['Event Name'].fillna(
            deadliest['Disaster Type'] + ' ' + deadliest['Start Year'].astype(str))

        fig3 = px.bar(deadliest, x='Total Deaths', y='Event Name', orientation='h',
                      title='Top 10 Deadliest Events')
        fig3.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig3, use_container_width=True)

    # 4. Map
    st.subheader("Disaster Locations")
    # Filter valid coordinates
    map_data = filtered_df.dropna(subset=['Latitude', 'Longitude'])

    if not map_data.empty:
        st.map(map_data, latitude='Latitude',
               longitude='Longitude', size=20, color='#ff000055')
    else:
        st.info("No location coordinates available for the selected data.")

    # Data Table
    with st.expander("📋 View Disaster Data"):
        st.dataframe(filtered_df[['Disaster Type', 'Start Year',
                     'Location', 'Total Deaths', "Total Damage ('000 US$)"]])
