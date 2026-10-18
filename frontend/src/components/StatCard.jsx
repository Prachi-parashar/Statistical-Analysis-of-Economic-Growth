import { HelpCircle } from 'lucide-react'

const COLOR_MAP = {
  blue:   { bg: 'bg-primary-50',  text: 'text-primary-700',  icon: 'text-primary-500',  border: 'border-primary-100'  },
  green:  { bg: 'bg-emerald-50',  text: 'text-emerald-700',  icon: 'text-emerald-500',  border: 'border-emerald-100'  },
  amber:  { bg: 'bg-amber-50',    text: 'text-amber-700',    icon: 'text-amber-500',    border: 'border-amber-100'    },
  violet: { bg: 'bg-violet-50',   text: 'text-violet-700',   icon: 'text-violet-500',   border: 'border-violet-100'   },
  slate:  { bg: 'bg-slate-100',   text: 'text-slate-700',    icon: 'text-slate-400',    border: 'border-slate-200'    },
  red:    { bg: 'bg-red-50',      text: 'text-red-700',      icon: 'text-red-500',      border: 'border-red-100'      },
  teal:   { bg: 'bg-teal-50',     text: 'text-teal-700',     icon: 'text-teal-500',     border: 'border-teal-100'     },
}

export default function StatCard({
  label, value, unit, description, icon: Icon,
  color = 'blue', pending = false, tooltip,
}) {
  const c = COLOR_MAP[color] || COLOR_MAP.blue

  return (
    <div className="stat-card group">
      {/* Header row */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-1.5">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wide">
            {label}
          </span>
          {tooltip && (
            <span title={tooltip} className="cursor-help">
              <HelpCircle size={11} className="text-slate-300 group-hover:text-slate-400 transition-colors" />
            </span>
          )}
        </div>
        {Icon && (
          <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${c.bg} border ${c.border}`}>
            <Icon size={15} className={c.icon} aria-hidden="true" />
          </div>
        )}
      </div>

      {/* Value */}
      {pending ? (
        <div className="space-y-1.5 mt-1">
          <div className="h-6 bg-slate-100 rounded animate-pulse w-3/4" />
          <div className="h-3 bg-slate-100 rounded animate-pulse w-1/2" />
        </div>
      ) : (
        <>
          <p className={`text-2xl font-bold leading-tight ${c.text}`}>
            {value ?? '—'}
            {unit && (
              <span className="text-sm font-normal text-slate-500 ml-1.5">{unit}</span>
            )}
          </p>
          {description && (
            <p className="text-xs text-slate-500 mt-1.5 leading-relaxed">{description}</p>
          )}
        </>
      )}
    </div>
  )
}
