import pandas as pd
import dashboard_disaster
import dashboard_nasa
import dashboard_agri
import sys
from unittest.mock import MagicMock

# Mock streamlit BEFORE importing it or any module that imports it
mock_st = MagicMock()
mock_st.cache_data = lambda func: func
mock_st.sidebar = MagicMock()
mock_st.columns = lambda n: [MagicMock() for _ in range(n)]
mock_st.plotly_chart = MagicMock()
mock_st.title = MagicMock()
mock_st.markdown = MagicMock()
mock_st.header = MagicMock()
mock_st.subheader = MagicMock()
mock_st.metric = MagicMock()
mock_st.divider = MagicMock()
mock_st.dataframe = MagicMock()
mock_st.map = MagicMock()
mock_st.expander = lambda x: MagicMock()
mock_st.set_page_config = MagicMock()

sys.modules['streamlit'] = mock_st

# Now import the modules


def test_loading():
    print("Testing Agriculture Data Loading...")
    try:
        df_agri = dashboard_agri.load_data()
        print(f"Agri Data Loaded. Shape: {df_agri.shape}")
        assert 'normalized_value' in df_agri.columns
    except Exception as e:
        print(f"FAILED Agri: {e}")

    print("\nTesting NASA Data Loading...")
    try:
        df_nasa = dashboard_nasa.load_data()
        print(f"NASA Data Loaded. Shape: {df_nasa.shape}")
        assert 'date_parsed' in df_nasa.columns
    except Exception as e:
        print(f"FAILED NASA: {e}")

    print("\nTesting Disaster Data Loading...")
    try:
        df_disaster = dashboard_disaster.load_data()
        print(f"Disaster Data Loaded. Shape: {df_disaster.shape}")
        assert 'Start Year' in df_disaster.columns
    except Exception as e:
        print(f"FAILED Disaster: {e}")

    print("\nTest Complete.")


if __name__ == "__main__":
    test_loading()
