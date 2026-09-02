# ML Model Performance & Benchmark Report

## 1. Experimental Setup & Leakage Prevention
- **Split Strategy**: Strictly Temporal Split to prevent spatial-temporal leakage.
  - **Training Set (<= 2013)**: 388 samples (127 positive events, 261 pseudo-absences)
  - **Validation Set (2014–2015)**: 163 samples (92 positive events, 71 pseudo-absences)
  - **Test Set (2016 Hold-out)**: 76 samples (32 positive events, 44 pseudo-absences)
- **Features (12)**: `latitude, longitude, month_sin, month_cos, is_monsoon, pre_monsoon, post_monsoon, elevation_proxy_m, slope_proxy_deg, rainfall_antecedent_proxy_mm, historical_density_50km, min_dist_to_historical_km`

---

## 2. Model Comparison Table (Test Set: 2016 Hold-Out)

| Model Architecture | Precision | Recall (Safety-Critical) | F1-Score | ROC-AUC | PR-AUC |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Logistic Regression Baseline** | 0.9688 | 0.9688 | 0.9688 | 0.9993 | 0.9991 |
| **Random Forest** | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| **Gradient Boosting** | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |

---

## 3. Confusion Matrix (Selected Model: Random Forest)
```
Test Set Ground Truth vs Predicted:
                   Predicted Negative (0)    Predicted Positive (1)
Actual Negative (0)        44                        0
Actual Positive (1)        0                         32
```

---

## 4. Precision vs. Recall Tradeoff Analysis
For a landslide early-warning system in high-risk mountainous corridors (NER), **Recall is prioritized** over precision because an unpredicted landslide carries catastrophic loss of life and critical transit disruption, whereas a false warning causes precautionary vigilance. Random Forest achieved a balanced high recall with strong ROC-AUC.
