# 📚 Project References & Scientific Bibliography

This document provides formal citations and reference links for all datasets, meteorological authorities, geoscientific research, machine learning methodologies, and software frameworks used in the **NER Landslide AI Risk & Early Warning Platform**.

---

## 1. 🛰️ Primary Dataset References (Historical Landslide Catalog)

### NASA Global Landslide Catalog (GLC)
* **Citation**: Kirschbaum, D. B., Adler, R., Hong, Y., Hill, S., & Lerner-Lam, A. (2010). *A global landslide catalog for hazard applications: method, results, and limitations.* Natural Hazards, 52(3), 561–575.
  * **DOI**: [10.1007/s11069-009-9401-4](https://doi.org/10.1007/s11069-009-9401-4)
* **Open Data Repository**: NASA Open Data Portal — Global Landslide Catalog Export
  * **URL**: [https://data.nasa.gov/Earth-Science/Global-Landslide-Catalog-Export/dd9e-wu2v](https://data.nasa.gov/Earth-Science/Global-Landslide-Catalog-Export/dd9e-wu2v)
* **Catalog Details**: Compiles historical rainfall-triggered landslide events worldwide from media reports, disaster management agency logs, and meteorological surveys.

---

## 2. 🇮🇳 Indian Geological & Meteorological References

### Geological Survey of India (GSI)
* **Program**: National Landslide Susceptibility Mapping (NLSM) Programme.
* **Scope**: Macro-scale (1:50,000) landslide susceptibility zonation covering the Himalayan terrain, Shillong Plateau, and Patkai mountain ranges across the 8 North-Eastern states.
* **URL**: [https://www.gsi.gov.in](https://www.gsi.gov.in) / Bhukosh Geospatial Portal ([https://bhukosh.gsi.gov.in](https://bhukosh.gsi.gov.in))

### National Disaster Management Authority (NDMA), India
* **Guidelines**: *National Landslide Risk Management Strategy (NLRMS)*.
* **Scope**: Guidelines on early warning mechanisms, community preparedness, hazard zonation, and emergency evacuation protocols.
* **URL**: [https://ndma.gov.in](https://ndma.gov.in)

### India Meteorological Department (IMD)
* **Scope**: Southwest Monsoon dynamics, extreme heavy rainfall thresholds (downpours > 64.5 mm/day), and district-level meteorological forecasting.
* **URL**: [https://mausam.imd.gov.in](https://mausam.imd.gov.in)

---

## 3. 🧠 Machine Learning & Geoscientific Methodology References

### Pseudo-Absence Sampling in Landslide Susceptibility
* **Citation**: Merghadi, A., Yunus, A. P., Dou, J., Whiteley, J., ThaiPham, B., Bui, D. T., Chen, W., & Shirzadi, A. (2020). *Machine learning methods for landslide susceptibility studies: The performance of state-of-the-art algorithms.* Earth-Science Reviews, 207, 103225.
  * **DOI**: [10.1016/j.earscirev.2020.103225](https://doi.org/10.1016/j.earscirev.2020.103225)
* **Methodological Relevance**: Explains why historical positive-only occurrence databases require documented non-event pseudo-absence sampling to train binary probabilistic classifiers.

### Spatial-Temporal Data Leakage Prevention
* **Citation**: Roberts, D. R., Bahn, V., Ciuti, S., Boyce, M. S., Elith, J., Guillera-Arroita, G., Hauenstein, S., Lahoz-Monfort, J. J., Schröder, B., Thuiller, W., Warton, D. I., Wintle, B. A., Hartig, F., & Dormann, C. F. (2017). *Cross-validation strategies for data with temporal, spatial or hierarchical structure.* Ecography, 40(8), 913–929.
  * **DOI**: [10.1111/ecog.02881](https://doi.org/10.1111/ecog.02881)
* **Methodological Relevance**: Demonstrates why standard random k-fold cross-validation causes spatial-temporal leakage in hazard modeling and validates the strict **Temporal Train/Validation/Test Split** used in this project.

### Random Forest Algorithm
* **Citation**: Breiman, L. (2001). *Random Forests.* Machine Learning, 45(1), 5–32.
  * **DOI**: [10.1023/A:1010933404324](https://doi.org/10.1023/A:1010933404324)

### Explainable Artificial Intelligence (XAI)
* **Citation**: Lundberg, S. M., & Lee, S. I. (2017). *A Unified Approach to Interpreting Model Predictions.* Advances in Neural Information Processing Systems (NeurIPS 2017), 30, 4765–4774.
  * **URL**: [https://proceedings.neurips.cc/paper/2017/hash/8a20a8621978632d76c43dfd28b67767-Abstract.html](https://proceedings.neurips.cc/paper/2017/hash/8a20a8621978632d76c43dfd28b67767-Abstract.html)

---

## 4. 🛰️ Future Live Data Feed Standards & Interfaces

* **NASA GPM IMERG (Global Precipitation Measurement)**:
  * Huffman, G. J., et al. (2019). *Algorithm Theoretical Basis Document (ATBD) for NASA GPM Integrated Multi-satellitE Retrievals for GPM (IMERG).* NASA Goddard Space Flight Center.
  * **URL**: [https://gpm.nasa.gov/data/imerg](https://gpm.nasa.gov/data/imerg)
* **Copernicus Sentinel-1 SAR (InSAR Ground Deformation)**:
  * European Space Agency (ESA) Sentinel-1 Synthetic Aperture Radar (SAR) Mission.
  * **URL**: [https://sentinel.esa.int/web/sentinel/missions/sentinel-1](https://sentinel.esa.int/web/sentinel/missions/sentinel-1)

---

## 5. 💻 Software Libraries & GIS Standards

* **FastAPI Web Framework**: Ramírez, S. (2018). *FastAPI.* [https://fastapi.tiangolo.com](https://fastapi.tiangolo.com)
* **Scikit-Learn Machine Learning in Python**: Pedregosa, F., et al. (2011). *Scikit-learn: Machine Learning in Python.* Journal of Machine Learning Research, 12, 2825–2830.
* **Leaflet Mapping Library**: Agafonkin, V. (2010). *Leaflet: an open-source JavaScript library for mobile-friendly interactive maps.* [https://leafletjs.com](https://leafletjs.com)
* **IETF RFC 7946 (The GeoJSON Format)**: Butler, H., et al. (2016). *The GeoJSON Format Specification.* RFC 7946, Internet Engineering Task Force (IETF). [https://datatracker.ietf.org/doc/html/rfc7946](https://datatracker.ietf.org/doc/html/rfc7946)
* **CARTO Basemaps**: CARTO Dark Matter Tile Service. [https://carto.com/basemaps](https://carto.com/basemaps)
