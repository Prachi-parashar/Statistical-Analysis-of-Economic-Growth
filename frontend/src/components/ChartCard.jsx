export default function ChartCard({ title, subtitle, children, className = '', note, action }) {
  return (
    <div className={`page-card ${className}`}>
      <div className="card-header">
        <div className="min-w-0">
          <h3 className="card-title">{title}</h3>
          {subtitle && <p className="card-subtitle text-xs text-slate-500 dark:text-slate-400 mt-0.5 leading-relaxed">{subtitle}</p>}
        </div>
        {action && <div className="flex-shrink-0">{action}</div>}
      </div>
      <div className="p-5">{children}</div>
      {note && (
        <div className="px-5 pb-4 -mt-2">
          <p className="text-xs text-slate-400 italic">{note}</p>
        </div>
      )}
    </div>
  )
}
