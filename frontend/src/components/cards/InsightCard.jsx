import { Lightbulb } from 'lucide-react';
import Card from '../ui/Card.jsx';

export default function InsightCard({ title = 'Key Insight', message }) {
  return (
    <Card title={title} className="bg-gradient-to-br from-white to-white/70 shadow-card">
      <div className="flex items-start gap-3">
        <span className="h-10 w-10 rounded-2xl bg-amber-50 text-amber-600 grid place-items-center">
          <Lightbulb size={18} />
        </span>
        <p className="text-sm leading-relaxed text-text-primary">{message || 'AI is generating recommendations based on live signals.'}</p>
      </div>
    </Card>
  );
}
