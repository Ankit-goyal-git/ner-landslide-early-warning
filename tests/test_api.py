import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True
    assert data["total_historical_events"] == 251

def test_states_endpoint():
    response = client.get("/api/states")
    assert response.status_code == 200
    states = response.json()
    assert len(states) == 8
    state_names = [s['name'] for s in states]
    assert "Sikkim" in state_names
    assert "Assam" in state_names

def test_landslides_endpoint():
    response = client.get("/api/landslides?state=Assam")
    assert response.status_code == 200
    events = response.json()
    assert len(events) == 82
    assert events[0]['state'] == "Assam"

def test_prediction_endpoint():
    payload = {
        "latitude": 27.3702,
        "longitude": 88.7334,
        "month": 7,
        "state": "Sikkim",
        "rainfall_mm": 450.0,
        "slope_deg": 35.0
    }
    response = client.post("/api/predict", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert "risk_score" in res
    assert res["risk_level"] in ["HIGH", "VERY HIGH", "MODERATE", "LOW"]
    assert "explanation" in res

def test_dashboard_summary_endpoint():
    response = client.get("/api/dashboard/summary")
    assert response.status_code == 200
    summary = response.json()
    assert summary["total_ner_landslides"] == 251
    assert "events_by_state" in summary
    assert "events_by_month" in summary

def test_citizen_reporting_endpoint():
    report_data = {
        "latitude": 27.33,
        "longitude": 88.61,
        "report_type": "crack",
        "description": "Test tension fissure detected across slope edge.",
        "state": "Sikkim",
        "severity": "HIGH",
        "reporter_name": "Test Inspector"
    }
    response = client.post("/api/reports", json=report_data)
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    
    get_res = client.get("/api/reports")
    assert get_res.status_code == 200
    assert len(get_res.json()) >= 1
