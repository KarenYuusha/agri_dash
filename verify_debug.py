import sys
import os
from unittest.mock import MagicMock
import pandas as pd


def main():
    print(f"CWD: {os.getcwd()}")
    print(f"Files in CWD: {os.listdir('.')}")
    if os.path.exists('data'):
        print(f"Files in data: {os.listdir('data')}")
    else:
        print("data folder NOT FOUND")

    # Setup mock
    mock_st = MagicMock()
    # Mock cache_data to return the function as-is
    mock_st.cache_data = lambda func: func
    sys.modules['streamlit'] = mock_st

    # Local imports
    import dashboard_agri
    import dashboard_nasa
    import dashboard_disaster

    print("--- Debug Verification ---")

    # Agri
    try:
        print("Loading Agri...")
        df_agri = dashboard_agri.load_data()
        print(f"Agri Type: {type(df_agri)}")
        print(f"Agri Shape: {df_agri.shape}")
        if not df_agri.empty:
            print(df_agri.head(2))
        else:
            print("Agri DF is Empty!")
    except Exception as e:
        print(f"[FAIL] Agri: {e}")
        import traceback
        traceback.print_exc()

    # NASA
    try:
        print("\nLoading NASA...")
        df_nasa = dashboard_nasa.load_data()
        print(f"NASA Shape: {df_nasa.shape}")
    except Exception as e:
        print(f"[FAIL] NASA: {e}")


if __name__ == "__main__":
    main()
