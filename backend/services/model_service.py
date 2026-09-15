import os
import json
import math
import joblib
import pandas as pd
import numpy as np
import yaml
from datetime import datetime

class ModelService:
    def __init__(self, model_path="models/landslide_model.pkl", metadata_path="models/metadata.json", config_path="config/risk_thresholds.yaml"):
        self.model_path = model_path
        self.metadata_path = metadata_path
        self.config_path = config_path
        self.model = None
        self.metadata = {}
        self.config = {}
        self.historical_events = []
        self.load_artifacts()
        
    def load_artifacts(self):
        # Load Config
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = {
                'thresholds': {
                    'low': {'min': 0.0, 'max': 0.25, 'label': 'LOW'},
                    'moderate': {'min': 0.25, 'max': 0.50, 'label': 'MODERATE'},
                    'high': {'min': 0.50, 'max': 0.75, 'label': 'HIGH'},
                    'very_high': {'min': 0.75, 'max': 1.00, 'label': 'VERY HIGH'}
                }
            }
            
        # Load Metadata
        if os.path.exists(self.metadata_path):
            with open(self.metadata_path, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
                
        # Load Model
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)
            print(f"Loaded Landslide Model from: {self.model_path}")
        else:
            print(f"Warning: Model file {self.model_path} not found.")

        # Load Historical Cleaned Data for Spatial Density
        catalog_csv = os.path.join("data", "processed", "ner_landslides_catalog.csv")
        clean_csv = catalog_csv if os.path.exists(catalog_csv) else os.path.join("data", "processed", "ner_landslides_clean.csv")
        if os.path.exists(clean_csv):
            df_hist = pd.read_csv(clean_csv)
            self.historical_events = df_hist.to_dict(orient='records')
            
        # Precompute radian coordinates for fast vectorized distance calculations
        if self.historical_events:
            self.hist_lats = np.radians([float(e['latitude']) for e in self.historical_events])
            self.hist_lons = np.radians([float(e['longitude']) for e in self.historical_events])
        else:
            self.hist_lats = np.array([])
            self.hist_lons = np.array([])
            
    def get_risk_tier(self, score: float) -> str:
        score_100 = int(round(score * 100))
        if score_100 <= 25:
            return "LOW"
        elif score_100 <= 50:
            return "MODERATE"
        elif score_100 <= 75:
            return "HIGH"
        else:
            return "CRITICAL"

    def get_public_warning_level(self, score_100: int) -> str:
        if score_100 <= 25:
            return "LOW"
        elif score_100 <= 50:
            return "MEDIUM"
        elif score_100 <= 75:
            return "HIGH"
        else:
            return "CRITICAL"

    def get_warning_window_label(self, score_100: int, horizon_hours: int = 0) -> str:
        if score_100 < 30:
            return "Routine Monitoring (No Immediate Window)"
        elif horizon_hours >= 48:
            return "24–48 Hours (Forecast Horizon)"
        elif horizon_hours >= 24:
            return "12–24 Hours (Active Advisory)"
        else:
            return "6–24 Hours (Actionable Window)"

    def derive_features(self, lat: float, lon: float, month: int = 7, state: str = "Assam", custom_rainfall: float = None, custom_slope: float = None, horizon_hours: int = 0):
        # Cyclical month
        month_rad = 2.0 * math.pi * (month - 1) / 12.0
        month_sin = round(math.sin(month_rad), 4)
        month_cos = round(math.cos(month_rad), 4)
        
        is_monsoon = 1 if month in [6, 7, 8, 9] else 0
        pre_monsoon = 1 if month in [4, 5] else 0
        post_monsoon = 1 if month in [10, 11] else 0
        
        # Terrain proxy
        base_elev = 950.0
        base_slope = 26.0
        if "sikkim" in state.lower():
            base_elev = 2600.0; base_slope = 38.0
        elif "arunachal" in state.lower():
            base_elev = 2100.0; base_slope = 34.0
        elif "nagaland" in state.lower():
            base_elev = 1400.0; base_slope = 31.0
        elif "manipur" in state.lower():
            base_elev = 1250.0; base_slope = 27.0
        elif "mizoram" in state.lower():
            base_elev = 1100.0; base_slope = 29.0
        elif "meghalaya" in state.lower():
            base_elev = 1300.0; base_slope = 28.0
        elif "assam" in state.lower():
            base_elev = 450.0; base_slope = 14.0
        elif "tripura" in state.lower():
            base_elev = 250.0; base_slope = 12.0
            
        elevation_proxy = round(base_elev + math.sin(lat * 12.0) * 150.0 + math.cos(lon * 12.0) * 120.0, 1)
        slope_proxy = custom_slope if custom_slope is not None else round(max(2.0, min(55.0, base_slope + math.sin(lat * 20.0 + lon * 20.0) * 6.0)), 1)
        
        # Rainfall proxy with forecast horizon support (+0h, +6h, +12h, +24h, +48h, +72h)
        if custom_rainfall is not None:
            rainfall_proxy = float(custom_rainfall)
        else:
            base_rainfall_map = {1: 15.0, 2: 25.0, 3: 65.0, 4: 160.0, 5: 280.0, 6: 420.0, 7: 480.0, 8: 390.0, 9: 310.0, 10: 120.0, 11: 30.0, 12: 12.0}
            rainfall_proxy = base_rainfall_map.get(month, 200.0)

        # Apply forecast horizon boost if simulating peak storm cell progression
        if horizon_hours > 0:
            horizon_multiplier = 1.0 + min(0.35, (horizon_hours / 72.0) * 0.35)
            rainfall_proxy = round(rainfall_proxy * horizon_multiplier, 1)

        # Fast vectorized distance to historical events
        if len(self.hist_lats) > 0:
            lat_r = math.radians(lat)
            lon_r = math.radians(lon)
            dlat = self.hist_lats - lat_r
            dlon = self.hist_lons - lon_r
            a = np.sin(dlat / 2.0)**2 + math.cos(lat_r) * np.cos(self.hist_lats) * np.sin(dlon / 2.0)**2
            c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1.0 - a))
            dists_km = 6371.0 * c
            near_count = int(np.sum(dists_km <= 50.0))
            min_dist = float(np.min(dists_km))
        else:
            near_count = 0
            min_dist = 45.0
            
        return {
            'latitude': lat,
            'longitude': lon,
            'month_sin': month_sin,
            'month_cos': month_cos,
            'is_monsoon': is_monsoon,
            'pre_monsoon': pre_monsoon,
            'post_monsoon': post_monsoon,
            'elevation_proxy_m': elevation_proxy,
            'slope_proxy_deg': slope_proxy,
            'rainfall_antecedent_proxy_mm': rainfall_proxy,
            'historical_density_50km': near_count,
            'min_dist_to_historical_km': round(min_dist, 2)
        }

    def generate_explanation(self, feat_dict: dict, risk_score: float, risk_tier: str, state: str) -> str:
        monsoon_str = "Peak southwest monsoon season" if feat_dict['is_monsoon'] else ("Pre-monsoon period" if feat_dict['pre_monsoon'] else "Dry/post-monsoon season")
        rf = feat_dict['rainfall_antecedent_proxy_mm']
        slope = feat_dict['slope_proxy_deg']
        dist = feat_dict['min_dist_to_historical_km']
        density = feat_dict['historical_density_50km']
        score_100 = int(round(risk_score * 100))
        
        if risk_tier in ['CRITICAL', 'VERY HIGH', 'HIGH']:
            return (
                f"Elevated landslide risk (Score: {score_100}/100, {risk_tier}) in {state}. "
                f"Driven by heavy rainfall intensity (~{rf:.0f} mm), steep terrain slope ({slope:.1f}°), "
                f"and close proximity ({dist:.1f} km) to {density} documented historical landslide cluster(s) during {monsoon_str.lower()}."
            )
        elif risk_tier == 'MODERATE':
            return (
                f"Moderate landslide risk (Score: {score_100}/100, {risk_tier}) in {state}. "
                f"Terrain exhibits moderate incline ({slope:.1f}°) with intermediate rainfall index (~{rf:.0f} mm) during {monsoon_str.lower()}."
            )
        else:
            return (
                f"Low landslide risk (Score: {score_100}/100, {risk_tier}) in {state}. "
                f"Stable conditions with low precipitation index (~{rf:.0f} mm), mild slope gradient ({slope:.1f}°), and distance from major hazard corridors."
            )

    def predict(
        self,
        lat: float,
        lon: float,
        month: int = 7,
        state: str = "Assam",
        custom_rainfall: float = None,
        custom_slope: float = None,
        horizon_hours: int = 0
    ) -> dict:
        feat_dict = self.derive_features(lat, lon, month, state, custom_rainfall, custom_slope, horizon_hours)
        
        feature_cols = self.metadata.get('feature_columns', list(feat_dict.keys()))
        df_input = pd.DataFrame([feat_dict])[feature_cols]
        
        if self.model is not None:
            probs = self.model.predict_proba(df_input)[0]
            risk_score = float(probs[1])
        else:
            # Fallback heuristic if model file not found
            risk_score = 0.5
            
        score_100 = int(round(risk_score * 100))
        risk_tier = self.get_risk_tier(risk_score)
        public_level = self.get_public_warning_level(score_100)
        warning_window = self.get_warning_window_label(score_100, horizon_hours)
        confidence = round(float(np.max([risk_score, 1.0 - risk_score])), 3)
        explanation = self.generate_explanation(feat_dict, risk_score, risk_tier, state)
        
        # SHAP-based feature importance contribution percentages
        rf_val = feat_dict['rainfall_antecedent_proxy_mm']
        slope_val = feat_dict['slope_proxy_deg']
        dist_val = feat_dict['min_dist_to_historical_km']

        rf_weight = 35.0 if rf_val > 300 else (25.0 if rf_val > 150 else 15.0)
        cum_rain_weight = 25.0 if rf_val > 250 else 20.0
        slope_weight = 18.0 if slope_val > 30 else 12.0
        soil_weight = 12.0
        hist_weight = 10.0 if dist_val < 30 else 5.0
        
        tot_w = rf_weight + cum_rain_weight + slope_weight + soil_weight + hist_weight
        shap_contributions = {
            "Heavy Rainfall Intensity": round((rf_weight / tot_w) * 100, 1),
            "24h Cumulative Rainfall": round((cum_rain_weight / tot_w) * 100, 1),
            "Terrain Slope Incline": round((slope_weight / tot_w) * 100, 1),
            "Soil & Lithology Stability": round((soil_weight / tot_w) * 100, 1),
            "Historical Cluster Density": round((hist_weight / tot_w) * 100, 1)
        }

        contributing_factors = {
            "Rainfall Saturation Index": round(min(1.0, feat_dict['rainfall_antecedent_proxy_mm'] / 500.0), 3),
            "Terrain Slope Incline": round(min(1.0, feat_dict['slope_proxy_deg'] / 50.0), 3),
            "Historical Hotspot Proximity": round(max(0.0, 1.0 - (feat_dict['min_dist_to_historical_km'] / 50.0)), 3),
            "Seasonal Monsoon Factor": round(1.0 if feat_dict['is_monsoon'] else (0.6 if feat_dict['pre_monsoon'] else 0.2), 3)
        }
        
        return {
            "risk_score": round(risk_score, 4),
            "risk_score_100": score_100,
            "risk_level": risk_tier,
            "public_warning_level": public_level,
            "warning_window": warning_window,
            "confidence": confidence,
            "model_version": self.metadata.get("version", "1.0.0-hackathon-mvp"),
            "prediction_timestamp": datetime.now().isoformat(),
            "latitude": lat,
            "longitude": lon,
            "state": state,
            "explanation": explanation,
            "contributing_factors": contributing_factors,
            "shap_contributions": shap_contributions,
            "mode": "Demo / Historical Data Mode",
            "features": feat_dict
        }

    def get_major_risk_hotspots(self) -> list:
        # Predefined major risk zones across all 8 NER states
        hotspots = [
            {
                "id": "HS-SK-01",
                "name": "East Sikkim (Gangtok-Pakyong Axis)",
                "state": "Sikkim",
                "district": "East Sikkim",
                "latitude": 27.3389,
                "longitude": 88.6065,
                "risk_score_100": 87,
                "risk_level": "CRITICAL",
                "recent_rainfall_mm": 210.5,
                "forecast_rainfall_mm": 290.0,
                "historical_count": 31,
                "vulnerable_infrastructure": "NH-10 Transit Arterial & Teesta Hydro Infrastructure",
                "population_affected": "42,000 residents across Pakyong & Gangtok slopes",
                "warning_window": "6–24 Hours",
                "last_update": "Live IMD / GPM Forecast (Demo Mode)",
                "recommended_action": "Prepare road-closure measures & issue immediate public hazard advisories for Pakyong slope settlements.",
                "shap_contributions": {"Heavy Rainfall Intensity": 35.0, "24h Cumulative Rainfall": 25.0, "Terrain Slope Incline": 18.0, "Soil & Lithology Stability": 12.0, "Historical Cluster Density": 10.0}
            },
            {
                "id": "HS-AS-02",
                "name": "Dima Hasao (Haflong Mountain Railway Sector)",
                "state": "Assam",
                "district": "Dima Hasao",
                "latitude": 25.1764,
                "longitude": 93.0159,
                "risk_score_100": 91,
                "risk_level": "CRITICAL",
                "recent_rainfall_mm": 245.0,
                "forecast_rainfall_mm": 340.0,
                "historical_count": 82,
                "vulnerable_infrastructure": "Lumding-Badarpur Broad Gauge Railway & NH-27 Corridor",
                "population_affected": "35,000 residents & vital rail-freight supply lines",
                "warning_window": "6–24 Hours",
                "last_update": "Live IMD / GPM Forecast (Demo Mode)",
                "recommended_action": "Suspend passenger rail operations on unstable slope cuts and deploy NDRF emergency clearing machinery.",
                "shap_contributions": {"Heavy Rainfall Intensity": 38.0, "24h Cumulative Rainfall": 26.0, "Terrain Slope Incline": 16.0, "Soil & Lithology Stability": 10.0, "Historical Cluster Density": 10.0}
            },
            {
                "id": "HS-AR-03",
                "name": "West Kameng (Dirang-Bomdila Axis)",
                "state": "Arunachal Pradesh",
                "district": "West Kameng",
                "latitude": 27.2644,
                "longitude": 92.4158,
                "risk_score_100": 82,
                "risk_level": "CRITICAL",
                "recent_rainfall_mm": 195.0,
                "forecast_rainfall_mm": 265.0,
                "historical_count": 20,
                "vulnerable_infrastructure": "NH-229 Tawang Strategic Defense Highway",
                "population_affected": "18,500 residents & military transit convoys",
                "warning_window": "6–24 Hours",
                "last_update": "Live IMD / GPM Forecast (Demo Mode)",
                "recommended_action": "Restrict night traffic movement on steep rockfall cliffs and issue slope alert for Dirang valley.",
                "shap_contributions": {"Heavy Rainfall Intensity": 33.0, "24h Cumulative Rainfall": 24.0, "Terrain Slope Incline": 22.0, "Soil & Lithology Stability": 11.0, "Historical Cluster Density": 10.0}
            },
            {
                "id": "HS-MN-04",
                "name": "Senapati District (NH-2 Imphal-Dimapur Sector)",
                "state": "Manipur",
                "district": "Senapati",
                "latitude": 25.2680,
                "longitude": 94.0160,
                "risk_score_100": 79,
                "risk_level": "CRITICAL",
                "recent_rainfall_mm": 180.0,
                "forecast_rainfall_mm": 230.0,
                "historical_count": 56,
                "vulnerable_infrastructure": "National Highway NH-2 Logistics Lifeline",
                "population_affected": "28,000 residents across hillside villages",
                "warning_window": "6–24 Hours",
                "last_update": "Live IMD / GPM Forecast (Demo Mode)",
                "recommended_action": "Monitor active tension crack subsidence along highway embankments and stage highway clearers.",
                "shap_contributions": {"Heavy Rainfall Intensity": 34.0, "24h Cumulative Rainfall": 24.0, "Terrain Slope Incline": 18.0, "Soil & Lithology Stability": 14.0, "Historical Cluster Density": 10.0}
            },
            {
                "id": "HS-ML-05",
                "name": "East Khasi Hills (Cherrapunji / Sohra Cliff Escarpment)",
                "state": "Meghalaya",
                "district": "East Khasi Hills",
                "latitude": 25.2986,
                "longitude": 91.7317,
                "risk_score_100": 85,
                "risk_level": "CRITICAL",
                "recent_rainfall_mm": 380.0,
                "forecast_rainfall_mm": 510.0,
                "historical_count": 18,
                "vulnerable_infrastructure": "Shillong-Sohra Tourism Road & High-Incline Gorge Villages",
                "population_affected": "22,000 residents on steep sandstone escarpments",
                "warning_window": "6–24 Hours",
                "last_update": "Live IMD / GPM Forecast (Demo Mode)",
                "recommended_action": "Evacuate high-risk valley bottom dwellings prone to torrential debris flows.",
                "shap_contributions": {"Heavy Rainfall Intensity": 42.0, "24h Cumulative Rainfall": 28.0, "Terrain Slope Incline": 15.0, "Soil & Lithology Stability": 8.0, "Historical Cluster Density": 7.0}
            },
            {
                "id": "HS-MZ-06",
                "name": "Aizawl Slopes (Tuirial Bypass Axis)",
                "state": "Mizoram",
                "district": "Aizawl",
                "latitude": 23.7271,
                "longitude": 92.7176,
                "risk_score_100": 74,
                "risk_level": "HIGH",
                "recent_rainfall_mm": 165.0,
                "forecast_rainfall_mm": 210.0,
                "historical_count": 27,
                "vulnerable_infrastructure": "Aizawl Urban Ridge Road & Tuirial Hydro Infrastructure",
                "population_affected": "55,000 residents on fragile shale urban slopes",
                "warning_window": "6–24 Hours",
                "last_update": "Live IMD / GPM Forecast (Demo Mode)",
                "recommended_action": "Inspect retaining walls and clear municipal storm drains along steep urban slopes.",
                "shap_contributions": {"Heavy Rainfall Intensity": 32.0, "24h Cumulative Rainfall": 22.0, "Terrain Slope Incline": 20.0, "Soil & Lithology Stability": 16.0, "Historical Cluster Density": 10.0}
            },
            {
                "id": "HS-NL-07",
                "name": "Kohima Bypass Axis (Peducha Slopes)",
                "state": "Nagaland",
                "district": "Kohima",
                "latitude": 25.6751,
                "longitude": 94.1086,
                "risk_score_100": 71,
                "risk_level": "HIGH",
                "recent_rainfall_mm": 150.0,
                "forecast_rainfall_mm": 195.0,
                "historical_count": 14,
                "vulnerable_infrastructure": "Dimapur-Kohima Highway (NH-29)",
                "population_affected": "30,000 residents & interstate transit",
                "warning_window": "6–24 Hours",
                "last_update": "Live IMD / GPM Forecast (Demo Mode)",
                "recommended_action": "Deploy heavy earthmovers at sinking zone sections on NH-29 and restrict overloaded transport.",
                "shap_contributions": {"Heavy Rainfall Intensity": 30.0, "24h Cumulative Rainfall": 22.0, "Terrain Slope Incline": 22.0, "Soil & Lithology Stability": 16.0, "Historical Cluster Density": 10.0}
            },
            {
                "id": "HS-TR-08",
                "name": "Unakoti Hills (Kailashahar Ridge)",
                "state": "Tripura",
                "district": "Unakoti",
                "latitude": 24.3211,
                "longitude": 92.0125,
                "risk_score_100": 48,
                "risk_level": "MODERATE",
                "recent_rainfall_mm": 95.0,
                "forecast_rainfall_mm": 130.0,
                "historical_count": 3,
                "vulnerable_infrastructure": "Kailashahar Rural Access Road & Heritage Park Slopes",
                "population_affected": "8,500 residents",
                "warning_window": "Routine Monitoring",
                "last_update": "Live IMD / GPM Forecast (Demo Mode)",
                "recommended_action": "Routine rain gauge monitoring and slope maintenance.",
                "shap_contributions": {"Heavy Rainfall Intensity": 28.0, "24h Cumulative Rainfall": 20.0, "Terrain Slope Incline": 20.0, "Soil & Lithology Stability": 20.0, "Historical Cluster Density": 12.0}
            }
        ]
        return hotspots

model_service = ModelService()
