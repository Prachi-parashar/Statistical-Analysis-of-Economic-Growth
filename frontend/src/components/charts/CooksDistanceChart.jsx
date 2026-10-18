import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  Label,
} from 'recharts'
import { useTheme } from '../../context/ThemeContext.jsx'

function CooksDistanceTooltip({ active, payload, threshold }) {
  if (!active || !payload?.length) return null
  const d = payload[0]?.payload
  if (!d) return null

  const cdVal = typeof d.cooks_d === 'number' ? d.cooks_d : parseFloat(d.cooks_d)
  const isInfluential = !isNaN(cdVal) && cdVal > threshold

  return (
    <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl shadow-lg p-3 text-xs min-w-[190px]">
      <div className="flex items-center justify-between font-semibold text-slate-700 dark:text-slate-200 pb-1.5 mb-1.5 border-b border-slate-100 dark:border-slate-700">
        <span className="text-slate-500 dark:text-slate-400">Observation</span>
        <span className="font-mono text-blue-600 dark:text-blue-400 font-bold">
          Year {d.year}
        </span>
      </div>
      <div className="space-y-1.5">
        <div className="flex items-center justify-between gap-3 text-slate-600 dark:text-slate-300">
          <span>Cook's Distance (D):</span>
          <strong className={`font-mono tabular-nums ${isInfluential ? 'text-red-600 dark:text-red-400 font-bold' : 'text-slate-900 dark:text-slate-100'}`}>
            {!isNaN(cdVal) ? cdVal.toFixed(4) : d.cooks_d}
          </strong>
        </div>
        <div className="flex items-center justify-between gap-3 text-slate-500 dark:text-slate-400 text-[11px]">
          <span>Screening Threshold:</span>
          <span className="font-mono tabular-nums">4/n ≈ {threshold.toFixed(3)}</span>
        </div>
        <div className="pt-1.5 mt-1 border-t border-slate-100 dark:border-slate-700/60">
          {isInfluential ? (
            <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-red-600 dark:text-red-400">
              <span className="w-1.5 h-1.5 rounded-full bg-red-500 inline-block" />
              Exceeds Threshold (Influential)
            </span>
          ) : (
            <span className="inline-flex items-center gap-1 text-[11px] text-slate-500 dark:text-slate-400">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 inline-block" />
              Within Screening Bound
            </span>
          )}
        </div>
      </div>
    </div>
  )
}

function LollipopShape(props) {
  const { x, y, width, height, payload, threshold, isDark } = props
  if (!payload || x === undefined || y === undefined || isNaN(x) || isNaN(y)) return null

  const cx = x + (width || 0) / 2
  const baseY = (y ?? 0) + (height ?? 0)
  const cdVal = typeof payload.cooks_d === 'number' ? payload.cooks_d : parseFloat(payload.cooks_d)
  const safeThreshold = typeof threshold === 'number' && !isNaN(threshold) ? threshold : 0.1143
  const isInfluential = !isNaN(cdVal) && cdVal > safeThreshold

  const stemColor = isInfluential ? '#dc2626' : (isDark ? '#60a5fa' : '#2563eb')
  const dotFill = isInfluential ? '#dc2626' : (isDark ? '#3b82f6' : '#1d4ed8')
  const radius = isInfluential ? 5.5 : 3.5

  // Careful placement for influential labels so they never overlap threshold line or edges
  let labelX = cx
  let labelY = y - 9
  let textAnchor = 'middle'

  if (payload.year === 1991) {
    // 1991 is at the left boundary: align slightly start/rightward so it does not touch the Y-axis
    labelX = cx + 3
    textAnchor = 'start'
    labelY = y - 10
  } else if (payload.year === 2020) {
    labelX = cx
    textAnchor = 'middle'
    labelY = y - 10
  }

  return (
    <g>
      {/* Vertical Stem Line */}
      <line
        x1={cx}
        y1={baseY}
        x2={cx}
        y2={y}
        stroke={stemColor}
        strokeWidth={isInfluential ? 2 : 1.4}
        strokeOpacity={isInfluential ? 1 : 0.75}
      />
      {/* Lollipop Circle Head */}
      <circle
        cx={cx}
        cy={y}
        r={radius}
        fill={dotFill}
        stroke="#ffffff"
        strokeWidth={1.5}
      />
      {/* Data Label for Influential Observations with text halo */}
      {isInfluential && !isNaN(cdVal) && (
        <text
          x={labelX}
          y={labelY}
          textAnchor={textAnchor}
          fill="#dc2626"
          stroke={isDark ? '#0f172a' : '#ffffff'}
          strokeWidth={3}
          style={{ paintOrder: 'stroke fill' }}
          fontSize={10.5}
          fontWeight={700}
        >
          {`${payload.year ?? ''} (${cdVal.toFixed(3)})`}
        </text>
      )}
    </g>
  )
}

export default function CooksDistanceChart({
  data = [],
  threshold = 0.1143,
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
  const safeThreshold = typeof threshold === 'number' && !isNaN(threshold) ? threshold : 0.1143

  // Find influential points directly from backend data
  const influentialItems = chartData.filter(d => {
    const v = typeof d.cooks_d === 'number' ? d.cooks_d : parseFloat(d.cooks_d)
    return !isNaN(v) && v > safeThreshold
  })

  // Max Cook's D directly from backend data
  const maxVal = chartData.reduce((acc, d) => {
    const v = typeof d.cooks_d === 'number' ? d.cooks_d : parseFloat(d.cooks_d)
    return !isNaN(v) ? Math.max(acc, v) : acc
  }, safeThreshold)

  const maxItem = chartData.find(d => {
    const v = typeof d.cooks_d === 'number' ? d.cooks_d : parseFloat(d.cooks_d)
    return Math.abs(v - maxVal) < 0.0001
  })

  // Clean evenly spaced Y-axis ticks (e.g. 0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7)
  const yTicks = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]
  const yDomainMax = 0.72

  return (
    <div className="space-y-3">
      {/* In-Chart Title & Description */}
      <div className="text-center space-y-0.5 pb-1">
        <h4 className="text-sm font-bold text-slate-900 dark:text-slate-100 tracking-tight">
          Cook's Distance — Influential Observations
        </h4>
        <p className="text-xs text-slate-500 dark:text-slate-400 leading-snug">
          Influence check: observations exceeding the Cook's D screening threshold 4/n ≈ {threshold.toFixed(3)}
        </p>
      </div>

      {/* Legend & Summary Info */}
      <div className="flex flex-wrap items-center justify-between gap-3 text-xs text-slate-500 dark:text-slate-400 px-1">
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-blue-600 inline-block" />
            <span>Observations (n = {n})</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-4 h-0.5 border-t-2 border-dashed border-red-500 inline-block" />
            <span className="text-red-600 dark:text-red-400 font-medium">
              Threshold 4/n ≈ {threshold.toFixed(3)}
            </span>
          </div>
          {influentialItems.length > 0 && (
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-red-600 inline-block" />
              <span className="text-red-700 dark:text-red-400 font-semibold">
                Influential ({influentialItems.length})
              </span>
            </div>
          )}
        </div>
        <span className="text-[11px] font-mono text-slate-400 dark:text-slate-500">
          Influence & Leverage Check
        </span>
      </div>

      {/* Chart Canvas */}
      <ResponsiveContainer width="100%" height={height}>
        <BarChart
          data={chartData}
          margin={{ top: 24, right: 28, left: 16, bottom: 28 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
          <XAxis
            dataKey="year"
            tick={{ fontSize: 10.5, fill: tickColor }}
            tickLine={false}
            axisLine={{ stroke: axisColor }}
            interval={4}
          >
            <Label
              value="Year"
              offset={-14}
              position="insideBottom"
              style={{ textAnchor: 'middle', fontSize: 11, fontWeight: 500, fill: labelColor }}
            />
          </XAxis>
          <YAxis
            dataKey="cooks_d"
            type="number"
            ticks={yTicks}
            domain={[0, yDomainMax]}
            tickFormatter={(val) => Number(val).toFixed(1)}
            tick={{ fontSize: 10.5, fill: tickColor }}
            tickLine={false}
            axisLine={false}
            width={48}
          >
            <Label
              value="Cook's Distance (D)"
              angle={-90}
              position="insideLeft"
              offset={0}
              style={{ textAnchor: 'middle', fontSize: 11, fontWeight: 500, fill: labelColor }}
            />
          </YAxis>
          {/* Position ReferenceLine label on the right side so it never collides with Year 1991 on the left */}
          <ReferenceLine
            y={safeThreshold}
            stroke="#dc2626"
            strokeDasharray="4 4"
            strokeWidth={1.5}
            label={{
              value: `Threshold 4/n ≈ ${safeThreshold.toFixed(3)}`,
              position: 'insideTopRight',
              fill: '#dc2626',
              fontSize: 10.5,
              fontWeight: 600,
            }}
          />
          <Tooltip
            content={<CooksDistanceTooltip threshold={safeThreshold} />}
            cursor={{ fill: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.03)' }}
          />
          <Bar
            dataKey="cooks_d"
            shape={<LollipopShape threshold={safeThreshold} isDark={isDark} />}
          />
        </BarChart>
      </ResponsiveContainer>

      {/* Statistical Summary Footer */}
      <div className="pt-2.5 border-t border-slate-100 dark:border-slate-800 text-xs flex flex-wrap items-center justify-between gap-2">
        <div className="flex flex-wrap items-center gap-2">
          <span className="inline-flex items-center px-2 py-0.5 rounded bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 font-mono text-[11px]">
            <span className="font-sans text-slate-500 mr-1">Threshold:</span> 4/{n || 35} ≈ ${safeThreshold.toFixed(3)}
          </span>
          <span className="inline-flex items-center px-2 py-0.5 rounded bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 font-mono text-[11px]">
            <span className="font-sans text-slate-500 mr-1">Max D:</span> {maxVal.toFixed(4)} {maxItem?.year ? `(Year ${maxItem.year})` : ''}
          </span>
          <span className={`inline-flex items-center px-2 py-0.5 rounded font-mono text-[11px] border ${
            influentialItems.length > 0
              ? 'bg-amber-50 dark:bg-amber-950/40 border-amber-200 dark:border-amber-800 text-amber-800 dark:text-amber-300'
              : 'bg-emerald-50 dark:bg-emerald-950/40 border-emerald-200 dark:border-emerald-800 text-emerald-800 dark:text-emerald-300'
          }`}>
            <span className="font-sans mr-1">Influential:</span> {influentialItems.length} obs ({influentialItems.map(i => `${i.year} [${Number(i.cooks_d).toFixed(3)}]`).join(', ') || 'None'})
          </span>
        </div>
        <span className="text-slate-500 dark:text-slate-400 text-[11px]">
          Points exceeding 4/n flagged for influence check; retained in primary OLS regression as valid data points.
        </span>
      </div>
    </div>
  )
}
