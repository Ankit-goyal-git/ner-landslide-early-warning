# ⚡ Core Technology Stack

## 📊 Summary Overview

| Layer | Primary Technologies | Key Role |
| :--- | :--- | :--- |
| **Frontend UI** | **React 18**, **Vite** | Modular, responsive Single Page Application (SPA) |
| **GIS & Mapping** | **Leaflet**, **React-Leaflet**, **GeoJSON** | Interactive geospatial mapping, hazard layers, and risk heatmaps |
| **Map Base Layer** | **CARTO Dark Matter Tiles** | High-contrast dark theme optimized for emergency monitoring |
| **Data Visualization** | **Chart.js**, **React-Chartjs-2** | Authority charts (state distribution, monsoon curves, trigger breakdown) |
| **Backend REST API** | **FastAPI** (Python 3.13), **Uvicorn** | High-performance asynchronous API with automatic Swagger OpenAPI docs |
| **Data Validation** | **Pydantic v2**, **PyYAML** | Strict schema validation and configurable hazard thresholds |
| **Machine Learning** | **Scikit-Learn**, **Joblib** | Calibrated Random Forest risk engine, baseline benchmarks, and serialization |
| **Data Processing** | **Pandas**, **NumPy** | Tabular cleaning, aggregation, and cyclical seasonal encoding (`sin`/`cos`) |
| **Dataset Source** | **NASA Global Landslide Catalog (GLC)** | 251 historical NER events + 376 documented pseudo-absences |
| **Localization (i18n)** | **In-house Dictionary Architecture** | 5 regional languages (*English, Hindi, Assamese, Bengali, Nepali*) |
| **Automated Testing** | **Pytest**, **HTTPX / TestClient** | 12/12 unit and integration tests passing |
| **DevOps & Deploy** | **Docker**, **Docker Compose**, **Git** | Containerized deployment and modular repository management |

---

## 🏛️ Architecture Flow

```text
[ React 18 + Leaflet GIS + Chart.js (Frontend) ]
                       │
                       ▼  (REST API / JSON / GeoJSON)
[ FastAPI + Pydantic + Uvicorn (Backend Engine) ]
                       │
                       ▼  (Calibrated Risk Scoring)
[ Scikit-Learn Random Forest Pipeline (ML Core) ]
                       │
                       ▼  (Data & Threshold Layer)
[ NASA GLC Cleaned Catalog + Configurable YAML Rules ]
```

---

## 🌟 Key Functional Highlights

1. **Interactive GIS Map**: Color-coded risk markers (LOW, MODERATE, HIGH, VERY HIGH) + Risk Heatmap Surface.
2. **What-If Simulation Sliders**: Real-time hazard sensitivity for Season/Month, Rainfall (10–650 mm), and Slope (5–55°).
3. **Operational Alerts**: Active early warning feed with instant **JSON** and **GeoJSON** exports for disaster authorities.
4. **Citizen Ground Reporting**: Field hazard reporting for tension cracks, rockfalls, and road blockages directly on the map.
5. **Anti-Leakage ML Strategy**: Strict temporal train/val/test splitting to prevent spatial-temporal leakage.
