import { useState } from 'react';
import { ShieldAlert, Settings, BellRing } from 'lucide-react';
import AlertCard from '../components/cards/AlertCard.jsx';
import Card from '../components/ui/Card.jsx';
import Skeleton from '../components/ui/Skeleton.jsx';
import Badge from '../components/ui/Badge.jsx';
import Button from '../components/ui/Button.jsx';
import useApi from '../hooks/useApi.js';
import { getAlerts } from '../services/api.js';

const fallbackAlerts = [
  { tone: 'red', issue: 'ICU occupancy at 92%', impact: 'Delay in critical admissions', action: 'Activate surge beds & reroute non-critical cases' },
  { tone: 'yellow', issue: 'Staff fatigue risk on night shift', impact: 'Lowered response time', action: 'Call in reserve nurse; cap OT at 2h' },
  { tone: 'green', issue: 'ER intake normal', impact: 'No action', action: 'Maintain standard staffing' },
];

const mockEscalations = [
  { id: 'ESC-1042', patient: 'Patient 102', reason: 'High Risk - Vitals Deterioration', assignedTo: 'Dr. Sarah Jenkins (Cardiology)', status: 'Active', time: '10 mins ago' },
  { id: 'ESC-1043', patient: 'Patient 107', reason: 'Critical SpO2 Drop', assignedTo: 'ER Response Team', status: 'In Progress', time: '2 mins ago' },
];

export default function Alerts() {
  const { data, loading, error } = useApi(() => getAlerts());
  const alerts = data?.alerts || data || fallbackAlerts;
  
  const [activeTab, setActiveTab] = useState('alerts');
  const [thresholds, setThresholds] = useState({
    hr: 120,
    spo2: 90,
    autoEscalate: true
  });

  return (
    <div className="space-y-6 fade-in">
      
      {/* Tabs */}
      <div className="flex space-x-2 border-b border-slate-200/70 pb-px">
        <button 
          onClick={() => setActiveTab('alerts')}
          className={`flex items-center gap-2 px-4 py-2 border-b-2 font-medium text-sm transition-colors ${activeTab === 'alerts' ? 'border-accent text-accent' : 'border-transparent text-text-muted hover:text-text-primary'}`}
        >
          <BellRing size={16} /> Live Alerts
        </button>
        <button 
          onClick={() => setActiveTab('escalations')}
          className={`flex items-center gap-2 px-4 py-2 border-b-2 font-medium text-sm transition-colors ${activeTab === 'escalations' ? 'border-danger text-danger' : 'border-transparent text-text-muted hover:text-text-primary'}`}
        >
          <ShieldAlert size={16} /> Active Escalations
        </button>
        <button 
          onClick={() => setActiveTab('admin')}
          className={`flex items-center gap-2 px-4 py-2 border-b-2 font-medium text-sm transition-colors ${activeTab === 'admin' ? 'border-text-primary text-text-primary' : 'border-transparent text-text-muted hover:text-text-primary'}`}
        >
          <Settings size={16} /> Admin Thresholds
        </button>
      </div>

      {activeTab === 'alerts' && (
        <Card title="System Alerts" subtitle="Operational & predictive notifications">
          {loading ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => <Skeleton key={i} className="h-20 w-full" />)}
            </div>
          ) : error ? (
            <p className="text-sm text-danger">{error.message || 'Unable to load alerts; showing cached defaults.'}</p>
          ) : null}

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mt-4">
            {alerts.map((alert, idx) => (
              <AlertCard key={idx} {...alert} />
            ))}
          </div>
        </Card>
      )}

      {activeTab === 'escalations' && (
        <Card title="Human Escalation Workflows" subtitle="Critical patient events automatically routed to staff">
          <div className="space-y-4 mt-4">
            {mockEscalations.map(esc => (
              <div key={esc.id} className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 rounded-xl border border-red-100 bg-red-50/30">
                <div>
                  <div className="flex items-center gap-3 mb-1">
                    <span className="text-xs font-bold text-danger bg-red-100 px-2 py-0.5 rounded">{esc.id}</span>
                    <span className="text-sm text-text-muted">{esc.time}</span>
                  </div>
                  <p className="font-medium text-text-primary">{esc.patient} — {esc.reason}</p>
                  <p className="text-sm text-text-muted mt-0.5">Assigned to: <span className="font-semibold text-text-primary">{esc.assignedTo}</span></p>
                </div>
                <div className="flex items-center gap-3">
                  <Badge variant={esc.status === 'In Progress' ? 'warning' : 'danger'}>{esc.status}</Badge>
                  <Button variant="outline" size="sm">Acknowledge</Button>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {activeTab === 'admin' && (
        <Card title="Escalation Rules & Routing" subtitle="Configure AI triggers for human intervention" className="max-w-2xl">
          <div className="space-y-6 mt-4">
            <div className="space-y-3">
              <label className="text-sm font-medium text-text-primary">Critical Heart Rate Threshold (bpm)</label>
              <input 
                type="number" 
                value={thresholds.hr}
                onChange={e => setThresholds({...thresholds, hr: e.target.value})}
                className="w-full rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-accent/20" 
              />
              <p className="text-xs text-text-muted">If heart rate exceeds this value, trigger escalation.</p>
            </div>
            
            <div className="space-y-3">
              <label className="text-sm font-medium text-text-primary">Critical SpO2 Drop (%)</label>
              <input 
                type="number" 
                value={thresholds.spo2}
                onChange={e => setThresholds({...thresholds, spo2: e.target.value})}
                className="w-full rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-accent/20" 
              />
              <p className="text-xs text-text-muted">If oxygen drops below this percentage, trigger escalation.</p>
            </div>

            <div className="flex items-center justify-between p-4 rounded-xl border border-slate-200 bg-slate-50/50">
              <div>
                <p className="font-medium text-sm">Auto-Route to Specialists</p>
                <p className="text-xs text-text-muted">Directly page department heads based on symptoms.</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input 
                  type="checkbox" 
                  className="sr-only peer" 
                  checked={thresholds.autoEscalate}
                  onChange={() => setThresholds({...thresholds, autoEscalate: !thresholds.autoEscalate})}
                />
                <div className="w-11 h-6 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-accent"></div>
              </label>
            </div>

            <Button className="w-full sm:w-auto">Save Thresholds</Button>
          </div>
        </Card>
      )}

    </div>
  );
}
