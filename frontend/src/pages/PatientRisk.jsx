import { useMemo, useState } from 'react';
import { Send } from 'lucide-react';
import Card from '../components/ui/Card.jsx';
import Button from '../components/ui/Button.jsx';
import Skeleton from '../components/ui/Skeleton.jsx';
import Badge from '../components/ui/Badge.jsx';
import ErrorBox from '../components/ui/ErrorBox.jsx';
import HorizontalBarChart from '../components/charts/HorizontalBarChart.jsx';
import { predictPatientRisk, getFeatureInsights } from '../services/api.js';
import { normalizeToPercent, formatPercent } from '../utils/formatters.js';

export default function PatientRisk() {
  const [form, setForm] = useState({
    age: 34,
    gender: 'F',
    waiting_days: 5,
    scheduled_hour: 10,
    neighbourhood: 'JARDIM CAMBURI',
  });
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
        gender: form.gender,
        waiting_days: Number(form.waiting_days),
        scheduled_hour: Number(form.scheduled_hour),
        neighbourhood: form.neighbourhood,
        // backend requires these; keep safe defaults for smooth UX
        scholarship: 0,
        hipertension: 0,
        diabetes: 0,
        alcoholism: 0,
        handcap: 0,
        sms_received: 1,
      };

      const { data } = await predictPatientRisk(payload);
      // backend returns probability (0-100) and risk label
      setResult(data);
      const importance = data?.feature_importances || data?.importance || data?.top_factors;
      if (importance) setFeatureData(importance);
      else {
        const insights = await getFeatureInsights().catch(() => null);
        if (insights?.data?.feature_importances) setFeatureData(insights.data.feature_importances);
      }
    } catch (err) {
      setError(err);
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

  const probPct = result?.probability ?? (result?.risk_score ? result.risk_score * 100 : undefined);
  const prob01 = probPct !== undefined ? probPct / 100 : 0;
  const riskLabel = result?.risk ?? (prob01 >= 0.7 ? 'High' : prob01 >= 0.4 ? 'Medium' : 'Low');
  const badgeVariant = riskLabel === 'High' ? 'danger' : riskLabel === 'Medium' ? 'warning' : 'success';

  const contributing = result?.contributing_factors || result?.drivers || result?.factors || (normalizedFeatures ? normalizedFeatures.slice(0, 3) : []);
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
            <label htmlFor="patient-age" className="text-sm text-text-muted">Age</label>
            <input
              id="patient-age"
              name="age"
              type="number"
              min={1}
              aria-label="Patient age"
              value={form.age}
              onChange={(e) => handleChange('age', e.target.value)}
              className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 focus:outline-none focus:ring-2 focus:ring-text-primary/20"
            />
          </div>

          <div className="space-y-2">
            <label htmlFor="waiting-days" className="text-sm text-text-muted">Waiting days</label>
            <input
              id="waiting-days"
              name="waiting_days"
              type="number"
              min={0}
              aria-label="Waiting days"
              value={form.waiting_days}
              onChange={(e) => handleChange('waiting_days', e.target.value)}
              className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 focus:outline-none focus:ring-2 focus:ring-text-primary/20"
            />
          </div>

          <div className="space-y-2">
            <label htmlFor="gender" className="text-sm text-text-muted">Gender</label>
            <select
              id="gender"
              name="gender"
              value={form.gender}
              onChange={(e) => handleChange('gender', e.target.value)}
              className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 focus:outline-none focus:ring-2 focus:ring-text-primary/20"
            >
              <option value="F">Female</option>
              <option value="M">Male</option>
            </select>
          </div>

          <div className="space-y-2">
            <label htmlFor="scheduled-hour" className="text-sm text-text-muted">Scheduled hour</label>
            <input
              id="scheduled-hour"
              name="scheduled_hour"
              type="number"
              min={0}
              max={23}
              aria-label="Scheduled hour"
              value={form.scheduled_hour}
              onChange={(e) => handleChange('scheduled_hour', e.target.value)}
              className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 focus:outline-none focus:ring-2 focus:ring-text-primary/20"
            />
          </div>

          <Button type="submit" className="w-full" disabled={loading}>
            <Send size={16} />
            {loading ? 'Analyzing patient risk...' : 'Get instant prediction'}
          </Button>

          <ErrorBox error={error} />
        </form>
      </Card>

      <div className="xl:col-span-2 space-y-4">
        <Card title="Risk Assessment" subtitle="Interpretable AI output" className="bg-white shadow-card">
          {!result && !loading && !error && (
            <p className="text-sm text-text-muted">Enter patient details to see prediction.</p>
          )}
          {loading ? (
            <div className="space-y-3">
              <Skeleton className="h-8 w-48" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-5/6" />
            </div>
          ) : result ? (
            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
              <div>
                <p className="text-sm text-text-muted">Overall probability</p>
                <p className="text-3xl font-semibold">{formatPercent(probPct)}</p>
                <p className="text-sm text-text-primary mt-1">{riskLabel} risk</p>
              </div>
              <Badge variant={badgeVariant}>
                {riskLabel === 'High' ? '🔴 High' : riskLabel === 'Medium' ? '🟠 Medium' : '🟢 Low'} no-show likelihood
              </Badge>
            </div>
          ) : null}
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <Card title="Contributing factors" subtitle="Top drivers">
            {loading ? (
              <div className="space-y-2">
                {[1, 2, 3].map((i) => <Skeleton key={i} className="h-4 w-3/4" />)}
              </div>
            ) : contributing?.length ? (
              <ul className="space-y-2 text-sm text-text-primary">
                {contributing.slice(0, 3).map((item, idx) => (
                  <li key={idx} className="flex items-center gap-2">
                    <span className="h-2 w-2 rounded-full bg-text-primary" />
                    <span className="font-semibold">{item.name || item.feature || item.label || item}</span>
                    <span className="text-text-muted">{item.value ? `${Number(item.value).toFixed(1)}%` : ''}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-text-muted">Run a prediction to see drivers.</p>
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
