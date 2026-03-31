import { useMemo, useState } from 'react';
import { ShieldAlert, Send } from 'lucide-react';
import Card from '../components/ui/Card.jsx';
import Button from '../components/ui/Button.jsx';
import Skeleton from '../components/ui/Skeleton.jsx';
import Badge from '../components/ui/Badge.jsx';
import HorizontalBarChart from '../components/charts/HorizontalBarChart.jsx';
import { predictNoShow, getFeatureInsights } from '../services/api.js';
import { normalizeToPercent, formatPercent } from '../utils/formatters.js';

export default function PatientRisk() {
  const [form, setForm] = useState({ age: 45, waiting_days: 4, sms_received: true });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [featureData, setFeatureData] = useState(null);

  const handleChange = (field, value) => setForm((prev) => ({ ...prev, [field]: value }));

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const payload = {
        age: Number(form.age),
        waiting_days: Number(form.waiting_days),
        sms_received: Boolean(form.sms_received),
      };
      const { data } = await predictNoShow(payload);
      setResult(data);
      const importance = data?.feature_importances || data?.importance || data?.top_factors;
      if (importance) setFeatureData(importance);
      else {
        const insights = await getFeatureInsights().catch(() => null);
        if (insights?.data?.feature_importances) setFeatureData(insights.data.feature_importances);
      }
    } catch (err) {
      setError(err?.message || 'Unable to score risk');
    } finally {
      setLoading(false);
    }
  };

  const normalizedFeatures = useMemo(() => {
    if (!featureData) return null;
    const mapped = Array.isArray(featureData)
      ? featureData.map((f) => ({ name: f.feature || f.name, value: Number(f.importance ?? f.value ?? 0) }))
      : Object.entries(featureData).map(([name, value]) => ({ name, value: Number(value) }));
    return normalizeToPercent(mapped).slice(0, 5);
  }, [featureData]);

  const riskScore = result?.probability ?? result?.risk_score ?? result?.risk ?? 0.67;
  const riskLabel = riskScore >= 0.7 ? 'High Risk' : riskScore >= 0.4 ? 'Medium Risk' : 'Low Risk';

  const contributing = result?.contributing_factors || result?.drivers || (normalizedFeatures ? normalizedFeatures.slice(0, 3) : []);
  const recommendations = result?.recommendations || [
    'Send empathetic SMS reminder 24h before appointment.',
    'Offer telehealth slot to reduce wait burden.',
    'Prioritize front-desk fast lane for high-risk patients.',
  ];

  return (
    <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 fade-in">
      <Card title="Patient Inputs" subtitle="Simple, interpretable factors" className="xl:col-span-1">
        <form onSubmit={submit} className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm text-text-muted">Age</label>
            <input
              type="number"
              min={1}
              value={form.age}
              onChange={(e) => handleChange('age', e.target.value)}
              className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 focus:outline-none focus:ring-2 focus:ring-text-primary/20"
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm text-text-muted">Waiting days</label>
            <input
              type="number"
              min={0}
              value={form.waiting_days}
              onChange={(e) => handleChange('waiting_days', e.target.value)}
              className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 focus:outline-none focus:ring-2 focus:ring-text-primary/20"
            />
          </div>

          <div className="flex items-center justify-between rounded-xl border border-slate-200 bg-white px-4 py-3">
            <div>
              <p className="text-sm font-semibold">SMS reminder sent?</p>
              <p className="text-xs text-text-muted">Switch off if patient did not receive SMS.</p>
            </div>
            <input
              type="checkbox"
              checked={form.sms_received}
              onChange={(e) => handleChange('sms_received', e.target.checked)}
              className="h-4 w-4 accent-text-primary"
            />
          </div>

          <Button type="submit" className="w-full" disabled={loading}>
            <Send size={16} />
            {loading ? 'Scoring...' : 'Run Risk Scoring'}
          </Button>

          {error && <p className="text-sm text-danger">{error}</p>}
        </form>
      </Card>

      <div className="xl:col-span-2 space-y-4">
        <Card title="Risk Assessment" subtitle="Interpretable AI output" className="bg-white shadow-card">
          {loading ? (
            <div className="space-y-3">
              <Skeleton className="h-8 w-48" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-5/6" />
            </div>
          ) : (
            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
              <div>
                <p className="text-sm text-text-muted">Overall probability</p>
                <p className="text-3xl font-semibold">{formatPercent(riskScore * 100)}</p>
                <p className="text-sm text-text-primary mt-1">{riskLabel}</p>
              </div>
              <Badge variant={riskScore >= 0.7 ? 'danger' : riskScore >= 0.4 ? 'warning' : 'success'}>
                Patient no-show likelihood
              </Badge>
            </div>
          )}
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <Card title="Contributing factors" subtitle="Top drivers">
            {loading ? (
              <div className="space-y-2">
                {[1, 2, 3].map((i) => <Skeleton key={i} className="h-4 w-3/4" />)}
              </div>
            ) : (
              <ul className="space-y-2 text-sm text-text-primary">
                {contributing?.length ? (
                  contributing.slice(0, 3).map((item, idx) => (
                    <li key={idx} className="flex items-center gap-2">
                      <span className="h-2 w-2 rounded-full bg-text-primary" />
                      <span className="font-semibold">{item.name || item.feature || item.label}</span>
                      <span className="text-text-muted">{item.value ? `${Number(item.value).toFixed(1)}%` : ''}</span>
                    </li>
                  ))
                ) : (
                  <p className="text-text-muted">Run a prediction to see drivers.</p>
                )}
              </ul>
            )}
          </Card>

          <Card title="Recommendations" subtitle="Actionable next steps">
            {loading ? (
              <div className="space-y-2">
                {[1, 2, 3].map((i) => <Skeleton key={i} className="h-4 w-5/6" />)}
              </div>
            ) : (
              <ul className="space-y-2 text-sm text-text-primary list-disc pl-4">
                {recommendations.map((rec, idx) => <li key={idx}>{rec}</li>)}
              </ul>
            )}
          </Card>
        </div>

        <Card title="Feature importance" subtitle="Normalized to percentages">
          {loading ? (
            <Skeleton className="h-48 w-full" />
          ) : normalizedFeatures ? (
            <HorizontalBarChart data={normalizedFeatures} />
          ) : (
            <p className="text-sm text-text-muted">Run a prediction to view importance.</p>
          )}
        </Card>
      </div>
    </div>
  );
}
