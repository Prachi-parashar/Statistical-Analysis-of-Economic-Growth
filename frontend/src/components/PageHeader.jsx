export default function PageHeader({ title, subtitle, badge, action }) {
  return (
    <div className="mb-6 flex items-start justify-between gap-4">
      <div>
        <div className="flex items-center gap-2.5 mb-1">
          <h2 className="text-xl font-bold text-slate-800 leading-tight">{title}</h2>
          {badge && (
            <span className="px-2 py-0.5 text-xs font-semibold bg-primary-50 text-primary-700
                             rounded-full border border-primary-200 whitespace-nowrap">
              {badge}
            </span>
          )}
        </div>
        {subtitle && (
          <p className="text-sm text-slate-500 leading-relaxed max-w-2xl">{subtitle}</p>
        )}
      </div>
      {action && <div className="flex-shrink-0">{action}</div>}
    </div>
  )
}
