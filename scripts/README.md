# 🛠️ Data Processing & Machine Learning Scripts

This directory contains standalone Python pipelines for data auditing, cleaning, feature engineering, and model training/evaluation for the **NER Landslide Early Warning System**.

---

## 📋 Pipeline Execution Order

```bash
# Step 1: Profile & Audit Raw Dataset
python scripts/profile_dataset.py

# Step 2: Clean & Filter 251 NER Records
python scripts/clean_landslide_data.py

# Step 3: Feature Engineering & Pseudo-Absence Generation
python scripts/create_features.py

# Step 4: Train & Benchmark ML Models
python scripts/train_model.py

# Step 5: Standalone Model Evaluation
python scripts/evaluate_model.py
```

---

## 📜 Script Descriptions

### 1. `profile_dataset.py`
- Ingests `LandSlide Dataset.csv` (11,033 global events from NASA GLC).
- Profiles column types, missing value percentages, coordinate boundaries, date formats, and detected NER records.

### 2. `clean_landslide_data.py`
- Normalizes column headers (`admin_division_name`, `landslide_trigger`, etc.).
- Converts raw event dates to ISO timestamps (`YYYY-MM-DD HH:MM:SS`).
- Extracts cyclical temporal angles: `event_month_sin` and `event_month_cos`.
- Standardizes administrative divisions into the 8 NER states: *Arunachal Pradesh, Assam, Manipur, Meghalaya, Mizoram, Nagaland, Sikkim, Tripura*.
- Validates latitude (-90 to +90) and longitude (-180 to +180) coordinates.
- Outputs [`data/processed/ner_landslides_clean.csv`](../data/processed/ner_landslides_clean.csv) (251 historical events) and [`reports/data_quality_report.md`](../reports/data_quality_report.md).

### 3. `create_features.py`
- Implements **Documented Spatial-Temporal Pseudo-Absence Sampling** (generating 376 non-event samples `label = 0`).
- Derives terrain proxies: `elevation_proxy_m` and `slope_proxy_deg`.
- Computes spatial hazard clustering: `historical_density_50km` and `min_dist_to_historical_km`.
- Estimates `rainfall_antecedent_proxy_mm` from seasonal monsoon dynamics.
- Outputs [`data/processed/ner_features.csv`](../data/processed/ner_features.csv) (627 total samples).

### 4. `train_model.py`
- Enforces a **Strict Temporal Split** (Train <= 2013, Val 2014-2015, Test Hold-out 2016) to eliminate data leakage.
- Trains and benchmarks **Logistic Regression**, **Random Forest (Selected)**, and **Gradient Boosting**.
- Prioritizes **Recall** for hazard early-warning safety.
- Exports calibrated model to [`models/landslide_model.pkl`](../models/landslide_model.pkl) and [`models/metadata.json`](../models/metadata.json).
- Generates [`reports/model_report.md`](../reports/model_report.md) and [`reports/model_explainability.md`](../reports/model_explainability.md).

### 5. `evaluate_model.py`
- Standalone verification script that loads `landslide_model.pkl` and computes Precision, Recall, F1, ROC-AUC, and Confusion Matrix on the hold-out test set.
