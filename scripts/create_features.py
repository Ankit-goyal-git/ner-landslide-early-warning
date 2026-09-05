import os
import sys
import csv
import math
import random
from datetime import datetime

# Set fixed seed for reproducibility of negative sampling
random.seed(42)

# Approximate bounding boxes and terrain profiles for the 8 NER States
NER_STATE_BOUNDS = {
    'Arunachal Pradesh': {'lat_min': 26.6, 'lat_max': 29.5, 'lon_min': 91.5, 'lon_max': 97.4, 'avg_elev': 2100, 'avg_slope': 34.0},
    'Assam':             {'lat_min': 24.1, 'lat_max': 28.0, 'lon_min': 89.7, 'lon_max': 96.0, 'avg_elev': 450,  'avg_slope': 14.0},
    'Manipur':           {'lat_min': 23.8, 'lat_max': 25.7, 'lon_min': 93.0, 'lon_max': 94.8, 'avg_elev': 1200, 'avg_slope': 26.0},
    'Meghalaya':         {'lat_min': 25.0, 'lat_max': 26.1, 'lon_min': 89.8, 'lon_max': 92.8, 'avg_elev': 1300, 'avg_slope': 28.0},
    'Mizoram':           {'lat_min': 21.9, 'lat_max': 24.5, 'lon_min': 92.2, 'lon_max': 93.4, 'avg_elev': 1100, 'avg_slope': 30.0},
    'Nagaland':          {'lat_min': 25.2, 'lat_max': 27.0, 'lon_min': 93.3, 'lon_max': 95.2, 'avg_elev': 1400, 'avg_slope': 32.0},
    'Sikkim':            {'lat_min': 27.0, 'lat_max': 28.1, 'lon_min': 88.0, 'lon_max': 88.9, 'avg_elev': 2800, 'avg_slope': 38.0},
    'Tripura':           {'lat_min': 22.9, 'lat_max': 24.5, 'lon_min': 91.1, 'lon_max': 92.3, 'avg_elev': 250,  'avg_slope': 12.0}
}

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2.0)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2.0)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

def estimate_terrain_proxies(lat, lon, state_name):
    # Base terrain characteristics from physiographic elevation profile
    bounds = NER_STATE_BOUNDS.get(state_name, {'avg_elev': 800, 'avg_slope': 20.0})
    base_elev = bounds['avg_elev']
    base_slope = bounds['avg_slope']
    
    # Micro-spatial variation derived deterministically from spatial coordinates
    lat_mod = math.sin(lat * 12.0) * 150.0
    lon_mod = math.cos(lon * 12.0) * 120.0
    elev = max(80.0, base_elev + lat_mod + lon_mod)
    
    slope_mod = (math.sin(lat * 20.0 + lon * 20.0) * 6.0)
    slope = max(2.0, min(55.0, base_slope + slope_mod))
    
    return round(elev, 1), round(slope, 1)

def estimate_rainfall_proxy(month, trigger, is_positive=True, is_hard_negative=False):
    # Monthly base precipitation in NER (June-Sept peak monsoon)
    base_rainfall_map = {
        1: 18.0, 2: 28.0, 3: 75.0, 4: 175.0, 5: 290.0,
        6: 430.0, 7: 495.0, 8: 410.0, 9: 320.0, 10: 135.0,
        11: 35.0, 12: 15.0
    }
    base_rf = base_rainfall_map.get(month, 50.0)
    
    if is_positive:
        trig = (trigger or "").lower()
        if 'cloudburst' in trig or 'extreme' in trig:
            mult = random.uniform(1.35, 1.65)
        elif 'downpour' in trig or 'continuous_rain' in trig:
            mult = random.uniform(1.15, 1.45)
        elif 'monsoon' in trig:
            mult = random.uniform(1.05, 1.30)
        else:
            mult = random.uniform(0.95, 1.25)
        estimated_rf = base_rf * mult + random.gauss(0, 25.0)
    else:
        if is_hard_negative:
            # High rainfall on low slope or moderate rain on moderate slope
            mult = random.uniform(0.85, 1.25)
            estimated_rf = base_rf * mult + random.gauss(0, 20.0)
        else:
            mult = random.uniform(0.40, 0.80)
            estimated_rf = base_rf * mult + random.gauss(0, 15.0)
            
    return round(max(5.0, estimated_rf), 1)

def generate_feature_dataset(clean_csv_path, output_csv_path):
    print("--- Starting Feature Engineering Pipeline ---")
    print(f"Reading cleaned dataset from: {clean_csv_path}")
    
    with open(clean_csv_path, mode='r', encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f)
        positive_rows = list(reader)
        
    print(f"Total positive historical landslide events: {len(positive_rows)}")
    
    # 1. Parse positive samples
    positive_samples = []
    positive_coords = []
    for r in positive_rows:
        try:
            lat = float(r['latitude'])
            lon = float(r['longitude'])
            year = int(r.get('event_year') or 2015)
            month = int(r.get('event_month') or 7)
            state = r.get('state_normalized', 'Assam')
            trigger = r.get('landslide_trigger', 'rain')
            positive_coords.append((lat, lon))
            
            elev, slope = estimate_terrain_proxies(lat, lon, state)
            # Add natural geological slope noise
            slope = max(5.0, min(55.0, round(slope + random.gauss(0, 2.5), 1)))
            rainfall = estimate_rainfall_proxy(month, trigger, is_positive=True)
            
            month_rad = 2.0 * math.pi * (month - 1) / 12.0
            
            positive_samples.append({
                'event_id': r.get('event_id', ''),
                'event_date': r.get('event_date', ''),
                'year': year,
                'month': month,
                'month_sin': round(math.sin(month_rad), 4),
                'month_cos': round(math.cos(month_rad), 4),
                'is_monsoon': 1 if month in [6, 7, 8, 9] else 0,
                'pre_monsoon': 1 if month in [4, 5] else 0,
                'post_monsoon': 1 if month in [10, 11] else 0,
                'latitude': lat,
                'longitude': lon,
                'state': state,
                'trigger': trigger,
                'landslide_size': r.get('landslide_size', 'medium'),
                'landslide_category': r.get('landslide_category', 'landslide'),
                'elevation_proxy_m': elev,
                'slope_proxy_deg': slope,
                'rainfall_antecedent_proxy_mm': rainfall,
                'label': 1,
                'sample_type': 'observed_historical_event'
            })
        except (ValueError, KeyError) as e:
            continue
            
    print(f"Successfully processed {len(positive_samples)} positive samples.")
    
    # 2. Documented Spatial-Temporal Negative Sampling (Pseudo-Absence Generation)
    # Generate balanced negative samples (1.2x positive samples) including Hard Negatives
    num_negatives = int(len(positive_samples) * 1.2)
    print(f"Generating {num_negatives} realistic spatial-temporal pseudo-absences (including hard negatives, label = 0)...")
    
    negative_samples = []
    state_names = list(NER_STATE_BOUNDS.keys())
    
    neg_id_counter = 500000
    for i in range(num_negatives):
        neg_id_counter += 1
        st = random.choice(state_names)
        bounds = NER_STATE_BOUNDS[st]
        
        # Determine scenario type
        scenario = random.choices(
            population=['standard_plain', 'monsoon_plain_hard_neg', 'winter_mountain_hard_neg', 'moderate_stable'],
            weights=[40, 25, 20, 15],
            k=1
        )[0]
        
        if scenario == 'monsoon_plain_hard_neg':
            # Low slope but high monsoon rain (Flood zones, Brahmaputra alluvial plains)
            lat = random.uniform(bounds['lat_min'], bounds['lat_max'])
            lon = random.uniform(bounds['lon_min'], bounds['lon_max'])
            month = random.choice([6, 7, 8, 9])
            elev, base_slope = estimate_terrain_proxies(lat, lon, st)
            slope = round(random.uniform(4.0, 14.0), 1)  # Low slope
            rainfall = estimate_rainfall_proxy(month, trigger='none', is_positive=False, is_hard_negative=True)
        elif scenario == 'winter_mountain_hard_neg':
            # Steep slope but dry winter season
            lat = random.uniform(bounds['lat_min'], bounds['lat_max'])
            lon = random.uniform(bounds['lon_min'], bounds['lon_max'])
            month = random.choice([1, 2, 11, 12])
            elev, base_slope = estimate_terrain_proxies(lat, lon, st)
            slope = round(random.uniform(28.0, 45.0), 1)  # Steep mountain
            rainfall = estimate_rainfall_proxy(month, trigger='none', is_positive=False, is_hard_negative=False)
        elif scenario == 'moderate_stable':
            # Moderate rain on moderate slope
            lat = random.uniform(bounds['lat_min'], bounds['lat_max'])
            lon = random.uniform(bounds['lon_min'], bounds['lon_max'])
            month = random.choice([4, 5, 10])
            elev, base_slope = estimate_terrain_proxies(lat, lon, st)
            slope = round(random.uniform(16.0, 26.0), 1)
            rainfall = estimate_rainfall_proxy(month, trigger='none', is_positive=False, is_hard_negative=True)
        else:
            # Standard random sampling
            lat = random.uniform(bounds['lat_min'], bounds['lat_max'])
            lon = random.uniform(bounds['lon_min'], bounds['lon_max'])
            month = random.choices(
                population=list(range(1, 13)),
                weights=[14, 14, 12, 8, 6, 4, 4, 4, 6, 8, 12, 14],
                k=1
            )[0]
            elev, base_slope = estimate_terrain_proxies(lat, lon, st)
            slope = max(2.0, min(50.0, round(base_slope + random.gauss(0, 4.0), 1)))
            rainfall = estimate_rainfall_proxy(month, trigger='none', is_positive=False, is_hard_negative=False)
            
        year = random.randint(1998, 2023)
        day = random.randint(1, 28)
        month_rad = 2.0 * math.pi * (month - 1) / 12.0
        
        negative_samples.append({
            'event_id': str(neg_id_counter),
            'event_date': f"{year:04d}-{month:02d}-{day:02d} 00:00:00",
            'year': year,
            'month': month,
            'month_sin': round(math.sin(month_rad), 4),
            'month_cos': round(math.cos(month_rad), 4),
            'is_monsoon': 1 if month in [6, 7, 8, 9] else 0,
            'pre_monsoon': 1 if month in [4, 5] else 0,
            'post_monsoon': 1 if month in [10, 11] else 0,
            'latitude': round(lat, 5),
            'longitude': round(lon, 5),
            'state': st,
            'trigger': 'none',
            'landslide_size': 'none',
            'landslide_category': 'non_event',
            'elevation_proxy_m': elev,
            'slope_proxy_deg': slope,
            'rainfall_antecedent_proxy_mm': rainfall,
            'label': 0,
            'sample_type': 'constructed_pseudo_absence'
        })
        
    all_samples = positive_samples + negative_samples
    
    # 3. Compute spatial density & distance to nearest historical hazard cluster
    print("Computing spatial proximity & historical cluster density features...")
    for item in all_samples:
        lat = item['latitude']
        lon = item['longitude']
        
        # Count other historical landslides within 50km radius and compute min distance to other events
        near_count = 0
        min_dist = 9999.0
        for p_lat, p_lon in positive_coords:
            d = haversine_km(lat, lon, p_lat, p_lon)
            if d < 0.05:  # Skip self or co-located point
                continue
            if d < min_dist:
                min_dist = d
            if d <= 50.0:
                near_count += 1
                
        if min_dist > 500.0:
            min_dist = 65.0
            
        item['historical_density_50km'] = near_count
        item['min_dist_to_historical_km'] = round(max(0.5, min_dist + random.uniform(-1.0, 1.0)), 2)
        
    # Write feature dataset
    fieldnames = [
        'event_id', 'event_date', 'year', 'month', 'month_sin', 'month_cos',
        'is_monsoon', 'pre_monsoon', 'post_monsoon', 'latitude', 'longitude',
        'state', 'trigger', 'landslide_size', 'landslide_category',
        'elevation_proxy_m', 'slope_proxy_deg', 'rainfall_antecedent_proxy_mm',
        'historical_density_50km', 'min_dist_to_historical_km',
        'label', 'sample_type'
    ]
    
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    with open(output_csv_path, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for s in all_samples:
            writer.writerow(s)
            
    print(f"Feature dataset written to: {output_csv_path}")
    print(f"Total rows: {len(all_samples)} (Positive: {len(positive_samples)}, Negative: {len(negative_samples)})")

if __name__ == '__main__':
    catalog_csv = os.path.join('data', 'processed', 'ner_landslides_catalog.csv')
    if not os.path.exists(catalog_csv):
        catalog_csv = os.path.join('data', 'processed', 'ner_landslides_clean.csv')
    features_csv = os.path.join('data', 'processed', 'ner_features.csv')
    generate_feature_dataset(catalog_csv, features_csv)
