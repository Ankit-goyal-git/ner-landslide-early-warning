import React from 'react';
import { Database, AlertOctagon, Flame, MapPin, Users, BellRing } from 'lucide-react';

export default function KpiBanner({ summary, t, selectedState }) {
  const cards = [
    {
      title: t('kpi_total_landslides'),
      value: summary?.total_ner_landslides || 251,
      subtitle: selectedState === 'All' ? 'Historical Catalog Events' : `${selectedState} Events`,
      icon: Database,
      color: '#3b82f6',
      bgGlow: 'rgba(59, 130, 246, 0.15)'
    },
    {
      title: t('kpi_very_high_risk'),
      value: summary?.very_high_risk_locations || 142,
      subtitle: 'Critical Hazard Probability',
      icon: Flame,
      color: '#ef4444',
      bgGlow: 'rgba(239, 68, 68, 0.2)',
      pulse: true
    },
    {
      title: t('kpi_high_risk'),
      value: summary?.high_risk_locations || 78,
      subtitle: 'Vigilance & Advisory Active',
      icon: AlertOctagon,
      color: '#f97316',
      bgGlow: 'rgba(249, 115, 22, 0.15)'
    },
    {
      title: t('kpi_most_affected'),
      value: summary?.most_affected_state || 'Assam',
      subtitle: '82 Documented Incidents',
      icon: MapPin,
      color: '#a855f7',
      bgGlow: 'rgba(168, 85, 247, 0.15)'
    },
    {
      title: t('kpi_active_alerts'),
      value: summary?.active_alerts_count || 5,
      subtitle: 'Active Early Warnings',
      icon: BellRing,
      color: '#eab308',
      bgGlow: 'rgba(234, 179, 8, 0.15)'
    },
    {
      title: t('kpi_casualties'),
      value: `${summary?.total_fatalities || 54} Fatal / ${summary?.total_injuries || 21} Inj`,
      subtitle: 'Historical Human Impact',
      icon: Users,
      color: '#06b6d4',
      bgGlow: 'rgba(6, 182, 212, 0.15)'
    }
  ];

  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(190px, 1fr))',
      gap: '16px',
      margin: '20px 0'
    }}>
      {cards.map((card, idx) => {
        const IconComponent = card.icon;
        return (
          <div
            key={idx}
            className="glass-card"
            style={{
              padding: '16px 20px',
              display: 'flex',
              alignItems: 'center',
              gap: '16px',
              borderLeft: `4px solid ${card.color}`,
              position: 'relative',
              overflow: 'hidden'
            }}
          >
            <div style={{
              width: '46px',
              height: '46px',
              borderRadius: '12px',
              background: card.bgGlow,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0
            }}>
              <IconComponent size={24} color={card.color} />
            </div>
            <div>
              <p style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                {card.title}
              </p>
              <h3 style={{
                fontSize: typeof card.value === 'string' && card.value.length > 8 ? '1.1rem' : '1.5rem',
                fontWeight: 800,
                color: '#fff',
                margin: '2px 0'
              }}>
                {card.value}
              </h3>
              <p style={{ fontSize: '0.72rem', color: 'var(--text-secondary)' }}>
                {card.subtitle}
              </p>
            </div>
          </div>
        );
      })}
    </div>
  );
}
