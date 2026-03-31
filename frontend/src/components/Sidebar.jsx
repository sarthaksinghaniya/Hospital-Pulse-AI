import { NavLink, useLocation } from 'react-router-dom';
import { LayoutDashboard, ShieldCheck, ActivitySquare, Bell, Sparkles } from 'lucide-react';
import clsx from 'classnames';

const navItems = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/risk', label: 'Patient Risk', icon: ShieldCheck },
  { to: '/monitoring', label: 'Monitoring', icon: ActivitySquare },
  { to: '/alerts', label: 'Alerts', icon: Bell },
];

export default function Sidebar() {
  const { pathname } = useLocation();

  return (
    <aside className="hidden lg:flex w-64 shrink-0 flex-col bg-shell/70 border-r border-slate-200/70 backdrop-blur-xl">
      <div className="flex items-center gap-3 px-6 py-6">
        <div className="h-10 w-10 rounded-2xl bg-text-primary text-white grid place-items-center shadow-soft">
          <Sparkles size={20} />
        </div>
        <div>
          <p className="text-sm text-text-muted">Hospital Pulse AI</p>
          <p className="text-lg font-semibold">HopX</p>
        </div>
      </div>

      <nav className="px-4 space-y-2">
        {navItems.map(({ to, label, icon: Icon }) => {
          const active = pathname === to;
          return (
            <NavLink
              key={to}
              to={to}
              className={clsx(
                'group flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium transition-all duration-150',
                active
                  ? 'bg-white shadow-card text-text-primary'
                  : 'text-text-muted hover:bg-white/70 hover:shadow-soft'
              )}
            >
              <Icon size={18} className={active ? 'text-text-primary' : 'text-text-muted group-hover:text-text-primary'} />
              <span>{label}</span>
            </NavLink>
          );
        })}
      </nav>

      <div className="mt-auto px-4 py-6">
        <div className="rounded-2xl bg-gradient-to-br from-white to-white/60 border border-slate-200 shadow-soft p-4">
          <p className="text-sm font-semibold">AI Operational Pulse</p>
          <p className="text-xs text-text-muted">Real-time signals across ER, ICU, and staffing.</p>
        </div>
      </div>
    </aside>
  );
}
