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
        thresh = self.config.get('thresholds', {})
        if score < thresh.get('low', {}).get('max', 0.25):
            return "LOW"
        elif score < thresh.get('moderate', {}).get('max', 0.50):
            return "MODERATE"
        elif score < thresh.get('high', {}).get('max', 0.75):
            return "HIGH"
        else:
            return "VERY HIGH"

    def derive_features(self, lat: float, lon: float, month: int = 7, state: str = "Assam", custom_rainfall: float = None, custom_slope: float = None):
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
        
        # Rainfall proxy
        if custom_rainfall is not None:
            rainfall_proxy = float(custom_rainfall)
        else:
            base_rainfall_map = {1: 15.0, 2: 25.0, 3: 65.0, 4: 160.0, 5: 280.0, 6: 420.0, 7: 480.0, 8: 390.0, 9: 310.0, 10: 120.0, 11: 30.0, 12: 12.0}
            rainfall_proxy = base_rainfall_map.get(month, 200.0)

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
        
        if risk_tier in ['VERY HIGH', 'HIGH']:
            return (
                f"Elevated landslide risk (Score: {risk_score:.2f}, {risk_tier}) in {state}. "
                f"Driven by high rainfall saturation index (~{rf:.0f} mm), steep terrain slope ({slope:.1f}°), "
                f"and close proximity ({dist:.1f} km) to {density} documented historical landslide cluster(s) during {monsoon_str.lower()}."
            )
        elif risk_tier == 'MODERATE':
            return (
                f"Moderate landslide risk (Score: {risk_score:.2f}, {risk_tier}) in {state}. "
                f"Terrain exhibits moderate incline ({slope:.1f}°) with intermediate rainfall index (~{rf:.0f} mm) during {monsoon_str.lower()}."
            )
        else:
            return (
                f"Low landslide risk (Score: {risk_score:.2f}, {risk_tier}) in {state}. "
                f"Stable conditions with low precipitation index (~{rf:.0f} mm), mild slope gradient ({slope:.1f}°), and distance from major hazard corridors."
            )

    def predict(self, lat: float, lon: float, month: int = 7, state: str = "Assam", custom_rainfall: float = None, custom_slope: float = None) -> dict:
        feat_dict = self.derive_features(lat, lon, month, state, custom_rainfall, custom_slope)
        
        feature_cols = self.metadata.get('feature_columns', list(feat_dict.keys()))
        df_input = pd.DataFrame([feat_dict])[feature_cols]
        
        if self.model is not None:
            probs = self.model.predict_proba(df_input)[0]
            risk_score = float(probs[1])
        else:
            # Fallback heuristic if model file not found
            risk_score = 0.5
            
        risk_tier = self.get_risk_tier(risk_score)
        confidence = round(float(np.max([risk_score, 1.0 - risk_score])), 3)
        explanation = self.generate_explanation(feat_dict, risk_score, risk_tier, state)
        
        # Calculate localized contributing factors
        contributing_factors = {
            "Rainfall Saturation Index": round(min(1.0, feat_dict['rainfall_antecedent_proxy_mm'] / 500.0), 3),
            "Terrain Slope Incline": round(min(1.0, feat_dict['slope_proxy_deg'] / 50.0), 3),
            "Historical Hotspot Proximity": round(max(0.0, 1.0 - (feat_dict['min_dist_to_historical_km'] / 50.0)), 3),
            "Seasonal Monsoon Factor": round(1.0 if feat_dict['is_monsoon'] else (0.6 if feat_dict['pre_monsoon'] else 0.2), 3)
        }
        
        return {
            "risk_score": round(risk_score, 4),
            "risk_level": risk_tier,
            "confidence": confidence,
            "model_version": self.metadata.get("version", "1.0.0-hackathon-mvp"),
            "prediction_timestamp": datetime.now().isoformat(),
            "latitude": lat,
            "longitude": lon,
            "state": state,
            "explanation": explanation,
            "contributing_factors": contributing_factors,
            "features": feat_dict
        }

model_service = ModelService()
