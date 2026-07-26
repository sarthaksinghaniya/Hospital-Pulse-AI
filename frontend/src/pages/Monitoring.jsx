import { useState, useEffect } from 'react';
import Card from '../components/ui/Card.jsx';
import Skeleton from '../components/ui/Skeleton.jsx';
import Badge from '../components/ui/Badge.jsx';
import ChatbotPanel from '../components/ChatbotPanel.jsx';
import useApi from '../hooks/useApi.js';
import { getVitalsOverview, getAdherenceOverview } from '../services/api.js';
import { formatPercent } from '../utils/formatters.js';

// Simulation hook to make vitals "live"
function useLiveVitals(initialData) {
  const [data, setData] = useState(initialData);

  useEffect(() => {
    if (!initialData || !initialData.length) return;
    setData(initialData);

    const interval = setInterval(() => {
      setData(prev => prev.map(patient => {
        // Randomly fluctuate vitals slightly
        const hrChange = Math.floor(Math.random() * 5) - 2;
        const o2Change = Math.floor(Math.random() * 3) - 1;
        
        let newHr = (patient.heart_rate || 75) + hrChange;
        let newO2 = (patient.oxygen_saturation || patient.spo2 || 98) + o2Change;
        
        newHr = Math.max(40, Math.min(180, newHr));
        newO2 = Math.max(75, Math.min(100, newO2));
        
        // Calculate dynamic risk
        let newRisk = 'low';
        if (newHr > 120 || newHr < 50 || newO2 < 90) newRisk = 'high';
        else if (newHr > 100 || newHr < 60 || newO2 < 95) newRisk = 'medium';

        return {
          ...patient,
          heart_rate: newHr,
          oxygen_saturation: newO2,
          risk: newRisk
        };
      }));
    }, 2000);
    return () => clearInterval(interval);
  }, [initialData]);

  return data;
}

export default function Monitoring() {
  const { data: vitals, loading: vitalsLoading, error: vitalsError } = useApi(() => getVitalsOverview());
  const { data: adherence, loading: adhLoading, error: adhError } = useApi(() => getAdherenceOverview());

  const vitalsList = vitals?.patients || vitals?.vitals || [];
  
  // Apply live simulation
  const liveVitals = useLiveVitals(vitalsList);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 fade-in">
      <Card title="Live Vitals Grid" subtitle="Real-time monitoring" className="lg:col-span-2">
        {vitalsLoading ? (
          <div className="space-y-2">
            {[1, 2, 3, 4, 5].map((i) => <Skeleton key={i} className="h-10 w-full" />)}
          </div>
        ) : vitalsError ? (
          <p className="text-sm text-danger">{vitalsError.message || 'Unable to load vitals'}</p>
        ) : liveVitals?.length ? (
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="text-xs text-text-muted uppercase bg-slate-50/50 border-b border-slate-200/60">
                <tr>
                  <th className="px-4 py-3 font-semibold rounded-tl-xl">Patient</th>
                  <th className="px-4 py-3 font-semibold">Heart Rate</th>
                  <th className="px-4 py-3 font-semibold">SpO2</th>
                  <th className="px-4 py-3 font-semibold rounded-tr-xl">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {liveVitals.slice(0, 8).map((item, idx) => {
                  const isHighRisk = item.risk === 'high';
                  return (
                    <tr 
                      key={idx} 
                      className={`transition-colors duration-500 ${isHighRisk ? 'bg-red-50/50 hover:bg-red-50' : 'hover:bg-slate-50/50'}`}
                    >
                      <td className="px-4 py-3 font-medium text-text-primary">
                        {item.patient_id || item.name || `Patient 10${idx}`}
                      </td>
                      <td className={`px-4 py-3 font-mono ${isHighRisk ? 'text-danger font-bold' : ''}`}>
                        {Math.round(item.heart_rate) || 75} bpm
                        {isHighRisk && <span className="ml-2 inline-block h-2 w-2 rounded-full bg-danger animate-pulse" />}
                      </td>
                      <td className={`px-4 py-3 font-mono ${item.oxygen_saturation < 92 ? 'text-warning font-bold' : ''}`}>
                        {Math.round(item.oxygen_saturation) || 98}%
                      </td>
                      <td className="px-4 py-3">
                        <Badge variant={isHighRisk ? 'danger' : (item.risk === 'medium' ? 'warning' : 'success')}>
                          {isHighRisk ? 'CRITICAL' : item.risk || 'STABLE'}
                        </Badge>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-sm text-text-muted">📡 Connect devices to start real-time monitoring.</p>
        )}
      </Card>

      <div className="space-y-6 lg:col-span-1">
        <Card title="Adherence overview" subtitle="Population nudges">
          {adhLoading ? (
            <Skeleton className="h-32 w-full" />
          ) : adhError ? (
            <p className="text-sm text-danger">{adhError.message || 'Unable to load adherence data'}</p>
          ) : adherence ? (
            <div className="space-y-3 text-sm text-text-primary">
              <div className="flex items-center justify-between">
                <span>Overall adherence</span>
                <Badge variant="success">{formatPercent((adherence.overall || adherence.score || 0) * 100)}</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span>Vitals completion</span>
                <span className="text-text-muted">{formatPercent((adherence.vitals || 0) * 100)}</span>
              </div>
              <div className="flex items-center justify-between">
                <span>Appointments kept</span>
                <span className="text-text-muted">{formatPercent((adherence.appointments || 0) * 100)}</span>
              </div>
              <p className="text-xs text-text-muted mt-3 pt-3 border-t border-slate-200/60">
                Use Alerts to schedule human follow-up for low adherence cohorts.
              </p>
            </div>
          ) : (
            <p className="text-sm text-text-muted">No adherence data available.</p>
          )}
        </Card>
        
        <ChatbotPanel baseUrl={import.meta.env.VITE_API_URL} />
      </div>
    </div>
  );
}
