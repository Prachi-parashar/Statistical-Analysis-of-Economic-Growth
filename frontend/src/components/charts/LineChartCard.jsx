import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis,
  CartesianGrid, Tooltip, Legend, ReferenceLine,
} from 'recharts'
import ChartCard from '../ChartCard.jsx'
import EmptyState from '../EmptyState.jsx'
import { TrendingUp } from 'lucide-react'
import { useTheme } from '../../context/ThemeContext.jsx'

function ChartTooltip({ active, payload, label, unit }) {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl shadow-lg p-3 text-xs min-w-[120px]">
      <p className="font-semibold text-slate-700 dark:text-slate-200 mb-1.5 border-b border-slate-100 dark:border-slate-700 pb-1">{label}</p>
      {payload.map((p, i) => (
        <div key={i} className="flex items-center gap-2 mt-1">
          <span
            className="w-2 h-2 rounded-full flex-shrink-0"
            style={{ backgroundColor: p.color }}
          />
          <span className="text-slate-500 dark:text-slate-400">{p.name}:</span>
          <span className="font-semibold text-slate-800 dark:text-slate-100">
            {typeof p.value === 'number' ? p.value.toFixed(2) : p.value}
            {unit && <span className="text-slate-400 dark:text-slate-500 font-normal ml-0.5">{unit}</span>}
          </span>
        </div>
      ))}
    </div>
  )
}

export default function LineChartCard({
  title, subtitle, data = [], xKey = 'year',
  lines = [], unit, note, referenceY, height = 290,
}) {
  const { theme } = useTheme()
  const isDark = theme === 'dark'
  const isEmpty = !data || data.length === 0

  const gridColor = isDark ? '#334155' : '#f1f5f9'
  const tickColor = isDark ? '#94a3b8' : '#64748b'
  const axisColor = isDark ? '#475569' : '#e2e8f0'

  return (
    <ChartCard title={title} subtitle={subtitle} note={note}>
      {isEmpty ? (
        <EmptyState icon={TrendingUp} title="Chart data pending"
          message="Connect the backend API to populate this chart." compact />
      ) : (
        <ResponsiveContainer width="100%" height={height}>
          <LineChart data={data} margin={{ top: 8, right: 16, left: -8, bottom: 4 }}>
            <CartesianGrid strokeDasharray="3 3" stroke={gridColor} vertical={false} />
            <XAxis
              dataKey={xKey}
              tick={{ fontSize: 10.5, fill: tickColor }}
              tickLine={false}
              axisLine={{ stroke: axisColor }}
              dy={4}
            />
            <YAxis
              tick={{ fontSize: 10.5, fill: tickColor }}
              tickLine={false}
              axisLine={false}
              width={38}
            />
            <Tooltip content={<ChartTooltip unit={unit} />} />
            <Legend
              wrapperStyle={{ fontSize: 11, paddingTop: 10, color: tickColor }}
              iconSize={10}
              iconType="circle"
            />
            {referenceY !== undefined && (
              <ReferenceLine
                y={referenceY}
                stroke={isDark ? '#64748b' : '#94a3b8'}
                strokeDasharray="5 3"
                strokeWidth={1.2}
                label={{ value: 'Mean', position: 'insideTopLeft', fontSize: 9, fill: isDark ? '#94a3b8' : '#94a3b8' }}
              />
            )}
            {lines.map((l) => (
              <Line
                key={l.key}
                type="monotone"
                dataKey={l.key}
                name={l.name || l.key}
                stroke={l.color || '#2563eb'}
                strokeWidth={2}
                dot={{ r: 3, fill: l.color || '#2563eb', strokeWidth: 0 }}
                activeDot={{ r: 5, strokeWidth: 2, stroke: isDark ? '#1e293b' : '#fff' }}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      )}
    </ChartCard>
  )
}
