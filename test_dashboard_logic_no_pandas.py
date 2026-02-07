
import sys

# Mocking the functions and data structures from dashboard_agri.py
UNIT_CATEGORIES = {
    '1000_ha': 'Area', 'ha': 'Area',
    '1000_ton': 'Mass', 'ton': 'Mass',
    '1000_USD': 'Currency', 'million_USD': 'Currency', 'USD': 'Currency', 'million_VND': 'Currency',
    '1000_m3': 'Volume',
    'million_trees': 'Count',
    'percent': 'Ratio'
}

def normalize_value(value, unit):
    if value == 'nan' or unit == 'nan':
        return float('nan')
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
    
    # Mock data rows
    rows = [
        {'attribute': 'Area_Planted', 'unit': '1000_ha'},
        {'attribute': 'Export_Value', 'unit': 'million_USD'},
        {'attribute': 'Area_Harvested', 'unit': 'ha'}
    ]
    
    # Test 1: Compatible Units (Area & Area)
    selected_attrs_1 = ['Area_Planted', 'Area_Harvested']
    categories_1 = set()
    for row in rows:
        if row['attribute'] in selected_attrs_1:
            cat = UNIT_CATEGORIES.get(row['unit'], 'Other')
            categories_1.add(cat)
            
    assert len(categories_1) == 1, f"Failed Test 1: Expected 1 category, got {categories_1}"
    print("PASS: Compatible Units check")

    # Test 2: Incompatible Units (Area & Currency)
    selected_attrs_2 = ['Area_Planted', 'Export_Value']
    categories_2 = set()
    for row in rows:
        if row['attribute'] in selected_attrs_2:
            cat = UNIT_CATEGORIES.get(row['unit'], 'Other')
            categories_2.add(cat)
            
    assert len(categories_2) > 1, f"Failed Test 2: Expected >1 category, got {categories_2}"
    print("PASS: Incompatible Units check")

def test_normalization():
    print("Testing Normalization...")
    val1 = normalize_value(2, '1000_ha')
    assert val1 == 2000, f"Failed 1000_ha: {val1}"
    
    val2 = normalize_value(5, 'million_trees')
    assert val2 == 5_000_000, f"Failed million_trees: {val2}"
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
