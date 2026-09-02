# Landslide Dataset Information & Provenance

## 1. Dataset Overview
- **Source**: NASA Global Landslide Catalog (GLC) Public Database.
- **Original Filename**: `LandSlide Dataset.csv` (located in project root / `data/raw/`).
- **Scope**: Global historical landslide events triggered by rainfall, monsoon, downpours, earthquakes, and other triggers.
- **Total Records (Global)**: 11,033 events.
- **Total Columns**: 31 columns.
- **Geographic Coverage**: Worldwide (Latitude: -46.7748 to 72.6275, Longitude: -179.9808 to 179.9914).
- **Temporal Range**: 1988 to 2017 (predominantly 2007–2016).

---

## 2. North-East India (NER) Subset
Filtering for the 8 North-East Indian states (`admin_division_name` matching Arunachal Pradesh, Assam, Manipur, Meghalaya, Mizoram, Nagaland, Sikkim, Tripura) yields **251 historical landslide events**.

### State Breakdown (Historical Events):
| State | Event Count | Percentage of NER Total |
| :--- | :---: | :---: |
| **Arunachal Pradesh** | 20 | 7.97% |
| **Assam** | 82 | 32.67% |
| **Manipur** | 56 | 22.31% |
| **Meghalaya** | 18 | 7.17% |
| **Mizoram** | 27 | 10.76% |
| **Nagaland** | 14 | 5.58% |
| **Sikkim** | 31 | 12.35% |
| **Tripura** | 3 | 1.20% |
| **Total NER Events** | **251** | **100.00%** |

---

## 3. Detected Schema & Field Mapping
- **Latitude Column**: `latitude` (Float, 0.00% missing)
- **Longitude Column**: `longitude` (Float, 0.00% missing)
- **Date Column**: `event_date` (Timestamp, 0.00% missing)
- **Country Column**: `country_name` / `country_code` (14.16% missing globally, 0.00% missing in NER filtered)
- **State / Admin Column**: `admin_division_name` (14.84% missing globally)
- **Trigger Column**: `landslide_trigger` (0.21% missing globally; top triggers in NER: `downpour`, `rain`, `monsoon`, `continuous_rain`)
- **Category Column**: `landslide_category` (0.01% missing globally; types: `landslide`, `mudslide`, `rockfall`, `debris_flow`)
- **Impact Fields**: `fatality_count` (12.55% missing), `injury_count` (51.43% missing)

---

## 4. Scientific Data Integrity Rules
- **No Negative Fabrication**: This dataset only contains positive landslide events (`label = 1`). In accordance with scientific integrity guidelines, non-events are strictly sampled and documented as spatial-temporal pseudo-absences / constructed non-events (`label = 0`), and never presented as "observed ground-truth non-landslides".
- **Real vs Derived Data Distinction**: All historical landslide coordinates, triggers, dates, and casualty counts are from the real historical NASA GLC record. Environmental and terrain susceptibility features are explicitly marked as *derived* or *synthetic baseline indicators*.
- **Temporal Split Validation**: Train/validation/test splits are strictly temporal to prevent spatial-temporal data leakage.
