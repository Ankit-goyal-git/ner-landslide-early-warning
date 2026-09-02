# 🧪 Automated Test Suite

Automated pytest tests covering data pipelines, ML predictions, and FastAPI REST endpoints.

---

## 🚀 Running the Tests

```bash
# Run all tests with verbose output
python -m pytest tests/ -v
```

---

## 📋 Test Modules

| Test File | Coverage |
| :--- | :--- |
| **`test_data_pipeline.py`** | Validates raw data existence, coordinate bounds (-90 to +90, -180 to +180), date parsing, and 251 NER state event count. |
| **`test_model.py`** | Validates `landslide_model.pkl` loading, prediction schema adherence, probability bounds (0.0 to 1.0), and monsoon sensitivity. |
| **`test_api.py`** | Tests `/api/health`, `/api/states`, `/api/landslides`, `/api/predict`, `/api/reports`, and `/api/dashboard/summary`. |
