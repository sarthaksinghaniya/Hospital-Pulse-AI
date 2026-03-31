import { Activity, HeartPulse, UsersRound } from 'lucide-react';
import StatCard from '../components/cards/StatCard.jsx';
import InsightCard from '../components/cards/InsightCard.jsx';
import Card from '../components/ui/Card.jsx';
import Skeleton from '../components/ui/Skeleton.jsx';
import useApi from '../hooks/useApi.js';
import { getEmergencyLoad, getIcuStatus, getStaffLoad, getRecommendations } from '../services/api.js';
import { formatNumber, formatPercent } from '../utils/formatters.js';

export default function Dashboard() {
  const { data: er, loading: erLoading, error: erError } = useApi(() => getEmergencyLoad());
  const { data: icu, loading: icuLoading, error: icuError } = useApi(() => getIcuStatus());
  const { data: staff, loading: staffLoading, error: staffError } = useApi(() => getStaffLoad());
  const { data: recos } = useApi(() => getRecommendations(), [], false);

  const cards = [
    {
      label: 'ER Load (7d)',
      value: er?.load ? formatNumber(er.load) : er?.prediction ? formatNumber(er.prediction) : '—',
      delta: er?.delta ?? er?.change ?? 0,
      trendLabel: 'Projected demand',
      icon: Activity,
      loading: erLoading,
      error: erError,
    },
    {
      label: 'ICU Status',
      value: icu?.capacity ? `${formatPercent(icu.capacity)}` : icu?.occupancy ? `${formatPercent(icu.occupancy)}` : '—',
      delta: icu?.delta ?? icu?.change ?? 0,
      trendLabel: 'Utilization',
      icon: HeartPulse,
      loading: icuLoading,
      error: icuError,
    },
    {
      label: 'Staff Load',
      value: staff?.score ? formatPercent(staff.score) : staff?.load ? formatPercent(staff.load) : '—',
      delta: staff?.delta ?? staff?.change ?? 0,
      trendLabel: 'Shifts at capacity',
      icon: UsersRound,
      loading: staffLoading,
      error: staffError,
    },
  ];

  const insightMessage = recos?.message || recos?.[0] || 'SEWI stable. Maintain current staffing; monitor ER inflow every 2 hours.';

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
            ) : (
              <StatCard {...card} />
            )}
          </div>
        ))}
      </div>

      <InsightCard message={insightMessage} />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card title="Live Operations" subtitle="System health summary">
          <ul className="space-y-3 text-sm text-text-primary">
            <li className="flex items-start gap-2"><span className="h-2 w-2 mt-1 rounded-full bg-success" />CORS-secured API at <code className="bg-slate-100 rounded px-2 py-0.5">{import.meta.env.VITE_API_URL || 'http://localhost:8000'}</code></li>
            <li className="flex items-start gap-2"><span className="h-2 w-2 mt-1 rounded-full bg-warning" />Realtime monitoring optimized for 12s API timeout.</li>
            <li className="flex items-start gap-2"><span className="h-2 w-2 mt-1 rounded-full bg-success" />Responsive layout tuned for tablet + desktop dashboards.</li>
          </ul>
        </Card>

        <Card title="SLA Checks" subtitle="Error handling & fallbacks">
          <ul className="space-y-2 text-sm text-text-primary list-disc pl-4">
            <li>API failures surface inline errors, never crash the view.</li>
            <li>Skeletons + optimistic placeholders keep UX snappy.</li>
            <li>Timeouts capped at 12s with retry hooks available.</li>
          </ul>
        </Card>
      </div>
    </div>
  );
}
