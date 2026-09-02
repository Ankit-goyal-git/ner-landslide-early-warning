import os
import sys
import csv
import math
import re
import shutil
from datetime import datetime

def normalize_column_name(col):
    # lowercase, trim, replace spaces with _, remove punctuation
    col = col.strip().lower()
    col = re.sub(r'[^\w\s]', '', col)
    col = re.sub(r'\s+', '_', col)
    return col

def parse_date(date_str):
    if not date_str or not date_str.strip():
        return None
    date_str = date_str.strip()
    
    # Common formats in NASA GLC:
    # '7/29/2010 23:00', '08-01-2015 00:00', '1/19/2007 0:00', '2014-05-12 10:30:00', '04-01-2014', '7/31/2009'
    formats = [
        '%m/%d/%Y %H:%M',
        '%m-%d-%Y %H:%M',
        '%d-%m-%Y %H:%M',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H:%M',
        '%m/%d/%Y %I:%M:%S %p',
        '%m/%d/%Y',
        '%m-%d-%Y',
        '%d-%m-%Y',
        '%Y-%m-%d',
        '%d/%m/%Y %H:%M',
        '%d/%m/%Y'
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            pass
            
    # Try regex fallback for tricky dates
    m = re.match(r'(\d{1,4})[/-](\d{1,2})[/-](\d{1,4})', date_str)
    if m:
        p1, p2, p3 = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if p1 > 1000: # YYYY-MM-DD
            try:
                return datetime(p1, p2, p3)
            except ValueError:
                pass
        elif p3 > 1000: # MM-DD-YYYY or DD-MM-YYYY
            try:
                return datetime(p3, p1, p2)
            except ValueError:
                try:
                    return datetime(p3, p2, p1)
                except ValueError:
                    pass
    return None

NER_CANONICAL_STATES = {
    'arunachal pradesh': 'Arunachal Pradesh',
    'arunachal': 'Arunachal Pradesh',
    'assam': 'Assam',
    'asom': 'Assam',
    'manipur': 'Manipur',
    'meghalaya': 'Meghalaya',
    'mizoram': 'Mizoram',
    'nagaland': 'Nagaland',
    'sikkim': 'Sikkim',
    'tripura': 'Tripura'
}

def normalize_state(admin_division, country, lat, lon):
    if not admin_division:
        admin_division = ""
    admin_clean = admin_division.lower().strip()
    
    for alias, canonical in NER_CANONICAL_STATES.items():
        # Match whole word or substring
        if re.search(r'\b' + re.escape(alias) + r'\b', admin_clean) or alias in admin_clean:
            return canonical, "administrative"
            
    return None, "missing"

def clean_data(raw_path, processed_path, quality_report_path):
    print(f"--- Starting Landslide Data Cleaning Pipeline ---")
    print(f"Source: {raw_path}")
    print(f"Destination: {processed_path}")
    
    os.makedirs(os.path.dirname(processed_path), exist_ok=True)
    os.makedirs(os.path.dirname(quality_report_path), exist_ok=True)
    
    with open(raw_path, mode='r', encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f)
        raw_headers = reader.fieldnames
        rows = list(reader)
        
    total_records = len(rows)
    print(f"Total raw records read: {total_records}")
    
    # 4.1 Column Normalization mapping
    norm_col_map = {orig: normalize_column_name(orig) for orig in raw_headers}
    
    # Metrics tracking
    valid_coords_count = 0
    invalid_coords_count = 0
    suspicious_coords_count = 0
    missing_dates_count = 0
    invalid_dates_count = 0
    duplicate_rows_count = 0
    
    ner_records = []
    non_ner_count = 0
    
    state_distribution = {s: 0 for s in ['Arunachal Pradesh', 'Assam', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Sikkim', 'Tripura']}
    trigger_distribution = {}
    temporal_year = {}
    temporal_month = {}
    ner_lats = []
    ner_lons = []
    
    seen_hashes = set()
    
    # Define processed fields
    # Standard columns from normalized + derived features
    base_normalized_cols = [norm_col_map[c] for c in raw_headers]
    derived_cols = [
        'event_year',
        'event_month',
        'event_day',
        'event_month_sin',
        'event_month_cos',
        'coordinate_valid',
        'state_normalized',
        'is_ner',
        'state_assignment_method'
    ]
    
    # Combine uniquely preserving order
    output_headers = []
    for c in base_normalized_cols:
        if c not in output_headers:
            output_headers.append(c)
    for c in derived_cols:
        if c not in output_headers:
            output_headers.append(c)
            
    for row in rows:
        row_hash = tuple(row.items())
        if row_hash in seen_hashes:
            duplicate_rows_count += 1
            continue
        seen_hashes.add(row_hash)
        
        # Build normalized dictionary
        clean_row = {norm_col_map[k]: v.strip() for k, v in row.items()}
        
        # Date cleaning
        date_raw = clean_row.get('event_date', '')
        parsed_dt = parse_date(date_raw)
        
        if not date_raw:
            missing_dates_count += 1
            clean_row['event_year'] = ''
            clean_row['event_month'] = ''
            clean_row['event_day'] = ''
            clean_row['event_month_sin'] = ''
            clean_row['event_month_cos'] = ''
        elif parsed_dt is None:
            invalid_dates_count += 1
            clean_row['event_year'] = ''
            clean_row['event_month'] = ''
            clean_row['event_day'] = ''
            clean_row['event_month_sin'] = ''
            clean_row['event_month_cos'] = ''
        else:
            clean_row['event_date'] = parsed_dt.strftime('%Y-%m-%d %H:%M:%S')
            clean_row['event_year'] = str(parsed_dt.year)
            clean_row['event_month'] = str(parsed_dt.month)
            clean_row['event_day'] = str(parsed_dt.day)
            # Cyclical temporal encoding for season/monsoon dynamics
            month_rad = 2.0 * math.pi * (parsed_dt.month - 1) / 12.0
            clean_row['event_month_sin'] = f"{math.sin(month_rad):.4f}"
            clean_row['event_month_cos'] = f"{math.cos(month_rad):.4f}"

        # Coordinate cleaning
        lat_str = clean_row.get('latitude', '')
        lon_str = clean_row.get('longitude', '')
        coord_valid = False
        parsed_lat = None
        parsed_lon = None
        
        try:
            if lat_str and lon_str:
                parsed_lat = float(lat_str)
                parsed_lon = float(lon_str)
                if -90.0 <= parsed_lat <= 90.0 and -180.0 <= parsed_lon <= 180.0:
                    coord_valid = True
                    valid_coords_count += 1
                    # Check India bounding box sanity (Lat ~ 6 to 38, Lon ~ 68 to 98)
                    cntry = clean_row.get('country_name', '').lower()
                    if cntry == 'india' and not (6.0 <= parsed_lat <= 38.0 and 68.0 <= parsed_lon <= 98.5):
                        suspicious_coords_count += 1
                else:
                    invalid_coords_count += 1
            else:
                invalid_coords_count += 1
        except ValueError:
            invalid_coords_count += 1
            
        clean_row['coordinate_valid'] = 'True' if coord_valid else 'False'
        
        # NER State Normalization
        admin_division = clean_row.get('admin_division_name', '')
        country = clean_row.get('country_name', '')
        norm_state, assign_method = normalize_state(admin_division, country, parsed_lat, parsed_lon)
        
        clean_row['state_normalized'] = norm_state if norm_state else ''
        clean_row['is_ner'] = 'True' if norm_state else 'False'
        clean_row['state_assignment_method'] = assign_method
        
        if norm_state and coord_valid:
            ner_records.append(clean_row)
            state_distribution[norm_state] += 1
            
            # Triggers
            trig = clean_row.get('landslide_trigger', 'unknown')
            if not trig:
                trig = 'unknown'
            trigger_distribution[trig] = trigger_distribution.get(trig, 0) + 1
            
            # Temporal
            if parsed_dt:
                yr = str(parsed_dt.year)
                mo = parsed_dt.strftime('%B')
                temporal_year[yr] = temporal_year.get(yr, 0) + 1
                temporal_month[mo] = temporal_month.get(mo, 0) + 1
                
            if parsed_lat is not None and parsed_lon is not None:
                ner_lats.append(parsed_lat)
                ner_lons.append(parsed_lon)
        else:
            non_ner_count += 1

    # Write cleaned NER dataset
    with open(processed_path, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=output_headers)
        writer.writeheader()
        for r in ner_records:
            # Ensure all keys exist
            row_out = {k: r.get(k, '') for k in output_headers}
            writer.writerow(row_out)
            
    print(f"Cleaned NER dataset written to: {processed_path}")
    print(f"Total valid NER records saved: {len(ner_records)}")
    
    # Generate Data Quality Report
    lat_min_str = f"{min(ner_lats):.4f}" if ner_lats else "N/A"
    lat_max_str = f"{max(ner_lats):.4f}" if ner_lats else "N/A"
    lon_min_str = f"{min(ner_lons):.4f}" if ner_lons else "N/A"
    lon_max_str = f"{max(ner_lons):.4f}" if ner_lons else "N/A"
    
    # Month order
    month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    
    report_content = f"""# Data Quality & NER Landslide Inventory Report

## 1. Dataset Summary
- **Total Input Records**: {total_records}
- **Cleaned NER Records**: {len(ner_records)}
- **Non-NER Records**: {non_ner_count}
- **Valid Coordinate Records**: {valid_coords_count}
- **Invalid Coordinate Records**: {invalid_coords_count}
- **Suspicious Coordinates Flagged**: {suspicious_coords_count}
- **Missing / Invalid Dates**: {missing_dates_count + invalid_dates_count}
- **Duplicate Records Removed**: {duplicate_rows_count}

---

## 2. North-East India (NER) State Distribution
| State | Number of Events | Percentage of NER Total |
| :--- | :---: | :---: |
"""
    for st, count in sorted(state_distribution.items(), key=lambda x: -x[1]):
        pct = (count / len(ner_records) * 100) if len(ner_records) > 0 else 0
        report_content += f"| {st} | {count} | {pct:.2f}% |\n"
        
    report_content += f"| **Total** | **{len(ner_records)}** | **100.00%** |\n\n---\n\n"
    report_content += "## 3. Landslide Trigger Distribution (NER)\n\n"
    report_content += "| Primary Trigger | Number of Events | Percentage |\n| :--- | :---: | :---: |\n"
    for trig, count in sorted(trigger_distribution.items(), key=lambda x: -x[1]):
        pct = (count / len(ner_records) * 100) if len(ner_records) > 0 else 0
        report_content += f"| {trig} | {count} | {pct:.2f}% |\n"
        
    report_content += "\n---\n\n## 4. Temporal Distribution\n\n"
    report_content += "### Events by Year\n\n| Year | Number of Events |\n| :--- | :---: |\n"
    for yr, count in sorted(temporal_year.items()):
        report_content += f"| {yr} | {count} |\n"
        
    report_content += "\n### Events by Month (Monsoon Dynamics)\n\n| Month | Number of Events |\n| :--- | :---: |\n"
    for mo in month_order:
        count = temporal_month.get(mo, 0)
        report_content += f"| {mo} | {count} |\n"
        
    report_content += "\n---\n\n## 5. Geographic Bounds (NER Region)\n"
    report_content += f"- **Latitude Min**: {lat_min_str}\n"
    report_content += f"- **Latitude Max**: {lat_max_str}\n"
    report_content += f"- **Longitude Min**: {lon_min_str}\n"
    report_content += f"- **Longitude Max**: {lon_max_str}\n"
    report_content += "\n*Note: All values reflect actual historical records from the NASA Global Landslide Catalog without synthetic interpolation.*"
    
    with open(quality_report_path, mode='w', encoding='utf-8') as f:
        f.write(report_content)
        
    print(f"Data Quality Report written to: {quality_report_path}")

if __name__ == '__main__':
    raw_csv = os.path.join('data', 'raw', 'LandSlide Dataset.csv')
    if not os.path.exists(raw_csv) and os.path.exists('LandSlide Dataset.csv'):
        os.makedirs(os.path.join('data', 'raw'), exist_ok=True)
        shutil.copy('LandSlide Dataset.csv', raw_csv)
        print(f"Copied 'LandSlide Dataset.csv' to '{raw_csv}'")
        
    processed_csv = os.path.join('data', 'processed', 'ner_landslides_clean.csv')
    report_file = os.path.join('reports', 'data_quality_report.md')
    
    clean_data(raw_csv, processed_csv, report_file)
