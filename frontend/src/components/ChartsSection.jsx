import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Bar, Line, Doughnut } from 'react-chartjs-2';
import { BarChart3, TrendingUp, PieChart, Shield } from 'lucide-react';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

export default function ChartsSection({ summary, t }) {
  if (!summary) return null;

  // 1. State Distribution Bar Chart
  const stateLabels = Object.keys(summary.events_by_state || {});
  const stateData = Object.values(summary.events_by_state || {});

  const stateChartConfig = {
    labels: stateLabels,
    datasets: [
      {
        label: 'Historical Landslides',
        data: stateData,
        backgroundColor: [
          '#3b82f6', '#10b981', '#f59e0b', '#ef4444',
          '#8b5cf6', '#ec4899', '#06b6d4', '#f97316'
        ],
        borderRadius: 6
      }
    ]
  };

  // 2. Monsoon Seasonal Distribution Line Chart
  const monthLabels = Object.keys(summary.events_by_month || {});
  const monthData = Object.values(summary.events_by_month || {});

  const seasonalChartConfig = {
    labels: monthLabels,
    datasets: [
      {
        label: 'Monthly Landslide Frequency',
        data: monthData,
        borderColor: '#38bdf8',
        backgroundColor: 'rgba(56, 189, 248, 0.15)',
        fill: true,
        tension: 0.35,
        pointBackgroundColor: '#0284c7',
        pointRadius: 4
      }
    ]
  };

  // 3. Trigger Distribution Doughnut Chart
  const triggerLabels = Object.keys(summary.trigger_distribution || {});
  const triggerData = Object.values(summary.trigger_distribution || {});

  const triggerChartConfig = {
    labels: triggerLabels.map(l => l.replace('_', ' ')),
    datasets: [
      {
        data: triggerData,
        backgroundColor: [
          '#ef4444', '#f97316', '#3b82f6', '#10b981',
          '#eab308', '#a855f7', '#64748b', '#ec4899'
        ],
        borderWidth: 0
      }
    ]
  };

  // 4. Hazard Risk Tiers Doughnut Chart
  const riskLabels = ['LOW', 'MODERATE', 'HIGH', 'VERY HIGH'];
  const riskData = riskLabels.map(lvl => summary.risk_distribution?.[lvl] || 0);

  const riskChartConfig = {
    labels: riskLabels,
    datasets: [
      {
        data: riskData,
        backgroundColor: ['#10b981', '#f59e0b', '#f97316', '#ef4444'],
        borderWidth: 0
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: { color: '#94a3b8', font: { size: 11, family: 'Inter' } }
      },
      tooltip: {
        backgroundColor: '#0f172a',
        titleColor: '#fff',
        bodyColor: '#cbd5e1',
        borderColor: 'rgba(255,255,255,0.15)',
        borderWidth: 1
      }
    },
    scales: {
      x: {
        ticks: { color: '#94a3b8', font: { size: 10 } },
        grid: { color: 'rgba(255,255,255,0.05)' }
      },
      y: {
        ticks: { color: '#94a3b8', font: { size: 10 } },
        grid: { color: 'rgba(255,255,255,0.05)' }
      }
    }
  };

  const doughnutOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'right',
        labels: { color: '#cbd5e1', font: { size: 11, family: 'Inter' } }
      }
    }
  };

  return (
    <div style={{ marginTop: '24px' }}>
      <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: '#fff', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
        <BarChart3 size={20} color="#3b82f6" />
        Authority Analytics & Spatio-Temporal Insights
      </h3>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
        gap: '16px'
      }}>
        
        {/* State Distribution Chart */}
        <div className="glass-card" style={{ padding: '16px', height: '260px' }}>
          <p style={{ fontSize: '0.8rem', fontWeight: 700, color: '#e2e8f0', marginBottom: '10px' }}>
            {t('chart_state_distribution')}
          </p>
          <div style={{ height: '200px' }}>
            <Bar data={stateChartConfig} options={chartOptions} />
          </div>
        </div>

        {/* Monsoon Seasonal Trend */}
        <div className="glass-card" style={{ padding: '16px', height: '260px' }}>
          <p style={{ fontSize: '0.8rem', fontWeight: 700, color: '#e2e8f0', marginBottom: '10px' }}>
            {t('chart_seasonal_trend')}
          </p>
          <div style={{ height: '200px' }}>
            <Line data={seasonalChartConfig} options={chartOptions} />
          </div>
        </div>

        {/* Trigger Breakdown */}
        <div className="glass-card" style={{ padding: '16px', height: '260px' }}>
          <p style={{ fontSize: '0.8rem', fontWeight: 700, color: '#e2e8f0', marginBottom: '10px' }}>
            {t('chart_trigger_breakdown')}
          </p>
          <div style={{ height: '200px' }}>
            <Doughnut data={triggerChartConfig} options={doughnutOptions} />
          </div>
        </div>

        {/* Risk Distribution */}
        <div className="glass-card" style={{ padding: '16px', height: '260px' }}>
          <p style={{ fontSize: '0.8rem', fontWeight: 700, color: '#e2e8f0', marginBottom: '10px' }}>
            {t('chart_risk_distribution')}
          </p>
          <div style={{ height: '200px' }}>
            <Doughnut data={riskChartConfig} options={doughnutOptions} />
          </div>
        </div>

      </div>
    </div>
  );
}
