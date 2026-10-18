import { useState, useEffect, useCallback } from 'react'
import {
  Database, Hash, Calendar, Globe, TrendingUp, GitBranch,
  BarChart2, Activity, RefreshCw,
} from 'lucide-react'
import { Link } from 'react-router-dom'
import PageHeader from '../components/PageHeader.jsx'
import StatCard from '../components/StatCard.jsx'
import ChartCard from '../components/ChartCard.jsx'
import EmptyState from '../components/EmptyState.jsx'
import LoadingState from '../components/LoadingState.jsx'
import ErrorState from '../components/ErrorState.jsx'
import LineChartCard from '../components/charts/LineChartCard.jsx'
import Heatmap from '../components/charts/Heatmap.jsx'

import { getProjectInfo } from '../api/projectApi'
import { getDataset } from '../api/datasetApi'
import { getMultipleRegression } from '../api/regressionApi'
import { getCorrelationAnalysis } from '../api/correlationApi'
import { getCurrentAnalysis } from '../api/reportApi'

const VARIABLES = [
  { name: 'GDP_Growth', label: 'GDP Growth', unit: 'Annual %', role: 'Dependent', color: '#2563eb' },
  { name: 'Inflation', label: 'Inflation (CPI)', unit: 'Annual %', role: 'Independent', color: '#e84855' },
  { name: 'FDI_Net_Inflows', label: 'FDI Net Inflows', unit: '% of GDP', role: 'Independent', color: '#f4a261' },
  { name: 'Exports', label: 'Exports of G&S', unit: '% of GDP', role: 'Independent', color: '#2a9d8f' },
  { name: 'Gross_Capital_Formation', label: 'Gross Capital Formation', unit: '% of GDP', role: 'Independent', color: '#6a4c93' },
  { name: 'Unemployment', label: 'Unemployment Rate', unit: '% labour force', role: 'Independent', color: '#457b9d' },
]

const PHASES = [
  { label: 'Descriptive Statistics', to: '/descriptive-statistics', icon: BarChart2, color: 'text-primary-500' },
  { label: 'Probability Distribution', to: '/probability', icon: Activity, color: 'text-emerald-500' },
  { label: 'Correlation Analysis', to: '/correlation', icon: GitBranch, color: 'text-violet-500' },
  { label: 'Regression Analysis', to: '/regression', icon: TrendingUp, color: 'text-amber-500' },
]

export default function Dashboard() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  
  const [project, setProject] = useState(null)
  const [currentAnalysis, setCurrentAnalysis] = useState(null)
  const [datasetData, setDatasetData] = useState([])
  const [regressionData, setRegressionData] = useState([])
  const [correlationData, setCorrelationData] = useState(null)

  const fetchData = useCallback(async (isSilent = false) => {
    if (!isSilent) setLoading(true)
    setError(null)
    try {
      const [projRes, dataRes, regRes, corrRes, currAnalysisRes] = await Promise.all([
        getProjectInfo().catch(() => null),
        getDataset().catch(() => ({ available: false })),
        getMultipleRegression().catch(() => ({ available: false })),
        getCorrelationAnalysis().catch(() => ({ available: false })),
        getCurrentAnalysis().catch(() => null),
      ])

      if (projRes) setProject(projRes)
      if (currAnalysisRes && currAnalysisRes.success) {
        setCurrentAnalysis(currAnalysisRes)
      }
      if (dataRes && dataRes.available) {
        setDatasetData(dataRes.data || [])
      } else {
        setDatasetData([])
      }

      if (regRes && regRes.available) {
        setRegressionData(regRes.data || [])
      }

      if (corrRes && corrRes.available && corrRes.pearson_matrix) {
        const vars = corrRes.variables || ['GDP_Growth', 'Inflation', 'FDI_Net_Inflows', 'Exports', 'Gross_Capital_Formation', 'Unemployment']
        const matrixArr = vars.map(v1 => vars.map(v2 => {
          const val = corrRes.pearson_matrix[v1]?.[v2]
          return typeof val === 'number' ? val : (v1 === v2 ? 1.0 : null)
        }))
        setCorrelationData({ labels: vars, matrix: matrixArr })
      } else {
        setCorrelationData(null)
      }
    } catch (err) {
      setError(err.message || 'Failed to load dashboard data')
    } finally {
      if (!isSilent) setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  if (loading && datasetData.length === 0) {
    return (
      <div className="p-5 sm:p-6 max-w-7xl mx-auto">
        <PageHeader title="Dashboard" subtitle="Loading project statistics and dataset..." badge="Overview" />
        <LoadingState message="Fetching data from FastAPI backend..." />
      </div>
    )
  }

  if (error && datasetData.length === 0) {
    return (
      <div className="p-5 sm:p-6 max-w-7xl mx-auto">
        <PageHeader title="Dashboard" subtitle="Error loading data" badge="Overview" />
        <ErrorState message={error} onRetry={() => fetchData(false)} />
      </div>
    )
  }

  // Calculate year range
  const years = datasetData.map(d => d.Year).filter(Boolean)
  const minYear = years.length ? Math.min(...years) : (currentAnalysis?.start_year || 1991)
  const maxYear = years.length ? Math.max(...years) : (currentAnalysis?.end_year || 2025)
  const periodStr = minYear && maxYear ? `${minYear}–${maxYear}` : '1991–2025'
  const dataSource = currentAnalysis?.source || 'World Bank WDI'
  const countryName = currentAnalysis?.country || 'India'
  const analysisId = currentAnalysis?.analysis_id || null

  // Format line chart data
  const trendChartData = datasetData.map(d => ({
    year: d.Year,
    gdp: d.GDP_Growth,
  }))

  return (
    <div className="p-5 sm:p-6 max-w-7xl mx-auto">
      {/* ── Top Header & Actions ── */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-6 gap-3">
        <PageHeader
          title={project?.title || "Dashboard"}
          subtitle="Project overview and live statistical analysis hub."
          badge="World Bank WDI"
        />
        <button
          onClick={() => fetchData(false)}
          className="flex items-center gap-1.5 px-3 py-2 text-xs font-medium text-slate-600 dark:text-slate-300 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700 rounded-lg transition-colors shadow-sm"
          title="Refresh dashboard data"
        >
          <RefreshCw size={13} className={loading ? 'animate-spin' : ''} />
          Refresh
        </button>
      </div>

      {/* ── Key facts ── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard
          label="Observations"
          value={datasetData.length || currentAnalysis?.observation_count || "35"}
          description={`Annual · ${periodStr}`}
          icon={Hash}
          color="blue"
          tooltip="Total number of annual data points"
        />
        <StatCard
          label="Variables"
          value="6"
          description="1 dependent · 5 independent"
          icon={Database}
          color="violet"
          tooltip="GDP_Growth (dependent) + 5 macroeconomic predictors"
        />
        <StatCard
          label="Year Range"
          value={periodStr}
          description="Post-liberalisation era"
          icon={Calendar}
          color="green"
          tooltip="Data collected from World Bank WDI API"
        />
        <StatCard
          label="Data Source"
          value="World Bank"
          description="WDI API · India (IND)"
          icon={Globe}
          color="amber"
          tooltip="World Bank World Development Indicators — real secondary data"
        />
      </div>

      {/* ── Charts row ── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 mb-5">
        <LineChartCard
          title="GDP Growth Trend"
          subtitle={`Annual % change · India${periodStr !== '—' ? `, ${periodStr}` : ''}`}
          data={trendChartData}
          xKey="year"
          lines={[{ key: 'gdp', name: 'GDP Growth (%)', color: '#2563eb' }]}
          unit="%"
          note="Loaded directly from FastAPI /api/dataset endpoint"
        />
        {correlationData ? (
          <Heatmap
            title="Pearson Correlation Heatmap"
            subtitle="Pearson matrix — all variables"
            data={correlationData}
            type="Pearson"
            note="Loaded from FastAPI /api/correlation/pearson"
          />
        ) : (
          <ChartCard title="Correlation Heatmap" subtitle="Pearson / Spearman — all variables">
            <EmptyState
              icon={GitBranch}
              title="Analysis result not available."
              message="Correlation matrix will render when data is returned by the API."
              compact
              onRefresh={() => fetchData(false)}
            />
          </ChartCard>
        )}
      </div>

      {/* ── Analysis phases quick-nav ── */}
      <div className="page-card mb-5">
        <div className="card-header">
          <div>
            <h3 className="card-title">Analysis Phases</h3>
            <p className="card-subtitle">Navigate to each statistical phase</p>
          </div>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-4 divide-x divide-slate-100 dark:divide-slate-700/70">
          {PHASES.map(({ label, to, icon: Icon, color }) => (
            <Link
              key={to}
              to={to}
              className="flex flex-col items-center gap-2.5 py-5 px-3 hover:bg-slate-50 dark:hover:bg-slate-700/40 transition-colors text-center group"
            >
              <div className="w-10 h-10 rounded-xl bg-slate-100 dark:bg-slate-700/70 group-hover:bg-primary-50 dark:group-hover:bg-primary-950/60 flex items-center justify-center transition-colors">
                <Icon size={18} className={`${color} group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors`} />
              </div>
              <span className="text-xs font-semibold text-slate-600 dark:text-slate-300 group-hover:text-primary-700 dark:group-hover:text-primary-300 leading-tight transition-colors">
                {label}
              </span>
            </Link>
          ))}
        </div>
      </div>

      {/* ── Variables list ── */}
      <div className="page-card mb-5">
        <div className="card-header">
          <div>
            <h3 className="card-title">Key Variables</h3>
            <p className="card-subtitle">All six variables analysed in this project</p>
          </div>
        </div>
        <div className="divide-y divide-slate-100 dark:divide-slate-700/70">
          {VARIABLES.map((v) => (
            <div
              key={v.name}
              className="flex items-center justify-between px-5 py-3 hover:bg-slate-50 dark:hover:bg-slate-700/40 transition-colors"
            >
              <div className="flex items-center gap-3 min-w-0">
                <span
                  className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                  style={{ backgroundColor: v.color }}
                  aria-hidden="true"
                />
                <div className="min-w-0">
                  <p className="text-sm font-medium text-slate-700 dark:text-slate-200 truncate">{v.label}</p>
                  <p className="text-xs text-slate-400 dark:text-slate-500 font-mono">{v.name}</p>
                </div>
              </div>
              <div className="flex items-center gap-3 flex-shrink-0 ml-3">
                <span className="text-xs text-slate-500 dark:text-slate-400 hidden sm:block">{v.unit}</span>
                <span className={`text-xs px-2 py-0.5 rounded-full font-semibold ${
                  v.role === 'Dependent'
                    ? 'bg-primary-100 text-primary-700 dark:bg-primary-950/80 dark:text-primary-300'
                    : 'bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300'
                }`}>
                  {v.role}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      <p className="text-xs text-slate-400 dark:text-slate-500 text-center mt-6 pb-2">
        Statistical Analysis of Economic Growth and Its Determinants in India ·
        World Bank WDI{periodStr !== '—' ? ` · ${periodStr}` : ''}
      </p>
    </div>
  )
}
