import clsx from 'classnames';

const variants = {
  success: 'bg-success/10 text-success border-success/30',
  warning: 'bg-warning/10 text-warning border-warning/30',
  danger: 'bg-danger/10 text-danger border-danger/30',
  neutral: 'bg-slate-100 text-text-primary border-slate-200',
};

export default function Badge({ children, variant = 'neutral', className }) {
  return (
    <span className={clsx('inline-flex items-center gap-1 rounded-full border px-3 py-1 text-xs font-semibold', variants[variant], className)}>
      {children}
    </span>
  );
}
