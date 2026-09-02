import os
import sys
import json
import csv
import math
from collections import Counter
from datetime import datetime

def profile_csv(file_path):
    print(f"Profiling dataset: {file_path}")
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return

    # Let's inspect using csv reader to avoid dependency failures if pandas is not yet installed
    with open(file_path, mode='r', encoding='utf-8', errors='replace') as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)

    num_rows = len(rows)
    num_cols = len(header)
    print(f"File: {os.path.basename(file_path)}")
    print(f"Rows: {num_rows}")
    print(f"Columns: {num_cols}")
    print("Column names:", header)

    # Missing counts
    missing_counts = {col: 0 for col in header}
    types_detected = {col: set() for col in header}
    unique_vals = {col: set() for col in header}
    num_min_max = {}

    # Likely column detection
    col_lower = [c.lower() for c in header]
    
    def find_col(candidates):
        for cand in candidates:
            for idx, c in enumerate(col_lower):
                if cand == c or cand in c:
                    return header[idx], idx
        return None, -1

    lat_col, lat_idx = find_col(['latitude', 'lat'])
    lon_col, lon_idx = find_col(['longitude', 'long', 'lon', 'lng'])
    date_col, date_idx = find_col(['event_date', 'date', 'datetime'])
    country_col, country_idx = find_col(['country_name', 'country', 'country_code'])
    state_col, state_idx = find_col(['admin_division_name', 'state', 'province', 'region', 'admin_division'])
    trigger_col, trigger_idx = find_col(['landslide_trigger', 'trigger'])
    category_col, cat_idx = find_col(['landslide_category', 'category', 'type', 'landslide_type'])
    size_col, size_idx = find_col(['landslide_size', 'size'])
    fatality_col, fat_idx = find_col(['fatality_count', 'fatalities', 'deaths'])
    injury_col, inj_idx = find_col(['injury_count', 'injuries'])

    print(f"\n--- Detected Likely Columns ---")
    print(f"Likely latitude column: {lat_col}")
    print(f"Likely longitude column: {lon_col}")
    print(f"Likely date column: {date_col}")
    print(f"Likely country column: {country_col}")
    print(f"Likely state column: {state_col}")
    print(f"Likely trigger column: {trigger_col}")
    print(f"Likely category/type column: {category_col}")
    print(f"Likely size column: {size_col}")
    print(f"Likely fatalities column: {fatality_col}")
    print(f"Likely injuries column: {injury_col}")

    # Process rows
    latitudes = []
    longitudes = []
    dates = []
    country_counts = Counter()
    state_counts = Counter()
    trigger_counts = Counter()
    ner_state_counts = Counter()
    
    ner_states = {
        'arunachal pradesh': 'Arunachal Pradesh',
        'assam': 'Assam',
        'manipur': 'Manipur',
        'meghalaya': 'Meghalaya',
        'mizoram': 'Mizoram',
        'nagaland': 'Nagaland',
        'sikkim': 'Sikkim',
        'tripura': 'Tripura'
    }

    india_count = 0
    ner_count = 0
    missing_coords = 0
    missing_dates = 0
    invalid_coords = 0
    suspicious_coords = 0
    duplicate_coord_set = set()
    coord_duplicates = 0
    row_hashes = set()
    duplicate_rows = 0

    ner_rows = []

    for row in rows:
        row_str = "||".join(row)
        if row_str in row_hashes:
            duplicate_rows += 1
        else:
            row_hashes.add(row_str)

        for idx, val in enumerate(row):
            col = header[idx]
            val_clean = val.strip()
            if not val_clean:
                missing_counts[col] += 1
            else:
                if len(unique_vals[col]) < 1000:
                    unique_vals[col].add(val_clean)

        # Latitude / Longitude
        lat_val = row[lat_idx].strip() if lat_idx >= 0 and lat_idx < len(row) else ""
        lon_val = row[lon_idx].strip() if lon_idx >= 0 and lon_idx < len(row) else ""

        has_coord = False
        parsed_lat = None
        parsed_lon = None
        if lat_val and lon_val:
            try:
                parsed_lat = float(lat_val)
                parsed_lon = float(lon_val)
                has_coord = True
                
                # Check valid bounds
                if not (-90 <= parsed_lat <= 90 and -180 <= parsed_lon <= 180):
                    invalid_coords += 1
                else:
                    latitudes.append(parsed_lat)
                    longitudes.append(parsed_lon)
                    coord_key = (round(parsed_lat, 5), round(parsed_lon, 5))
                    if coord_key in duplicate_coord_set:
                        coord_duplicates += 1
                    else:
                        duplicate_coord_set.add(coord_key)
            except ValueError:
                invalid_coords += 1
        else:
            missing_coords += 1

        # Date
        dt_val = row[date_idx].strip() if date_idx >= 0 and date_idx < len(row) else ""
        if not dt_val:
            missing_dates += 1
        else:
            dates.append(dt_val)

        # Country
        cntry_val = row[country_idx].strip() if country_idx >= 0 and country_idx < len(row) else ""
        country_counts[cntry_val] += 1

        # State / Admin
        st_val = row[state_idx].strip() if state_idx >= 0 and state_idx < len(row) else ""
        st_lower = st_val.lower().strip()
        state_counts[st_val] += 1

        # Trigger
        trig_val = row[trigger_idx].strip() if trigger_idx >= 0 and trigger_idx < len(row) else ""
        trigger_counts[trig_val] += 1

        # Check India
        is_india = (cntry_val.lower() == 'india' or (country_idx + 1 < len(row) and row[country_idx + 1].strip().upper() == 'IN'))
        if is_india:
            india_count += 1

        # Check NER
        matched_ner = None
        for ner_k, ner_std in ner_states.items():
            if ner_k in st_lower:
                matched_ner = ner_std
                break
        
        # Check if coordinates fall in NER rough bounding box (Lat: 21.5 to 29.5, Lon: 88.0 to 97.5) if in India or state matched
        if matched_ner:
            ner_count += 1
            ner_state_counts[matched_ner] += 1
            ner_rows.append((matched_ner, row))
        elif is_india and parsed_lat and parsed_lon:
            # Check if coordinates in NER area
            # Note: section 5 rules: do NOT blindly assign state if missing, but check if state was missing or differently named
            pass

    print(f"\n--- Data Quality & Summary ---")
    print(f"Total rows: {num_rows}")
    print(f"Duplicate rows: {duplicate_rows}")
    print(f"Missing coordinates count: {missing_coords} ({missing_coords/num_rows*100:.2f}%)")
    print(f"Invalid coordinates count: {invalid_coords}")
    print(f"Duplicate coordinates: {coord_duplicates}")
    print(f"Missing dates count: {missing_dates} ({missing_dates/num_rows*100:.2f}%)")
    
    if latitudes and longitudes:
        print(f"Latitude range (all): [{min(latitudes):.4f}, {max(latitudes):.4f}]")
        print(f"Longitude range (all): [{min(longitudes):.4f}, {max(longitudes):.4f}]")

    print(f"\n--- Geographic Distribution ---")
    print(f"India records: {india_count}")
    print(f"NER records: {ner_count}")
    print("NER State distribution:")
    for state_name in ['Arunachal Pradesh', 'Assam', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Sikkim', 'Tripura']:
        print(f"  {state_name}: {ner_state_counts[state_name]}")

    print("\n--- Top Triggers ---")
    for trig, count in trigger_counts.most_common(10):
        print(f"  {trig if trig else '[EMPTY]'}: {count}")

    print("\n--- Missing Percentage Per Column ---")
    for col in header:
        pct = (missing_counts[col] / num_rows) * 100
        print(f"  {col}: {missing_counts[col]} ({pct:.2f}%)")

    return {
        "num_rows": num_rows,
        "num_cols": num_cols,
        "header": header,
        "missing_coords": missing_coords,
        "missing_dates": missing_dates,
        "duplicate_rows": duplicate_rows,
        "india_count": india_count,
        "ner_count": ner_count,
        "ner_state_counts": ner_state_counts,
        "trigger_counts": trigger_counts
    }

if __name__ == '__main__':
    csv_path = sys.argv[1] if len(sys.argv) > 1 else 'LandSlide Dataset.csv'
    profile_csv(csv_path)
