import clsx from 'classnames';

export default function Card({ title, subtitle, children, className, actions }) {
  return (
    <section className={clsx('glass-card rounded-2xl border border-slate-200/70 p-4 sm:p-5 transition-transform duration-150 hover:-translate-y-[2px]', className)}>
      {(title || subtitle || actions) && (
        <header className="mb-3 flex items-start justify-between gap-3">
          <div>
            {title && <h2 className="text-base sm:text-lg font-semibold text-text-primary">{title}</h2>}
            {subtitle && <p className="text-sm text-text-muted mt-0.5">{subtitle}</p>}
          </div>
          {actions && <div className="flex items-center gap-2">{actions}</div>}
        </header>
      )}
      {children}
    </section>
  );
}
