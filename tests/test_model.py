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
    assert "risk_score_100" in pred
    assert 0 <= pred['risk_score_100'] <= 100
    assert pred['risk_level'] in ['LOW', 'MODERATE', 'HIGH', 'VERY HIGH', 'CRITICAL']
    assert "confidence" in pred
    assert "explanation" in pred
    assert len(pred['explanation']) > 10
    assert "contributing_factors" in pred
    assert "shap_contributions" in pred
    assert "Rainfall Saturation Index" in pred['contributing_factors']

def test_model_dry_vs_monsoon_sensitivity():
    # Dry season prediction
    dry_pred = model_service.predict(lat=26.14, lon=91.78, month=1, state="Assam", custom_rainfall=10.0)
    # Peak monsoon prediction
    monsoon_pred = model_service.predict(lat=26.14, lon=91.78, month=7, state="Assam", custom_rainfall=480.0)
    
    assert monsoon_pred['risk_score'] >= dry_pred['risk_score']

def test_shap_service_explanation():
    from backend.services.shap_service import shap_service
    exp = shap_service.explain_prediction(
        lat=27.3389,
        lon=88.6065,
        month=7,
        state="Sikkim",
        custom_rainfall=350.0,
        location_name="East Sikkim Test Zone"
    )
    assert exp["location"] == "East Sikkim Test Zone"
    assert "risk_score_100" in exp
    assert len(exp["features"]) >= 5
    assert len(exp["explanation_summary"]) > 10
    assert exp["features"][0]["shap_value"] is not None
    assert "impact" in exp["features"][0]

