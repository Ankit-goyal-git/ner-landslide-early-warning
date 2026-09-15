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
    assert data["total_historical_events"] >= 1000

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
    assert len(events) >= 50
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
    assert res["risk_level"] in ["HIGH", "VERY HIGH", "CRITICAL", "MODERATE", "LOW"]
    assert "explanation" in res

def test_shap_api_endpoints():
    # GET /api/explain
    res = client.get("/api/explain?lat=27.3389&lon=88.6065&state=Sikkim")
    assert res.status_code == 200
    data = res.json()
    assert "features" in data
    assert len(data["features"]) >= 5

    # GET /api/explain/global
    glob_res = client.get("/api/explain/global")
    assert glob_res.status_code == 200
    assert "features" in glob_res.json()

def test_hotspots_and_lhasa_endpoints():
    # GET /api/hotspots
    res = client.get("/api/hotspots")
    assert res.status_code == 200
    hotspots = res.json()
    assert len(hotspots) == 8
    assert hotspots[0]["risk_score_100"] >= 0

    # GET /api/nasa-lhasa/info
    lhasa_res = client.get("/api/nasa-lhasa/info")
    assert lhasa_res.status_code == 200
    assert "nrt_latency_hours" in lhasa_res.json()

def test_timeline_demo_endpoint():
    res = client.get("/api/timeline-demo")
    assert res.status_code == 200
    steps = res.json()
    assert len(steps) == 5
    assert steps[0]["step_id"] == "T-24h"

def test_dashboard_summary_endpoint():
    response = client.get("/api/dashboard/summary")
    assert response.status_code == 200
    summary = response.json()
    assert summary["total_ner_landslides"] >= 1000
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

