import {
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  Label,
} from 'recharts'
import { useTheme } from '../../context/ThemeContext.jsx'

function ResidualsTooltip({ active, payload }) {
  if (!active || !payload?.length) return null
  const d = payload[0]?.payload
  if (!d) return null

  const fitStr = typeof d.fitted === 'number' ? `${d.fitted.toFixed(2)}%` : d.fitted
  const resStr = typeof d.residual === 'number'
    ? `${d.residual > 0 ? '+' : ''}${d.residual.toFixed(4)}`
    : d.residual
  const stdResStr = typeof d.standardized_residual === 'number'
    ? d.standardized_residual.toFixed(3)
    : d.standardized_residual

  return (
    <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl shadow-lg p-3 text-xs min-w-[170px]">
      <div className="flex items-center justify-between font-semibold text-slate-700 dark:text-slate-200 pb-1.5 mb-1.5 border-b border-slate-100 dark:border-slate-700">
        <span className="text-slate-500 dark:text-slate-400">Observation</span>
        <span className="font-mono text-purple-600 dark:text-purple-400 font-bold">
          {d.year ? `Year ${d.year}` : 'Data Point'}
        </span>
      </div>
      <div className="space-y-1.5">
        <div className="flex items-center justify-between gap-3 text-slate-600 dark:text-slate-300">
          <span>Fitted GDP:</span>
          <strong className="font-mono text-slate-900 dark:text-slate-100 tabular-nums">{fitStr}</strong>
        </div>
        <div className="flex items-center justify-between gap-3 text-slate-600 dark:text-slate-300">
          <span>Residual:</span>
          <strong className="font-mono text-slate-900 dark:text-slate-100 tabular-nums">{resStr}</strong>
        </div>
        {stdResStr !== undefined && (
          <div className="flex items-center justify-between gap-3 text-slate-500 dark:text-slate-400 text-[11px] pt-0.5 border-t border-slate-100 dark:border-slate-700/60">
            <span>Std. Residual:</span>
            <span className="font-mono tabular-nums">{stdResStr}</span>
          </div>
        )}
      </div>
    </div>
  )
}

export default function ResidualsFittedChart({
  data = [],
  height = 320,
}) {
  const { theme } = useTheme()
  const isDark = theme === 'dark'

  const gridColor = isDark ? '#334155' : '#f1f5f9'
  const tickColor = isDark ? '#94a3b8' : '#64748b'
  const axisColor = isDark ? '#475569' : '#e2e8f0'
  const labelColor = isDark ? '#94a3b8' : '#64748b'

  const chartData = Array.isArray(data) ? data : []
  const n = chartData.length

  // Calculate clean, evenly spaced integer ticks for Y-axis (Residuals) directly from backend data
  const residuals = chartData.map(d => d.residual).filter(r => typeof r === 'number' && !isNaN(r))
  const minRes = residuals.length > 0 ? Math.min(...residuals) : -10
  const maxRes = residuals.length > 0 ? Math.max(...residuals) : 4

  const yStep = 2
  let yMinBound = Math.floor(minRes / yStep) * yStep // e.g. -10
  let yMaxBound = Math.ceil(maxRes / yStep) * yStep  // e.g. 4
  if (yMinBound >= yMaxBound) {
    yMinBound -= yStep
    yMaxBound += yStep
  }
  const yTicks = []
  for (let v = yMinBound; v <= yMaxBound; v += yStep) {
    yTicks.push(v)
  }
  if (!yTicks.includes(0)) {
    yTicks.push(0)
    yTicks.sort((a, b) => a - b)
  }

  // Calculate clean, evenly spaced integer ticks for X-axis (Fitted GDP Growth) directly from backend data
  const fittedVals = chartData.map(d => d.fitted).filter(f => typeof f === 'number' && !isNaN(f))
  const minFit = fittedVals.length > 0 ? Math.min(...fittedVals) : 2
  const maxFit = fittedVals.length > 0 ? Math.max(...fittedVals) : 10
  let xMinBound = Math.floor(minFit)
  let xMaxBound = Math.ceil(maxFit)
  if (xMinBound >= xMaxBound) {
    xMinBound -= 1
    xMaxBound += 1
  }
  const xTicks = []
  for (let v = xMinBound; v <= xMaxBound; v += 1) {
    xTicks.push(v)
  }

  // Map coordinates explicitly for Recharts ScatterChart compatibility
  const scatterPoints = chartData.map(d => ({
    ...d,
    x: typeof d.fitted === 'number' ? d.fitted : parseFloat(d.fitted),
    y: typeof d.residual === 'number' ? d.residual : parseFloat(d.residual),
  }))

  return (
    <div className="space-y-3">
      {/* In-Chart Title & Description */}
      <div className="text-center space-y-0.5 pb-1">
        <h4 className="text-sm font-bold text-slate-900 dark:text-slate-100 tracking-tight">
          Residuals vs Fitted Values
        </h4>
        <p className="text-xs text-slate-500 dark:text-slate-400 leading-snug">
          Evaluates linearity and constancy of error variance across predicted GDP Growth
        </p>
      </div>

      {/* Legend & Summary Info */}
      <div className="flex flex-wrap items-center justify-between gap-3 text-xs text-slate-500 dark:text-slate-400 px-1">
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-purple-600 inline-block" />
            <span>Observed Residuals (n = {n})</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-4 h-0.5 border-t-2 border-dashed border-red-500 inline-block" />
            <span className="text-red-600 dark:text-red-400 font-medium">Reference Line (y = 0)</span>
          </div>
        </div>
        <span className="text-[11px] font-mono text-slate-400 dark:text-slate-500">
          Linearity & Homoscedasticity Check
        </span>
      </div>

      {/* Chart Canvas */}
      <ResponsiveContainer width="100%" height={height}>
        <ScatterChart margin={{ top: 16, right: 28, left: 16, bottom: 28 }}>
          <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
          <XAxis
            dataKey="fitted"
            type="number"
            name="Fitted GDP Growth"
            unit="%"
            ticks={xTicks}
            domain={[xMinBound, xMaxBound]}
            tickFormatter={(val) => Number(val).toFixed(0)}
            tick={{ fontSize: 10.5, fill: tickColor }}
            tickLine={false}
            axisLine={{ stroke: axisColor }}
          >
            <Label
              value="Fitted GDP Growth (%)"
              offset={-14}
              position="insideBottom"
              style={{ textAnchor: 'middle', fontSize: 11, fontWeight: 500, fill: labelColor }}
            />
          </XAxis>
          <YAxis
            dataKey="residual"
            type="number"
            name="Residuals"
            ticks={yTicks}
            domain={[yMinBound, yMaxBound]}
            tickFormatter={(val) => Number(val).toFixed(0)}
            tick={{ fontSize: 10.5, fill: tickColor }}
            tickLine={false}
            axisLine={false}
            width={48}
          >
            <Label
              value="Residuals"
              angle={-90}
              position="insideLeft"
              offset={0}
              style={{ textAnchor: 'middle', fontSize: 11, fontWeight: 500, fill: labelColor }}
            />
          </YAxis>
          <ReferenceLine
            y={0}
            stroke="#dc2626"
            strokeDasharray="4 4"
            strokeWidth={1.5}
            label={{
              value: 'y = 0',
              position: 'insideTopRight',
              fill: '#dc2626',
              fontSize: 11,
              fontWeight: 600,
            }}
          />
          <Tooltip content={<ResidualsTooltip />} cursor={{ strokeDasharray: '3 3' }} />
          <Scatter
            name="Residuals"
            data={scatterPoints}
            fill="#8b5cf6"
            stroke="#7c3aed"
            strokeWidth={1.2}
            fillOpacity={0.8}
            shape="circle"
          />
        </ScatterChart>
      </ResponsiveContainer>

      {/* Statistical Summary Footer */}
      <div className="pt-2.5 border-t border-slate-100 dark:border-slate-800 text-xs flex flex-wrap items-center justify-between gap-2">
        <div className="flex flex-wrap items-center gap-2">
          <span className="inline-flex items-center px-2 py-0.5 rounded bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 font-mono text-[11px]">
            <span className="font-sans text-slate-500 mr-1">Sample:</span> n = {n}
          </span>
          {minRes !== null && (
            <span className="inline-flex items-center px-2 py-0.5 rounded bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 font-mono text-[11px]">
              <span className="font-sans text-slate-500 mr-1">Min Residual:</span> {minRes.toFixed(4)}
            </span>
          )}
          {maxRes !== null && (
            <span className="inline-flex items-center px-2 py-0.5 rounded bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 font-mono text-[11px]">
              <span className="font-sans text-slate-500 mr-1">Max Residual:</span> +{maxRes.toFixed(4)}
            </span>
          )}
        </div>
        <span className="text-slate-500 dark:text-slate-400 text-[11px]">
          Inspect residual patterns for evidence of non-linearity and non-constant variance.
        </span>
      </div>
    </div>
  )
}
