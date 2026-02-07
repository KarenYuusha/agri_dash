
import csv
import sys
from collections import defaultdict

# Set output to utf-8
sys.stdout.reconfigure(encoding='utf-8')

try:
    print("\n--- Reading data/luong_thuc.csv ---")
    attr_units = set()
    
    # Store data for aggregation check
    # Structure: test_data[attribute][geo_level] = sum(value)
    # We will pick the first attribute we encounter to test
    test_data = defaultdict(lambda: defaultdict(float))
    test_year = '2008'
    
    with open('data/luong_thuc.csv', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            attr = row['attribute']
            unit = row['unit']
            if attr and unit:
                attr_units.add((attr, unit))
            
            # Check for aggregation on year 2008
            if row['year'] == test_year and row['value']:
                try:
                    val = float(row['value'])
                    geo = row['geo_level']
                    test_data[attr][geo] += val
                except ValueError:
                    pass

    print("\n--- Attribute Unit Counts ---")
    attr_unit_counts = defaultdict(int)
    
    # Re-read to count
    f.seek(0)
    reader = csv.DictReader(f)
    for row in reader:
        if row['attribute'] and row['unit']:
            attr_unit_counts[(row['attribute'], row['unit'])] += 1
            
    sorted_counts = sorted(attr_unit_counts.items())
    for (attr, unit), count in sorted_counts:
        print(f"{attr} ({unit}): {count}")
    
    print("\n--- Check Geo Level Aggregation (Year {test_year}) ---")
    # Show stats for a few attributes
    count = 0
    for attr in sorted_attrs:
        a_name = attr[0]
        if a_name in test_data:
            national = test_data[a_name].get('National', 0)
            provincial = test_data[a_name].get('Provincial', 0)
            
            if national > 0 and provincial > 0:
                print(f"Attribute: {a_name}")
                print(f"  National Sum: {national:,.2f}")
                print(f"  Provincial Sum: {provincial:,.2f}")
                print(f"  Ratio (Prov/Nat): {provincial/national:.2f}")
                count += 1
                if count >= 5: # check 5 examples
                    break

except Exception as e:
    print(f"Error: {e}")
