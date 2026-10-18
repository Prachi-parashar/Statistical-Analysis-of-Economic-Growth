import { useState, useEffect, useCallback } from 'react'
import { useSearchParams } from 'react-router-dom'
import { Activity, RefreshCw } from 'lucide-react'
import PageHeader from '../components/PageHeader.jsx'
import ChartCard from '../components/ChartCard.jsx'
import EmptyState from '../components/EmptyState.jsx'
import DataTable from '../components/DataTable.jsx'
import VarPillSelector from '../components/VarPillSelector.jsx'
import LoadingState from '../components/LoadingState.jsx'
import ErrorState from '../components/ErrorState.jsx'
import ErrorBoundary from '../components/ErrorBoundary.jsx'
import Histogram from '../components/charts/Histogram.jsx'
import BoxPlot from '../components/charts/BoxPlot.jsx'

import { getProbability, getNormalityTests, getDescriptiveStatistics, getDistributionAnalysis } from '../api/statisticsApi'
import { getDataset } from '../api/datasetApi'
import { getFigureUrl } from '../api/reportApi'
import NormalQQPlotChart from '../components/charts/NormalQQPlotChart.jsx'

const VARIABLES = [
  'Gross_Capital_Formation', 'GDP_Growth', 'Inflation', 'FDI_Net_Inflows',
  'Exports', 'Unemployment',
]

const VAR_NAMES = {
  'Gross_Capital_Formation': 'Gross Capital Formation (% of GDP)',
  'GDP_Growth': 'GDP Growth (%)',
  'Inflation': 'Inflation (Annual %)',
  'FDI_Net_Inflows': 'FDI Net Inflows (% of GDP)',
  'Exports': 'Exports of Goods and Services (% of GDP)',
  'Unemployment': 'Unemployment Rate (% of Labor Force)',
}

const VAR_UNITS = {
  'Gross_Capital_Formation': '% of GDP',
  'GDP_Growth': 'Annual %',
  'Inflation': 'Annual %',
  'FDI_Net_Inflows': '% of GDP',
  'Exports': '% of GDP',
  'Unemployment': '% of Labor Force',
}

const NORM_COLS = [
  { key: 'Variable', label: 'Variable' },
  { key: 'Shapiro_Wilk_Stat', label: 'Shapiro-Wilk W', numeric: true },
  { key: 'Shapiro_Wilk_p', label: 'SW p-value', numeric: true },
  { key: 'Anderson_Darling_Stat', label: 'AD Statistic', numeric: true },
  { key: 'AD_Critical_5pct', label: 'AD Crit (5%)', numeric: true },
  { key: 'Skewness', label: 'Skewness', numeric: true },
  { key: 'Kurtosis', label: 'Exc. Kurtosis', numeric: true },
  { key: 'Assessment', label: 'Assessment (α = 0.05)' },
]

const formatPValue = (p) => {
  if (p === undefined || p === null || isNaN(p)) return '—'
  const numP = Number(p)
  if (numP < 0.0001) {
    return 'p < 0.0001'
  }
  return numP.toFixed(4)
}

const formatAssessment = (pVal, swNormal, rec) => {
  if (pVal !== undefined && pVal !== null && !isNaN(pVal)) {
    return Number(pVal) >= 0.05
      ? 'No evidence against normality (α = 0.05)'
      : 'Evidence of non-normality (α = 0.05)'
  }
  if (rec && typeof rec === 'string' && rec.includes('No evidence')) {
    return 'No evidence against normality (α = 0.05)'
  }
  if (swNormal === true || swNormal === 'Yes' || swNormal === 'Normal distribution') {
    return 'No evidence against normality (α = 0.05)'
  }
  return 'Evidence of non-normality (α = 0.05)'
}

export default function ProbabilityDistribution() {
  const [searchParams, setSearchParams] = useSearchParams()
  const initialVar = searchParams.get('var') || 'Gross_Capital_Formation'
  const [selected, setSelected] = useState(initialVar)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  
  const [distributionRows, setDistributionRows] = useState([])
  const [normalityRows, setNormalityRows] = useState([])
  const [statsRows, setStatsRows] = useState([])
  const [datasetRows, setDatasetRows] = useState([])
  const [variablesAnalysis, setVariablesAnalysis] = useState({})
  const [isAvailable, setIsAvailable] = useState(true)

  const fetchData = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const [distRes, normRes, statsRes, dataRes, distAnalysisRes] = await Promise.all([
        getProbability(),
        getNormalityTests().catch(() => ({ available: false })),
        getDescriptiveStatistics().catch(() => ({ available: false })),
        getDataset().catch(() => ({ available: false })),
        getDistributionAnalysis().catch(() => ({ available: false })),
      ])

      if (distRes && distRes.available) {
        setDistributionRows(distRes.data || [])
        setIsAvailable(true)
      } else {
        setDistributionRows([])
        setIsAvailable(false)
      }

      if (normRes && normRes.available) {
        setNormalityRows(normRes.data || [])
      }

      if (statsRes && statsRes.available) {
        setStatsRows(statsRes.data || [])
      }

      if (dataRes && dataRes.available) {
        setDatasetRows(dataRes.data || [])
      }

      if (distAnalysisRes && distAnalysisRes.available) {
        setVariablesAnalysis(distAnalysisRes.variables_analysis || {})
      }
    } catch (err) {
      setError(err.message || 'Failed to fetch probability distribution data')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  const handleSelectVariable = (varKey) => {
    setSelected(varKey)
    setSearchParams({ var: varKey }, { replace: true })
  }

  useEffect(() => {
    const v = searchParams.get('var')
    if (v && VARIABLES.includes(v) && v !== selected) {
      setSelected(v)
    }
  }, [searchParams, selected])

  if (loading) {
    return (
      <div className="p-5 sm:p-6 max-w-7xl mx-auto">
        <PageHeader title="Probability Distribution Analysis" subtitle="Loading distribution tests..." badge="API Data" />
        <LoadingState message="Fetching Shapiro-Wilk and Anderson-Darling test results..." />
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-5 sm:p-6 max-w-7xl mx-auto">
        <PageHeader title="Probability Distribution Analysis" subtitle="Error loading data" badge="Error" />
        <ErrorState message={error} onRetry={fetchData} />
      </div>
    )
  }

  // Sample size and period
  const nObs = datasetRows.length || 35
  const years = datasetRows.map(r => r.Year).filter(Boolean)
  const periodSub = years.length ? `${Math.min(...years)}–${Math.max(...years)}` : '1991–2025'

  // Selected variable details from backend API responses
  const normRow = normalityRows.find(r => r.Variable === selected) || {}
  const distRow = distributionRows.find(r => r.Variable === selected) || {}
  const statsRow = statsRows.find(r => r.Variable === selected) || {}

  // Selected variable normality test metrics directly from backend
  const selSwStat = normRow.Shapiro_Wilk_Stat
    ?? distRow.Shapiro_Wilk_Stat
    ?? variablesAnalysis?.[selected]?.normality_tests?.shapiro_wilk?.statistic
  const selSwP = normRow.Shapiro_Wilk_p
    ?? distRow.Shapiro_Wilk_p
    ?? variablesAnalysis?.[selected]?.normality_tests?.shapiro_wilk?.p_value
  const selAdStat = normRow.Anderson_Darling_Stat
    ?? distRow.Anderson_Darling_Stat
    ?? variablesAnalysis?.[selected]?.normality_tests?.anderson_darling?.statistic
  const selAdCrit = normRow.AD_Critical_5pct
    ?? distRow.AD_Critical_5pct
    ?? variablesAnalysis?.[selected]?.normality_tests?.anderson_darling?.critical_value_5pct
    ?? 0.719
  const selSkew = distRow.Skewness ?? normRow.Skewness ?? statsRow.Skewness
  const selKurt = distRow.Kurtosis ?? normRow.Kurtosis ?? statsRow.Excess_Kurtosis

  const selIsNormal = typeof selSwP === 'number'
    ? selSwP >= 0.05
    : (normRow.SW_Normal_5pct === 'Yes' || distRow.Is_Normal_SW === true || variablesAnalysis?.[selected]?.normality_tests?.is_normal === true)

  const normTestRows = [
    {
      label: 'Shapiro-Wilk W',
      val: typeof selSwStat === 'number' && !isNaN(selSwStat) ? selSwStat.toFixed(4) : (selSwStat ?? 'Not available'),
      note: 'Preferred omnibus test statistic for n < 50',
    },
    {
      label: 'Shapiro-Wilk p-value',
      val: typeof selSwP === 'number' && !isNaN(selSwP)
        ? (selSwP < 0.0001 ? 'p < 0.0001' : `p = ${selSwP.toFixed(4)}`)
        : (selSwP ? String(selSwP) : 'Not available'),
      note: 'H₀: Data is normally distributed (reject if p < 0.05)',
    },
    {
      label: 'Anderson-Darling stat',
      val: typeof selAdStat === 'number' && !isNaN(selAdStat) ? selAdStat.toFixed(4) : (selAdStat ?? 'Not available'),
      note: 'Empirical distribution vs normal CDF (tail-weighted)',
    },
    {
      label: 'AD Critical Value 5%',
      val: typeof selAdCrit === 'number' && !isNaN(selAdCrit) ? selAdCrit.toFixed(3) : (selAdCrit ? String(selAdCrit) : 'Not available'),
      note: `Critical threshold at α = 0.05 (n = ${nObs})`,
    },
    {
      label: 'Skewness',
      val: typeof selSkew === 'number' && !isNaN(selSkew)
        ? (selSkew > 0 ? `+${selSkew.toFixed(4)}` : selSkew.toFixed(4))
        : (selSkew ?? 'Not available'),
      note: distRow.Skew_Type || 'Symmetry of distribution (Fisher-Pearson)',
    },
    {
      label: 'Excess Kurtosis',
      val: typeof selKurt === 'number' && !isNaN(selKurt)
        ? (selKurt > 0 ? `+${selKurt.toFixed(4)}` : selKurt.toFixed(4))
        : (selKurt ?? 'Not available'),
      note: distRow.Kurtosis_Type || 'Tail weight / peakedness (Normal = 0)',
    },
    {
      label: 'Assessment at α = 0.05',
      val: selIsNormal ? 'Fail to reject H₀ · Normally distributed' : 'Reject H₀ · Evidence of non-normality',
      isBadge: true,
      isNormal: selIsNormal,
      note: 'Decision at significance level α = 0.05',
    },
  ]

  // Merge table rows for all 6 variables from backend data
  const combinedNormRows = VARIABLES.map(varKey => {
    const nr = normalityRows.find(r => r.Variable === varKey) || {}
    const dr = distributionRows.find(r => r.Variable === varKey) || {}
    const sr = statsRows.find(r => r.Variable === varKey) || {}

    const swStat = nr.Shapiro_Wilk_Stat ?? dr.Shapiro_Wilk_Stat
    const swP = nr.Shapiro_Wilk_p ?? dr.Shapiro_Wilk_p
    const adStat = nr.Anderson_Darling_Stat ?? dr.Anderson_Darling_Stat
    const adCrit = nr.AD_Critical_5pct ?? dr.AD_Critical_5pct ?? 0.719
    const skew = dr.Skewness ?? nr.Skewness ?? sr.Skewness
    const kurt = dr.Kurtosis ?? nr.Kurtosis ?? sr.Excess_Kurtosis

    const isNormal = typeof swP === 'number'
      ? swP >= 0.05
      : (nr.SW_Normal_5pct === 'Yes' || dr.Is_Normal_SW === true)

    let swPFormatted = 'Not available'
    if (typeof swP === 'number' && !isNaN(swP)) {
      swPFormatted = swP < 0.0001 ? '< 0.0001' : swP.toFixed(4)
    }

    return {
      Variable: (
        <span className="font-semibold text-slate-900 dark:text-slate-100">
          {VAR_NAMES[varKey] || varKey.replace(/_/g, ' ')}
        </span>
      ),
      Shapiro_Wilk_Stat: typeof swStat === 'number' && !isNaN(swStat) ? swStat.toFixed(4) : (swStat ?? 'Not available'),
      Shapiro_Wilk_p: swPFormatted,
      Anderson_Darling_Stat: typeof adStat === 'number' && !isNaN(adStat) ? adStat.toFixed(4) : (adStat ?? 'Not available'),
      AD_Critical_5pct: typeof adCrit === 'number' && !isNaN(adCrit) ? adCrit.toFixed(3) : (adCrit ?? '0.719'),
      Skewness: typeof skew === 'number' && !isNaN(skew) ? (skew > 0 ? `+${skew.toFixed(4)}` : skew.toFixed(4)) : (skew ?? 'Not available'),
      Kurtosis: typeof kurt === 'number' && !isNaN(kurt) ? (kurt > 0 ? `+${kurt.toFixed(4)}` : kurt.toFixed(4)) : (kurt ?? 'Not available'),
      Assessment: (
        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${
          isNormal
            ? 'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800'
            : 'bg-amber-50 text-amber-800 border-amber-200 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-800'
        }`}>
          {isNormal ? '✓ Normal (p ≥ 0.05)' : '⚠ Non-normal (p < 0.05)'}
        </span>
      ),
    }
  })

  // Raw observations for selected variable
  const varValues = datasetRows.map(r => r[selected]).filter(v => v !== null && v !== undefined && !isNaN(v))

  // Boxplot statistics (Tukey 1.5xIQR rule) for selected variable
  let boxPlotStats = null
  if (statsRow.Min !== undefined && statsRow.Q1 !== undefined && statsRow.Q3 !== undefined) {
    const q1 = statsRow.Q1
    const q3 = statsRow.Q3
    const iqr = statsRow.IQR !== undefined ? statsRow.IQR : (q3 - q1)
    const lowerFence = q1 - 1.5 * iqr
    const upperFence = q3 + 1.5 * iqr

    const nonOutliers = varValues.filter(v => v >= lowerFence && v <= upperFence)
    const whiskerLow = nonOutliers.length > 0 ? Math.min(...nonOutliers) : statsRow.Min
    const whiskerHigh = nonOutliers.length > 0 ? Math.max(...nonOutliers) : statsRow.Max
    const outliers = varValues.filter(v => v < lowerFence || v > upperFence)

    boxPlotStats = {
      min: statsRow.Min,
      q1: statsRow.Q1,
      median: statsRow.Median,
      q3: statsRow.Q3,
      max: statsRow.Max,
      mean: statsRow.Mean,
      whiskerLow,
      whiskerHigh,
      outliers,
      lowerFence,
      upperFence,
    }
  }

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
      histData.push({ bin: `${bMin.toFixed(1)}–${bMax.toFixed(1)}`, count })
    }
  }

  return (
    <div className="p-5 sm:p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <PageHeader
          title="Probability Distribution Analysis"
          subtitle="Histogram, KDE, Box Plot, Q-Q Plot, and normality tests for each macroeconomic variable."
          badge="Shapiro-Wilk · Anderson-Darling"
        />
        <button
          onClick={fetchData}
          className="self-start sm:self-auto flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-600 dark:text-slate-300 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700 rounded-lg transition-colors shadow-sm"
          title="Refresh distribution analysis"
        >
          <RefreshCw size={13} className={loading ? 'animate-spin' : ''} />
          Refresh
        </button>
      </div>

      {/* Variable selector */}
      <div className="page-card">
        <div className="card-header border-b border-slate-200 dark:border-slate-800">
          <h3 className="card-title text-sm font-semibold text-slate-800 dark:text-slate-100">Select Variable</h3>
        </div>
        <VarPillSelector items={VARIABLES} selected={selected} onChange={handleSelectVariable} />
      </div>

      {/* Histogram + Box plot */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <ErrorBoundary title="Histogram Chart Error">
          <Histogram
            title={`Histogram — ${VAR_NAMES[selected] || selected.replace(/_/g, '\u00A0')}`}
            subtitle="Observed frequency distribution"
            data={histData}
            mean={statsRow.Mean}
            median={statsRow.Median}
            note="Live API data points"
          />
        </ErrorBoundary>
        <ErrorBoundary title="Box Plot Error">
          <BoxPlot
            title={`Box Plot — ${VAR_NAMES[selected] || selected.replace(/_/g, '\u00A0')}`}
            subtitle="Quartiles, whiskers, and spread"
            stats={boxPlotStats}
            note="Calculated from backend dataset"
          />
        </ErrorBoundary>
      </div>

      {/* Q-Q plot + Normality test */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <ErrorBoundary title="Q-Q Plot Figure Error">
          <ChartCard
            title={`Q-Q Plot Figure — ${VAR_NAMES[selected] || selected.replace(/_/g, '\u00A0')}`}
            subtitle="Theoretical normal quantiles vs observed sample quantiles"
            className="flex flex-col h-full"
          >
            {selected === 'Gross_Capital_Formation' ? (
              <NormalQQPlotChart
                variable="Gross_Capital_Formation"
                unit="% of GDP"
                data={variablesAnalysis?.Gross_Capital_Formation?.qq_plot || []}
                fitData={variablesAnalysis?.Gross_Capital_Formation?.qq_fit || null}
                rawObservations={varValues}
                height={320}
                swStat={selSwStat}
                swP={selSwP}
                alpha={0.05}
              />
            ) : (
              <>
                <div className="flex flex-col items-center justify-center flex-1 w-full min-h-[350px] p-1">
                  <div className="w-full flex items-center justify-center bg-white dark:bg-slate-900/60 rounded-xl p-2 border border-slate-100 dark:border-slate-800 shadow-xs">
                    <img
                      key={selected}
                      src={getFigureUrl(`distributions/qqplot_${selected}.png`)}
                      alt={`Normal Q-Q plot for ${selected}`}
                      className="w-full h-auto max-h-[360px] object-contain rounded-lg transition-opacity duration-150"
                      onError={(e) => {
                        if (!e.target.dataset.triedFallback) {
                          e.target.dataset.triedFallback = 'true'
                          e.target.src = getFigureUrl(`probability_distributions/qqplot_${selected}.png`)
                        } else {
                          e.target.style.display = 'none'
                          if (e.target.parentElement?.nextElementSibling) {
                            e.target.parentElement.nextElementSibling.style.display = 'flex'
                          }
                        }
                      }}
                    />
                  </div>
                  <div style={{ display: 'none' }} className="w-full">
                    <EmptyState icon={Activity} title="Analysis result not available." message="Q-Q plot figure not found on server." compact />
                  </div>
                </div>
                <div className="pt-2 text-center">
                  <p className="text-[11px] text-slate-500 dark:text-slate-400">
                    Observations following the theoretical diagonal line indicate consistency with normal distribution.
                  </p>
                </div>
              </>
            )}
          </ChartCard>
        </ErrorBoundary>

        <ErrorBoundary title="Normality Tests Table Error">
          <div className="page-card flex flex-col h-full">
            <div className="card-header border-b border-slate-200 dark:border-slate-800">
              <div>
                <h3 className="card-title text-base font-semibold text-slate-900 dark:text-slate-100">
                  Normality Tests — <span className="text-primary-600 dark:text-primary-400">{VAR_NAMES[selected] || selected.replace(/_/g, '\u00A0')}</span>
                </h3>
                <p className="card-subtitle text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                  India{periodSub ? `, ${periodSub}` : ''} · n = {nObs} · Significance level α = 0.05
                </p>
              </div>
            </div>
            {!isAvailable ? (
              <div className="p-5 flex-1 flex items-center justify-center">
                <EmptyState title="Analysis result not available." message="Normality tests not returned by backend API." onRefresh={fetchData} />
              </div>
            ) : (
              <div className="divide-y divide-slate-100 dark:divide-slate-800 flex-1">
                {normTestRows.map(({ label, val, isBadge, isNormal, note }) => {
                  const isAvailableVal = val !== 'Not available' && val !== '—' && val !== null && val !== undefined
                  return (
                    <div
                      key={label}
                      className="flex items-center justify-between px-5 py-3 hover:bg-slate-50/80 dark:hover:bg-slate-800/40 transition-colors"
                    >
                      <div className="min-w-0 pr-3">
                        <p className="text-sm font-medium text-slate-800 dark:text-slate-200">{label}</p>
                        <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5 leading-relaxed">{note}</p>
                      </div>
                      <div className="flex-shrink-0 text-right ml-2">
                        {isBadge ? (
                          <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold border ${
                            isNormal
                              ? 'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800'
                              : 'bg-amber-50 text-amber-800 border-amber-200 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-800'
                          }`}>
                            {val}
                          </span>
                        ) : !isAvailableVal ? (
                          <span className="text-xs text-slate-400 dark:text-slate-500 italic">Not available</span>
                        ) : (
                          <span className="text-sm font-mono font-bold text-slate-900 dark:text-slate-100 tabular-nums">
                            {val}
                          </span>
                        )}
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        </ErrorBoundary>
      </div>

      {/* Full normality table */}
      <ErrorBoundary title="All Variables Table Error">
        <div className="page-card">
          <div className="card-header border-b border-slate-200 dark:border-slate-800">
            <div>
              <h3 className="card-title text-base font-semibold text-slate-900 dark:text-slate-100">Normality Test Results — All Variables</h3>
              <p className="card-subtitle text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                Shapiro-Wilk test, Anderson-Darling test, skewness, and excess kurtosis across all macroeconomic series (India, n = {nObs}, α = 0.05)
              </p>
            </div>
          </div>
          <div className="p-5">
            {!isAvailable || combinedNormRows.length === 0 ? (
              <EmptyState title="Analysis result not available." message="Normality test table not available." onRefresh={fetchData} />
            ) : (
              <DataTable columns={NORM_COLS} rows={combinedNormRows} />
            )}
          </div>
        </div>
      </ErrorBoundary>
    </div>
  )
}
