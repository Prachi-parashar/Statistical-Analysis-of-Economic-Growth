import ChartCard from '../ChartCard.jsx'
import EmptyState from '../EmptyState.jsx'
import { GitBranch } from 'lucide-react'
import { useTheme } from '../../context/ThemeContext.jsx'

/** Map correlation value → background colour */
function cellBg(value, isDark = false) {
  if (value == null || isNaN(value)) return isDark ? '#1e293b' : '#f8fafc'
  const v = Math.max(-1, Math.min(1, value))
  if (v > 0) {
    const t = v
    return isDark
      ? `rgb(${Math.round(30 + (1 - t) * 30)}, ${Math.round(60 + t * 70)}, ${Math.round(120 + t * 135)})`
      : `rgb(${Math.round(255 * (1 - t * 0.55))},${Math.round(255 * (1 - t * 0.35))},255)`
  }
  if (v < 0) {
    const t = -v
    return isDark
      ? `rgb(${Math.round(140 + t * 115)}, ${Math.round(40 + (1 - t) * 40)}, ${Math.round(50 + (1 - t) * 50)})`
      : `rgb(255,${Math.round(255 * (1 - t * 0.35))},${Math.round(255 * (1 - t * 0.55))})`
  }
  return isDark ? '#1e293b' : '#f8fafc'
}

function cellFg(value, isDark = false) {
  if (value == null || isNaN(value)) return isDark ? '#64748b' : '#94a3b8'
  if (isDark) {
    return Math.abs(value) > 0.4 ? '#ffffff' : '#f1f5f9'
  }
  return Math.abs(value) > 0.5 ? '#fff' : '#1e293b'
}

/** Shorten long variable names for display inside small cells */
function shortLabel(s) {
  if (!s) return ''
  return s
    .replace('Gross_Capital_Formation', 'GCF')
    .replace('FDI_Net_Inflows', 'FDI')
    .replace('GDP_Growth', 'GDP Growth')
    .replace(/_/g, ' ')
}

export default function Heatmap({ title, subtitle, data, note, type = 'Pearson' }) {
  const { theme } = useTheme()
  const isDark = theme === 'dark'
  const isEmpty = !data || !data.labels || !data.matrix

  return (
    <ChartCard title={title || `${type} Correlation Matrix`} subtitle={subtitle} note={note}>
      {isEmpty ? (
        <EmptyState
          icon={GitBranch}
          title="Matrix data pending"
          message="Correlation matrix will be populated from the backend API."
          compact
        />
      ) : (
        <div className="overflow-x-auto">
          <table className="mx-auto border-collapse text-xs" aria-label={`${type} correlation matrix`}>
            <thead>
              <tr>
                <th className="w-10" aria-hidden="true" />
                {data.labels.map((l) => (
                  <th
                    key={l}
                    scope="col"
                    className="text-slate-500 dark:text-slate-400 font-medium pb-2 px-1 text-center leading-tight"
                    style={{ fontSize: 9, maxWidth: 56, wordBreak: 'break-word' }}
                    title={l}
                  >
                    {shortLabel(l)}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.matrix.map((row, ri) => (
                <tr key={ri}>
                  <th
                    scope="row"
                    className="text-slate-500 dark:text-slate-400 font-medium pr-2 text-right whitespace-nowrap"
                    style={{ fontSize: 9 }}
                    title={data.labels[ri]}
                  >
                    {shortLabel(data.labels[ri])}
                  </th>
                  {row.map((val, ci) => (
                    <td
                      key={ci}
                      title={`${shortLabel(data.labels[ri])} vs ${shortLabel(data.labels[ci])}: ${type} r = ${
                        typeof val === 'number' ? val.toFixed(4) : '—'
                      }`}
                      style={{
                        backgroundColor: cellBg(val, isDark),
                        color: cellFg(val, isDark),
                        width: 50, height: 40,
                        textAlign: 'center', fontWeight: 600, fontSize: 10,
                        border: isDark ? '2px solid #1e293b' : '2px solid #fff',
                        borderRadius: 4,
                        cursor: 'default',
                      }}
                    >
                      {typeof val === 'number' ? val.toFixed(2) : '—'}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>

          {/* Legend */}
          <div className="flex items-center justify-center gap-5 mt-4 text-xs text-slate-500 dark:text-slate-400">
            {[
              { val: 1,  label: '+1 (positive)' },
              { val: 0,  label: '0 (none)'       },
              { val: -1, label: '−1 (negative)'  },
            ].map(({ val, label }) => (
              <div key={val} className="flex items-center gap-1.5">
                <span
                  className="w-4 h-4 rounded"
                  style={{ backgroundColor: cellBg(val, isDark) }}
                  aria-hidden="true"
                />
                <span>{label}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </ChartCard>
  )
}
