# ML Model Performance & Benchmark Report

## 1. Experimental Setup & Leakage Prevention
- **Split Strategy**: Strictly Temporal Split to prevent spatial-temporal leakage across 1998–2023.
  - **Training Set (<= 2018)**: 881 samples (568 positive events, 313 pseudo-absences)
  - **Validation Set (2019–2021)**: 649 samples (419 positive events, 230 pseudo-absences)
  - **Test Set (2022–2023 Hold-out)**: 170 samples (113 positive events, 57 pseudo-absences)
- **Features (12)**: `latitude, longitude, month_sin, month_cos, is_monsoon, pre_monsoon, post_monsoon, elevation_proxy_m, slope_proxy_deg, rainfall_antecedent_proxy_mm, historical_density_50km, min_dist_to_historical_km`

---

## 2. Model Comparison Table (Test Set: 2022–2023 Hold-Out)

| Model Architecture | Accuracy | Precision | Recall (Safety-Critical) | F1-Score | ROC-AUC | PR-AUC |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Logistic Regression Baseline** | 0.7941 | 0.8900 | 0.7876 | 0.8357 | 0.8907 | 0.9409 |
| **Random Forest** | 0.8118 | 0.8649 | 0.8496 | 0.8571 | 0.8791 | 0.9269 |
| **Gradient Boosting** | 0.8000 | 0.8692 | 0.8230 | 0.8455 | 0.8728 | 0.9328 |

---

## 3. Confusion Matrix (Selected Model: Random Forest)
```
Test Set Ground Truth vs Predicted:
                   Predicted Negative (0)    Predicted Positive (1)
Actual Negative (0)        42                        15
Actual Positive (1)        17                        96
```

---

## 4. Precision vs. Recall Tradeoff Analysis
For a landslide early-warning system in high-risk mountainous corridors (NER), **Recall is prioritized** over precision because an unpredicted landslide carries catastrophic loss of life and critical transit disruption, whereas a false warning causes precautionary vigilance. Random Forest achieved a balanced high recall with strong ROC-AUC.
