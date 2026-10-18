/**
 * Reusable variable / category pill-button row.
 * items: Array<string | { value: string, label: string }>
 */
export default function VarPillSelector({ items = [], selected, onChange, label }) {
  return (
    <div className="p-4 flex flex-wrap gap-2 items-center">
      {label && (
        <span className="text-xs font-semibold text-slate-500 uppercase tracking-wide mr-1">
          {label}:
        </span>
      )}
      {items.map((item) => {
        const value = typeof item === 'string' ? item : item.value
        const display = typeof item === 'string'
          ? item.replace(/_/g, '\u00A0')   // non-breaking space looks cleaner
          : item.label
        const active = selected === value
        return (
          <button
            key={value}
            onClick={() => onChange(value)}
            className={[
              'pill-btn',
              active ? 'pill-btn-active' : 'pill-btn-inactive',
            ].join(' ')}
            aria-pressed={active}
          >
            {display}
          </button>
        )
      })}
    </div>
  )
}
