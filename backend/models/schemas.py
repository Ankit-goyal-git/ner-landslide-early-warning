from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class PredictRequest(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude in decimal degrees")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude in decimal degrees")
    month: Optional[int] = Field(default=7, ge=1, le=12, description="Month of prediction (1-12)")
    state: Optional[str] = Field(default="Assam", description="NER State name")
    rainfall_mm: Optional[float] = Field(default=None, description="Optional custom rainfall observation in mm")
    slope_deg: Optional[float] = Field(default=None, description="Optional custom slope in degrees")

class PredictionResponse(BaseModel):
    risk_score: float = Field(..., description="Calculated landslide risk probability between 0.0 and 1.0")
    risk_level: str = Field(..., description="Prototype risk tier: LOW, MODERATE, HIGH, or VERY HIGH")
    confidence: float = Field(..., description="Prediction confidence score")
    model_version: str = Field(..., description="Model version tag")
    prediction_timestamp: str = Field(..., description="ISO timestamp of inference")
    latitude: float
    longitude: float
    state: str
    explanation: str = Field(..., description="Human-interpretable risk rationale")
    contributing_factors: Dict[str, float] = Field(..., description="Key feature influence weights")

class LandslideEvent(BaseModel):
    event_id: str
    event_date: str
    latitude: float
    longitude: float
    state: str
    district: Optional[str] = None
    landslide_type: str
    landslide_size: str
    trigger: str
    fatalities: Optional[int] = 0
    injuries: Optional[int] = 0
    location_description: Optional[str] = ""
    source_name: Optional[str] = ""

class CitizenReportCreate(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    report_type: str = Field(..., description="crack, slope movement, road blockage, rockfall, landslide, other")
    description: str = Field(..., min_length=3, max_length=1000)
    image_url: Optional[str] = None
    state: Optional[str] = None
    severity: Optional[str] = Field(default="MODERATE", description="LOW, MODERATE, HIGH, CRITICAL")
    reporter_name: Optional[str] = "Citizen Reporter"

class CitizenReport(CitizenReportCreate):
    id: str
    timestamp: str
    status: str = "VERIFIED"

class AlertItem(BaseModel):
    alert_id: str
    state: str
    latitude: float
    longitude: float
    risk_score: float
    risk_level: str
    message: str
    created_at: str
    status: str

class StateSummary(BaseModel):
    state: str
    total_events: int
    high_risk_zones: int
    fatalities: int
    injuries: int
    primary_trigger: str

class DashboardSummary(BaseModel):
    total_ner_landslides: int
    high_risk_locations: int
    very_high_risk_locations: int
    most_affected_state: str
    active_alerts_count: int
    total_fatalities: int
    total_injuries: int
    events_by_state: Dict[str, int]
    events_by_year: Dict[str, int]
    events_by_month: Dict[str, int]
    trigger_distribution: Dict[str, int]
    risk_distribution: Dict[str, int]
