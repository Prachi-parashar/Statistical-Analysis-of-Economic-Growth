import { AlertCircle, RotateCcw } from 'lucide-react'

export default function ErrorState({
  title = 'Failed to load data',
  message = 'An error occurred while fetching analysis results from the backend.',
  onRetry,
  compact = false,
}) {
  return (
    <div
      className={[
        'flex flex-col items-center justify-center text-center p-6 bg-red-50/50 border border-red-100 rounded-xl',
        compact ? 'py-8' : 'py-12',
      ].join(' ')}
      aria-label={title}
    >
      <div className="w-11 h-11 bg-red-100 rounded-full flex items-center justify-center mb-3">
        <AlertCircle size={20} className="text-red-600" aria-hidden="true" />
      </div>
      <p className="text-sm font-semibold text-red-900 mb-1">{title}</p>
      <p className="text-xs text-red-600 max-w-md leading-relaxed mb-4">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="flex items-center gap-1.5 px-3.5 py-1.5 bg-red-600 hover:bg-red-700 text-white rounded-lg text-xs font-medium transition-colors shadow-sm"
        >
          <RotateCcw size={13} />
          Retry Request
        </button>
      )}
    </div>
  )
}
