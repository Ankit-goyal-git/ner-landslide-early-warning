import React, { useEffect, useState, useRef } from 'react';
import { MapContainer, TileLayer, CircleMarker, Marker, Popup, useMap, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import { Layers, Eye, EyeOff, Navigation, AlertTriangle, Shield, CheckCircle } from 'lucide-react';

// Custom icons for citizen reports
const createCitizenIcon = () => {
  return L.divIcon({
    className: 'custom-citizen-icon',
    html: `<div style="
      background: #06b6d4;
      width: 18px;
      height: 18px;
      border-radius: 50%;
      border: 2px solid #ffffff;
      box-shadow: 0 0 10px #06b6d4;
      display: flex;
      align-items: center;
      justify-content: center;
    ">
      <div style="background: white; width: 6px; height: 6px; border-radius: 50%;"></div>
    </div>`,
    iconSize: [18, 18],
    iconAnchor: [9, 9]
  });
};

function MapController({ center, zoom }) {
  const map = useMap();

  useEffect(() => {
    // Invalidate size on mount & layout settle to prevent grey/broken tiles in flex/grid
    const timer = setTimeout(() => {
      map.invalidateSize();
    }, 250);
    return () => clearTimeout(timer);
  }, [map]);

  useEffect(() => {
    if (center) {
      map.flyTo(center, zoom, { duration: 1.0 });
      map.invalidateSize();
    }
  }, [center, zoom, map]);

  return null;
}

function MapClickHandler({ onMapClick, statesList }) {
  useMapEvents({
    click(e) {
      const clickLat = e.latlng.lat;
      const clickLon = e.latlng.lng;
      
      // Determine nearest state if available
      let nearestState = 'Assam';
      let minD = 999999;
      if (statesList && statesList.length > 0) {
        statesList.forEach(s => {
          const d = Math.pow(s.lat - clickLat, 2) + Math.pow(s.lon - clickLon, 2);
          if (d < minD) {
            minD = d;
            nearestState = s.name;
          }
        });
      }
      onMapClick(clickLat, clickLon, nearestState);
    }
  });
  return null;
}

export default function GisMap({
  riskPoints,
  citizenReports,
  selectedState,
  statesList,
  onLocationSelect,
  t,
  filterRiskLevel,
  setFilterRiskLevel
}) {
  const [showHeatmap, setShowHeatmap] = useState(true);
  const [showHistorical, setShowHistorical] = useState(true);
  const [showCitizenReports, setShowCitizenReports] = useState(true);
  const [baseLayer, setBaseLayer] = useState('esri_dark');
  
  // Default NER Center
  const defaultCenter = [26.1433, 91.7898];
  const [mapCenter, setMapCenter] = useState(defaultCenter);
  const [mapZoom, setMapZoom] = useState(7);

  useEffect(() => {
    if (selectedState && selectedState !== 'All') {
      const match = statesList.find(s => s.name.toLowerCase() === selectedState.toLowerCase());
      if (match) {
        setMapCenter([match.lat, match.lon]);
        setMapZoom(match.zoom || 8);
      }
    } else {
      setMapCenter([25.8, 92.5]);
      setMapZoom(7);
    }
  }, [selectedState, statesList]);

  const getColor = (tier) => {
    switch (tier) {
      case 'VERY HIGH': return '#ef4444';
      case 'HIGH': return '#f97316';
      case 'MODERATE': return '#f59e0b';
      default: return '#10b981';
    }
  };

  const filteredPoints = riskPoints.filter(pt => {
    if (selectedState !== 'All' && pt.state.toLowerCase() !== selectedState.toLowerCase()) {
      return false;
    }
    if (filterRiskLevel !== 'All' && pt.risk_level !== filterRiskLevel) {
      return false;
    }
    return true;
  });

  return (
    <div className="glass-card" style={{ height: '580px', position: 'relative', overflow: 'hidden' }}>
      
      {/* Map Control Bar Header */}
      <div style={{
        position: 'absolute',
        top: 12,
        right: 12,
        zIndex: 500,
        display: 'flex',
        flexWrap: 'wrap',
        gap: '8px',
        background: 'rgba(15, 23, 42, 0.90)',
        backdropFilter: 'blur(12px)',
        padding: '8px 12px',
        borderRadius: '10px',
        border: '1px solid var(--border-color)'
      }}>
        {/* Basemap Style Selector (100% Free, NO API Key Ever) */}
        <select
          value={baseLayer}
          onChange={(e) => setBaseLayer(e.target.value)}
          style={{
            background: 'rgba(30, 41, 59, 0.9)',
            color: '#93c5fd',
            border: '1px solid rgba(59, 130, 246, 0.4)',
            borderRadius: '6px',
            padding: '4px 8px',
            fontSize: '0.78rem',
            fontWeight: 600,
            cursor: 'pointer'
          }}
        >
          <option value="esri_dark">🗺️ Dark GIS (Esri)</option>
          <option value="osm">🌐 OpenStreetMap</option>
          <option value="topo">🏔️ Topo Relief (Esri)</option>
        </select>

        {/* Risk Level Quick Filter */}
        <select
          value={filterRiskLevel}
          onChange={(e) => setFilterRiskLevel(e.target.value)}
          style={{
            background: 'rgba(30, 41, 59, 0.9)',
            color: '#fff',
            border: '1px solid rgba(255, 255, 255, 0.15)',
            borderRadius: '6px',
            padding: '4px 8px',
            fontSize: '0.78rem',
            cursor: 'pointer'
          }}
        >
          <option value="All">{t('filter_risk_level')}</option>
          <option value="VERY HIGH">🔴 Very High Risk</option>
          <option value="HIGH">🟠 High Risk</option>
          <option value="MODERATE">🟡 Moderate Risk</option>
          <option value="LOW">🟢 Low Risk</option>
        </select>

        {/* Layer Toggles */}
        <button
          onClick={() => setShowHeatmap(!showHeatmap)}
          style={{
            background: showHeatmap ? 'rgba(59, 130, 246, 0.25)' : 'rgba(51, 65, 85, 0.5)',
            color: showHeatmap ? '#93c5fd' : '#94a3b8',
            border: `1px solid ${showHeatmap ? 'rgba(59, 130, 246, 0.5)' : 'transparent'}`,
            padding: '4px 10px',
            borderRadius: '6px',
            fontSize: '0.75rem',
            fontWeight: 600,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '4px'
          }}
        >
          <Layers size={13} />
          {t('layer_heatmap')}
        </button>

        <button
          onClick={() => setShowHistorical(!showHistorical)}
          style={{
            background: showHistorical ? 'rgba(239, 68, 68, 0.25)' : 'rgba(51, 65, 85, 0.5)',
            color: showHistorical ? '#fca5a5' : '#94a3b8',
            border: `1px solid ${showHistorical ? 'rgba(239, 68, 68, 0.5)' : 'transparent'}`,
            padding: '4px 10px',
            borderRadius: '6px',
            fontSize: '0.75rem',
            fontWeight: 600,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '4px'
          }}
        >
          {showHistorical ? <Eye size={13} /> : <EyeOff size={13} />}
          {t('layer_historical')}
        </button>

        <button
          onClick={() => setShowCitizenReports(!showCitizenReports)}
          style={{
            background: showCitizenReports ? 'rgba(6, 182, 212, 0.25)' : 'rgba(51, 65, 85, 0.5)',
            color: showCitizenReports ? '#67e8f9' : '#94a3b8',
            border: `1px solid ${showCitizenReports ? 'rgba(6, 182, 212, 0.5)' : 'transparent'}`,
            padding: '4px 10px',
            borderRadius: '6px',
            fontSize: '0.75rem',
            fontWeight: 600,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '4px'
          }}
        >
          <Navigation size={13} />
          {t('layer_citizen')} ({citizenReports?.length || 0})
        </button>
      </div>

      {/* Map Legend (Bottom Left) */}
      <div style={{
        position: 'absolute',
        bottom: 16,
        left: 16,
        zIndex: 500,
        background: 'rgba(15, 23, 42, 0.92)',
        backdropFilter: 'blur(10px)',
        padding: '10px 14px',
        borderRadius: '8px',
        border: '1px solid var(--border-color)',
        fontSize: '0.75rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '6px'
      }}>
        <span style={{ fontWeight: 700, color: '#f8fafc', marginBottom: '2px' }}>
          Calibrated Hazard Risk Legend
        </span>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#ef4444', display: 'inline-block', boxShadow: '0 0 8px #ef4444' }}></span>
          <span style={{ color: '#fca5a5' }}>Very High Risk (0.82 – 1.00)</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#f97316', display: 'inline-block' }}></span>
          <span style={{ color: '#fdba74' }}>High Risk (0.65 – 0.82)</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#f59e0b', display: 'inline-block' }}></span>
          <span style={{ color: '#fde047' }}>Moderate Risk (0.35 – 0.65)</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#10b981', display: 'inline-block' }}></span>
          <span style={{ color: '#86efac' }}>Low Risk (0.00 – 0.35)</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', borderTop: '1px solid rgba(255,255,255,0.1)', paddingTop: '4px', marginTop: '2px' }}>
          <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#06b6d4', display: 'inline-block', border: '1px solid white' }}></span>
          <span style={{ color: '#67e8f9' }}>Citizen Ground Report</span>
        </div>
      </div>

      {/* Interactive Map */}
      <MapContainer
        center={mapCenter}
        zoom={mapZoom}
        style={{ width: '100%', height: '100%' }}
        zoomControl={true}
      >
        <MapController center={mapCenter} zoom={mapZoom} />
        <MapClickHandler onMapClick={onLocationSelect} statesList={statesList} />

        {/* 100% Free, Zero-API-Key Tile Layer Engine */}
        {baseLayer === 'esri_dark' && (
          <TileLayer
            attribution='Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ'
            url="https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}"
            maxZoom={18}
          />
        )}
        {baseLayer === 'osm' && (
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            subdomains="abc"
            maxZoom={19}
          />
        )}
        {baseLayer === 'topo' && (
          <TileLayer
            attribution='Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ, TomTom, Intermap'
            url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}"
            maxZoom={18}
          />
        )}

        {/* 1. Risk Heatmap Surface Layer */}
        {showHeatmap && filteredPoints.map((pt, idx) => {
          const color = getColor(pt.risk_level);
          const radius = pt.risk_level === 'VERY HIGH' ? 24 : (pt.risk_level === 'HIGH' ? 18 : 12);
          const opacity = pt.risk_level === 'VERY HIGH' ? 0.35 : (pt.risk_level === 'HIGH' ? 0.25 : 0.15);
          return (
            <CircleMarker
              key={`heat-${idx}`}
              center={[pt.latitude, pt.longitude]}
              radius={radius}
              pathOptions={{
                color: 'transparent',
                fillColor: color,
                fillOpacity: opacity
              }}
            />
          );
        })}

        {/* 2. Historical Landslide Points Layer */}
        {showHistorical && filteredPoints.map((pt) => {
          const color = getColor(pt.risk_level);
          return (
            <CircleMarker
              key={`point-${pt.id}`}
              center={[pt.latitude, pt.longitude]}
              radius={pt.risk_level === 'VERY HIGH' ? 7 : 5}
              pathOptions={{
                color: '#ffffff',
                weight: 1.2,
                fillColor: color,
                fillOpacity: 0.95
              }}
              eventHandlers={{
                click: () => onLocationSelect(pt.latitude, pt.longitude, pt.state)
              }}
            >
              <Popup>
                <div style={{ minWidth: '220px', fontSize: '0.82rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <strong style={{ color: '#fff', fontSize: '0.95rem' }}>{pt.state} Landslide</strong>
                    <span className={`badge-${pt.risk_level.toLowerCase().replace(' ', '-')}`}>
                      {pt.risk_level}
                    </span>
                  </div>
                  
                  <p style={{ color: '#cbd5e1', marginBottom: '4px' }}>
                    <strong>Risk Score:</strong> {(pt.risk_score * 100).toFixed(1)}% (Prob: {pt.risk_score.toFixed(3)})
                  </p>
                  <p style={{ color: '#cbd5e1', marginBottom: '4px' }}>
                    <strong>Coordinates:</strong> {pt.latitude.toFixed(4)}° N, {pt.longitude.toFixed(4)}° E
                  </p>
                  <p style={{ color: '#cbd5e1', marginBottom: '4px' }}>
                    <strong>Event Date:</strong> {pt.event_date || 'Historical'}
                  </p>
                  <p style={{ color: '#cbd5e1', marginBottom: '4px' }}>
                    <strong>Trigger:</strong> {pt.trigger} ({pt.category})
                  </p>
                  <p style={{ color: '#94a3b8', fontSize: '0.75rem', marginTop: '6px', borderTop: '1px solid rgba(255,255,255,0.1)', paddingTop: '6px' }}>
                    {pt.explanation}
                  </p>
                </div>
              </Popup>
            </CircleMarker>
          );
        })}

        {/* 3. Citizen Reports Layer */}
        {showCitizenReports && citizenReports?.map((rpt) => (
          <Marker
            key={rpt.id}
            position={[rpt.latitude, rpt.longitude]}
            icon={createCitizenIcon()}
          >
            <Popup>
              <div style={{ minWidth: '200px', fontSize: '0.82rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                  <strong style={{ color: '#06b6d4', fontSize: '0.9rem' }}>Citizen Report</strong>
                  <span style={{
                    background: 'rgba(6, 182, 212, 0.2)',
                    color: '#67e8f9',
                    fontSize: '0.7rem',
                    padding: '2px 6px',
                    borderRadius: '4px'
                  }}>
                    {rpt.severity || 'OBSERVED'}
                  </span>
                </div>
                <p style={{ color: '#fff', fontWeight: 600 }}>Type: {rpt.report_type}</p>
                <p style={{ color: '#cbd5e1', margin: '4px 0' }}>"{rpt.description}"</p>
                <p style={{ color: '#94a3b8', fontSize: '0.72rem' }}>
                  Logged: {rpt.timestamp} | {rpt.reporter_name || 'Citizen'}
                </p>
              </div>
            </Popup>
          </Marker>
        ))}

      </MapContainer>
    </div>
  );
}
