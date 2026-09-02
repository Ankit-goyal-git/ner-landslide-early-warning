# 🌐 React + Leaflet GIS Dashboard Frontend

Ultra-modern, authority-grade Geospatial Information System (GIS) and Early Warning interface built with **React 18 + Vite + Leaflet + Chart.js**.

---

## 🚀 Quick Start

```bash
# Install Node dependencies
npm install

# Start development server
npm run dev

# Build production bundle
npm run build
```

The Vite dev server runs at **`http://localhost:5173`** and proxies `/api` calls to the FastAPI backend at `http://127.0.0.1:8000`.

---

## 🎨 UI/UX Highlights & Capabilities

1. **Authority KPI Banner**: Total Landslides (251), High/Very High Risk Zones, Most Affected State, Active Early Warnings, Reported Casualties.
2. **Interactive Leaflet GIS Map**:
   - Color-coded hazard markers: `LOW` (Green), `MODERATE` (Amber), `HIGH` (Orange), `VERY HIGH` (Red / Glowing Pulse).
   - **Continuous Risk Heatmap Surface** showing spatial hazard concentration.
   - Citizen hazard report markers.
   - Coordinate inspection popups with event date, triggers, and causal factors.
3. **Prediction Inspector**:
   - Interactive simulation sliders for **Season/Month**, **Antecedent Rain (10–650 mm)**, and **Slope Angle (5–55°)**.
   - Immediate ML inference score recalculation and dynamic plain-language explainability text.
4. **Authority Analytics**:
   - Landslides by State (Bar Chart).
   - Monsoon Seasonal Frequency Curve (Line Chart).
   - Trigger Distribution Breakdown (Doughnut Chart).
   - Risk Tier Proportions (Doughnut Chart).
5. **Early Warning Feed**:
   - Active disaster mitigation advisories with **Export to JSON** and **Export to GeoJSON** actions.
6. **Citizen Hazard Reporter Modal**:
   - Submit field observations for tension cracks, slope movements, rockfalls, and road blockages directly onto the map.
7. **Multilingual Support (5 Regional Languages)**:
   - Built-in localization for **English**, **Hindi (हिन्दी)**, **Assamese (অসমীয়া)**, **Bengali (বাংলা)**, and **Nepali (नेपाली)**.
8. **Offline Resilience**:
   - Automatic caching of GIS layers and KPIs in browser localStorage with live network status indicators.

---

## 📂 Component Structure

- **`src/components/Navbar.jsx`**: Top header, branding, state dropdown, language switcher, network status.
- **`src/components/KpiBanner.jsx`**: Glassmorphic metric cards.
- **`src/components/GisMap.jsx`**: Leaflet geospatial map with layer toggles.
- **`src/components/PredictionInspector.jsx`**: What-if simulation sliders and feature contribution bars.
- **`src/components/ChartsSection.jsx`**: Chart.js analytics panels.
- **`src/components/AlertsFeed.jsx`**: Early warning feed and download exports.
- **`src/components/CitizenReportModal.jsx`**: Ground hazard submission form.
- **`src/components/ModelInfoModal.jsx`**: Model architecture, ROC-AUC metrics, and scientific provenance dialog.
- **`src/i18n/`**: Translation dictionary files (`en.json`, `hi.json`, `as.json`, `bn.json`, `ne.json`).
