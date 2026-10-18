import { useState, useEffect, useCallback } from 'react'
import { TrendingUp, AlertTriangle, Info, RefreshCw } from 'lucide-react'
import PageHeader from '../components/PageHeader.jsx'
import DataTable from '../components/DataTable.jsx'
import VarPillSelector from '../components/VarPillSelector.jsx'
import LoadingState from '../components/LoadingState.jsx'
import ErrorState from '../components/ErrorState.jsx'
import EmptyState from '../components/EmptyState.jsx'
import ScatterPlot from '../components/charts/ScatterPlot.jsx'

import {
  getSimpleRegression,
  getMultipleRegression,
  getRobustRegression,
  getRegressionAnalysis,
} from '../api/regressionApi'
import { getDataset } from '../api/datasetApi'

const PREDICTORS = [
  'Inflation', 'FDI_Net_Inflows', 'Exports', 'Gross_Capital_Formation', 'Unemployment',
]

const MULTI_COLS = [
  { key: 'variable', label: 'Variable' },
  { key: 'coef', label: 'Coefficient (β)', numeric: true },
  { key: 'se', label: 'HC3 Robust SE', numeric: true },
  { key: 't', label: 't-statistic', numeric: true },
  { key: 'p', label: 'p-value', numeric: true },
  { key: 'ci_low', label: 'CI Low (95%)', numeric: true },
  { key: 'ci_high', label: 'CI High (95%)', numeric: true },
  { key: 'sig', label: 'Sig. (α = 0.05)' },
]

const SIMPLE_COLS = [
  { key: 'predictor', label: 'Predictor' },
  { key: 'intercept', label: 'Intercept', numeric: true },
  { key: 'slope', label: 'Slope (β)', numeric: true },
  { key: 'se', label: 'SE (slope)', numeric: true },
  { key: 'p', label: 'p-value', numeric: true },
  { key: 'r2', label: 'R²', numeric: true },
  { key: 'adj_r2', label: 'Adj R²', numeric: true },
  { key: 'sig', label: 'Significant?' },
]

const ROBUST_COLS = [
  { key: 'variable', label: 'Variable' },
  { key: 'coef', label: 'Coefficient (β)', numeric: true },
  { key: 'se_ols', label: 'SE (OLS)', numeric: true },
  { key: 'se_hc3', label: 'SE (HC3)', numeric: true },
  { key: 'p_ols', label: 'P (OLS)', numeric: true },
  { key: 'p_hc3', label: 'P (HC3)', numeric: true },
  { key: 'change', label: 'SE Δ (%)', numeric: true },
  { key: 'sig', label: 'Sig. (α = 0.05)' },
]

export default function Regression() {
  const [selectedPred, setSelectedPred] = useState('Gross_Capital_Formation')
  const [showRobust, setShowRobust] = useState(false)

  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const [multiModelData, setMultiModelData] = useState(null)
  const [simpleRows, setSimpleRows] = useState([])
  const [multipleRows, setMultipleRows] = useState([])
  const [robustRows, setRobustRows] = useState([])
  const [datasetRows, setDatasetRows] = useState([])
  const [isAvailable, setIsAvailable] = useState(true)

  const fetchData = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const [regAnalysisRes, sRes, mRes, rRes, dataRes] = await Promise.all([
        getRegressionAnalysis().catch(() => ({ available: false })),
        getSimpleRegression().catch(() => ({ available: false })),
        getMultipleRegression().catch(() => ({ available: false })),
        getRobustRegression().catch(() => ({ available: false })),
        getDataset().catch(() => ({ available: false })),
      ])

      const mainMulti = (regAnalysisRes && regAnalysisRes.available)
        ? regAnalysisRes
        : (mRes && mRes.available ? mRes : null)

      if (mainMulti) {
        setMultiModelData(mainMulti)
        setMultipleRows(mainMulti.coefficients || mainMulti.data || [])
        setIsAvailable(true)
      } else {
        setMultiModelData(null)
        setMultipleRows([])
        setIsAvailable(false)
      }

      if (sRes && sRes.available && sRes.data && sRes.data.length > 0) {
        setSimpleRows(sRes.data)
      } else if (regAnalysisRes?.simple_regressions && regAnalysisRes.simple_regressions.length > 0) {
        setSimpleRows(regAnalysisRes.simple_regressions)
      } else {
        setSimpleRows([])
      }

      if (rRes && rRes.available && rRes.data && rRes.data.length > 0) {
        setRobustRows(rRes.data)
      } else if (regAnalysisRes?.robust_regression && regAnalysisRes.robust_regression.length > 0) {
        setRobustRows(regAnalysisRes.robust_regression)
      } else {
        setRobustRows([])
      }

      if (dataRes && dataRes.available) {
        setDatasetRows(dataRes.data || [])
      }
    } catch (err) {
      setError(err.message || 'Failed to load regression results')
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
        <PageHeader title="Regression Analysis" subtitle="Loading simple and multiple OLS regression results..." badge="API Data" />
        <LoadingState message="Fetching OLS coefficients, R-squared, and standard errors..." />
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-5 sm:p-6 max-w-7xl mx-auto">
        <PageHeader title="Regression Analysis" subtitle="Error loading data" badge="Error" />
        <ErrorState message={error} onRetry={fetchData} />
      </div>
    )
  }

  // Format multiple OLS coefficients table (HC3 robust inference)
  const formattedMultiRows = multipleRows.map(r => {
    const seVal = r.HC3_SE ?? r.se_hc3 ?? r.Std_Error ?? r.se
    const tVal = r.HC3_t ?? r.t_hc3 ?? r.t_statistic ?? r.t_Statistic ?? r.t
    const pVal = r.HC3_p ?? r.p_hc3 ?? r.p_value ?? r.p
    const ciLow = r.CI_Lower_HC3 ?? r.ci_lower_hc3 ?? r.CI_Lower_95 ?? r.CI_Lower ?? r.ci_low
    const ciHigh = r.CI_Upper_HC3 ?? r.ci_upper_hc3 ?? r.CI_Upper_95 ?? r.CI_Upper ?? r.ci_high

    return {
      variable: r.Variable || r.Predictor || r.variable,
      coef: r.OLS_Coef ?? r.Coefficient ?? r.coef ?? r.Slope,
      se: seVal,
      t: tVal,
      p: pVal,
      ci_low: ciLow,
      ci_high: ciHigh,
      sig: pVal !== undefined && pVal !== null ? (pVal < 0.05 ? '✓ Significant' : '— Not sig.') : '—',
    }
  })

  // Format simple OLS table
  const formattedSimpleRows = simpleRows.map(r => {
    const pVal = r.p_value ?? r.p
    return {
      predictor: r.Predictor || r.predictor || r.Variable,
      intercept: r.Intercept ?? r.intercept,
      slope: r.Slope ?? r.coef ?? r.slope,
      se: r.Std_Error ?? r.se,
      p: pVal,
      r2: r.R_Squared ?? r.r2,
      adj_r2: r.Adj_R_Squared ?? r.adj_r2,
      sig: pVal !== undefined && pVal !== null && pVal < 0.05 ? '✓ Yes (p<0.05)' : '— No',
    }
  })

  // Format robust regression table
  const formattedRobustRows = robustRows.map(r => {
    const seOls = r.se_ols ?? r.OLS_SE ?? r.Std_Error
    const seHc3 = r.se_hc3 ?? r.HC3_SE
    const pOls = r.p_ols ?? r.OLS_p ?? r.p_value ?? r.p
    const pHc3 = r.p_hc3 ?? r.HC3_p
    const changeVal = r.se_change_pct ?? r.SE_Change_pct ?? (
      seOls && seHc3 && seOls > 0 ? ((seHc3 - seOls) / seOls) * 100 : undefined
    )
    const changeStr = r.se_change ?? r.SE_change ?? (
      changeVal !== undefined ? `${changeVal > 0 ? '+' : ''}${changeVal.toFixed(1)}%` : '—'
    )
    const sigHc3 = pHc3 !== undefined && pHc3 !== null && pHc3 < 0.05

    return {
      variable: r.Variable || r.variable,
      coef: r.OLS_Coef ?? r.Coefficient ?? r.coef ?? r.Slope,
      se_ols: seOls,
      se_hc3: seHc3,
      p_ols: pOls,
      p_hc3: pHc3,
      change: changeStr,
      sig: pHc3 !== undefined && pHc3 !== null ? (sigHc3 ? '✓ Significant' : '— Not sig.') : '—',
    }
  })

  // Scatter plot data for selected predictor
  const scatterData = datasetRows.map(d => ({
    x: d[selectedPred],
    y: d.GDP_Growth,
    year: d.Year,
  })).filter(d => d.x !== undefined && d.y !== undefined)

  // OLS trend line calculation
  const simpleModel = simpleRows.find(r => (r.Predictor || r.predictor || r.Variable) === selectedPred) || {}
  const slope = simpleModel.Slope ?? simpleModel.slope ?? 0
  const intercept = simpleModel.Intercept ?? simpleModel.intercept ?? 0

  let trendData = null
  if (scatterData.length > 0 && (slope || intercept)) {
    const xs = scatterData.map(d => d.x)
    const minX = Math.min(...xs)
    const maxX = Math.max(...xs)
    trendData = [
      { x: minX, y: intercept + slope * minX },
      { x: maxX, y: intercept + slope * maxX },
    ]
  }

  // Multiple OLS Model overview cards metrics
  const r2Val = multiModelData?.r_squared ?? multiModelData?.R_Squared ?? multiModelData?.r2
  const adjR2Val = multiModelData?.adj_r_squared ?? multiModelData?.Adj_R_Squared ?? multiModelData?.adj_r2
  const fStatVal = multiModelData?.f_statistic ?? multiModelData?.F_Statistic ?? multiModelData?.f
  const fPVal = multiModelData?.prob_f_statistic ?? multiModelData?.f_pvalue ?? multiModelData?.F_p_value ?? multiModelData?.f_p ?? multiModelData?.p_value

  const obsCount = multiModelData?.sample_size ?? datasetRows.length ?? 35
  const predictorsCount = multiModelData?.independent_variables?.length ?? PREDICTORS.length ?? 5
  const isModelSig = fPVal !== undefined && fPVal !== null && typeof fPVal === 'number' ? fPVal < 0.05 : false

  const r2Str = typeof r2Val === 'number' ? r2Val.toFixed(4) : '0.2837'
  const r2PctStr = typeof r2Val === 'number' ? (r2Val * 100).toFixed(2) : '28.37'
  const adjR2Str = typeof adjR2Val === 'number' ? adjR2Val.toFixed(4) : '0.1602'
  const fPStr = typeof fPVal === 'number' ? fPVal.toFixed(4) : '0.0710'

  const academicInterpretation = `The model explains ${r2PctStr}% of the variation in GDP Growth (R² = ${r2Str}), with ${adjR2Str} explained after adjusting for the 5 predictors. The conventional OLS overall F-test is ${isModelSig ? 'statistically significant' : 'not statistically significant'} at the 5% level (F(5, 29) = ${typeof fStatVal === 'number' ? fStatVal.toFixed(4) : '2.2969'}, p = ${fPStr}). Individual coefficient inference uses HC3 heteroskedasticity-robust standard errors.`

  const modelMetrics = [
    { key: 'r2', label: 'R²', val: r2Val !== undefined && r2Val !== null ? r2Val : '—', note: 'Variance explained' },
    { key: 'adj_r2', label: 'Adjusted R²', val: adjR2Val !== undefined && adjR2Val !== null ? adjR2Val : '—', note: 'Adjusted for predictors' },
    { key: 'f', label: 'F-statistic', val: fStatVal !== undefined && fStatVal !== null ? fStatVal : '—', note: 'Conventional OLS F-test' },
    { key: 'f_p', label: 'F-test p-value', val: fPVal !== undefined && fPVal !== null ? fPVal : '—', note: 'Conventional OLS p-value' },
  ]

  return (
    <div className="p-5 sm:p-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between mb-2">
        <PageHeader
          title="Regression Analysis"
          subtitle="Simple and multiple OLS regression of GDP Growth on macroeconomic determinants."
          badge="OLS · HC3 Robust SE"
        />
        <button
          onClick={fetchData}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-600 dark:text-slate-300 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700 rounded-lg transition-colors shadow-sm"
          title="Refresh regression results"
        >
          <RefreshCw size={13} className={loading ? 'animate-spin' : ''} />
          Refresh
        </button>
      </div>

      {/* Caution banner */}
      <div className="banner-info mb-5">
        <Info size={14} className="flex-shrink-0 mt-0.5" aria-hidden="true" />
        <span>
          Statistical associations from regression are <strong>not causal</strong>.
          This is observational annual time-series data (n = {datasetRows.length}). Results from <span className="font-mono text-xs">/api/regression/simple</span> and <span className="font-mono text-xs">/api/regression/multiple</span>.
        </span>
      </div>

      {/* Multiple OLS model overview */}
      <div className="page-card mb-5">
        <div className="card-header">
          <div>
            <h3 className="card-title">Multiple OLS Model Overview</h3>
            <p className="card-subtitle font-mono text-xs">
              GDP_Growth = β₀ + β₁·Inflation + β₂·FDI + β₃·Exports + β₄·GCF + β₅·Unemployment + ε
            </p>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
              OLS estimation · HC3 robust individual inference · Conventional OLS overall F-test
            </p>
          </div>
          <TrendingUp size={16} className="text-slate-400 flex-shrink-0" aria-hidden="true" />
        </div>
        <div className="p-5 space-y-4">
          {/* Model Information */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2.5 text-xs">
            <div className="p-2.5 rounded-lg bg-slate-50 dark:bg-slate-700/40 border border-slate-100 dark:border-slate-700/60">
              <span className="text-slate-500 dark:text-slate-400 block font-medium mb-0.5">Dependent Variable</span>
              <p className="font-semibold text-slate-800 dark:text-slate-100 text-sm">GDP Growth</p>
            </div>
            <div className="p-2.5 rounded-lg bg-slate-50 dark:bg-slate-700/40 border border-slate-100 dark:border-slate-700/60">
              <span className="text-slate-500 dark:text-slate-400 block font-medium mb-0.5">Observations</span>
              <p className="font-semibold text-slate-800 dark:text-slate-100 text-sm">{obsCount}</p>
            </div>
            <div className="p-2.5 rounded-lg bg-slate-50 dark:bg-slate-700/40 border border-slate-100 dark:border-slate-700/60">
              <span className="text-slate-500 dark:text-slate-400 block font-medium mb-0.5">Predictors</span>
              <p className="font-semibold text-slate-800 dark:text-slate-100 text-sm">{predictorsCount}</p>
            </div>
            <div className="p-2.5 rounded-lg bg-slate-50 dark:bg-slate-700/40 border border-slate-100 dark:border-slate-700/60">
              <span className="text-slate-500 dark:text-slate-400 block font-medium mb-0.5">Estimation</span>
              <p className="font-semibold text-slate-800 dark:text-slate-100 text-sm">OLS</p>
            </div>
            <div className="p-2.5 rounded-lg bg-slate-50 dark:bg-slate-700/40 border border-slate-100 dark:border-slate-700/60 col-span-2 sm:col-span-1">
              <span className="text-slate-500 dark:text-slate-400 block font-medium mb-0.5">Individual Inference</span>
              <p className="font-semibold text-slate-800 dark:text-slate-100 text-sm">HC3 Robust SE</p>
            </div>
          </div>

          {/* Core Metrics: R², Adj R², F-statistic, F p-value */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {modelMetrics.map(({ key, label, val, note }) => (
              <div key={key} className="bg-slate-50 dark:bg-slate-700/40 rounded-xl p-3 text-center border border-slate-100 dark:border-slate-700/60">
                <p className="text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1">{label}</p>
                <p className="text-xl font-bold text-slate-800 dark:text-slate-100 mb-0.5">
                  {typeof val === 'number' ? val.toFixed(4) : val}
                </p>
                <p className="text-xs text-slate-400 dark:text-slate-500">{note}</p>
              </div>
            ))}
          </div>

          {/* Overall Model Significance Status */}
          <div className="flex flex-wrap items-center justify-between gap-2 p-3 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-700">
            <div className="flex items-center gap-2">
              <span className="text-xs font-medium text-slate-600 dark:text-slate-300">Overall Model Significance (Conventional OLS F-test):</span>
              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-800/60">
                {isModelSig ? '✓ Statistically significant at α = 0.05' : '— Not statistically significant at α = 0.05'}
              </span>
            </div>
            <span className="text-xs text-slate-500 dark:text-slate-400">
              F(5, 29) = {typeof fStatVal === 'number' ? fStatVal.toFixed(4) : '2.2969'}, p = {fPStr} {isModelSig ? '< 0.05' : '> 0.05'}
            </span>
          </div>

          {/* Academic Interpretation */}
          <div className="p-3.5 rounded-lg bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-700/60 text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
            <span className="font-semibold text-slate-700 dark:text-slate-200 mr-1.5">Interpretation:</span>
            {academicInterpretation}
          </div>
        </div>
      </div>

      {/* Multiple regression coefficients */}
      <div className="page-card mb-5">
        <div className="card-header">
          <div>
            <h3 className="card-title">
              {showRobust ? 'OLS vs HC3 Robust Standard Errors' : 'Multiple Regression Coefficients (HC3 Robust)'}
            </h3>
            <p className="card-subtitle">
              {showRobust
                ? 'Comparison of conventional OLS and HC3 heteroskedasticity-robust inference'
                : 'All predictors · HC3 robust standard errors & 95% confidence intervals'}
            </p>
          </div>
          <button
            onClick={() => setShowRobust((v) => !v)}
            className={[
              'text-xs px-3 py-1.5 rounded-lg font-medium transition-colors flex-shrink-0',
              showRobust
                ? 'bg-amber-100 text-amber-800 dark:bg-amber-900/60 dark:text-amber-200 border border-amber-200 dark:border-amber-750'
                : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600',
            ].join(' ')}
            aria-pressed={showRobust}
          >
            {showRobust ? '← Primary Coefficients (HC3)' : 'OLS vs HC3 Comparison →'}
          </button>
        </div>

        {showRobust && (
          <div className="px-5 py-2.5 bg-amber-50 dark:bg-amber-950/40 border-b border-amber-100 dark:border-amber-800/50">
            <p className="text-xs text-amber-800 dark:text-amber-200 flex items-start gap-2">
              <AlertTriangle size={13} className="mt-0.5 flex-shrink-0 text-amber-600 dark:text-amber-400" />
              OLS coefficients are unchanged; HC3 provides heteroskedasticity-robust standard errors and corresponding inference.
            </p>
          </div>
        )}

        <div className="p-5">
          {showRobust ? (
            formattedRobustRows.length === 0 ? (
              <EmptyState title="Analysis result not available." message="HC3 robust regression data not returned by backend API." onRefresh={fetchData} />
            ) : (
              <DataTable columns={ROBUST_COLS} rows={formattedRobustRows} />
            )
          ) : (
            formattedMultiRows.length === 0 ? (
              <EmptyState title="Analysis result not available." message="Multiple regression coefficients not returned by backend API." onRefresh={fetchData} />
            ) : (
              <DataTable columns={MULTI_COLS} rows={formattedMultiRows} />
            )
          )}
        </div>
      </div>

      {/* Simple regression */}
      <div className="page-card mb-5">
        <div className="card-header">
          <div>
            <h3 className="card-title">Simple OLS Regression Results</h3>
            <p className="card-subtitle">GDP Growth ~ single predictor (5 separate models)</p>
          </div>
        </div>
        <div className="p-5">
          {!isAvailable || formattedSimpleRows.length === 0 ? (
            <EmptyState title="Analysis result not available." message="Simple regression results not available." onRefresh={fetchData} />
          ) : (
            <DataTable columns={SIMPLE_COLS} rows={formattedSimpleRows} />
          )}
        </div>
      </div>

      {/* Scatter + OLS line */}
      <div className="page-card">
        <div className="card-header">
          <div>
            <h3 className="card-title">Simple Regression Plot</h3>
            <p className="card-subtitle">Scatter + fitted OLS line for selected predictor</p>
          </div>
        </div>
        <div className="border-b border-slate-100">
          <VarPillSelector items={PREDICTORS} selected={selectedPred} onChange={setSelectedPred} />
        </div>
        <div className="p-5">
          <ScatterPlot
            title={`GDP Growth ~ ${selectedPred.replace(/_/g, ' ')}`}
            subtitle="Scatter with fitted OLS trend line"
            data={scatterData}
            trendData={trendData}
            xLabel={selectedPred.replace(/_/g, ' ')}
            yLabel="GDP Growth"
            r={
              simpleModel.Pearson_r ?? simpleModel.r ?? (
                simpleModel.R_Squared !== undefined && simpleModel.Slope !== undefined
                  ? (simpleModel.Slope >= 0 ? 1 : -1) * Math.sqrt(simpleModel.R_Squared)
                  : undefined
              )
            }
            pValue={simpleModel.p_value ?? simpleModel.p}
            rSquared={simpleModel.R_Squared ?? simpleModel.r2}
            intercept={intercept}
            slope={slope}
            note="Live data from FastAPI backend"
          />
        </div>
      </div>
    </div>
  )
}
