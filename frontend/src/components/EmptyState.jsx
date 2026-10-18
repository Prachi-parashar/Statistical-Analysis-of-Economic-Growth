import { ServerOff } from 'lucide-react'

export default function EmptyState({
  icon: Icon = ServerOff,
  title = 'Analysis result not available.',
  message = 'No data returned from backend API.',
  compact = false,
  onRefresh,
}) {
  return (
    <div
      className={[
        'flex flex-col items-center justify-center text-center select-none p-6 bg-slate-50/70 border border-slate-200/60 rounded-xl',
        compact ? 'py-8' : 'py-12',
      ].join(' ')}
      aria-label={title}
    >
      <div className="w-10 h-10 bg-slate-100 rounded-xl flex items-center justify-center mb-3">
        <Icon size={20} className="text-slate-400" aria-hidden="true" />
      </div>
      <p className="text-sm font-semibold text-slate-700 mb-1">{title}</p>
      <p className="text-xs text-slate-400 max-w-sm leading-relaxed">{message}</p>
      {onRefresh && (
        <button
          onClick={onRefresh}
          className="mt-4 text-xs font-medium text-primary-600 hover:text-primary-700 hover:underline"
        >
          Refresh Data
        </button>
      )}
    </div>
  )
}
