import ChartCard from '../ChartCard.jsx'
import EmptyState from '../EmptyState.jsx'
import { Activity } from 'lucide-react'
import { useTheme } from '../../context/ThemeContext.jsx'

function SVGBoxPlot({ stats, color = '#3b82f6', unit, isDark }) {
  const { min, q1, median, q3, max, whiskerLow, whiskerHigh, outliers = [], mean } = stats
  
  // Whiskers extend to actual smallest/largest non-outlier observations
  const wLow = whiskerLow !== undefined ? whiskerLow : min
  const wHigh = whiskerHigh !== undefined ? whiskerHigh : max

  const W = 340, H = 120, PAD = 44
  const plotW = W - PAD * 2
  const mid = H / 2
  const range = (max - min) || 1
  const sx = (v) => PAD + ((v - min) / range) * plotW

  const labelFill = isDark ? '#94a3b8' : '#64748b'

  return (
    <svg
      width="100%"
      viewBox={`0 0 ${W} ${H}`}
      className="max-w-md mx-auto"
      aria-label="Tukey Box plot"
      role="img"
    >
      {/* Whiskers extending to non-outlier extremes (wLow, wHigh) */}
      <line x1={sx(wLow)} y1={mid} x2={sx(q1)} y2={mid} stroke={color} strokeWidth={1.5} />
      <line x1={sx(q3)} y1={mid} x2={sx(wHigh)} y2={mid} stroke={color} strokeWidth={1.5} />
      
      {/* Caps at non-outlier endpoints */}
      <line x1={sx(wLow)} y1={mid - 10} x2={sx(wLow)} y2={mid + 10} stroke={color} strokeWidth={1.5} />
      <line x1={sx(wHigh)} y1={mid - 10} x2={sx(wHigh)} y2={mid + 10} stroke={color} strokeWidth={1.5} />
      
      {/* Box (Q1 to Q3) */}
      <rect
        x={sx(q1)} y={mid - 19}
        width={Math.max(sx(q3) - sx(q1), 1)} height={38}
        fill={color} fillOpacity={isDark ? 0.25 : 0.15}
        stroke={color} strokeWidth={2} rx={3}
      />
      
      {/* Median (Q2) */}
      <line x1={sx(median)} y1={mid - 19} x2={sx(median)} y2={mid + 19} stroke={color} strokeWidth={3} />
      
      {/* Mean diamond */}
      {mean !== undefined && (
        <polygon
          points={`${sx(mean)},${mid - 7} ${sx(mean) + 6},${mid} ${sx(mean)},${mid + 7} ${sx(mean) - 6},${mid}`}
          fill={isDark ? '#1e293b' : 'white'} stroke={color} strokeWidth={1.5}
        />
      )}
      
      {/* Outliers displayed as individual points */}
      {outliers.map((o, i) => (
        <circle
          key={i}
          cx={sx(o)}
          cy={mid}
          r={4}
          fill="#ef4444"
          fillOpacity={0.85}
          stroke="#b91c1c"
          strokeWidth={1}
        >
          <title>{`Outlier: ${Number(o).toFixed(3)}`}</title>
        </circle>
      ))}
      
      {/* Axis labels */}
      <text x={sx(min)} y={mid + 33} textAnchor="middle" fontSize={9} fill={labelFill}>
        {Number(min).toFixed(2)}
      </text>
      <text x={sx(max)} y={mid + 33} textAnchor="middle" fontSize={9} fill={labelFill}>
        {Number(max).toFixed(2)}
      </text>
      <text x={sx(median)} y={mid - 26} textAnchor="middle" fontSize={9} fill={color} fontWeight={600}>
        Md={Number(median).toFixed(2)}
      </text>
      {unit && (
        <text x={W - 2} y={H - 2} textAnchor="end" fontSize={8} fill={labelFill}>{unit}</text>
      )}
    </svg>
  )
}

export default function BoxPlot({ title, subtitle, stats, color, unit, note }) {
  const { theme } = useTheme()
  const isDark = theme === 'dark'

  return (
    <ChartCard title={title} subtitle={subtitle} note={note}>
      {!stats ? (
        <EmptyState icon={Activity} title="Box plot data pending"
          message="Connect the backend API to populate this chart." compact />
      ) : (
        <div className="py-2">
          <SVGBoxPlot stats={stats} color={color} unit={unit} isDark={isDark} />
          
          {/* Subtle Legend */}
          <div className="mt-2 mb-1 py-1.5 px-3 bg-slate-50/80 dark:bg-slate-900/50 border border-slate-100 dark:border-slate-700/80 rounded-lg max-w-md mx-auto flex flex-wrap items-center justify-center gap-5 text-xs text-slate-600 dark:text-slate-300">
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-3 inline-flex items-center justify-center">
                <span className="w-2.5 h-1 bg-primary-600 rounded-full"></span>
              </span>
              <span className="font-medium text-slate-700 dark:text-slate-200">Median</span>
            </div>
            <div className="flex items-center gap-1.5">
              <svg className="w-3 h-3 flex-shrink-0" viewBox="0 0 16 16">
                <polygon points="8,1 15,8 8,15 1,8" fill={isDark ? '#1e293b' : 'white'} stroke={color || '#3b82f6'} strokeWidth="2.5" />
              </svg>
              <span className="font-medium text-slate-700 dark:text-slate-200">Mean</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-red-500 border border-red-700 inline-block flex-shrink-0"></span>
              <span className="font-medium text-slate-700 dark:text-slate-200">Outlier</span>
            </div>
          </div>

          {/* Stat Cards */}
          <div className="mt-3 grid grid-cols-5 gap-1.5 text-center">
            {[
              { k: 'min',    l: 'Min'    },
              { k: 'q1',     l: 'Q1'     },
              { k: 'median', l: 'Median' },
              { k: 'q3',     l: 'Q3'     },
              { k: 'max',    l: 'Max'    },
            ].map(({ k, l }) => (
              <div key={k} className="bg-slate-50 dark:bg-slate-700/40 border border-slate-100 dark:border-slate-700/50 rounded-lg py-2 px-1">
                <p className="text-xs text-slate-400 dark:text-slate-400 font-medium">{l}</p>
                <p className="text-sm font-semibold text-slate-700 dark:text-slate-200 mt-0.5 font-mono tabular-nums">
                  {stats[k] !== undefined ? Number(stats[k]).toFixed(3) : '—'}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </ChartCard>
  )
}
