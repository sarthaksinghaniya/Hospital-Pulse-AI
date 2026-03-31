import AlertCard from '../components/cards/AlertCard.jsx';
import Card from '../components/ui/Card.jsx';
import Skeleton from '../components/ui/Skeleton.jsx';
import useApi from '../hooks/useApi.js';
import { getAlerts } from '../services/api.js';

const fallbackAlerts = [
  { tone: 'red', issue: 'ICU occupancy at 92%', impact: 'Delay in critical admissions', action: 'Activate surge beds & reroute non-critical cases' },
  { tone: 'yellow', issue: 'Staff fatigue risk on night shift', impact: 'Lowered response time', action: 'Call in reserve nurse; cap OT at 2h' },
  { tone: 'green', issue: 'ER intake normal', impact: 'No action', action: 'Maintain standard staffing' },
];

export default function Alerts() {
  const { data, loading, error } = useApi(() => getAlerts());
  const alerts = data?.alerts || data || fallbackAlerts;

  return (
    <div className="space-y-4 fade-in">
      <Card title="Real-time alerts" subtitle="Notification style cards">
        {loading ? (
          <div className="space-y-3">
            {[1, 2, 3].map((i) => <Skeleton key={i} className="h-20 w-full" />)}
          </div>
        ) : error ? (
          <p className="text-sm text-danger">{error.message || 'Unable to load alerts; showing cached defaults.'}</p>
        ) : null}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-3 mt-3">
          {alerts.map((alert, idx) => (
            <AlertCard key={idx} {...alert} />
          ))}
        </div>
      </Card>
    </div>
  );
}
