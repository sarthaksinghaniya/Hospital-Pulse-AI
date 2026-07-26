import clsx from 'classnames';

export default function Card({ title, subtitle, children, className, actions }) {
  return (
    <section className={clsx('glass-card rounded-2xl border border-slate-200/60 p-4 sm:p-6 transition-all duration-300 ease-smooth hover:-translate-y-[3px] hover:shadow-card-hover group', className)}>
      {(title || subtitle || actions) && (
        <header className="mb-4 flex items-start justify-between gap-3">
          <div>
            {title && <h2 className="text-base sm:text-lg font-semibold text-text-primary tracking-tight">{title}</h2>}
            {subtitle && <p className="text-sm text-text-muted mt-0.5">{subtitle}</p>}
          </div>
          {actions && <div className="flex items-center gap-2">{actions}</div>}
        </header>
      )}
      {children}
    </section>
  );
}
