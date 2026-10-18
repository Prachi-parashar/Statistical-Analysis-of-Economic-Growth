export default function LoadingState({ message = 'Loading data…', compact = false }) {
  return (
    <div className={`flex flex-col items-center justify-center gap-3 ${compact ? 'py-10' : 'py-16'}`}>
      <div className="relative w-9 h-9">
        <div className="absolute inset-0 rounded-full border-2 border-slate-200" />
        <div className="absolute inset-0 rounded-full border-2 border-t-primary-600 animate-spin" />
      </div>
      <p className="text-sm text-slate-500">{message}</p>
    </div>
  )
}
