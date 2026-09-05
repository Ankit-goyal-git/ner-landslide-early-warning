import React, { useState, useEffect } from 'react';
import { Cpu, Sliders, AlertTriangle, ArrowRight, CheckCircle2, ShieldAlert, RefreshCw } from 'lucide-react';
import axios from 'axios';

const STATE_PROFILES = {
  'Arunachal Pradesh': { lat: 27.0987, lon: 93.8160, slope: 34, baseRain: 450 },
  'Assam': { lat: 26.1433, lon: 91.7898, slope: 14, baseRain: 390 },
  'Manipur': { lat: 24.8170, lon: 93.9368, slope: 27, baseRain: 380 },
  'Meghalaya': { lat: 25.5788, lon: 91.8933, slope: 28, baseRain: 560 },
  'Mizoram': { lat: 23.7271, lon: 92.7176, slope: 29, baseRain: 430 },
  'Nagaland': { lat: 25.6751, lon: 94.1086, slope: 31, baseRain: 410 },
  'Sikkim': { lat: 27.3389, lon: 88.6065, slope: 38, baseRain: 480 },
  'Tripura': { lat: 23.8315, lon: 91.2868, slope: 12, baseRain: 360 }
};

const getEstimatedRainfall = (stateName, selectedMonth) => {
  const prof = STATE_PROFILES[stateName] || { baseRain: 400 };
  const monthWeights = {
    1: 0.05, 2: 0.08, 3: 0.18, 4: 0.45, 5: 0.70,
    6: 1.05, 7: 1.20, 8: 1.00, 9: 0.80, 10: 0.35,
    11: 0.10, 12: 0.04
  };
  const w = monthWeights[selectedMonth] || 1.0;
  return Math.round(prof.baseRain * w);
};

export default function PredictionInspector({
  selectedLocation,
  selectedState,
  statesList,
  t,
  onAlertCreated
}) {
  const [lat, setLat] = useState(27.3389);
  const [lon, setLon] = useState(88.6065);
  const [state, setState] = useState('Sikkim');
  const [month, setMonth] = useState(7);
  const [rainfallMm, setRainfallMm] = useState(480);
  const [slopeDeg, setSlopeDeg] = useState(38);
  
  const [loading, setLoading] = useState(false);
  const [prediction, setPrediction] = useState(null);

  // Sync when selectedState in Navbar changes
  useEffect(() => {
    if (selectedState && selectedState !== 'All' && STATE_PROFILES[selectedState]) {
      const prof = STATE_PROFILES[selectedState];
      const rain = getEstimatedRainfall(selectedState, month);
      setState(selectedState);
      setLat(prof.lat);
      setLon(prof.lon);
      setSlopeDeg(prof.slope);
      setRainfallMm(rain);
      runPrediction(prof.lat, prof.lon, selectedState, month, rain, prof.slope);
    }
  }, [selectedState]);

  // Sync when user clicks map or historical marker
  useEffect(() => {
    if (selectedLocation) {
      const targetState = selectedLocation.state || state;
      const prof = STATE_PROFILES[targetState] || { slope: 25 };
      const rain = getEstimatedRainfall(targetState, month);
      
      setLat(selectedLocation.lat);
      setLon(selectedLocation.lon);
      setState(targetState);
      setSlopeDeg(prof.slope);
      setRainfallMm(rain);
      runPrediction(selectedLocation.lat, selectedLocation.lon, targetState, month, rain, prof.slope);
    }
  }, [selectedLocation]);

  const handleStateChange = (newState) => {
    const prof = STATE_PROFILES[newState] || { lat: 26.0, lon: 92.0, slope: 25 };
    const rain = getEstimatedRainfall(newState, month);
    setState(newState);
    setLat(prof.lat);
    setLon(prof.lon);
    setSlopeDeg(prof.slope);
    setRainfallMm(rain);
    runPrediction(prof.lat, prof.lon, newState, month, rain, prof.slope);
  };

  const handleMonthChange = (newMonth) => {
    setMonth(newMonth);
    const rain = getEstimatedRainfall(state, newMonth);
    setRainfallMm(rain);
    runPrediction(lat, lon, state, newMonth, rain, slopeDeg);
  };

  const runPrediction = async (pLat = lat, pLon = lon, pState = state, pMonth = month, pRain = rainfallMm, pSlope = slopeDeg) => {
    setLoading(true);
    try {
      const res = await axios.post('/api/predict', {
        latitude: parseFloat(pLat),
        longitude: parseFloat(pLon),
        state: pState,
        month: parseInt(pMonth),
        rainfall_mm: parseFloat(pRain),
        slope_deg: parseFloat(pSlope)
      });
      setPrediction(res.data);
    } catch (err) {
      console.error('Error computing risk prediction:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    runPrediction();
  }, []);

  const getTierColor = (tier) => {
    switch (tier) {
      case 'VERY HIGH': return '#ef4444';
      case 'HIGH': return '#f97316';
      case 'MODERATE': return '#f59e0b';
      default: return '#10b981';
    }
  };

  const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

  return (
    <div className="glass-card" style={{ padding: '20px', height: '100%' }}>
      
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px', borderBottom: '1px solid var(--border-color)', paddingBottom: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            background: 'rgba(59, 130, 246, 0.2)',
            padding: '8px',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <Cpu size={20} color="#60a5fa" />
          </div>
          <div>
            <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#fff' }}>
              {t('inspector_title')}
            </h3>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Real-Time Calibrated Random Forest Risk Estimator
            </p>
          </div>
        </div>

        <button
          onClick={() => runPrediction()}
          disabled={loading}
          className="btn-primary"
          style={{ fontSize: '0.78rem', padding: '6px 12px' }}
        >
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
          {loading ? 'Evaluating...' : t('btn_predict')}
        </button>
      </div>

      {/* Control Inputs Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '12px', marginBottom: '18px' }}>
        <div>
          <label style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', fontWeight: 600 }}>Latitude (°N)</label>
          <input
            type="number"
            step="0.0001"
            value={lat}
            onChange={(e) => {
              const val = parseFloat(e.target.value) || 0;
              setLat(val);
              if (val >= 20.0 && val <= 32.0) {
                runPrediction(val, lon, state, month, rainfallMm, slopeDeg);
              }
            }}
            style={{
              width: '100%',
              background: 'rgba(30, 41, 59, 0.8)',
              border: '1px solid var(--border-color)',
              color: '#fff',
              padding: '6px 8px',
              borderRadius: '6px',
              fontSize: '0.82rem',
              marginTop: '4px'
            }}
          />
        </div>

        <div>
          <label style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', fontWeight: 600 }}>Longitude (°E)</label>
          <input
            type="number"
            step="0.0001"
            value={lon}
            onChange={(e) => {
              const val = parseFloat(e.target.value) || 0;
              setLon(val);
              if (val >= 85.0 && val <= 98.0) {
                runPrediction(lat, val, state, month, rainfallMm, slopeDeg);
              }
            }}
            style={{
              width: '100%',
              background: 'rgba(30, 41, 59, 0.8)',
              border: '1px solid var(--border-color)',
              color: '#fff',
              padding: '6px 8px',
              borderRadius: '6px',
              fontSize: '0.82rem',
              marginTop: '4px'
            }}
          />
        </div>

        <div>
          <label style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', fontWeight: 600 }}>State Context</label>
          <select
            value={state}
            onChange={(e) => handleStateChange(e.target.value)}
            style={{
              width: '100%',
              background: 'rgba(30, 41, 59, 0.8)',
              border: '1px solid var(--border-color)',
              color: '#fff',
              padding: '6px 8px',
              borderRadius: '6px',
              fontSize: '0.82rem',
              marginTop: '4px'
            }}
          >
            {['Arunachal Pradesh', 'Assam', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Sikkim', 'Tripura'].map(st => (
              <option key={st} value={st}>{st}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Sliders for Sensitivity Simulation */}
      <div style={{ background: 'rgba(30, 41, 59, 0.4)', padding: '12px 14px', borderRadius: '8px', border: '1px solid var(--border-color)', marginBottom: '18px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '10px' }}>
          <Sliders size={14} color="#94a3b8" />
          <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#e2e8f0', textTransform: 'uppercase' }}>
            Environmental & Climatic Simulation Sliders
          </span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '14px' }}>
          {/* Month Slider */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', color: 'var(--text-secondary)' }}>
              <span>Season Month:</span>
              <strong style={{ color: '#60a5fa' }}>{monthNames[month - 1]} ({month})</strong>
            </div>
            <input
              type="range"
              min="1"
              max="12"
              value={month}
              onChange={(e) => handleMonthChange(parseInt(e.target.value))}
              style={{ width: '100%', cursor: 'pointer', marginTop: '4px' }}
            />
          </div>

          {/* Rainfall Slider */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', color: 'var(--text-secondary)' }}>
              <span>Antecedent Rain:</span>
              <strong style={{ color: '#38bdf8' }}>{rainfallMm} mm</strong>
            </div>
            <input
              type="range"
              min="10"
              max="650"
              step="10"
              value={rainfallMm}
              onChange={(e) => {
                const r = parseFloat(e.target.value);
                setRainfallMm(r);
                runPrediction(lat, lon, state, month, r, slopeDeg);
              }}
              style={{ width: '100%', cursor: 'pointer', marginTop: '4px' }}
            />
          </div>

          {/* Slope Slider */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', color: 'var(--text-secondary)' }}>
              <span>Slope Angle:</span>
              <strong style={{ color: '#f59e0b' }}>{slopeDeg}°</strong>
            </div>
            <input
              type="range"
              min="5"
              max="55"
              value={slopeDeg}
              onChange={(e) => {
                const s = parseFloat(e.target.value);
                setSlopeDeg(s);
                runPrediction(lat, lon, state, month, rainfallMm, s);
              }}
              style={{ width: '100%', cursor: 'pointer', marginTop: '4px' }}
            />
          </div>
        </div>
      </div>

      {/* Prediction Output Section */}
      {prediction && (
        <div style={{
          background: 'rgba(15, 23, 42, 0.95)',
          borderRadius: '10px',
          border: `1px solid ${getTierColor(prediction.risk_level)}40`,
          padding: '16px',
          position: 'relative'
        }}>
          {/* Top Score & Badge */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <div>
              <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                Landslide Probability Score
              </span>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
                <h2 style={{ fontSize: '1.8rem', fontWeight: 800, color: getTierColor(prediction.risk_level) }}>
                  {(prediction.risk_score * 100).toFixed(1)}%
                </h2>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                  (Confidence: {(prediction.confidence * 100).toFixed(0)}%)
                </span>
              </div>
            </div>

            <div style={{ textAlign: 'right' }}>
              <span className={`badge-${prediction.risk_level.toLowerCase().replace(' ', '-')}`} style={{ fontSize: '0.85rem', padding: '6px 14px' }}>
                {prediction.risk_level} RISK
              </span>
              <p style={{ fontSize: '0.68rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                Model: {prediction.model_version}
              </p>
            </div>
          </div>

          {/* Explanation Text */}
          <div style={{
            background: 'rgba(30, 41, 59, 0.6)',
            padding: '10px 12px',
            borderRadius: '6px',
            borderLeft: `3px solid ${getTierColor(prediction.risk_level)}`,
            marginBottom: '14px'
          }}>
            <p style={{ fontSize: '0.78rem', color: '#e2e8f0', lineHeight: 1.45 }}>
              {prediction.explanation}
            </p>
          </div>

          {/* Contributing Factors Bars */}
          <div>
            <span style={{ fontSize: '0.72rem', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: '8px' }}>
              Feature Contribution & Sensitivity Breakdown:
            </span>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px 16px' }}>
              {Object.entries(prediction.contributing_factors || {}).map(([factor, weight]) => (
                <div key={factor}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', color: '#cbd5e1', marginBottom: '2px' }}>
                    <span>{factor}</span>
                    <strong>{(weight * 100).toFixed(0)}%</strong>
                  </div>
                  <div style={{ width: '100%', height: '5px', background: 'rgba(255,255,255,0.1)', borderRadius: '3px', overflow: 'hidden' }}>
                    <div style={{
                      width: `${Math.min(100, weight * 100)}%`,
                      height: '100%',
                      background: 'linear-gradient(90deg, #3b82f6, #ef4444)',
                      borderRadius: '3px'
                    }} />
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>
      )}

    </div>
  );
}
