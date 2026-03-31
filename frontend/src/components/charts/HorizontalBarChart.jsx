import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell } from 'recharts';

const palette = ['#0F766E', '#0891B2', '#3B82F6', '#6366F1', '#14B8A6'];

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-xl bg-white shadow-card border border-slate-100 px-3 py-2 text-sm">
      <p className="font-semibold text-text-primary">{label}</p>
      <p className="text-text-muted">{payload[0].value}%</p>
    </div>
  );
};

export default function HorizontalBarChart({ data }) {
  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} layout="vertical" barSize={18} margin={{ left: 24, right: 12 }}>
          <XAxis type="number" domain={[0, 100]} hide />
          <YAxis type="category" dataKey="name" width={120} tick={{ fill: '#475569', fontSize: 12 }} />
          <Tooltip cursor={{ fill: 'rgba(15, 118, 110, 0.05)' }} content={<CustomTooltip />} />
          <Bar dataKey="value" radius={[6, 6, 6, 6]}>
            {data.map((entry, index) => (
              <Cell key={entry.name} fill={palette[index % palette.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
