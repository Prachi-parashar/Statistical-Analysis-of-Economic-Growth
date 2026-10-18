import { useState, useEffect, useCallback } from 'react'
import { HelpCircle, RefreshCw } from 'lucide-react'
import PageHeader from '../components/PageHeader.jsx'
import DataTable from '../components/DataTable.jsx'
import VarPillSelector from '../components/VarPillSelector.jsx'
import LoadingState from '../components/LoadingState.jsx'
import ErrorState from '../components/ErrorState.jsx'
import EmptyState from '../components/EmptyState.jsx'
import Histogram from '../components/charts/Histogram.jsx'
import { getDescriptiveStatistics } from '../api/statisticsApi'
import { getDataset } from '../api/datasetApi'

const VARIABLES = [
  'GDP_Growth', 'Inflation', 'FDI_Net_Inflows',
  'Exports', 'Gross_Capital_Formation', 'Unemployment',
]

const STAT_FIELDS = [
  { key: 'Mean', label: 'Mean', description: 'Arithmetic average (μ)', group: 'central' },
  { key: 'Median', label: 'Median (Q2)', description: '50th percentile — middle value', group: 'central' },
  { key: 'Mode', label: 'Mode', description: 'Most frequently observed value', group: 'central' },
  { key: 'Variance', label: 'Variance (sample, s²)', description: 'Average squared deviation from mean (ddof=1)', group: 'spread' },
  { key: 'Std_Dev', label: 'Std Deviation (sample)', description: 'Square root of sample variance (ddof=1)', group: 'spread' },
  { key: 'Min', label: 'Minimum', description: 'Smallest observed value', group: 'spread' },
  { key: 'Max', label: 'Maximum', description: 'Largest observed value', group: 'spread' },
  { key: 'Range', label: 'Range', description: 'Max − Min', group: 'spread' },
  { key: 'Q1', label: 'Q1 (25th pct)', description: 'First quartile', group: 'quartile' },
  { key: 'Q3', label: 'Q3 (75th pct)', description: 'Third quartile', group: 'quartile' },
  { key: 'IQR', label: 'IQR', description: 'Interquartile range: Q3 − Q1', group: 'quartile' },
  { key: 'Skewness', label: 'Skewness', description: 'Fisher–Pearson: 0 = symmetric', group: 'shape' },
  { key: 'Excess_Kurtosis', label: 'Excess Kurtosis', description: 'Fisher convention: normal = 0', group: 'shape' },
]

const GROUP_LABELS = {
  central: { label: 'Central Tendency', color: 'bg-primary-50 text-primary-600' },
  spread: { label: 'Dispersion', color: 'bg-emerald-50 text-emerald-700' },
  quartile: { label: 'Quartiles', color: 'bg-violet-50 text-violet-700' },
  shape: { label: 'Shape', color: 'bg-amber-50 text-amber-700' },
}

const TABLE_COLS = [
  { key: 'Variable', label: 'Variable' },
  { key: 'Mean', label: 'Mean', numeric: true },
  { key: 'Median', label: 'Median', numeric: true },
  { key: 'Mode', label: 'Mode' },
  { key: 'Std_Dev', label: 'Std Dev', numeric: true },
  { key: 'Min', label: 'Min', numeric: true },
  { key: 'Max', label: 'Max', numeric: true },
  { key: 'Skewness', label: 'Skewness', numeric: true },
  { key: 'Excess_Kurtosis', label: 'Exc. Kurtosis', numeric: true },
]

export default function DescriptiveStatistics() {
  const [selected, setSelected] = useState('GDP_Growth')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  
  const [statsData, setStatsData] = useState([])
  const [datasetRows, setDatasetRows] = useState([])
  const [isAvailable, setIsAvailable] = useState(true)

  const fetchData = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const [statsRes, dataRes] = await Promise.all([
        getDescriptiveStatistics(),
        getDataset().catch(() => ({ available: false })),
      ])

      if (statsRes && statsRes.available) {
        setStatsData(statsRes.data || [])
        setIsAvailable(true)
      } else {
        setStatsData([])
        setIsAvailable(false)
      }

      if (dataRes && dataRes.available) {
        setDatasetRows(dataRes.data || [])
      }
    } catch (err) {
      setError(err.message || 'Failed to load descriptive statistics')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  if (loading) {
    return (
      <div className="p-5 sm:p-6 max-w-7xl mx-auto">
        <PageHeader title="Descriptive Statistics" subtitle="Loading statistics from API..." badge="API Data" />
        <LoadingState message="Fetching central tendency and dispersion metrics..." />
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-5 sm:p-6 max-w-7xl mx-auto">
        <PageHeader title="Descriptive Statistics" subtitle="Error loading data" badge="Error" />
        <ErrorState message={error} onRetry={fetchData} />
      </div>
    )
  }

  // Find row for selected variable
  const selectedRow = statsData.find(r => r.Variable === selected) || {}

  // Generate histogram bins for selected variable from raw dataset observations
  const varValues = datasetRows.map(r => r[selected]).filter(v => v !== null && v !== undefined && !isNaN(v))
  let histData = []
  if (varValues.length > 0) {
    const minVal = Math.min(...varValues)
    const maxVal = Math.max(...varValues)
    const numBins = 6
    const binWidth = (maxVal - minVal) / numBins || 1
    
    for (let i = 0; i < numBins; i++) {
      const bMin = minVal + i * binWidth
      const bMax = minVal + (i + 1) * binWidth
      const count = varValues.filter(v => i === numBins - 1 ? (v >= bMin && v <= bMax) : (v >= bMin && v < bMax)).length
      histData.push({
        bin: `${bMin.toFixed(1)}–${bMax.toFixed(1)}`,
        count,
      })
    }
  }

  const years = datasetRows.map(r => r.Year).filter(Boolean)
  const periodSub = years.length ? `${Math.min(...years)}–${Math.max(...years)}` : ''

  return (
    <div className="p-5 sm:p-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between mb-2">
        <PageHeader
          title="Descriptive Statistics"
          subtitle="Central tendency, dispersion, quartiles, and distributional shape for each variable."
          badge="All Variables"
        />
        <button
          onClick={fetchData}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-600 dark:text-slate-300 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700 rounded-lg transition-colors shadow-sm"
          title="Refresh statistics"
        >
          <RefreshCw size={13} className={loading ? 'animate-spin' : ''} />
          Refresh
        </button>
      </div>

      {/* Variable selector */}
      <div className="page-card mb-5">
        <div className="card-header">
          <h3 className="card-title">Select Variable</h3>
        </div>
        <VarPillSelector items={VARIABLES} selected={selected} onChange={setSelected} />
      </div>

      {/* Stats detail + chart */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 mb-5">
        {/* Stat rows */}
        <div className="page-card">
          <div className="card-header">
            <div>
              <h3 className="card-title">
                Statistics — <span className="text-primary-600">{selected.replace(/_/g, '\u00A0')}</span>
              </h3>
              <p className="card-subtitle">
                India{periodSub ? `, ${periodSub}` : ''} · n = {datasetRows.length}
              </p>
            </div>
            <HelpCircle
              size={15}
              className="text-slate-300"
              title="ddof=1 used for sample variance/std dev"
              aria-label="Note: sample statistics use Bessel's correction (ddof=1)"
            />
          </div>

          {!isAvailable ? (
            <div className="p-5">
              <EmptyState title="Analysis result not available." message="Descriptive statistics file not returned by backend API." onRefresh={fetchData} />
            </div>
          ) : (
            Object.entries(GROUP_LABELS).map(([groupKey, { label, color }]) => {
              const fields = STAT_FIELDS.filter((r) => r.group === groupKey)
              return (
                <div key={groupKey}>
                  <div className="px-5 py-1.5 bg-slate-50 border-y border-slate-100">
                    <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${color}`}>
                      {label}
                    </span>
                  </div>
                  {fields.map(({ key, label: rowLabel, description }) => {
                    const rawVal = selectedRow[key]
                    let formattedVal = '—'
                    if (rawVal !== undefined && rawVal !== null) {
                      formattedVal = typeof rawVal === 'number' ? rawVal.toFixed(4).replace(/\.?0+$/, '') : rawVal
                    }
                    return (
                      <div
                        key={key}
                        className="flex items-center justify-between px-5 py-2.5 hover:bg-slate-50/80 transition-colors border-b border-slate-100 last:border-0"
                      >
                        <div className="min-w-0 mr-4">
                          <p className="text-sm font-medium text-slate-700">{rowLabel}</p>
                          <p className="text-xs text-slate-400">{description}</p>
                        </div>
                        <span className="text-sm font-mono font-semibold text-slate-800 flex-shrink-0">
                          {formattedVal}
                        </span>
                      </div>
                    )
                  })}
                </div>
              )
            })
          )}
        </div>

        {/* Distribution chart */}
        <Histogram
          title={`Frequency Bins — ${selected.replace(/_/g, '\u00A0')}`}
          subtitle="Observed sample distribution"
          data={histData}
          mean={selectedRow.Mean}
          median={selectedRow.Median}
          note="Live calculation from backend observations"
        />
      </div>

      {/* Comparative table */}
      <div className="page-card">
        <div className="card-header">
          <div>
            <h3 className="card-title">Comparative Table — All Variables</h3>
            <p className="card-subtitle">Descriptive summary loaded from backend API</p>
          </div>
        </div>
        <div className="p-5">
          {!isAvailable || statsData.length === 0 ? (
            <EmptyState title="Analysis result not available." message="Descriptive statistics matrix not available." onRefresh={fetchData} />
          ) : (
            <DataTable columns={TABLE_COLS} rows={statsData} />
          )}
        </div>
      </div>
    </div>
  )
}
