import clsx from 'classnames';
import { AlertTriangle, CheckCircle, Info } from 'lucide-react';
import Card from '../ui/Card.jsx';

const toneMap = {
  green: { bg: 'bg-success/10', text: 'text-success', border: 'border-success/30', icon: CheckCircle },
  yellow: { bg: 'bg-warning/10', text: 'text-warning', border: 'border-warning/30', icon: Info },
  red: { bg: 'bg-danger/10', text: 'text-danger', border: 'border-danger/30', icon: AlertTriangle },
};

export default function AlertCard({ issue, impact, action, tone = 'green' }) {
  const toneStyles = toneMap[tone] || toneMap.green;
  const Icon = toneStyles.icon;

  return (
    <Card className={clsx('border-l-4', toneStyles.border, toneStyles.bg)}>
      <div className="flex items-start gap-3">
        <div className={clsx('p-2 rounded-xl', toneStyles.bg)}>
          <Icon size={18} className={toneStyles.text} />
        </div>
        <div className="space-y-1">
          <p className="font-semibold text-text-primary">{issue}</p>
          <p className="text-sm text-text-muted">Impact: {impact}</p>
          <p className="text-sm text-text-primary font-medium">Action: {action}</p>
        </div>
      </div>
    </Card>
  );
}
