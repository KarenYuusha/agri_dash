import sys
from unittest.mock import MagicMock


def main():
    # Setup mock
    mock_st = MagicMock()
    sys.modules['streamlit'] = mock_st

    # Local imports to avoid auto-formatter reordering
    import dashboard_agri
    import dashboard_nasa
    import dashboard_disaster

    print("--- Starting FINAL Verification ---")
    try:
        df_agri = dashboard_agri.load_data()
        print(f"[OK] Agri: {len(df_agri)} rows")
    except Exception as e:
        print(f"[FAIL] Agri: {e}")

    try:
        df_nasa = dashboard_nasa.load_data()
        print(f"[OK] NASA: {len(df_nasa)} rows")
    except Exception as e:
        print(f"[FAIL] NASA: {e}")

    try:
        df_disaster = dashboard_disaster.load_data()
        print(f"[OK] Disaster: {len(df_disaster)} rows")
    except Exception as e:
        print(f"[FAIL] Disaster: {e}")


if __name__ == "__main__":
    main()
