
import pandas as pd
import numpy as np

# Mocking the functions and data structures from dashboard_agri.py
UNIT_CATEGORIES = {
    '1000_ha': 'Area', 'ha': 'Area',
    '1000_ton': 'Mass', 'ton': 'Mass',
    '1000_USD': 'Currency', 'million_USD': 'Currency', 'USD': 'Currency', 'million_VND': 'Currency',
    '1000_m3': 'Volume',
    'million_trees': 'Count',
    'percent': 'Ratio'
}

def normalize_value(row):
    value, unit = row['value'], row['unit']
    if pd.isna(value) or pd.isna(unit):
        return np.nan
    multipliers = {
        '1000_ha': 1000, 'ha': 1,
        '1000_USD': 1000, 'million_USD': 1_000_000, 'USD': 1,
        'million_VND': 1, 
        '1000_ton': 1000, 'ton': 1,
        '1000_m3': 1000,
        'million_trees': 1_000_000,
        'percent': 1
    }
    return value * multipliers.get(unit, 1)

def test_unit_consistency():
    print("Testing Unit Consistency Logic...")
    
    # Mock DF
    data = {
        'attribute': ['Area_Planted', 'Export_Value', 'Area_Harvested'],
        'unit': ['1000_ha', 'million_USD', 'ha'],
        'value': [10, 5, 20]
    }
    df = pd.DataFrame(data)
    df['unit_category'] = df['unit'].map(UNIT_CATEGORIES).fillna('Other')
    
    # Test 1: Compatible Units (Area & Area)
    selected_attrs_1 = ['Area_Planted', 'Area_Harvested']
    selected_units_1 = df[df['attribute'].isin(selected_attrs_1)]['unit_category'].unique()
    assert len(selected_units_1) == 1, f"Failed Test 1: Expected 1 category, got {selected_units_1}"
    print("PASS: Compatible Units check")

    # Test 2: Incompatible Units (Area & Currency)
    selected_attrs_2 = ['Area_Planted', 'Export_Value']
    selected_units_2 = df[df['attribute'].isin(selected_attrs_2)]['unit_category'].unique()
    assert len(selected_units_2) > 1, f"Failed Test 2: Expected >1 category, got {selected_units_2}"
    print("PASS: Incompatible Units check")

def test_normalization():
    print("Testing Normalization...")
    row = {'value': 2, 'unit': '1000_ha'}
    norm = normalize_value(row)
    assert norm == 2000, f"Failed 1000_ha: {norm}"
    
    row2 = {'value': 5, 'unit': 'million_trees'}
    norm2 = normalize_value(row2)
    assert norm2 == 5_000_000, f"Failed million_trees: {norm2}"
    print("PASS: Normalization logic")

if __name__ == "__main__":
    try:
        test_unit_consistency()
        test_normalization()
        print("\nAll Tests Passed!")
    except AssertionError as e:
        print(f"\nTEST FAILED: {e}")
    except Exception as e:
        print(f"\nERROR: {e}")
