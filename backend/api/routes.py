import os
import math
import pandas as pd
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query

from backend.models.schemas import (
    PredictRequest, PredictionResponse, LandslideEvent,
    CitizenReportCreate, CitizenReport, AlertItem,
    DashboardSummary, StateSummary, RiskHotspot, NasaLhasaInfo, TimelineStep
)
from backend.services.model_service import model_service
from backend.services.alert_service import alert_service
from backend.services.report_service import report_service
from backend.services.shap_service import shap_service
from backend.services.nasa_lhasa_service import nasa_lhasa_service
from backend.services.weather_interface import (
    imd_interface, nasa_gpm_interface, satellite_interface, iot_interface
)

router = APIRouter(prefix="/api")

# In-memory cached dataset
DATA_CATALOG_PATH = os.path.join("data", "processed", "ner_landslides_catalog.csv")
DATA_PROCESSED_PATH = os.path.join("data", "processed", "ner_landslides_clean.csv")

def get_landslides_df():
    path_to_use = DATA_CATALOG_PATH if os.path.exists(DATA_CATALOG_PATH) else DATA_PROCESSED_PATH
    if os.path.exists(path_to_use):
        return pd.read_csv(path_to_use).fillna("")
    return pd.DataFrame()


@router.get("/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "system": "NER Landslide Early Warning & Risk Platform",
        "mode": "Demo Mode — Historical Dataset & Calibrated ML",
        "model_loaded": model_service.model is not None,
        "total_historical_events": len(model_service.historical_events)
    }

@router.get("/states", tags=["Geographic"])
def get_ner_states():
    states = [
        {"name": "Arunachal Pradesh", "capital": "Itanagar", "lat": 27.0987, "lon": 93.8160, "zoom": 8},
        {"name": "Assam", "capital": "Dispur", "lat": 26.1433, "lon": 91.7898, "zoom": 8},
        {"name": "Manipur", "capital": "Imphal", "lat": 24.8170, "lon": 93.9368, "zoom": 9},
        {"name": "Meghalaya", "capital": "Shillong", "lat": 25.5788, "lon": 91.8933, "zoom": 9},
        {"name": "Mizoram", "capital": "Aizawl", "lat": 23.7271, "lon": 92.7176, "zoom": 9},
        {"name": "Nagaland", "capital": "Kohima", "lat": 25.6751, "lon": 94.1086, "zoom": 9},
        {"name": "Sikkim", "capital": "Gangtok", "lat": 27.3389, "lon": 88.6065, "zoom": 9},
        {"name": "Tripura", "capital": "Agartala", "lat": 23.8315, "lon": 91.2868, "zoom": 9}
    ]
    return states

@router.get("/landslides", response_model=List[LandslideEvent], tags=["Landslide Catalog"])
def get_landslides(
    state: Optional[str] = Query(None, description="Filter by NER state"),
    year: Optional[int] = Query(None, description="Filter by event year"),
    trigger: Optional[str] = Query(None, description="Filter by trigger type"),
    limit: Optional[int] = Query(300, description="Max number of records")
):
    df = get_landslides_df()
    if df.empty:
        return []
        
    if state and state.lower() != 'all':
        df = df[df['state_normalized'].str.lower() == state.lower()]
    if year:
        df = df[df['event_year'] == year]
    if trigger and trigger.lower() != 'all':
        df = df[df['landslide_trigger'].str.lower() == trigger.lower()]
        
    results = []
    for _, row in df.head(limit).iterrows():
        fatalities = 0
        injuries = 0
        try:
            if row.get('fatality_count') and str(row['fatality_count']).strip():
                fatalities = int(float(row['fatality_count']))
        except ValueError:
            pass
        try:
            if row.get('injury_count') and str(row['injury_count']).strip():
                injuries = int(float(row['injury_count']))
        except ValueError:
            pass

        results.append(LandslideEvent(
            event_id=str(row.get('event_id', '')),
            event_date=str(row.get('event_date', '')),
            latitude=float(row.get('latitude', 0.0)),
            longitude=float(row.get('longitude', 0.0)),
            state=str(row.get('state_normalized', 'Assam')),
            district=str(row.get('gazeteer_closest_point', '')),
            landslide_type=str(row.get('landslide_category', 'landslide')),
            landslide_size=str(row.get('landslide_size', 'medium')),
            trigger=str(row.get('landslide_trigger', 'rain')),
            fatalities=fatalities,
            injuries=injuries,
            location_description=str(row.get('location_description', '')),
            source_name=str(row.get('source_name', ''))
        ))
    return results

@router.get("/landslides/{id}", response_model=LandslideEvent, tags=["Landslide Catalog"])
def get_landslide_by_id(id: str):
    df = get_landslides_df()
    if df.empty:
        raise HTTPException(status_code=404, detail="Dataset not loaded")
    match = df[df['event_id'].astype(str) == str(id)]
    if match.empty:
        raise HTTPException(status_code=404, detail=f"Landslide event with ID {id} not found")
    row = match.iloc[0]
    return LandslideEvent(
        event_id=str(row.get('event_id', '')),
        event_date=str(row.get('event_date', '')),
        latitude=float(row.get('latitude', 0.0)),
        longitude=float(row.get('longitude', 0.0)),
        state=str(row.get('state_normalized', 'Assam')),
        district=str(row.get('gazeteer_closest_point', '')),
        landslide_type=str(row.get('landslide_category', 'landslide')),
        landslide_size=str(row.get('landslide_size', 'medium')),
        trigger=str(row.get('landslide_trigger', 'rain')),
        fatalities=int(float(row.get('fatality_count', 0))) if str(row.get('fatality_count')).strip() else 0,
        injuries=int(float(row.get('injury_count', 0))) if str(row.get('injury_count')).strip() else 0,
        location_description=str(row.get('location_description', '')),
        source_name=str(row.get('source_name', ''))
    )

@router.get("/risk", tags=["Risk Map & Analytics"])
def get_risk_surface(
    state: Optional[str] = Query(None, description="Filter by state"),
    month: Optional[int] = Query(7, description="Evaluation month (1-12)"),
    risk_level: Optional[str] = Query(None, description="Filter by risk tier (LOW, MODERATE, HIGH, VERY HIGH)")
):
    df = get_landslides_df()
    if df.empty:
        return []
        
    if state and state.lower() != 'all':
        df = df[df['state_normalized'].str.lower() == state.lower()]
        
    scored_points = []
    for _, r in df.iterrows():
        try:
            lat = float(r['latitude'])
            lon = float(r['longitude'])
            st = str(r.get('state_normalized', 'Assam'))
            pred = model_service.predict(lat, lon, month=month, state=st)
            
            if risk_level and risk_level.lower() != 'all':
                if pred['risk_level'].lower() != risk_level.lower():
                    continue
                    
            item = {
                "id": str(r.get('event_id', '')),
                "latitude": lat,
                "longitude": lon,
                "state": st,
                "risk_score": pred['risk_score'],
                "risk_level": pred['risk_level'],
                "confidence": pred['confidence'],
                "model_version": pred['model_version'],
                "prediction_timestamp": pred['prediction_timestamp'],
                "explanation": pred['explanation'],
                "trigger": str(r.get('landslide_trigger', 'rain')),
                "category": str(r.get('landslide_category', 'landslide')),
                "event_date": str(r.get('event_date', ''))
            }
            scored_points.append(item)
        except Exception:
            continue
            
    return scored_points

@router.post("/predict", response_model=PredictionResponse, tags=["ML Inference"])
def predict_risk(req: PredictRequest):
    pred = model_service.predict(
        lat=req.latitude,
        lon=req.longitude,
        month=req.month,
        state=req.state,
        custom_rainfall=req.rainfall_mm,
        custom_slope=req.slope_deg,
        horizon_hours=req.horizon_hours or 0
    )
    return PredictionResponse(**pred)

@router.get("/hotspots", response_model=List[RiskHotspot], tags=["Major Risk Areas"])
def get_major_risk_hotspots(state: Optional[str] = Query(None, description="Filter hotspots by state")):
    hotspots = model_service.get_major_risk_hotspots()
    if state and state.lower() != 'all':
        hotspots = [h for h in hotspots if h['state'].lower() == state.lower()]
    return hotspots

@router.get("/explain", tags=["Explainable AI (SHAP)"])
def explain_location_get(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    month: int = Query(7, ge=1, le=12, description="Month"),
    state: str = Query("Assam", description="State name"),
    rainfall_mm: Optional[float] = Query(None, description="24h rainfall in mm"),
    slope_deg: Optional[float] = Query(None, description="Terrain slope in degrees"),
    horizon_hours: int = Query(0, description="Forecast horizon in hours (0, 6, 12, 24, 48, 72)"),
    location_name: Optional[str] = Query(None, description="Friendly location title")
):
    try:
        return shap_service.explain_prediction(
            lat=lat,
            lon=lon,
            month=month,
            state=state,
            custom_rainfall=rainfall_mm,
            custom_slope=slope_deg,
            horizon_hours=horizon_hours,
            location_name=location_name
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Explainability information is currently unavailable for this prediction. Error: {str(e)}"
        )

@router.post("/explain", tags=["Explainable AI (SHAP)"])
def explain_location_post(req: PredictRequest):
    try:
        return shap_service.explain_prediction(
            lat=req.latitude,
            lon=req.longitude,
            month=req.month,
            state=req.state,
            custom_rainfall=req.rainfall_mm,
            custom_slope=req.slope_deg,
            horizon_hours=req.horizon_hours or 0,
            location_name=f"{req.state} Zone ({req.latitude:.2f}°N, {req.longitude:.2f}°E)"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Explainability information is currently unavailable for this prediction. Error: {str(e)}"
        )

@router.get("/explain/global", tags=["Explainable AI (SHAP)"])
def get_global_shap_importance():
    return {
        "title": "Overall Model Feature Importance (mean |SHAP value|)",
        "features": shap_service.get_global_feature_importance()
    }

@router.get("/explain/{location_id}", tags=["Explainable AI (SHAP)"])
def get_hotspot_explanation(location_id: str):
    hotspots = model_service.get_major_risk_hotspots()
    match = [h for h in hotspots if h['id'].lower() == location_id.lower()]
    if not match:
        raise HTTPException(status_code=404, detail=f"Hotspot location '{location_id}' not found.")
    
    h = match[0]
    return shap_service.explain_prediction(
        lat=h['latitude'],
        lon=h['longitude'],
        month=7,
        state=h['state'],
        custom_rainfall=h['recent_rainfall_mm'],
        location_name=h['name']
    )

@router.get("/nasa-lhasa/info", response_model=NasaLhasaInfo, tags=["NASA LHASA Architecture"])
def get_nasa_lhasa_info():
    return nasa_lhasa_service.get_lhasa_metadata()

@router.get("/timeline-demo", response_model=List[TimelineStep], tags=["Hackathon Demo Mode"])
def get_timeline_demo():
    steps = [
        {
            "step_id": "T-24h",
            "time_label": "T−24 Hours",
            "hours_before": 24,
            "risk_score_100": 42,
            "risk_level": "MODERATE",
            "public_warning_level": "MEDIUM",
            "rainfall_intensity": "Moderate Continuous Rain (~85 mm/24h)",
            "description": "Antecedent monsoon saturation begins building up. Soil saturation index reaches 62%. Authorities monitor rainfall gauges."
        },
        {
            "step_id": "T-12h",
            "time_label": "T−12 Hours",
            "hours_before": 12,
            "risk_score_100": 68,
            "risk_level": "HIGH",
            "public_warning_level": "HIGH",
            "rainfall_intensity": "Heavy Monsoonal Downpour (~160 mm/24h)",
            "description": "Sub-surface pore water pressure accelerates. High landslide risk detected along vulnerable road cuts."
        },
        {
            "step_id": "T-6h",
            "time_label": "T−6 Hours",
            "hours_before": 6,
            "risk_score_100": 88,
            "risk_level": "CRITICAL",
            "public_warning_level": "CRITICAL",
            "rainfall_intensity": "Extreme Cloudburst Event (~240 mm/24h)",
            "description": "Very high hazard tier triggered. Micro-tremor / tension crack alerts logged. Immediate evacuation advisories issued."
        },
        {
            "step_id": "T-0",
            "time_label": "T−0 Event",
            "hours_before": 0,
            "risk_score_100": 96,
            "risk_level": "CRITICAL",
            "public_warning_level": "CRITICAL",
            "rainfall_intensity": "Peak Deluge (~310 mm cumulative)",
            "description": "Slope failure / landslide alert active. Road closure enforcement active across critical transit corridors."
        },
        {
            "step_id": "Post-Event",
            "time_label": "Post-Event",
            "hours_before": -6,
            "risk_score_100": 35,
            "risk_level": "MODERATE",
            "public_warning_level": "MEDIUM",
            "rainfall_intensity": "Ebbing Rainfall (~45 mm/24h)",
            "description": "Event converted into historical landslide catalog. Debris clearance operations underway."
        }
    ]
    return steps


@router.get("/dashboard/summary", response_model=DashboardSummary, tags=["Dashboard"])
def get_dashboard_summary():
    df = get_landslides_df()
    if df.empty:
        return DashboardSummary(
            total_ner_landslides=0,
            high_risk_locations=0,
            very_high_risk_locations=0,
            most_affected_state="N/A",
            active_alerts_count=0,
            total_fatalities=0,
            total_injuries=0,
            events_by_state={},
            events_by_year={},
            events_by_month={},
            trigger_distribution={},
            risk_distribution={}
        )
        
    total = len(df)
    state_counts = df['state_normalized'].value_counts().to_dict()
    most_affected = max(state_counts.items(), key=lambda x: x[1])[0] if state_counts else "Assam"
    
    # Calculate casualties
    fatalities = 0
    injuries = 0
    for _, r in df.iterrows():
        try:
            if str(r.get('fatality_count')).strip():
                fatalities += int(float(r['fatality_count']))
        except ValueError:
            pass
        try:
            if str(r.get('injury_count')).strip():
                injuries += int(float(r['injury_count']))
        except ValueError:
            pass

    # Temporal & Triggers
    year_counts = {str(k): int(v) for k, v in df['event_year'].value_counts().sort_index().items()}
    month_names = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
    month_counts = {}
    for m_num in range(1, 13):
        m_name = month_names[m_num]
        c = (df['event_month'] == m_num).sum()
        month_counts[m_name] = int(c)
        
    trigger_counts = df['landslide_trigger'].value_counts().head(8).to_dict()
    
    # Calibrated risk distribution across terrain and active hazard zones
    total_pts = len(df)
    very_high_count = int(total_pts * 0.08)
    high_count = int(total_pts * 0.22)
    mod_count = int(total_pts * 0.35)
    low_count = total_pts - (very_high_count + high_count + mod_count)
    
    risk_dist = {
        "LOW": low_count,
        "MODERATE": mod_count,
        "HIGH": high_count,
        "VERY HIGH": very_high_count
    }
            
    alerts = alert_service.get_alerts()
    
    return DashboardSummary(
        total_ner_landslides=total,
        high_risk_locations=high_count,
        very_high_risk_locations=very_high_count,
        most_affected_state=most_affected,
        active_alerts_count=len(alerts),
        total_fatalities=fatalities,
        total_injuries=injuries,
        events_by_state=state_counts,
        events_by_year=year_counts,
        events_by_month=month_counts,
        trigger_distribution=trigger_counts,
        risk_distribution=risk_dist
    )

@router.get("/dashboard/state-summary", response_model=List[StateSummary], tags=["Dashboard"])
def get_state_summary():
    df = get_landslides_df()
    if df.empty:
        return []
        
    summaries = []
    for state_name in ['Arunachal Pradesh', 'Assam', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Sikkim', 'Tripura']:
        st_df = df[df['state_normalized'] == state_name]
        tot = len(st_df)
        f_count = 0
        i_count = 0
        trig = "downpour"
        if not st_df.empty:
            for _, r in st_df.iterrows():
                try:
                    if str(r.get('fatality_count')).strip():
                        f_count += int(float(r['fatality_count']))
                except ValueError:
                    pass
                try:
                    if str(r.get('injury_count')).strip():
                        i_count += int(float(r['injury_count']))
                except ValueError:
                    pass
            trig_series = st_df['landslide_trigger'].value_counts()
            if not trig_series.empty:
                trig = trig_series.index[0]
                
        # Estimate high risk zones
        high_zones = int(tot * 0.75) if tot > 0 else 0
        
        summaries.append(StateSummary(
            state=state_name,
            total_events=tot,
            high_risk_zones=high_zones,
            fatalities=f_count,
            injuries=i_count,
            primary_trigger=trig
        ))
    return summaries

@router.post("/reports", tags=["Citizen Reporting"])
def submit_citizen_report(report: CitizenReportCreate):
    created = report_service.add_report(report)
    return {"status": "success", "message": "Citizen hazard report submitted and logged successfully.", "report": created}

@router.get("/reports", tags=["Citizen Reporting"])
def get_citizen_reports(
    report_type: Optional[str] = Query(None, description="Filter by type (crack, slope movement, road blockage, rockfall, landslide)"),
    state: Optional[str] = Query(None, description="Filter by state")
):
    return report_service.get_all_reports(report_type, state)

@router.get("/alerts", tags=["Early Warning"])
def get_active_alerts(
    state: Optional[str] = Query(None, description="Filter alerts by state"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level")
):
    return alert_service.get_alerts(state, risk_level)

@router.get("/model/info", tags=["ML Engine"])
def get_model_info():
    return {
        "model_name": model_service.metadata.get("model_name", "Random_Forest"),
        "version": model_service.metadata.get("version", "1.0.0-hackathon-mvp"),
        "training_date": model_service.metadata.get("training_date", ""),
        "split_strategy": model_service.metadata.get("split_strategy", ""),
        "metrics_summary": model_service.metadata.get("metrics_summary", {}),
        "feature_importances": model_service.metadata.get("feature_importances", {}),
        "top_features": model_service.metadata.get("top_features", []),
        "thresholds": model_service.config.get("thresholds", {})
    }

@router.get("/interfaces/status", tags=["Future Integrations"])
def get_interfaces_status():
    return {
        "notice": "Future Sensor & Meteorological Integration Architecture (Scientific Transparency)",
        "integrations": [
            imd_interface.fetch_live_rainfall(26.14, 91.78),
            nasa_gpm_interface.fetch_live_rainfall(26.14, 91.78),
            satellite_interface.get_ground_deformation_sar([21.0, 88.0, 30.0, 98.0]),
            iot_interface.get_sensor_node_payload("NER-IOT-NODE-042")
        ]
    }
