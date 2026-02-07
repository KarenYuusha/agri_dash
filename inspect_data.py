
import pandas as pd
import sys

# Set output to utf-8
sys.stdout.reconfigure(encoding='utf-8')


def inspect(file_path, file_type='csv'):
    try:
        if file_type == 'csv':
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        print(f"\n--- {file_path} ---")
        print("Columns:", list(df.columns))
        print("Head:")
        print(df.head().to_string())
        print("dtypes:")
        print(df.dtypes)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")


with open('data_inspection.txt', 'w', encoding='utf-8') as f:
    sys.stdout = f
    inspect('data/luong_thuc.csv', 'csv')
    inspect('data/nasa_power_daily.csv', 'csv')
    inspect('data/disaster-in-vietnam_1900-to-2024.xlsx', 'excel')
