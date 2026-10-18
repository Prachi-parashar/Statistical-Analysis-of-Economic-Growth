import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, Legend, Cell,
} from 'recharts'
import ChartCard from '../ChartCard.jsx'
import EmptyState from '../EmptyState.jsx'
import { BarChart2 } from 'lucide-react'

function ChartTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-white border border-slate-200 rounded-xl shadow-lg p-3 text-xs min-w-[120px]">
      <p className="font-semibold text-slate-700 mb-1 border-b border-slate-100 pb-1">{label}</p>
      {payload.map((p, i) => (
        <div key={i} className="flex items-center gap-2 mt-1">
          <span className="w-2 h-2 rounded-sm flex-shrink-0" style={{ backgroundColor: p.fill }} />
          <span className="text-slate-500">{p.name}:</span>
          <span className="font-semibold text-slate-800">
            {typeof p.value === 'number' ? p.value.toFixed(4) : p.value}
          </span>
        </div>
      ))}
    </div>
  )
}

export default function BarChartCard({
  title, subtitle, data = [], xKey = 'variable',
  bars = [], note, height = 290, colorKey,
}) {
  const isEmpty = !data || data.length === 0

  return (
    <ChartCard title={title} subtitle={subtitle} note={note}>
      {isEmpty ? (
        <EmptyState icon={BarChart2} title="Chart data pending"
          message="Connect the backend API to populate this chart." compact />
      ) : (
        <ResponsiveContainer width="100%" height={height}>
          <BarChart data={data} margin={{ top: 8, right: 16, left: -8, bottom: 32 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
            <XAxis
              dataKey={xKey}
              tick={{ fontSize: 10, fill: '#64748b' }}
              tickLine={false}
              axisLine={{ stroke: '#e2e8f0' }}
              angle={-30}
              textAnchor="end"
              interval={0}
              dy={4}
            />
            <YAxis
              tick={{ fontSize: 10.5, fill: '#64748b' }}
              tickLine={false}
              axisLine={false}
              width={38}
            />
            <Tooltip content={<ChartTooltip />} />
            <Legend wrapperStyle={{ fontSize: 11 }} iconSize={10} iconType="square" />
            {bars.map((b) => (
              <Bar key={b.key} dataKey={b.key} name={b.name || b.key} radius={[3, 3, 0, 0]}>
                {data.map((entry, idx) => (
                  <Cell key={idx} fill={(colorKey ? entry[colorKey] : null) || b.color || '#3b82f6'} />
                ))}
              </Bar>
            ))}
          </BarChart>
        </ResponsiveContainer>
      )}
    </ChartCard>
  )
}
