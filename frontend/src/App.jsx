import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Navbar from './components/Navbar';
import KpiBanner from './components/KpiBanner';
import GisMap from './components/GisMap';
import PredictionInspector from './components/PredictionInspector';
import ChartsSection from './components/ChartsSection';
import AlertsFeed from './components/AlertsFeed';
import CitizenReportModal from './components/CitizenReportModal';
import ModelInfoModal from './components/ModelInfoModal';
import { getTranslation } from './i18n';

export default function App() {
  const [lang, setLang] = useState('en');
  const [activeTab, setActiveTab] = useState('dashboard');
  const [selectedState, setSelectedState] = useState('All');
  const [filterRiskLevel, setFilterRiskLevel] = useState('All');
  
  const [statesList, setStatesList] = useState([]);
  const [summary, setSummary] = useState(null);
  const [riskPoints, setRiskPoints] = useState([]);
  const [citizenReports, setCitizenReports] = useState([]);
  const [alerts, setAlerts] = useState([]);
  
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [isReportModalOpen, setIsReportModalOpen] = useState(false);
  const [isModelModalOpen, setIsModelModalOpen] = useState(false);
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  const t = (key) => getTranslation(lang, key);

  // Network status listener
  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Fetch initial dashboard data & cache in localStorage
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statesRes, sumRes, riskRes, reportsRes, alertsRes] = await Promise.all([
          axios.get('/api/states'),
          axios.get('/api/dashboard/summary'),
          axios.get('/api/risk'),
          axios.get('/api/reports'),
          axios.get('/api/alerts')
        ]);

        setStatesList(statesRes.data);
        setSummary(sumRes.data);
        setRiskPoints(riskRes.data);
        setCitizenReports(reportsRes.data);
        setAlerts(alertsRes.data);

        // Local cache for offline resilience
        localStorage.setItem('ner_summary', JSON.stringify(sumRes.data));
        localStorage.setItem('ner_risk_points', JSON.stringify(riskRes.data));
        localStorage.setItem('ner_states', JSON.stringify(statesRes.data));
      } catch (err) {
        console.warn('API fetch error, restoring from local cache:', err);
        const cachedSum = localStorage.getItem('ner_summary');
        const cachedPoints = localStorage.getItem('ner_risk_points');
        const cachedStates = localStorage.getItem('ner_states');
        if (cachedSum) setSummary(JSON.parse(cachedSum));
        if (cachedPoints) setRiskPoints(JSON.parse(cachedPoints));
        if (cachedStates) setStatesList(JSON.parse(cachedStates));
      }
    };

    fetchData();
  }, []);

  const handleLocationSelect = (lat, lon, stateName) => {
    setSelectedLocation({ lat, lon, state: stateName });
  };

  const handleReportSubmitted = (newReport) => {
    setCitizenReports(prev => [newReport, ...prev]);
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      
      {/* Navigation */}
      <Navbar
        currentLang={lang}
        setLang={setLang}
        t={t}
        selectedState={selectedState}
        setSelectedState={setSelectedState}
        statesList={statesList}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onOpenReportModal={() => setIsReportModalOpen(true)}
        onOpenModelModal={() => setIsModelModalOpen(true)}
        activeAlertsCount={alerts.length}
        isOnline={isOnline}
      />

      {/* Main Container */}
      <main style={{ flex: 1, padding: '0 24px 40px', maxWidth: '1600px', width: '100%', margin: '0 auto', boxSizing: 'border-box' }}>
        
        {/* KPI Banner */}
        <KpiBanner
          summary={summary}
          t={t}
          selectedState={selectedState}
        />

        {activeTab === 'dashboard' && (
          <>
            {/* GIS Map & Real-Time Inspector Grid */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'minmax(500px, 1.7fr) minmax(380px, 1.1fr)',
              gap: '20px',
              alignItems: 'stretch'
            }}>
              
              {/* GIS Map */}
              <div>
                <GisMap
                  riskPoints={riskPoints}
                  citizenReports={citizenReports}
                  selectedState={selectedState}
                  statesList={statesList}
                  onLocationSelect={handleLocationSelect}
                  t={t}
                  filterRiskLevel={filterRiskLevel}
                  setFilterRiskLevel={setFilterRiskLevel}
                />
              </div>

              {/* Real-time ML Prediction Inspector */}
              <div>
                <PredictionInspector
                  selectedLocation={selectedLocation}
                  selectedState={selectedState}
                  statesList={statesList}
                  t={t}
                  onAlertCreated={(alt) => setAlerts(prev => [alt, ...prev])}
                />
              </div>

            </div>

            {/* Authority Charts Section */}
            <ChartsSection
              summary={summary}
              t={t}
            />
          </>
        )}

        {activeTab === 'alerts' && (
          <AlertsFeed
            alerts={alerts}
            t={t}
            selectedState={selectedState}
          />
        )}

      </main>

      {/* Modals */}
      <CitizenReportModal
        isOpen={isReportModalOpen}
        onClose={() => setIsReportModalOpen(false)}
        onReportSubmitted={handleReportSubmitted}
        t={t}
      />

      <ModelInfoModal
        isOpen={isModelModalOpen}
        onClose={() => setIsModelModalOpen(false)}
      />

      {/* Footer */}
      <footer style={{
        borderTop: '1px solid var(--border-color)',
        padding: '16px 24px',
        textAlign: 'center',
        fontSize: '0.78rem',
        color: 'var(--text-muted)',
        background: 'rgba(15, 23, 42, 0.8)'
      }}>
        <p>
          AI-Based Landslide Risk Monitoring & Early Warning Platform for North-East India (NER) &bull; Built with NASA GLC Historical Data & Calibrated Machine Learning
        </p>
      </footer>

    </div>
  );
}
