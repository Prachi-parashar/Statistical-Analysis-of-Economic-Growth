import { AlertTriangle, Database } from 'lucide-react'

export default function DataTable({
  columns = [],
  rows = [],
  caption,
  mock = false,
  stickyHeader = false,
  emptyMessage = 'Analysis result not available.',
}) {
  return (
    <div className="overflow-x-auto -mx-0.5">
      {mock && (
        <div className="mb-3">
          <span className="badge-warn gap-1.5">
            <AlertTriangle size={11} aria-hidden="true" />
            Demo / placeholder data — not real project results
          </span>
        </div>
      )}

      <table className="w-full text-sm border-collapse">
        {caption && (
          <caption className="text-left text-xs text-slate-400 dark:text-slate-500 pb-2 pl-0.5 caption-top">
            {caption}
          </caption>
        )}
        <thead>
          <tr>
            {columns.map((col, ci) => (
              <th
                key={col.key}
                title={col.tooltip}
                className={[
                  'text-left text-xs font-semibold text-slate-600 dark:text-slate-300 uppercase tracking-wide',
                  'py-2.5 px-3 bg-slate-50 dark:bg-slate-900/60 border-b border-slate-200 dark:border-slate-700/80',
                  'whitespace-nowrap',
                  stickyHeader ? 'sticky top-0 z-10' : '',
                  ci === 0 ? 'rounded-tl-lg' : '',
                  ci === columns.length - 1 ? 'rounded-tr-lg' : '',
                  col.numeric ? 'text-right' : '',
                ].join(' ')}
              >
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.length === 0 ? (
            <tr>
              <td
                colSpan={columns.length}
                className="text-center py-10 text-sm text-slate-400 dark:text-slate-500"
              >
                <div className="flex flex-col items-center gap-2">
                  <Database size={20} className="text-slate-300 dark:text-slate-600" aria-hidden="true" />
                  <span className="italic">{emptyMessage}</span>
                </div>
              </td>
            </tr>
          ) : (
            rows.map((row, ri) => (
              <tr
                key={ri}
                className="border-b border-slate-100 dark:border-slate-700/60 hover:bg-slate-50/80 dark:hover:bg-slate-700/40 transition-colors"
              >
                {columns.map((col) => {
                  const val = row[col.key]
                  let formatted = val
                  if (typeof val === 'number') {
                    formatted = Number.isInteger(val) ? val.toString() : val.toFixed(4).replace(/\.?0+$/, '')
                  }
                  return (
                    <td
                      key={col.key}
                      className={[
                        'py-2.5 px-3',
                        col.numeric
                          ? 'font-mono text-right tabular-nums text-slate-700 dark:text-slate-200'
                          : 'text-slate-700 dark:text-slate-200',
                        col.className || '',
                      ].join(' ')}
                    >
                      {formatted ?? '—'}
                    </td>
                  )
                })}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  )
}
