# ⚡ FastAPI Backend & Early Warning Engine

Production-grade RESTful API service powering the **NER Landslide Early Warning & Risk Platform**.

---

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r ../requirements.txt

# Start backend development server
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

- **Interactive Swagger Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 📡 Key REST Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | System health check and model loading verification. |
| `GET` | `/api/states` | Geographic metadata for the 8 NER states. |
| `GET` | `/api/landslides` | Historical landslide catalog filtered by state, year, and trigger. |
| `GET` | `/api/landslides/{id}` | Specific event details. |
| `GET` | `/api/risk` | Model-scored continuous risk points and hazard levels across NER. |
| `POST` | `/api/predict` | Real-time risk probability calculation and explainability for any coordinate. |
| `GET` | `/api/dashboard/summary` | Aggregated authority KPIs, casualties, monthly monsoon curves, and triggers. |
| `GET` | `/api/dashboard/state-summary` | State-by-state risk rankings and primary hazards. |
| `POST` | `/api/reports` | Citizen & field inspector ground hazard report submission. |
| `GET` | `/api/reports` | Retrieve active citizen hazard observations. |
| `GET` | `/api/alerts` | Active high and very-high early warning advisories. |
| `GET` | `/api/model/info` | ML model version, metrics summary, and feature importances. |
| `GET` | `/api/interfaces/status` | Future integration interface contracts (IMD, NASA GPM, Sentinel SAR, IoT). |

---

## 🏗️ Architecture & Modules

- **`backend/main.py`**: Initializes FastAPI, CORS middleware, mounts `/api` routes, and serves the compiled React SPA at `/`.
- **`backend/models/schemas.py`**: Pydantic models for request validation and structured responses.
- **`backend/services/model_service.py`**: Loads `models/landslide_model.pkl`, performs feature transformations, and derives plain-language explainability.
- **`backend/services/alert_service.py`**: Automated alert generation engine triggered by high/very-high risk thresholds.
- **`backend/services/report_service.py`**: In-memory and persistent citizen ground report store.
- **`backend/services/weather_interface.py`**: Clean interfaces for future real-time Doppler radar (IMD), satellite precipitation (NASA GPM IMERG), InSAR ground deformation (Sentinel-1), and IoT sensors.
