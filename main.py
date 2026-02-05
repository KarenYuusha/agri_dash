import streamlit as st
import dashboard_agri
import dashboard_nasa
import dashboard_disaster

# Set page config once at the main level
st.set_page_config(
    page_title="Vietnam Data Analytics Hub",
    page_icon="🇻🇳",
    layout="wide"
)


def main():
    st.sidebar.title("Navigation")
    options = ["Home", "🌾 Agriculture", "🛰️ NASA Sensor", "🌪️ Disaster Data"]
    selection = st.sidebar.radio("Go to", options)

    if selection == "Home":
        st.title("🇻🇳 Vietnam Data Analytics Hub")
        st.markdown("""
        Welcome to the centralized analytics reports.
        
        ### Available Dashboards:
        
        - **🌾 Agriculture Report**: Analysis of production, crops, and regional data.
        - **🛰️ NASA Sensor Data**: Daily weather data including temperature, rainfall, and humidity.
        - **🌪️ Disaster Data**: Historical records of natural disasters in Vietnam (1900-2024).
        
        ---
        Select a dashboard from the sidebar to get started.
        """)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.info("📊 3 Datasets Integrated")
        with col2:
            st.info("🗺️ Interactive Maps")
        with col3:
            st.info("📈 Trend Analysis")

    elif selection == "🌾 Agriculture":
        dashboard_agri.show()

    elif selection == "🛰️ NASA Sensor":
        dashboard_nasa.show()

    elif selection == "🌪️ Disaster Data":
        dashboard_disaster.show()


if __name__ == "__main__":
    main()
