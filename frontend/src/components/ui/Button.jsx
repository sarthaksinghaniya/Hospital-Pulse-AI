import clsx from 'classnames';

export default function Button({ children, variant = 'primary', className, ...props }) {
  const base = 'inline-flex items-center justify-center gap-2 rounded-xl px-4 py-2 text-sm font-semibold transition-all duration-150';
  const styles = {
    primary: 'bg-text-primary text-white shadow-soft hover:-translate-y-0.5',
    ghost: 'bg-white text-text-primary border border-slate-200 hover:shadow-soft',
    subtle: 'bg-slate-100 text-text-primary hover:bg-slate-200',
  };

  return (
    <button className={clsx(base, styles[variant], className)} {...props}>
      {children}
    </button>
  );
}
