import { useMemo } from 'react';
import { useLocation, NavLink } from 'react-router-dom';
import { Bell, UserRound, LayoutDashboard, ShieldCheck, ActivitySquare, BellRing } from 'lucide-react';
import clsx from 'classnames';

const navItems = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/risk', label: 'Risk', icon: ShieldCheck },
  { to: '/monitoring', label: 'Monitoring', icon: ActivitySquare },
  { to: '/alerts', label: 'Alerts', icon: BellRing },
];

export default function Header() {
  const location = useLocation();

  const title = useMemo(() => {
    if (location.pathname.startsWith('/risk')) return 'Patient Risk';
    if (location.pathname.startsWith('/monitoring')) return 'Monitoring';
    if (location.pathname.startsWith('/alerts')) return 'Alerts';
    return 'Operational Pulse';
  }, [location.pathname]);

  const today = new Intl.DateTimeFormat('en-US', {
    weekday: 'short', month: 'short', day: 'numeric'
  }).format(new Date());

  return (
    <header className="sticky top-0 z-30 backdrop-blur bg-shell/80 border-b border-slate-200/70">
      <div className="flex items-center justify-between px-4 sm:px-6 lg:px-8 py-4">
        <div>
          <p className="text-xs text-text-muted uppercase tracking-[0.08em]">Hospital Pulse AI</p>
          <h1 className="text-xl sm:text-2xl font-semibold">{title}</h1>
        </div>

        <div className="flex items-center gap-4">
          <div className="hidden md:flex items-center gap-2 px-3 py-2 rounded-full bg-white shadow-soft border border-slate-100 text-xs text-text-muted">
            <span className="h-2 w-2 rounded-full bg-success" aria-hidden />
            <span>Live</span>
            <span className="text-text-primary">{today}</span>
          </div>
          <button className="h-10 w-10 rounded-full bg-white shadow-soft border border-slate-200 grid place-items-center hover:-translate-y-0.5 transition-transform">
            <Bell size={18} className="text-text-primary" />
          </button>
          <div className="flex items-center gap-2 rounded-full bg-white shadow-soft border border-slate-200 px-3 py-2">
            <div className="h-8 w-8 rounded-full bg-text-primary text-white grid place-items-center">
              <UserRound size={16} />
            </div>
            <div className="text-sm leading-tight">
              <p className="font-semibold">Ops Lead</p>
              <p className="text-text-muted text-xs">Online</p>
            </div>
          </div>
        </div>
      </div>

      <div className="lg:hidden px-4 sm:px-6 pb-3 flex gap-2 overflow-x-auto">
        {navItems.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) => clsx(
              'flex items-center gap-2 px-4 py-2 rounded-xl text-sm whitespace-nowrap border',
              isActive ? 'bg-white shadow-soft text-text-primary border-slate-100' : 'text-text-muted bg-white/70 border-transparent'
            )}
          >
            <Icon size={16} />
            {label}
          </NavLink>
        ))}
      </div>
    </header>
  );
}
