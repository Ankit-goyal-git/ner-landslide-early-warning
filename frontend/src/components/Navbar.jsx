import React from 'react';
import { AlertTriangle, MapPin, Globe, Activity, ShieldAlert, FileText, Info, Wifi, WifiOff } from 'lucide-react';
import { languages } from '../i18n';

export default function Navbar({ 
  currentLang, 
  setLang, 
  t, 
  selectedState, 
  setSelectedState, 
  statesList,
  activeTab,
  setActiveTab,
  onOpenReportModal,
  onOpenModelModal,
  activeAlertsCount,
  isOnline
}) {
  return (
    <header style={{
      background: 'rgba(15, 23, 42, 0.92)',
      backdropFilter: 'blur(16px)',
      borderBottom: '1px solid var(--border-color)',
      position: 'sticky',
      top: 0,
      zIndex: 1000,
      padding: '12px 24px'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
        
        {/* Branding & Demo Mode Tag */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div style={{
            width: '42px',
            height: '42px',
            borderRadius: '10px',
            background: 'linear-gradient(135deg, #ef4444, #f97316)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 16px rgba(239, 68, 68, 0.4)'
          }}>
            <AlertTriangle color="#fff" size={24} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <h1 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#f8fafc', letterSpacing: '-0.02em' }}>
                NER Landslide AI Risk & Warning
              </h1>
              <span style={{
                background: 'rgba(59, 130, 246, 0.2)',
                color: '#60a5fa',
                border: '1px solid rgba(59, 130, 246, 0.35)',
                fontSize: '0.68rem',
                fontWeight: 700,
                padding: '2px 8px',
                borderRadius: '6px'
              }}>
                {t('demo_mode')}
              </span>
            </div>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              8 North-East Indian States Hazard Monitoring & Disaster Management System
            </p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <button
            onClick={() => setActiveTab('dashboard')}
            style={{
              background: activeTab === 'dashboard' ? 'rgba(59, 130, 246, 0.25)' : 'transparent',
              color: activeTab === 'dashboard' ? '#93c5fd' : '#94a3b8',
              border: activeTab === 'dashboard' ? '1px solid rgba(59, 130, 246, 0.4)' : '1px solid transparent',
              padding: '6px 14px',
              borderRadius: '8px',
              fontWeight: 600,
              fontSize: '0.875rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            <Activity size={16} />
            {t('nav_dashboard')}
          </button>

          <button
            onClick={() => setActiveTab('alerts')}
            style={{
              background: activeTab === 'alerts' ? 'rgba(239, 68, 68, 0.25)' : 'transparent',
              color: activeTab === 'alerts' ? '#fca5a5' : '#94a3b8',
              border: activeTab === 'alerts' ? '1px solid rgba(239, 68, 68, 0.4)' : '1px solid transparent',
              padding: '6px 14px',
              borderRadius: '8px',
              fontWeight: 600,
              fontSize: '0.875rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            <ShieldAlert size={16} />
            {t('nav_alerts')}
            {activeAlertsCount > 0 && (
              <span style={{
                background: '#ef4444',
                color: '#fff',
                borderRadius: '9999px',
                padding: '1px 6px',
                fontSize: '0.7rem',
                fontWeight: 800
              }}>
                {activeAlertsCount}
              </span>
            )}
          </button>

          <button
            onClick={onOpenReportModal}
            className="btn-danger"
            style={{ fontSize: '0.82rem', padding: '6px 12px' }}
          >
            <FileText size={15} />
            {t('nav_citizen_report')}
          </button>

          <button
            onClick={onOpenModelModal}
            className="btn-secondary"
            style={{ fontSize: '0.82rem', padding: '6px 12px' }}
          >
            <Info size={15} />
            {t('nav_model_info')}
          </button>
        </div>

        {/* State Selector & Language Switcher */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          
          {/* State Filter */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <MapPin size={16} color="#94a3b8" />
            <select
              value={selectedState}
              onChange={(e) => setSelectedState(e.target.value)}
              style={{
                background: 'rgba(30, 41, 59, 0.8)',
                color: '#f8fafc',
                border: '1px solid var(--border-color)',
                borderRadius: '8px',
                padding: '6px 10px',
                fontSize: '0.85rem',
                outline: 'none',
                cursor: 'pointer'
              }}
            >
              <option value="All">{t('filter_state')}</option>
              {statesList.map(s => (
                <option key={s.name} value={s.name}>{s.name}</option>
              ))}
            </select>
          </div>

          {/* Language Switcher */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Globe size={16} color="#94a3b8" />
            <select
              value={currentLang}
              onChange={(e) => setLang(e.target.value)}
              style={{
                background: 'rgba(30, 41, 59, 0.8)',
                color: '#f8fafc',
                border: '1px solid var(--border-color)',
                borderRadius: '8px',
                padding: '6px 10px',
                fontSize: '0.85rem',
                outline: 'none',
                cursor: 'pointer'
              }}
            >
              {languages.map(l => (
                <option key={l.code} value={l.code}>{l.native} ({l.name})</option>
              ))}
            </select>
          </div>

          {/* Network Status Badge */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            fontSize: '0.75rem',
            color: isOnline ? '#34d399' : '#f87171',
            background: isOnline ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
            padding: '4px 8px',
            borderRadius: '6px',
            border: `1px solid ${isOnline ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`
          }}>
            {isOnline ? <Wifi size={13} /> : <WifiOff size={13} />}
            <span>{isOnline ? t('status_online') : t('status_offline')}</span>
          </div>

        </div>

      </div>
    </header>
  );
}
