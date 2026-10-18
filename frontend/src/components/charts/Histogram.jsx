import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, ReferenceLine,
} from 'recharts'
import ChartCard from '../ChartCard.jsx'
import EmptyState from '../EmptyState.jsx'
import { Activity } from 'lucide-react'
import { useTheme } from '../../context/ThemeContext.jsx'

export default function Histogram({
  title, subtitle, data = [], xKey = 'bin', yKey = 'count',
  color = '#3b82f6', mean, median, unit, note, height = 260,
}) {
  const { theme } = useTheme()
  const isDark = theme === 'dark'
  const isEmpty = !data || data.length === 0

  const gridColor = isDark ? '#334155' : '#f1f5f9'
  const tickColor = isDark ? '#94a3b8' : '#64748b'
  const axisColor = isDark ? '#475569' : '#e2e8f0'
  const tooltipBg = isDark ? '#1e293b' : '#ffffff'
  const tooltipBorder = isDark ? '#334155' : '#e2e8f0'
  const tooltipText = isDark ? '#f8fafc' : '#1e293b'

  return (
    <ChartCard title={title} subtitle={subtitle} note={note}>
      {isEmpty ? (
        <EmptyState icon={Activity} title="Histogram data pending"
          message="Connect the backend API to populate this chart." compact />
      ) : (
        <ResponsiveContainer width="100%" height={height}>
          <BarChart data={data} margin={{ top: 8, right: 12, left: -8, bottom: 4 }} barCategoryGap="6%">
            <CartesianGrid strokeDasharray="3 3" stroke={gridColor} vertical={false} />
            <XAxis
              dataKey={xKey}
              tick={{ fontSize: 10, fill: tickColor }}
              tickLine={false}
              axisLine={{ stroke: axisColor }}
            />
            <YAxis
              tick={{ fontSize: 10.5, fill: tickColor }}
              tickLine={false}
              axisLine={false}
              width={32}
              label={{
                value: 'Frequency', angle: -90, position: 'insideLeft',
                style: { fontSize: 9, fill: tickColor },
              }}
            />
            <Tooltip
              formatter={(v) => [v, 'Count']}
              labelFormatter={(l) => `Bin: ${l}${unit ? ' ' + unit : ''}`}
              contentStyle={{
                backgroundColor: tooltipBg,
                color: tooltipText,
                fontSize: 11, borderRadius: 10,
                border: `1px solid ${tooltipBorder}`,
                boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
              }}
            />
            {mean !== undefined && (
              <ReferenceLine x={mean} stroke="#ef4444" strokeDasharray="4 2" strokeWidth={1.5}
                label={{ value: 'Mean', fontSize: 9, fill: '#ef4444', position: 'insideTopRight' }} />
            )}
            {median !== undefined && (
              <ReferenceLine x={median} stroke="#8b5cf6" strokeDasharray="4 2" strokeWidth={1.5}
                label={{ value: 'Median', fontSize: 9, fill: '#a78bfa', position: 'insideTopLeft' }} />
            )}
            <Bar dataKey={yKey} fill={color} fillOpacity={0.7} radius={[3, 3, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      )}
    </ChartCard>
  )
}
