import { useState, useEffect, useCallback } from 'react'
import { Database, ExternalLink, RefreshCw } from 'lucide-react'
import PageHeader from '../components/PageHeader.jsx'
import DataTable from '../components/DataTable.jsx'
import LoadingState from '../components/LoadingState.jsx'
import ErrorState from '../components/ErrorState.jsx'
import EmptyState from '../components/EmptyState.jsx'
import { getDataset } from '../api/datasetApi'

const DATA_COLS = [
  { key: 'Year', label: 'Year' },
  { key: 'GDP_Growth', label: 'GDP Growth (%)', numeric: true },
  { key: 'Inflation', label: 'Inflation (%)', numeric: true },
  { key: 'FDI_Net_Inflows', label: 'FDI (% GDP)', numeric: true },
  { key: 'Exports', label: 'Exports (% GDP)', numeric: true },
  { key: 'Gross_Capital_Formation', label: 'GCF (% GDP)', numeric: true },
  { key: 'Unemployment', label: 'Unemp. (%)', numeric: true },
]

export default function Dataset() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  
  const [datasetRows, setDatasetRows] = useState([])
  const [datasetAvailable, setDatasetAvailable] = useState(true)

  const fetchData = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const dataRes = await getDataset()

      if (dataRes && dataRes.available) {
        setDatasetRows(dataRes.data || [])
        setDatasetAvailable(true)
      } else {
        setDatasetRows([])
        setDatasetAvailable(false)
      }
    } catch (err) {
      setError(err.message || 'Failed to fetch dataset')
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
        <PageHeader title="Dataset" subtitle="Loading cleaned dataset from backend..." badge="API Data" />
        <LoadingState message="Fetching raw observations..." />
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-5 sm:p-6 max-w-7xl mx-auto">
        <PageHeader title="Dataset" subtitle="Error loading dataset" badge="Error" />
        <ErrorState message={error} onRetry={fetchData} />
      </div>
    )
  }

  const recordCount = datasetRows.length
  const firstYear = datasetRows[0]?.Year
  const lastYear = datasetRows[recordCount - 1]?.Year
  const periodText = recordCount && firstYear && lastYear ? `${firstYear}–${lastYear} (${recordCount} annual observations)` : 'Loading...'

  const sourceMeta = [
    { label: 'Source', value: 'World Bank World Development Indicators (WDI)' },
    { label: 'Country', value: 'India (ISO: IND)' },
    { label: 'Period', value: periodText },
    { label: 'Access Method', value: 'World Bank Open Data API v2' },
    { label: 'Missing Values', value: '0 (in cleaned dataset)' },
    { label: 'Duplicates', value: '0' },
  ]

  return (
    <div className="p-5 sm:p-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between mb-2">
        <PageHeader
          title="Dataset"
          subtitle="Data source and cleaned dataset structure."
          badge={`n = ${recordCount}`}
        />
        <button
          onClick={fetchData}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-600 dark:text-slate-300 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700 rounded-lg transition-colors shadow-sm"
          title="Refresh dataset"
        >
          <RefreshCw size={13} className={loading ? 'animate-spin' : ''} />
          Refresh
        </button>
      </div>

      {/* ── Source overview ── */}
      <div className="page-card mb-5">
        <div className="card-header">
          <div>
            <h3 className="card-title">Data Source</h3>
            <p className="card-subtitle">World Bank World Development Indicators</p>
          </div>
          <Database size={16} className="text-slate-400 dark:text-slate-500" aria-hidden="true" />
        </div>
        <div className="p-5">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 mb-4">
            {sourceMeta.map(({ label, value }) => (
              <div key={label} className="bg-slate-50 dark:bg-slate-700/40 rounded-xl p-3 border border-slate-100 dark:border-slate-700/50">
                <p className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-1">
                  {label}
                </p>
                <p className="text-sm font-medium text-slate-800 dark:text-slate-100">{value}</p>
              </div>
            ))}
          </div>
          <div className="flex items-center gap-2">
            <ExternalLink size={13} className="text-primary-600 dark:text-primary-400" aria-hidden="true" />
            <a
              href="https://databank.worldbank.org/source/world-development-indicators"
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs text-primary-600 dark:text-primary-400 hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-400 rounded"
            >
              World Bank DataBank — World Development Indicators
            </a>
          </div>
        </div>
      </div>

      {/* ── Live data table ── */}
      <div className="page-card">
        <div className="card-header">
          <div>
            <h3 className="card-title">Cleaned Dataset</h3>
            <p className="card-subtitle">
              Annual observations · India · Live API output from{' '}
              <span className="font-mono text-xs">/api/dataset</span>
            </p>
          </div>
        </div>
        <div className="p-5">
          {!datasetAvailable || datasetRows.length === 0 ? (
            <EmptyState
              icon={Database}
              title="Analysis result not available."
              message="No dataset records returned from backend server."
              onRefresh={fetchData}
            />
          ) : (
            <DataTable columns={DATA_COLS} rows={datasetRows} />
          )}
        </div>
      </div>
    </div>
  )
}
