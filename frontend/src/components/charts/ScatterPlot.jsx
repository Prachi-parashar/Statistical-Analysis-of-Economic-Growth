import {
  ResponsiveContainer, ScatterChart, Scatter, XAxis, YAxis,
  CartesianGrid, Tooltip, Label,
} from 'recharts'
import ChartCard from '../ChartCard.jsx'
import EmptyState from '../EmptyState.jsx'
import { GitBranch, TrendingUp } from 'lucide-react'
import { useTheme } from '../../context/ThemeContext.jsx'

function ScatterTooltip({ active, payload, xLabel = 'Predictor', yLabel = 'GDP Growth', unit = '%' }) {
  if (!active || !payload?.length) return null
  const d = payload[0]?.payload
  if (!d) return null

  const xFormatted = typeof d.x === 'number' ? `${d.x.toFixed(2)}${unit}` : d.x
  const yFormatted = typeof d.y === 'number' ? `${d.y.toFixed(2)}${unit}` : d.y

  return (
    <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl shadow-lg p-3 text-xs min-w-[150px]">
      {d.year && (
        <div className="flex items-center justify-between font-semibold text-slate-700 dark:text-slate-200 pb-1.5 mb-1.5 border-b border-slate-100 dark:border-slate-700">
          <span className="text-slate-500 dark:text-slate-400">Year</span>
          <span className="font-mono text-blue-600 dark:text-blue-400">{d.year}</span>
        </div>
      )}
      <div className="space-y-1.5">
        <div className="flex items-center justify-between gap-3 text-slate-600 dark:text-slate-300">
          <span className="truncate max-w-[110px]">{xLabel}:</span>
          <strong className="font-mono text-slate-900 dark:text-slate-100 tabular-nums">{xFormatted}</strong>
        </div>
        <div className="flex items-center justify-between gap-3 text-slate-600 dark:text-slate-300">
          <span className="truncate max-w-[110px]">{yLabel}:</span>
          <strong className="font-mono text-slate-900 dark:text-slate-100 tabular-nums">{yFormatted}</strong>
        </div>
      </div>
    </div>
  )
}

export default function ScatterPlot({
  title,
  subtitle,
  data = [],
  xLabel = 'Predictor',
  yLabel = 'GDP Growth',
  color = '#2563eb',
  trendData,
  note,
  height = 300,
  r,
  pValue,
  rSquared,
  intercept,
  slope,
  unit = '%',
}) {
  const { theme } = useTheme()
  const isDark = theme === 'dark'
  const isEmpty = !data || data.length === 0
  const n = data.length

  const gridColor = isDark ? '#334155' : '#f1f5f9'
  const tickColor = isDark ? '#94a3b8' : '#64748b'
  const axisColor = isDark ? '#475569' : '#e2e8f0'
  const labelColor = isDark ? '#94a3b8' : '#64748b'

  // Signed Pearson r format (+0.3180, -0.1412)
  const rNum = typeof r === 'number' ? r : (r !== undefined && r !== null && !isNaN(Number(r)) ? Number(r) : null)
  const pNum = typeof pValue === 'number' ? pValue : (pValue !== undefined && pValue !== null && !isNaN(Number(pValue)) ? Number(pValue) : null)
  const r2Num = typeof rSquared === 'number' ? rSquared : (rSquared !== undefined && rSquared !== null && !isNaN(Number(rSquared)) ? Number(rSquared) : null)

  const rSignedStr = rNum !== null ? `${rNum > 0 ? '+' : ''}${rNum.toFixed(4)}` : null
  const pStr = pNum !== null ? pNum.toFixed(4) : null
  const r2Str = r2Num !== null ? r2Num.toFixed(4) : null

  const isSig = pNum !== null && pNum < 0.05
  const isPositive = rNum !== null && rNum > 0

  let interpretationText = ''
  if (rNum !== null && pNum !== null) {
    const dir = isPositive ? 'Positive' : 'Negative'
    const connector = isSig ? 'and' : 'but'
    const sigPart = isSig ? 'statistically significant' : 'not statistically significant'
    interpretationText = `${dir} linear association, ${connector} ${sigPart} at α = 0.05 (p = ${pStr}).`
  }

  const r2PctStr = r2Num !== null ? `${(r2Num * 100).toFixed(2)}% explained` : null

  // Compact legend element
  const legendElement = (
    <div className="flex flex-wrap items-center gap-4 text-xs text-slate-500 dark:text-slate-400 pt-1">
      <div className="flex items-center gap-1.5">
        <span className="w-2.5 h-2.5 rounded-full bg-blue-600 inline-block" />
        <span>Observed data (n = {n})</span>
      </div>
      {trendData && trendData.length > 0 && (
        <div className="flex items-center gap-1.5">
          <span className="w-4 h-0.5 border-t-2 border-dashed border-slate-700 dark:border-slate-300 inline-block" />
          <span>OLS fitted line</span>
        </div>
      )}
    </div>
  )

  return (
    <ChartCard
      title={title}
      subtitle={subtitle}
    >
      {isEmpty ? (
        <EmptyState icon={GitBranch} title="Scatter data pending"
          message="Connect the backend API to populate this chart." compact />
      ) : (
        <div className="space-y-3">
          {/* Header Legend */}
          <div className="flex items-center justify-between px-1">
            {legendElement}
          </div>

          {/* Chart Graphic */}
          <ResponsiveContainer width="100%" height={height}>
            <ScatterChart margin={{ top: 12, right: 24, left: 16, bottom: 28 }}>
              <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
              <XAxis
                dataKey="x"
                type="number"
                name={xLabel}
                tick={{ fontSize: 10.5, fill: tickColor }}
                tickLine={false}
                axisLine={{ stroke: axisColor }}
              >
                {xLabel && (
                  <Label
                    value={xLabel}
                    offset={-14}
                    position="insideBottom"
                    style={{ textAnchor: 'middle', fontSize: 11, fontWeight: 500, fill: labelColor }}
                  />
                )}
              </XAxis>
              <YAxis
                dataKey="y"
                type="number"
                name={yLabel}
                tick={{ fontSize: 10.5, fill: tickColor }}
                tickLine={false}
                axisLine={false}
                width={48}
              >
                {yLabel && (
                  <Label
                    value={yLabel}
                    angle={-90}
                    position="insideLeft"
                    offset={0}
                    style={{ textAnchor: 'middle', fontSize: 11, fontWeight: 500, fill: labelColor }}
                  />
                )}
              </YAxis>
              <Tooltip
                content={<ScatterTooltip xLabel={xLabel} yLabel={yLabel} unit={unit} />}
                cursor={{ strokeDasharray: '3 3' }}
              />
              <Scatter
                name="Observed data"
                data={data}
                fill={color}
                fillOpacity={0.75}
                shape="circle"
              />
              {trendData && trendData.length > 0 && (
                <Scatter
                  name="OLS fitted line"
                  data={trendData}
                  line={{
                    stroke: isDark ? '#cbd5e1' : '#1e293b',
                    strokeWidth: 1.75,
                    strokeDasharray: '5 3',
                  }}
                  shape={() => null}
                  legendType="none"
                />
              )}
            </ScatterChart>
          </ResponsiveContainer>

          {/* Statistical Summary & Academic Interpretation Footer */}
          {(rSignedStr !== null || r2Str !== null || slope !== undefined) && (
            <div className="pt-3 border-t border-slate-100 dark:border-slate-700/60 text-xs space-y-2">
              <div className="flex flex-wrap items-center justify-between gap-2.5">
                {/* Core metrics pills */}
                <div className="flex flex-wrap items-center gap-2">
                  {rSignedStr !== null && (
                    <span className="inline-flex items-center px-2.5 py-1 rounded-md bg-slate-50 dark:bg-slate-700/50 border border-slate-200/80 dark:border-slate-700 font-mono text-slate-800 dark:text-slate-100">
                      <span className="text-slate-500 dark:text-slate-400 mr-1.5 font-sans font-medium">Pearson r:</span>
                      <strong>{rSignedStr}</strong>
                    </span>
                  )}
                  {pStr !== null && (
                    <span className="inline-flex items-center px-2.5 py-1 rounded-md bg-slate-50 dark:bg-slate-700/50 border border-slate-200/80 dark:border-slate-700 font-mono text-slate-800 dark:text-slate-100">
                      <span className="text-slate-500 dark:text-slate-400 mr-1.5 font-sans font-medium">p-value:</span>
                      <strong>{pStr}</strong>
                    </span>
                  )}
                  {r2Str !== null && (
                    <span className="inline-flex items-center px-2.5 py-1 rounded-md bg-slate-50 dark:bg-slate-700/50 border border-slate-200/80 dark:border-slate-700 font-mono text-slate-800 dark:text-slate-100">
                      <span className="text-slate-500 dark:text-slate-400 mr-1.5 font-sans font-medium">R²:</span>
                      <strong>{r2Str}</strong>
                      {r2PctStr && (
                        <span className="text-slate-500 dark:text-slate-400 font-sans ml-1 text-[11px]">
                          ({r2PctStr})
                        </span>
                      )}
                    </span>
                  )}
                  <span className="inline-flex items-center px-2.5 py-1 rounded-md bg-slate-50 dark:bg-slate-700/50 border border-slate-200/80 dark:border-slate-700 font-mono text-slate-800 dark:text-slate-100">
                    <span className="text-slate-500 dark:text-slate-400 mr-1.5 font-sans font-medium">Sample:</span>
                    n = {n}
                  </span>
                </div>

                {/* Significance badge */}
                {pNum !== null && (
                  <span className={[
                    'inline-flex items-center px-2.5 py-1 rounded-md text-xs font-semibold border',
                    isSig
                      ? 'bg-blue-50 dark:bg-blue-950/40 text-blue-700 dark:text-blue-300 border-blue-200 dark:border-blue-800/60'
                      : 'bg-slate-50 dark:bg-slate-700/50 text-slate-600 dark:text-slate-300 border-slate-200/80 dark:border-slate-700'
                  ].join(' ')}>
                    {isSig ? '✓ Significant (p < 0.05)' : '— Not significant (p ≥ 0.05)'}
                  </span>
                )}
              </div>

              {/* Human-readable Simple OLS equation */}
              {slope !== undefined && intercept !== undefined && (
                <div className="flex items-center gap-1.5 text-slate-600 dark:text-slate-300 text-xs">
                  <span className="text-slate-500 dark:text-slate-400 font-medium">Simple OLS:</span>
                  <span className="font-mono font-medium text-slate-800 dark:text-slate-200">
                    GDP Growth = {intercept >= 0 ? intercept.toFixed(4) : `−${Math.abs(intercept).toFixed(4)}`} {slope >= 0 ? '+' : '−'} {Math.abs(slope).toFixed(4)} × {xLabel}
                  </span>
                </div>
              )}

              {/* Non-causal interpretation */}
              {interpretationText && (
                <p className="text-slate-600 dark:text-slate-300 text-xs leading-relaxed pt-0.5">
                  <span className="font-semibold text-slate-700 dark:text-slate-200 mr-1">Interpretation:</span>
                  {interpretationText}
                </p>
              )}
            </div>
          )}
        </div>
      )}
    </ChartCard>
  )
}
