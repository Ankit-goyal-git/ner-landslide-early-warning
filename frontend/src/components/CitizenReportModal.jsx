import React, { useState } from 'react';
import { X, Send, AlertTriangle, Upload, CheckCircle2 } from 'lucide-react';
import axios from 'axios';

export default function CitizenReportModal({ isOpen, onClose, onReportSubmitted, t }) {
  const [reportType, setReportType] = useState('crack');
  const [severity, setSeverity] = useState('HIGH');
  const [state, setState] = useState('Sikkim');
  const [lat, setLat] = useState(27.3389);
  const [lon, setLon] = useState(88.6065);
  const [description, setDescription] = useState('');
  const [reporterName, setReporterName] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const payload = {
        latitude: parseFloat(lat),
        longitude: parseFloat(lon),
        report_type: reportType,
        severity: severity,
        state: state,
        description: description,
        reporter_name: reporterName || 'Citizen Inspector'
      };
      const res = await axios.post('/api/reports', payload);
      setSuccessMsg('Report submitted successfully! Plotted on map.');
      if (onReportSubmitted) {
        onReportSubmitted(res.data.report);
      }
      setTimeout(() => {
        setSuccessMsg('');
        onClose();
      }, 1400);
    } catch (err) {
      console.error('Error submitting report:', err);
    } finally {
      setSubmitting(false);
    }
  };

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
        maxWidth: '520px',
        padding: '24px',
        background: 'rgba(15, 23, 42, 0.98)',
        border: '1px solid rgba(255, 255, 255, 0.15)',
        boxShadow: '0 20px 40px rgba(0, 0, 0, 0.6)'
      }}>
        
        {/* Modal Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', borderBottom: '1px solid var(--border-color)', paddingBottom: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <AlertTriangle size={20} color="#ef4444" />
            <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: '#fff' }}>
              Citizen & Field Ground Hazard Reporting
            </h3>
          </div>
          <button onClick={onClose} style={{ background: 'transparent', border: 'none', color: '#94a3b8', cursor: 'pointer' }}>
            <X size={20} />
          </button>
        </div>

        {successMsg ? (
          <div style={{ padding: '30px', textAlign: 'center', color: '#34d399' }}>
            <CheckCircle2 size={42} style={{ margin: '0 auto 12px' }} />
            <h4>{successMsg}</h4>
          </div>
        ) : (
          <form onSubmit={handleSubmit}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '12px' }}>
              <div>
                <label style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)' }}>Report Type</label>
                <select
                  value={reportType}
                  onChange={(e) => setReportType(e.target.value)}
                  style={{ width: '100%', background: 'rgba(30, 41, 59, 0.8)', color: '#fff', border: '1px solid var(--border-color)', padding: '7px 10px', borderRadius: '6px', fontSize: '0.82rem', marginTop: '4px' }}
                >
                  <option value="crack">Road/Ground Tension Crack</option>
                  <option value="slope movement">Active Slope Movement</option>
                  <option value="rockfall">Rockfall / Debris Falling</option>
                  <option value="road blockage">Landslide Road Blockage</option>
                  <option value="landslide">Full Landslide Occurrence</option>
                  <option value="other">Other Geological Hazard</option>
                </select>
              </div>

              <div>
                <label style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)' }}>Observed Severity</label>
                <select
                  value={severity}
                  onChange={(e) => setSeverity(e.target.value)}
                  style={{ width: '100%', background: 'rgba(30, 41, 59, 0.8)', color: '#fff', border: '1px solid var(--border-color)', padding: '7px 10px', borderRadius: '6px', fontSize: '0.82rem', marginTop: '4px' }}
                >
                  <option value="LOW">Low (Minor seep/pebble roll)</option>
                  <option value="MODERATE">Moderate (Tension fissures)</option>
                  <option value="HIGH">High (Active slumping/road cut)</option>
                  <option value="CRITICAL">Critical (Impending mass collapse)</option>
                </select>
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '10px', marginBottom: '12px' }}>
              <div>
                <label style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)' }}>State</label>
                <select
                  value={state}
                  onChange={(e) => setState(e.target.value)}
                  style={{ width: '100%', background: 'rgba(30, 41, 59, 0.8)', color: '#fff', border: '1px solid var(--border-color)', padding: '7px 8px', borderRadius: '6px', fontSize: '0.82rem', marginTop: '4px' }}
                >
                  {['Arunachal Pradesh', 'Assam', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Sikkim', 'Tripura'].map(st => (
                    <option key={st} value={st}>{st}</option>
                  ))}
                </select>
              </div>

              <div>
                <label style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)' }}>Latitude (°N)</label>
                <input
                  type="number"
                  step="0.0001"
                  required
                  value={lat}
                  onChange={(e) => setLat(e.target.value)}
                  style={{ width: '100%', background: 'rgba(30, 41, 59, 0.8)', color: '#fff', border: '1px solid var(--border-color)', padding: '7px 8px', borderRadius: '6px', fontSize: '0.82rem', marginTop: '4px' }}
                />
              </div>

              <div>
                <label style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)' }}>Longitude (°E)</label>
                <input
                  type="number"
                  step="0.0001"
                  required
                  value={lon}
                  onChange={(e) => setLon(e.target.value)}
                  style={{ width: '100%', background: 'rgba(30, 41, 59, 0.8)', color: '#fff', border: '1px solid var(--border-color)', padding: '7px 8px', borderRadius: '6px', fontSize: '0.82rem', marginTop: '4px' }}
                />
              </div>
            </div>

            <div style={{ marginBottom: '12px' }}>
              <label style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)' }}>Observation Description</label>
              <textarea
                required
                rows={3}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Describe exact location landmark, crack width, water seepage, or road blockage..."
                style={{ width: '100%', background: 'rgba(30, 41, 59, 0.8)', color: '#fff', border: '1px solid var(--border-color)', padding: '8px 10px', borderRadius: '6px', fontSize: '0.82rem', marginTop: '4px', resize: 'vertical' }}
              />
            </div>

            <div style={{ marginBottom: '18px' }}>
              <label style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)' }}>Reporter Name / Agency (Optional)</label>
              <input
                type="text"
                value={reporterName}
                onChange={(e) => setReporterName(e.target.value)}
                placeholder="e.g., BRO Engineer / Local Volunteer"
                style={{ width: '100%', background: 'rgba(30, 41, 59, 0.8)', color: '#fff', border: '1px solid var(--border-color)', padding: '7px 10px', borderRadius: '6px', fontSize: '0.82rem', marginTop: '4px' }}
              />
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
              <button type="button" onClick={onClose} className="btn-secondary" style={{ fontSize: '0.82rem' }}>
                Cancel
              </button>
              <button type="submit" disabled={submitting} className="btn-primary" style={{ fontSize: '0.82rem' }}>
                <Send size={14} />
                {submitting ? 'Submitting...' : t('btn_submit_report')}
              </button>
            </div>
          </form>
        )}

      </div>
    </div>
  );
}
