import React, { useState } from 'react';
import { ShieldAlert, Download, AlertTriangle, CheckCircle, Clock, MapPin, Send } from 'lucide-react';

export default function AlertsFeed({ alerts, t, selectedState }) {
  const [filterLevel, setFilterLevel] = useState('All');

  const filteredAlerts = alerts.filter(a => {
    if (selectedState !== 'All' && a.state.toLowerCase() !== selectedState.toLowerCase()) return false;
    if (filterLevel !== 'All' && a.risk_level !== filterLevel) return false;
    return true;
  });

  const exportJSON = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(filteredAlerts, null, 2));
    const dlAnchorElem = document.createElement('a');
    dlAnchorElem.setAttribute("href", dataStr);
    dlAnchorElem.setAttribute("download", `ner_landslide_alerts_${Date.now()}.json`);
    dlAnchorElem.click();
  };

  const exportGeoJSON = () => {
    const geojson = {
      type: "FeatureCollection",
      features: filteredAlerts.map(a => ({
        type: "Feature",
        geometry: {
          type: "Point",
          coordinates: [a.longitude, a.latitude]
        },
        properties: {
          alert_id: a.alert_id,
          state: a.state,
          risk_level: a.risk_level,
          risk_score: a.risk_score,
          message: a.message,
          created_at: a.created_at
        }
      }))
    };
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(geojson, null, 2));
    const dlAnchorElem = document.createElement('a');
    dlAnchorElem.setAttribute("href", dataStr);
    dlAnchorElem.setAttribute("download", `ner_landslide_alerts_${Date.now()}.geojson`);
    dlAnchorElem.click();
  };

  return (
    <div style={{ marginTop: '20px' }}>
      
      {/* Action Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px', marginBottom: '16px' }}>
        <div>
          <h2 style={{ fontSize: '1.3rem', fontWeight: 800, color: '#fff', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <ShieldAlert size={22} color="#ef4444" />
            Active Early Warnings & Disaster Mitigation Advisories
          </h2>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            Real-time hazard notifications dispatched to state disaster management authorities (SDMA/DDMA)
          </p>
        </div>

        <div style={{ display: 'flex', gap: '10px' }}>
          <button onClick={exportJSON} className="btn-secondary" style={{ fontSize: '0.8rem' }}>
            <Download size={14} />
            {t('btn_export_json')}
          </button>
          <button onClick={exportGeoJSON} className="btn-primary" style={{ fontSize: '0.8rem' }}>
            <Download size={14} />
            {t('btn_export_geojson')}
          </button>
        </div>
      </div>

      {/* Alert Feed List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {filteredAlerts.length === 0 ? (
          <div className="glass-card" style={{ padding: '30px', textAlign: 'center', color: 'var(--text-muted)' }}>
            <CheckCircle size={32} color="#10b981" style={{ margin: '0 auto 10px' }} />
            <p>No active warning alerts for the selected criteria.</p>
          </div>
        ) : (
          filteredAlerts.map(alert => (
            <div
              key={alert.alert_id}
              className="glass-card"
              style={{
                padding: '16px 20px',
                borderLeft: `4px solid ${alert.risk_level === 'VERY HIGH' ? '#ef4444' : '#f97316'}`,
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'flex-start',
                flexWrap: 'wrap',
                gap: '12px'
              }}
            >
              <div style={{ flex: 1, minWidth: '280px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '6px' }}>
                  <span className={`badge-${alert.risk_level.toLowerCase().replace(' ', '-')}`}>
                    {alert.risk_level}
                  </span>
                  <span style={{ fontSize: '0.78rem', color: '#94a3b8', display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <MapPin size={13} />
                    <strong>{alert.state}</strong> ({alert.latitude.toFixed(4)}°N, {alert.longitude.toFixed(4)}°E)
                  </span>
                  <span style={{ fontSize: '0.75rem', color: '#64748b', display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <Clock size={12} />
                    {alert.created_at}
                  </span>
                </div>

                <p style={{ fontSize: '0.875rem', color: '#f1f5f9', fontWeight: 500, marginBottom: '6px' }}>
                  {alert.message}
                </p>

                {alert.action_required && (
                  <p style={{ fontSize: '0.78rem', color: '#fca5a5', background: 'rgba(239, 68, 68, 0.1)', padding: '4px 8px', borderRadius: '4px', display: 'inline-block' }}>
                    <strong>Action:</strong> {alert.action_required}
                  </p>
                )}
              </div>

              <div style={{ textAlign: 'right' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Alert ID</span>
                <p style={{ fontSize: '0.85rem', fontWeight: 700, color: '#60a5fa' }}>{alert.alert_id}</p>
                <span style={{
                  background: 'rgba(16, 185, 129, 0.15)',
                  color: '#34d399',
                  padding: '2px 8px',
                  borderRadius: '4px',
                  fontSize: '0.7rem',
                  fontWeight: 700,
                  display: 'inline-block',
                  marginTop: '4px'
                }}>
                  {alert.status}
                </span>
              </div>
            </div>
          ))
        )}
      </div>

    </div>
  );
}
