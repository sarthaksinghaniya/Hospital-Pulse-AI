import clsx from 'classnames';
import Card from '../ui/Card.jsx';
import Badge from '../ui/Badge.jsx';

export default function StatCard({ label, value, delta, icon: Icon, trendLabel }) {
  const deltaVariant = delta > 0 ? 'danger' : delta < 0 ? 'success' : 'neutral';
  const deltaText = delta !== undefined ? `${delta > 0 ? '+' : ''}${delta}%` : null;

  return (
    <Card className="hover:shadow-card">
      <div className="flex items-center justify-between mb-3">
        <div>
          <p className="text-sm text-text-muted">{label}</p>
          <p className="text-2xl font-semibold">{value}</p>
        </div>
        {Icon && (
          <div className="h-11 w-11 rounded-2xl bg-slate-100 grid place-items-center text-text-primary">
            <Icon size={18} />
          </div>
        )}
      </div>
      <div className="flex items-center gap-2 text-sm">
        {deltaText && <Badge variant={deltaVariant}>{deltaText}</Badge>}
        {trendLabel && <span className="text-text-muted">{trendLabel}</span>}
      </div>
    </Card>
  );
}
