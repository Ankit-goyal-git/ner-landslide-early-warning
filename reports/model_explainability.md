# Model Explainability & Feature Importance Report

## 1. Global Feature Importance (Random Forest Risk Engine)

| Feature | Importance Score | Domain Interpretation |
| :--- | :---: | :--- |
| `rainfall_antecedent_proxy_mm` | **0.3392** | Cumulative antecedent rainfall proxy (primary trigger for slope saturation and pore water pressure increase) |
| `month_cos` | **0.1759** | Cyclical month encoding capturing seasonal climatic transitions |
| `is_monsoon` | **0.0944** | Seasonal monsoon indicator capturing peak Southwest monsoon intensity in NER |
| `slope_proxy_deg` | **0.0859** | Physiographic terrain inclination (steeper slopes > 28° exhibit higher shear stress) |
| `elevation_proxy_m` | **0.0644** | Himalayan/Patkai elevation profile proxy reflecting orographic rain and soil stratum |
| `min_dist_to_historical_km` | **0.0526** | Spatial proximity to documented historical hazard hotspots and geological fault zones |
| `latitude` | **0.0430** | Geospatial coordinate anchoring state-specific climatic zones |
| `month_sin` | **0.0379** | Cyclical month encoding capturing seasonal climatic transitions |
| `longitude` | **0.0374** | Geospatial coordinate anchoring state-specific climatic zones |
| `post_monsoon` | **0.0333** | Seasonal monsoon indicator capturing peak Southwest monsoon intensity in NER |
| `historical_density_50km` | **0.0201** | Spatial proximity to documented historical hazard hotspots and geological fault zones |
| `pre_monsoon` | **0.0159** | Seasonal monsoon indicator capturing peak Southwest monsoon intensity in NER |

---

## 2. Local Prediction Explanation Template
For every real-time point prediction, the backend generates an interpretable rationale:
- **Example HIGH/VERY HIGH Explanation**:
  > *"Elevated landslide risk (Score: 0.84, VERY HIGH) driven primarily by high antecedent rainfall accumulation index, active southwest monsoon seasonality, steep topographical slope (>32°), and close proximity (<4.2 km) to recurring historical landslide corridors in Sikkim."*
- **Example LOW Explanation**:
  > *"Low landslide risk (Score: 0.12, LOW) due to minimal seasonal precipitation, mild slope gradient, and significant distance from historical hazard clusters."*

---

## 3. Scientific Transparency
- All model predictions represent baseline statistical susceptibility calibrated with documented historical event clusters.
- When real-time IMD or NASA GPM IMERG feeds are connected, rainfall features will seamlessly substitute the antecedent proxy.
