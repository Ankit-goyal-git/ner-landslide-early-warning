import uuid
from datetime import datetime
from typing import List, Dict, Any
from backend.models.schemas import AlertItem
from backend.services.model_service import model_service

class AlertService:
    def __init__(self):
        self.active_alerts: List[Dict[str, Any]] = []
        self.generate_baseline_alerts()
        
    def generate_baseline_alerts(self):
        # Generate initial realistic early-warning alerts for current high-risk locations in NER
        critical_hotspots = [
            {"state": "Sikkim", "lat": 27.3702, "lon": 88.7334, "location": "Gangtok - Nathu La Highway corridor"},
            {"state": "Manipur", "lat": 24.8286, "lon": 93.5935, "location": "Tamenglong - Imphal Sector NH-37"},
            {"state": "Assam", "lat": 25.1175, "lon": 92.8573, "location": "Dima Hasao - Haflong Railway Sector"},
            {"state": "Arunachal Pradesh", "lat": 27.0987, "lon": 93.8160, "location": "Itanagar - Banderdewa Pass"},
            {"state": "Meghalaya", "lat": 25.9703, "lon": 91.8584, "location": "Umling - Ri-Bhoi NH-40"}
        ]
        
        for spot in critical_hotspots:
            pred = model_service.predict(spot['lat'], spot['lon'], month=7, state=spot['state'])
            if pred['risk_level'] in ['HIGH', 'VERY HIGH']:
                alert = {
                    "alert_id": f"ALT-{str(uuid.uuid4())[:8].upper()}",
                    "state": spot['state'],
                    "location_name": spot['location'],
                    "latitude": spot['lat'],
                    "longitude": spot['lon'],
                    "risk_score": pred['risk_score'],
                    "risk_level": pred['risk_level'],
                    "message": f"Landslide Warning [{pred['risk_level']}]: Heightened ground saturation detected near {spot['location']}, {spot['state']}. {pred['explanation']}",
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "ACTIVE",
                    "action_required": "Deploy quick-response teams and monitor slope sensors."
                }
                self.active_alerts.append(alert)

    def get_alerts(self, state: str = None, risk_level: str = None) -> List[Dict[str, Any]]:
        results = self.active_alerts
        if state:
            results = [a for a in results if a['state'].lower() == state.lower()]
        if risk_level:
            results = [a for a in results if a['risk_level'].lower() == risk_level.lower()]
        return results

    def create_alert(self, state: str, lat: float, lon: float, risk_score: float, risk_level: str, message: str) -> Dict[str, Any]:
        alert = {
            "alert_id": f"ALT-{str(uuid.uuid4())[:8].upper()}",
            "state": state,
            "latitude": lat,
            "longitude": lon,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "message": message,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "ACTIVE",
            "action_required": "Early warning alert issued."
        }
        self.active_alerts.insert(0, alert)
        return alert

alert_service = AlertService()
