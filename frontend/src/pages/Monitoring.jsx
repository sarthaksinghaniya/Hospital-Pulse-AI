import Card from '../components/ui/Card.jsx';
import Skeleton from '../components/ui/Skeleton.jsx';
import Badge from '../components/ui/Badge.jsx';
import ChatbotPanel from '../components/ChatbotPanel.jsx';
import useApi from '../hooks/useApi.js';
import { getVitalsOverview, getAdherenceOverview } from '../services/api.js';
import { formatPercent } from '../utils/formatters.js';

export default function Monitoring() {
  const { data: vitals, loading: vitalsLoading, error: vitalsError } = useApi(() => getVitalsOverview());
  const { data: adherence, loading: adhLoading, error: adhError } = useApi(() => getAdherenceOverview());

  const vitalsList = vitals?.patients || vitals?.vitals || [];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 fade-in">
      <Card title="Vitals overview" subtitle="Stability by patient">
        {vitalsLoading ? (
          <div className="space-y-2">
            {[1, 2, 3].map((i) => <Skeleton key={i} className="h-5 w-full" />)}
          </div>
        ) : vitalsError ? (
          <p className="text-sm text-danger">{vitalsError.message || 'Unable to load vitals'}</p>
        ) : vitalsList.length ? (
          <ul className="divide-y divide-slate-100">
            {vitalsList.slice(0, 6).map((item, idx) => (
              <li key={idx} className="py-3 flex items-center justify-between">
                <div>
                  <p className="font-semibold">{item.patient_id || item.name || 'Patient'}</p>
                  <p className="text-xs text-text-muted">{item.status || 'Stable'}</p>
                </div>
                <Badge variant={(item.risk === 'high' && 'danger') || (item.risk === 'medium' && 'warning') || 'success'}>
                  {item.risk || 'low'}
                </Badge>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-text-muted">📡 Connect devices to start real-time monitoring.</p>
        )}
      </Card>

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
            <p className="text-xs text-text-muted">Use Alerts to schedule human follow-up for low adherence cohorts.</p>
          </div>
        ) : (
          <p className="text-sm text-text-muted">No adherence data available.</p>
        )}
      </Card>

      <div className="lg:col-span-2">
        <ChatbotPanel baseUrl={import.meta.env.VITE_API_URL} />
      </div>
    </div>
  );
}
