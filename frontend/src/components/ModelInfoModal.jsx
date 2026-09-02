import React, { useEffect, useState } from 'react';
import { X, Cpu, ShieldCheck, Database, Award, Info, GitFork, Radio } from 'lucide-react';
import axios from 'axios';

export default function ModelInfoModal({ isOpen, onClose }) {
  const [modelInfo, setModelInfo] = useState(null);
  const [interfaces, setInterfaces] = useState(null);

  useEffect(() => {
    if (isOpen) {
      axios.get('/api/model/info').then(res => setModelInfo(res.data)).catch(console.error);
      axios.get('/api/interfaces/status').then(res => setInterfaces(res.data)).catch(console.error);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0, 0, 0, 0.75)',
      backdropFilter: 'blur(8px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 2000,
      padding: '16px'
    }}>
      <div className="glass-card" style={{
        width: '100%',
        maxWidth: '680px',
        maxHeight: '90vh',
        overflowY: 'auto',
        padding: '24px',
        background: 'rgba(15, 23, 42, 0.98)',
        border: '1px solid rgba(255, 255, 255, 0.15)',
        boxShadow: '0 20px 40px rgba(0, 0, 0, 0.6)'
      }}>
        
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', borderBottom: '1px solid var(--border-color)', paddingBottom: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Cpu size={22} color="#3b82f6" />
            <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#fff' }}>
              ML Architecture & Scientific Provenance
            </h3>
          </div>
          <button onClick={onClose} style={{ background: 'transparent', border: 'none', color: '#94a3b8', cursor: 'pointer' }}>
            <X size={20} />
          </button>
        </div>

        {/* Core Architecture Overview */}
        <div style={{ marginBottom: '20px' }}>
          <h4 style={{ fontSize: '0.9rem', fontWeight: 700, color: '#60a5fa', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <ShieldCheck size={16} />
            Calibrated Model Specifications
          </h4>
          <div style={{ background: 'rgba(30, 41, 59, 0.6)', padding: '12px 16px', borderRadius: '8px', fontSize: '0.82rem', color: '#cbd5e1', lineHeight: 1.6 }}>
            <p><strong>Selected Model:</strong> Random Forest Classifier (Calibrated Probability Ensemble)</p>
            <p><strong>Baseline Benchmark:</strong> Logistic Regression (Standard Scaled) & Gradient Boosting</p>
            <p><strong>Data Leakage Prevention:</strong> Strictly Temporal Split (Train &le; 2013, Val 2014-2015, Test Hold-out 2016)</p>
            <p><strong>Optimization Target:</strong> Recall prioritized for safety-critical early warning</p>
          </div>
        </div>

        {/* Feature Importance Table */}
        <div style={{ marginBottom: '20px' }}>
          <h4 style={{ fontSize: '0.9rem', fontWeight: 700, color: '#38bdf8', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Award size={16} />
            Top Predictive Feature Importances
          </h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            {Object.entries(modelInfo?.feature_importances || {}).slice(0, 6).map(([feat, score]) => (
              <div key={feat} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(30, 41, 59, 0.4)', padding: '6px 12px', borderRadius: '6px', fontSize: '0.78rem' }}>
                <span style={{ color: '#e2e8f0', fontFamily: 'monospace' }}>{feat}</span>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <div style={{ width: '80px', height: '6px', background: 'rgba(255,255,255,0.1)', borderRadius: '3px', overflow: 'hidden' }}>
                    <div style={{ width: `${(score * 100).toFixed(0)}%`, height: '100%', background: '#3b82f6' }} />
                  </div>
                  <strong style={{ color: '#60a5fa' }}>{score.toFixed(4)}</strong>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Future Live Data Architecture Interfaces */}
        <div style={{ marginBottom: '16px' }}>
          <h4 style={{ fontSize: '0.9rem', fontWeight: 700, color: '#a855f7', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Radio size={16} />
            Future Live Data Integration Interfaces
          </h4>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
            <div style={{ background: 'rgba(30, 41, 59, 0.5)', padding: '10px', borderRadius: '8px', fontSize: '0.75rem' }}>
              <strong style={{ color: '#c084fc' }}>IMD Nowcast & Radar API</strong>
              <p style={{ color: '#94a3b8', marginTop: '2px' }}>Interface ready for real-time Doppler radar rainfall accumulation streaming.</p>
            </div>
            <div style={{ background: 'rgba(30, 41, 59, 0.5)', padding: '10px', borderRadius: '8px', fontSize: '0.75rem' }}>
              <strong style={{ color: '#c084fc' }}>NASA GPM IMERG Feed</strong>
              <p style={{ color: '#94a3b8', marginTop: '2px' }}>Satellite half-hourly precipitation grid integration schema defined.</p>
            </div>
            <div style={{ background: 'rgba(30, 41, 59, 0.5)', padding: '10px', borderRadius: '8px', fontSize: '0.75rem' }}>
              <strong style={{ color: '#c084fc' }}>Copernicus Sentinel-1 SAR</strong>
              <p style={{ color: '#94a3b8', marginTop: '2px' }}>InSAR ground displacement and hill slope velocity contract active.</p>
            </div>
            <div style={{ background: 'rgba(30, 41, 59, 0.5)', padding: '10px', borderRadius: '8px', fontSize: '0.75rem' }}>
              <strong style={{ color: '#c084fc' }}>IoT In-Situ Sensor Nodes</strong>
              <p style={{ color: '#94a3b8', marginTop: '2px' }}>Telemetry schema for pore water pressure and biaxial tilt sensors.</p>
            </div>
          </div>
        </div>

        <div style={{ textAlign: 'right' }}>
          <button onClick={onClose} className="btn-secondary" style={{ fontSize: '0.82rem' }}>
            Close
          </button>
        </div>

      </div>
    </div>
  );
}
