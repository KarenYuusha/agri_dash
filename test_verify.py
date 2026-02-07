import dashboard_disaster
import dashboard_nasa
import dashboard_agri
import sys
from unittest.mock import MagicMock

# 1. Force mock streamlit into sys.modules
mock_st = MagicMock()
sys.modules['streamlit'] = mock_st

# 2. Also mock extra streamlit modules that might be imported internally if the mock isn't sufficient
# (Though usually sys.modules['streamlit'] is enough if done first)

# 3. Now import the user modules


def main():
    print("--- Starting Verification ---")

    # Agri
    try:
        df = dashboard_agri.load_data()
        print(
            f"[OK] Agri Data: {df.shape} rows. Cols: {list(df.columns)[:3]}...")
    except Exception as e:
        print(f"[FAIL] Agri: {e}")

    # NASA
    try:
        df = dashboard_nasa.load_data()
        print(
            f"[OK] NASA Data: {df.shape} rows. Cols: {list(df.columns)[:3]}...")
    except Exception as e:
        print(f"[FAIL] NASA: {e}")

    # Disaster
    try:
        df = dashboard_disaster.load_data()
        print(
            f"[OK] Disaster Data: {df.shape} rows. Cols: {list(df.columns)[:3]}...")
    except Exception as e:
        print(f"[FAIL] Disaster: {e}")

    print("--- Verification Finished ---")


if __name__ == "__main__":
    main()
