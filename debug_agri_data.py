
import pandas as pd
import sys

# Set output to utf-8
sys.stdout.reconfigure(encoding='utf-8')

try:
    df = pd.read_csv('data/luong_thuc.csv')
    
    print("\n--- Unique Attributes and Units ---")
    attr_units = df[['attribute', 'unit']].drop_duplicates().sort_values('attribute')
    print(attr_units.to_string())

    print("\n--- Check Geo Level Aggregation ---")
    # Filter for a common attribute
    test_attr = attr_units['attribute'].iloc[0]
    print(f"Testing attribute: {test_attr}")
    
    # Check 2008 data
    df_2008 = df[(df['year'] == 2008) & (df['attribute'] == test_attr)]
    
    national = df_2008[df_2008['geo_level'] == 'National']['value'].sum()
    provincial = df_2008[df_2008['geo_level'] == 'Provincial']['value'].sum()
    
    print(f"National Sum: {national}")
    print(f"Provincial Sum: {provincial}")
    
    if national > 0 and provincial > 0:
        ratio = provincial / national
        print(f"Ratio (Provincial/National): {ratio:.2f}")

    print("\n--- Sample Duplicate Check ---")
    # Check if we have multiple rows for the same year/month/location/attribute
    # This checks if summing everything blindly causes duplication
    duplicates = df.groupby(['year', 'month', 'location_name', 'attribute']).size()
    print(f"Max duplicates for a single location/time/attribute: {duplicates.max()}")
    if duplicates.max() > 1:
        print("Duplicate rows found:")
        print(duplicates[duplicates > 1].head())

except Exception as e:
    print(f"Error: {e}")
