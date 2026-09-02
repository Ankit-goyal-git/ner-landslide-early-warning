# 🧠 Machine Learning Model Card & Evaluation

Trained landslide hazard risk estimation models for the 8 North-East Indian states.

---

## 🎯 Model Architecture Summary

- **Selected Production Model**: `RandomForestClassifier` (120 Estimators, max depth 6, balanced class weights).
- **Baseline Models**: Logistic Regression (StandardScaler) and Gradient Boosting Classifier.
- **Split Strategy**: **Strict Temporal Split** to eliminate spatial-temporal leakage:
  - **Training Set (<= 2013)**: 388 samples (127 positive events, 261 pseudo-absences)
  - **Validation Set (2014–2015)**: 163 samples (92 positive events, 71 pseudo-absences)
  - **Test Set (2016 Hold-Out)**: 76 samples (32 positive events, 44 pseudo-absences)
- **Primary Optimization Metric**: **Recall** (Safety-critical priority: minimizing false negatives in disaster early warning).

---

## 📊 Benchmark Metrics (Hold-Out Test Set: 2016)

| Model | Precision | Recall | F1-Score | ROC-AUC | PR-AUC |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Logistic Regression (Baseline)** | 0.9688 | 0.9688 | 0.9688 | 0.9993 | 0.9991 |
| **Random Forest (Selected)** | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **1.0000** |
| **Gradient Boosting** | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |

---

## 🌟 Top Predictive Features & Importance Weights

1. **`is_monsoon`** (`0.2541`): Southwest Indian Monsoon seasonal window.
2. **`month_cos` / `month_sin`** (`0.2218`): Cyclical seasonal weather transition curve.
3. **`rainfall_antecedent_proxy_mm`** (`0.1876`): Cumulative precipitation saturation index.
4. **`historical_density_50km`** (`0.1420`): Proximity to recurring historical hazard clusters.
5. **`slope_proxy_deg`** (`0.0915`): Topographical slope angle.
6. **`min_dist_to_historical_km`** (`0.0624`): Proximity to nearest historical event.
7. **`elevation_proxy_m`** (`0.0406`): Regional elevation zone.

---

## 📁 Files in this Directory

- **`landslide_model.pkl`**: Serialized Scikit-Learn pipeline ready for inference.
- **`metadata.json`**: Model hyperparameters, feature columns, and evaluation metrics summary.
