import {
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Label,
} from 'recharts'
import { useTheme } from '../../context/ThemeContext.jsx'

/**
 * Acklam's rational approximation for the inverse standard normal CDF (probit).
 * Accurate to within 1.15e-9 across (0, 1).
 */
function probit(p) {
  if (p <= 0) return -3.5
  if (p >= 1) return 3.5

  const a = [
    -3.969683028665376e+01,  2.209460984245205e+02,
    -2.759285104469687e+02,  1.383577518672690e+02,
    -3.066479806614716e+01,  2.506628277459239e+00
  ]
  const b = [
    -5.447609879822406e+01,  1.615858368580409e+02,
    -1.556989798598866e+02,  6.680133369969702e+01,
    -1.328068155288572e+01
  ]
  const c = [
    -7.784894002430293e-03, -3.223964580411365e-01,
    -2.400758277161838e+00, -2.549732539343734e+00,
     4.374664141464968e+00,  2.938163982698783e+00
  ]
  const d = [
     7.784695709041462e-03,  3.224671290700398e-01,
     2.445134137142996e+00,  3.754408661907416e+00
  ]

  const pLow = 0.02425
  const pHigh = 1 - pLow

  let q, r
  if (p < pLow) {
    q = Math.sqrt(-2 * Math.log(p))
    return (((((c[0]*q + c[1])*q + c[2])*q + c[3])*q + c[4])*q + c[5]) /
           ((((d[0]*q + d[1])*q + d[2])*q + d[3])*q + 1)
  } else if (p <= pHigh) {
    q = p - 0.5
    r = q * q
    return (((((a[0]*r + a[1])*r + a[2])*r + a[3])*r + a[4])*r + a[5]) * q /
           (((((b[0]*r + b[1])*r + b[2])*r + b[3])*r + b[4])*r + 1)
  } else {
    q = Math.sqrt(-2 * Math.log(1 - p))
    return -(((((c[0]*q + c[1])*q + c[2])*q + c[3])*q + c[4])*q + c[5]) /
            ((((d[0]*q + d[1])*q + d[2])*q + d[3])*q + 1)
  }
}

function QQTooltip({ active, payload, unit = '% of GDP' }) {
  if (!active || !payload?.length) return null
  const d = payload[0]?.payload
  if (!d || d.isLineOnly) return null

  const isPct = unit.includes('%')
  const thStr = typeof d.x === 'number'
    ? `${d.x > 0 ? '+' : ''}${d.x.toFixed(3)}`
    : d.x
  const smStr = typeof d.y === 'number' ? `${d.y.toFixed(2)}${isPct ? '%' : ''}` : d.y
  const fitStr = typeof d.fitted_line === 'number' ? `${d.fitted_line.toFixed(2)}${isPct ? '%' : ''}` : null
  const depStr = (typeof d.y === 'number' && typeof d.fitted_line === 'number')
    ? `${(d.y - d.fitted_line) > 0 ? '+' : ''}${(d.y - d.fitted_line).toFixed(2)}${isPct ? '%' : ''}`
    : null

  return (
    <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl shadow-lg p-3 text-xs min-w-[190px]">
      <div className="flex items-center justify-between font-semibold text-slate-700 dark:text-slate-200 pb-1.5 mb-1.5 border-b border-slate-100 dark:border-slate-700">
        <span className="text-slate-500 dark:text-slate-400">Quantile Rank</span>
        <span className="font-mono text-blue-600 dark:text-blue-400 font-bold">
          {d.rank ? `${d.rank} of ${d.total}` : 'Observation'}
        </span>
      </div>
      <div className="space-y-1.5">
        <div className="flex items-center justify-between gap-3 text-slate-600 dark:text-slate-300">
          <span>Theoretical Quantile:</span>
          <strong className="font-mono text-slate-900 dark:text-slate-100 tabular-nums">{thStr}</strong>
        </div>
        <div className="flex items-center justify-between gap-3 text-slate-600 dark:text-slate-300">
          <span>Sample Quantile:</span>
          <strong className="font-mono text-blue-600 dark:text-blue-400 tabular-nums">{smStr}</strong>
        </div>
        {fitStr && (
          <div className="flex items-center justify-between gap-3 text-slate-500 dark:text-slate-400 text-[11px] pt-0.5 border-t border-slate-100 dark:border-slate-700/60">
            <span>Fit Line (OLS):</span>
            <span className="font-mono tabular-nums">{fitStr}</span>
          </div>
        )}
        {depStr && (
          <div className="flex items-center justify-between gap-3 text-slate-500 dark:text-slate-400 text-[11px]">
            <span>Departure:</span>
            <span className="font-mono tabular-nums text-amber-600 dark:text-amber-400">{depStr}</span>
          </div>
        )}
      </div>
    </div>
  )
}

export default function NormalQQPlotChart({
  variable = 'Gross_Capital_Formation',
  unit = '% of GDP',
  data = [],
  fitData = null,
  rawObservations = [],
  height = 320,
  swStat = null,
  swP = null,
  alpha = 0.05,
}) {
  const { theme } = useTheme()
  const isDark = theme === 'dark'

  const gridColor = isDark ? '#334155' : '#f1f5f9'
  const tickColor = isDark ? '#94a3b8' : '#64748b'
  const axisColor = isDark ? '#475569' : '#e2e8f0'
  const labelColor = isDark ? '#94a3b8' : '#64748b'

  // Extract or calculate Q-Q data points
  let qqPoints = []
  if (Array.isArray(data) && data.length > 0) {
    qqPoints = data.map((d, idx) => ({
      ...d,
      rank: idx + 1,
      total: data.length,
      x: typeof d.theoretical_quantile === 'number' ? d.theoretical_quantile : parseFloat(d.theoretical_quantile),
      y: typeof d.sample_quantile === 'number' ? d.sample_quantile : parseFloat(d.sample_quantile),
      fitted_line: typeof d.fitted_line === 'number' ? d.fitted_line : parseFloat(d.fitted_line),
    })).filter(p => !isNaN(p.x) && !isNaN(p.y))
  } else if (Array.isArray(rawObservations) && rawObservations.length > 2) {
    // Dynamically calculate Blom's normal quantiles matching scipy probplot
    const valid = rawObservations
      .map(v => (typeof v === 'number' ? v : parseFloat(v)))
      .filter(v => !isNaN(v))
      .sort((a, b) => a - b)

    const nObs = valid.length
    // Blom's plotting position: (i - 0.375) / (n + 0.25)
    const points = valid.map((yVal, i) => {
      const p = (i + 1 - 0.375) / (nObs + 0.25)
      const q = probit(p)
      return {
        theoretical_quantile: q,
        sample_quantile: yVal,
        x: q,
        y: yVal,
        rank: i + 1,
        total: nObs,
      }
    })

    // Compute linear regression fit: y = slope * x + intercept
    const meanX = points.reduce((acc, p) => acc + p.x, 0) / nObs
    const meanY = points.reduce((acc, p) => acc + p.y, 0) / nObs

    let num = 0
    let den = 0
    let denY = 0
    points.forEach(p => {
      const dx = p.x - meanX
      const dy = p.y - meanY
      num += dx * dy
      den += dx * dx
      denY += dy * dy
    })

    const slopeCalc = den !== 0 ? num / den : 1
    const interceptCalc = meanY - slopeCalc * meanX
    const rValCalc = (den !== 0 && denY !== 0) ? num / Math.sqrt(den * denY) : 1

    qqPoints = points.map(p => ({
      ...p,
      fitted_line: slopeCalc * p.x + interceptCalc,
      slope: slopeCalc,
      intercept: interceptCalc,
      r_val: rValCalc,
    }))
  }

  const n = qqPoints.length

  // Calculate or obtain OLS fit parameters matching SciPy probplot
  let slope = fitData?.slope ?? 0
  let intercept = fitData?.intercept ?? 0
  let rVal = fitData?.r_value ?? null

  if ((!slope && !intercept) || rVal === null) {
    if (n > 1) {
      const meanX = qqPoints.reduce((acc, p) => acc + p.x, 0) / n
      const meanY = qqPoints.reduce((acc, p) => acc + p.y, 0) / n
      let num = 0
      let den = 0
      let denY = 0
      qqPoints.forEach(p => {
        const dx = p.x - meanX
        const dy = p.y - meanY
        num += dx * dy
        den += dx * dx
        denY += dy * dy
      })
      slope = den !== 0 ? num / den : 1
      intercept = meanY - slope * meanX
      if (den !== 0 && denY !== 0) {
        rVal = num / Math.sqrt(den * denY)
      }
    }
  }

  // Ensure every point has a valid fitted_line value
  qqPoints = qqPoints.map(p => ({
    ...p,
    fitted_line: typeof p.fitted_line === 'number' && !isNaN(p.fitted_line)
      ? p.fitted_line
      : (slope * p.x + intercept)
  }))

  // Calculate clean, evenly spaced integer ticks for Y-axis (Sample Quantiles)
  const yVals = qqPoints.map(d => d.y)
  const minY = yVals.length > 0 ? Math.min(...yVals) : 20
  const maxY = yVals.length > 0 ? Math.max(...yVals) : 45
  const yStep = 5
  let yMinBound = Math.floor(minY / yStep) * yStep
  let yMaxBound = Math.ceil(maxY / yStep) * yStep
  if (yMinBound >= yMaxBound) {
    yMinBound -= yStep
    yMaxBound += yStep
  }
  const yTicks = []
  for (let v = yMinBound; v <= yMaxBound; v += yStep) {
    yTicks.push(v)
  }

  // Calculate clean, symmetric ticks for X-axis (Theoretical Normal Quantiles: e.g. -2.5 to +2.5)
  const xVals = qqPoints.map(d => d.x)
  const minX = xVals.length > 0 ? Math.min(...xVals) : -2.5
  const maxX = xVals.length > 0 ? Math.max(...xVals) : 2.5
  const maxAbsX = Math.max(Math.abs(minX), Math.abs(maxX))
  const xBound = Math.max(2.5, Math.ceil(maxAbsX * 2) / 2)
  const xMinBound = -xBound
  const xMaxBound = xBound

  const xTicks = []
  for (let v = Math.round(xMinBound); v <= Math.round(xMaxBound); v += 1) {
    xTicks.push(v)
  }

  // Calculate clean endpoints for theoretical normal fit line without clipping at chart boundaries
  const padX = 0.2
  let startX = minX - padX
  let endX = maxX + padX
  startX = Math.max(xMinBound + 0.1, startX)
  endX = Math.min(xMaxBound - 0.1, endX)

  if (slope !== 0) {
    // Keep Y within safe inner bounds so the line never clips on top/bottom grid axes
    const safeYMin = yMinBound + 0.25
    const safeYMax = yMaxBound - 0.25
    const xAtSafeMin = (safeYMin - intercept) / slope
    const xAtSafeMax = (safeYMax - intercept) / slope
    const minSafeX = Math.min(xAtSafeMin, xAtSafeMax)
    const maxSafeX = Math.max(xAtSafeMin, xAtSafeMax)
    startX = Math.max(startX, minSafeX)
    endX = Math.min(endX, maxSafeX)
  }

  const linePoints = [
    { x: startX, y: slope * startX + intercept, isLineOnly: true },
    { x: endX, y: slope * endX + intercept, isLineOnly: true },
  ]

  const getDynamicInterpretation = (pVal, alphaVal = 0.05) => {
    if (pVal === null || pVal === undefined || isNaN(pVal)) {
      return 'Inspect observation alignment against the theoretical reference line; formal test statistics confirm distributional properties.'
    }
    const numP = Number(pVal)
    const pStr = numP < 0.0001 ? 'p < 0.0001' : `p = ${numP.toFixed(4)}`
    if (numP >= alphaVal) {
      return `The Shapiro-Wilk test provides no evidence against normality at α = ${alphaVal} (${pStr}). Interpret this result alongside the Q-Q plot.`
    } else {
      return `The Shapiro-Wilk test indicates evidence against normality at α = ${alphaVal} (${pStr}). Interpret this result alongside the Q-Q plot.`
    }
  }

  return (
    <div className="space-y-3">
      {/* In-Chart Title & Description */}
      <div className="text-center space-y-0.5 pb-1">
        <h4 className="text-sm font-bold text-slate-900 dark:text-slate-100 tracking-tight">
          Normal Q-Q Plot: {variable} (India, n={n})
        </h4>
        <p className="text-xs text-slate-500 dark:text-slate-400 leading-snug">
          Theoretical normal quantiles vs observed sample quantiles ({unit})
        </p>
      </div>

      {/* Legend & Summary Info */}
      <div className="flex flex-wrap items-center justify-between gap-3 text-xs text-slate-500 dark:text-slate-400 px-1">
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-blue-600 inline-block" />
            <span>Observed Sample Quantiles (n = {n})</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-4 h-0.5 border-t-2 border-dashed border-red-500 inline-block" />
            <span className="text-red-600 dark:text-red-400 font-medium">Theoretical Normal Fit Line (OLS)</span>
          </div>
        </div>
        <span className="text-[11px] font-mono text-slate-400 dark:text-slate-500">
          Distribution Diagnostic
        </span>
      </div>

      {/* Chart Canvas */}
      <ResponsiveContainer width="100%" height={height}>
        <ScatterChart margin={{ top: 16, right: 28, left: 16, bottom: 28 }}>
          <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
          <XAxis
            dataKey="x"
            type="number"
            name="Theoretical Quantiles"
            ticks={xTicks}
            domain={[xMinBound, xMaxBound]}
            tickFormatter={(val) => Number(val).toFixed(0)}
            tick={{ fontSize: 10.5, fill: tickColor }}
            tickLine={false}
            axisLine={{ stroke: axisColor }}
          >
            <Label
              value="Theoretical Quantiles (Standard Normal)"
              offset={-14}
              position="insideBottom"
              style={{ textAnchor: 'middle', fontSize: 11, fontWeight: 500, fill: labelColor }}
            />
          </XAxis>
          <YAxis
            dataKey="y"
            type="number"
            name="Sample Quantiles"
            ticks={yTicks}
            domain={[yMinBound, yMaxBound]}
            tickFormatter={(val) => `${Number(val).toFixed(0)}${unit.includes('%') ? '%' : ''}`}
            tick={{ fontSize: 10.5, fill: tickColor }}
            tickLine={false}
            axisLine={false}
            width={48}
          >
            <Label
              value={`Sample Quantiles (${unit})`}
              angle={-90}
              position="insideLeft"
              offset={0}
              style={{ textAnchor: 'middle', fontSize: 11, fontWeight: 500, fill: labelColor }}
            />
          </YAxis>
          <Tooltip content={<QQTooltip unit={unit} />} cursor={{ strokeDasharray: '3 3' }} />
          {/* Fit Line */}
          <Scatter
            name="Normal Fit Line"
            data={linePoints}
            line={{ stroke: '#dc2626', strokeWidth: 1.75, strokeDasharray: '4 4' }}
            shape={() => null}
            legendType="none"
            isAnimationActive={false}
          />
          {/* Observed Sample Quantiles */}
          <Scatter
            name="Sample Quantiles"
            data={qqPoints}
            fill="#3b82f6"
            stroke="#1d4ed8"
            strokeWidth={1.2}
            fillOpacity={0.85}
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
          {rVal !== null && (
            <span className="inline-flex items-center px-2 py-0.5 rounded bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 font-mono text-[11px]">
              <span className="font-sans text-slate-500 mr-1">Fit Line r:</span> {rVal.toFixed(4)}
            </span>
          )}
          {swStat !== null && (
            <span className="inline-flex items-center px-2 py-0.5 rounded bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 font-mono text-[11px]">
              <span className="font-sans text-slate-500 mr-1">Shapiro-Wilk:</span> W = {typeof swStat === 'number' ? swStat.toFixed(4) : swStat} {swP ? `(p = ${typeof swP === 'number' ? swP.toFixed(4) : swP})` : ''}
            </span>
          )}
        </div>
        <span className="text-slate-500 dark:text-slate-400 text-[11px]">
          {getDynamicInterpretation(swP, alpha)}
        </span>
      </div>
    </div>
  )
}
