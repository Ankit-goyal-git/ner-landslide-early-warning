import os
import json
import joblib
import pytest
from backend.services.model_service import model_service

def test_model_artifact_exists():
    assert os.path.exists("models/landslide_model.pkl")
    assert os.path.exists("models/metadata.json")

def test_model_prediction_schema():
    pred = model_service.predict(
        lat=27.3341,
        lon=88.6083,
        month=7,
        state="Sikkim"
    )
    assert "risk_score" in pred
    assert 0.0 <= pred['risk_score'] <= 1.0
    assert pred['risk_level'] in ['LOW', 'MODERATE', 'HIGH', 'VERY HIGH']
    assert "confidence" in pred
    assert "explanation" in pred
    assert len(pred['explanation']) > 10
    assert "contributing_factors" in pred
    assert "Rainfall Saturation Index" in pred['contributing_factors']

def test_model_dry_vs_monsoon_sensitivity():
    # Dry season prediction
    dry_pred = model_service.predict(lat=26.14, lon=91.78, month=1, state="Assam", custom_rainfall=10.0)
    # Peak monsoon prediction
    monsoon_pred = model_service.predict(lat=26.14, lon=91.78, month=7, state="Assam", custom_rainfall=480.0)
    
    assert monsoon_pred['risk_score'] >= dry_pred['risk_score']
