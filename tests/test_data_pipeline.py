import os
import csv
import pytest

def test_raw_data_exists():
    assert os.path.exists(os.path.join("data", "raw", "LandSlide Dataset.csv")) or os.path.exists("LandSlide Dataset.csv")

def test_cleaned_data_exists_and_valid():
    cleaned_path = os.path.join("data", "processed", "ner_landslides_clean.csv")
    assert os.path.exists(cleaned_path), "Cleaned dataset does not exist"
    
    with open(cleaned_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
    assert len(rows) == 251, f"Expected 251 cleaned NER events, found {len(rows)}"
    
    valid_states = {'Arunachal Pradesh', 'Assam', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Sikkim', 'Tripura'}
    for r in rows:
        assert r['state_normalized'] in valid_states
        lat = float(r['latitude'])
        lon = float(r['longitude'])
        assert -90.0 <= lat <= 90.0
        assert -180.0 <= lon <= 180.0
        assert r['coordinate_valid'] == 'True'
        assert r['is_ner'] == 'True'

def test_feature_dataset_exists():
    feat_path = os.path.join("data", "processed", "ner_features.csv")
    assert os.path.exists(feat_path), "Engineered feature dataset does not exist"
    
    with open(feat_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
    assert len(rows) >= 1500
    positives = [r for r in rows if r['label'] == '1']
    negatives = [r for r in rows if r['label'] == '0']
    assert len(positives) >= 1000
    assert len(negatives) >= 500
