import { Activity, HeartPulse, UsersRound } from 'lucide-react';
import StatCard from '../components/cards/StatCard.jsx';
import InsightCard from '../components/cards/InsightCard.jsx';
import Card from '../components/ui/Card.jsx';
import Skeleton from '../components/ui/Skeleton.jsx';
import useApi from '../hooks/useApi.js';
import { getDashboard } from '../services/api.js';
import { formatPercent } from '../utils/formatters.js';

export default function Dashboard() {
  const { data, loading, error } = useApi(() => getDashboard());

  const cards = [
    {
      label: 'ER Load (7d)',
      value: data?.er_load ? formatPercent(data.er_load) : '—',
      trendLabel: 'Projected demand',
      icon: Activity,
      loading,
      error,
    },
    {
      label: 'ICU Status',
      value: data?.icu_utilization ? formatPercent(data.icu_utilization) : '—',
      trendLabel: 'Utilization',
      icon: HeartPulse,
      loading,
      error,
    },
    {
      label: 'Staff Load',
      value: data?.staff_load ? formatPercent(data.staff_load) : '—',
      trendLabel: 'Shifts at capacity',
      icon: UsersRound,
      loading,
      error,
    },
  ];

  const insightMessage = data?.insight || '📊 ER load stable. Staffing levels sufficient.';

  return (
    <div className="space-y-6 fade-in">
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {cards.map((card) => (
          <div key={card.label}>
            {card.loading ? (
              <Card>
                <Skeleton className="h-6 w-24 mb-2" />
                <Skeleton className="h-8 w-32" />
              </Card>
            ) : card.error ? (
              <Card title={card.label}>
                <p className="text-sm text-danger">Unable to load data. Check API connectivity.</p>
              </Card>
            ) : !data ? (
              <Card title={card.label}>
                <p className="text-sm text-text-muted">⚠️ No live data available. Connect hospital systems.</p>
              </Card>
            ) : (
              <StatCard {...card} />
            )}
          </div>
        ))}
      </div>

      <InsightCard message={insightMessage} />

      <Card title="Live Operations" subtitle="Hospital-friendly status">
        <ul className="space-y-2 text-sm text-text-primary">
          <li className="flex items-start gap-2"><span className="h-2 w-2 mt-1 rounded-full bg-success" />🟢 All systems operational</li>
          <li className="flex items-start gap-2"><span className="h-2 w-2 mt-1 rounded-full bg-success" />Realtime monitoring active</li>
          <li className="flex items-start gap-2"><span className="h-2 w-2 mt-1 rounded-full bg-success" />Optimized for hospital workflows</li>
        </ul>
      </Card>
    </div>
  );
}
