import { useState, useEffect, useCallback } from 'react'
import { GitBranch, Info, RefreshCw } from 'lucide-react'
import PageHeader from '../components/PageHeader.jsx'
import DataTable from '../components/DataTable.jsx'
import VarPillSelector from '../components/VarPillSelector.jsx'
import LoadingState from '../components/LoadingState.jsx'
import ErrorState from '../components/ErrorState.jsx'
import EmptyState from '../components/EmptyState.jsx'
import Heatmap from '../components/charts/Heatmap.jsx'
import ScatterPlot from '../components/charts/ScatterPlot.jsx'

import {
  getPearsonCorrelation,
  getSpearmanCorrelation,
  getPredictorCorrelationCheck,
  getCorrelationAnalysis,
} from '../api/correlationApi'
import { getDataset } from '../api/datasetApi'

const PREDICTORS = [
  'Inflation', 'FDI_Net_Inflows', 'Exports', 'Gross_Capital_Formation', 'Unemployment',
]

const ALL_VARS = ['GDP_Growth', ...PREDICTORS]

const CORR_COLS = [
  { key: 'predictor', label: 'Predictor' },
  { key: 'r', label: 'Pearson r', numeric: true },
  { key: 'rho', label: 'Spearman ρ', numeric: true },
  { key: 'p_pearson', label: 'P (Pearson)', numeric: true },
  { key: 'p_spearman', label: 'P (Spearman)', numeric: true },
  { key: 'sig', label: 'Sig. (α=0.05)' },
  { key: 'direction', label: 'Direction' },
]

const MC_COLS = [
  { key: 'pair', label: 'Variable Pair' },
  { key: 'r', label: 'Pearson r', numeric: true },
  { key: 'concern', label: 'Concern Level' },
  { key: 'note', label: 'Note' },
]

export default function Correlation() {
  const [xVar, setXVar] = useState('Gross_Capital_Formation')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  
  const [corrAnalysisData, setCorrAnalysisData] = useState(null)
  const [pearsonRows, setPearsonRows] = useState([])
  const [spearmanRows, setSpearmanRows] = useState([])
  const [predictorCheckRows, setPredictorCheckRows] = useState([])
  const [datasetRows, setDatasetRows] = useState([])
  const [isAvailable, setIsAvailable] = useState(true)

  const fetchData = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const [cRes, pRes, sRes, mcRes, dataRes] = await Promise.all([
        getCorrelationAnalysis().catch(() => ({ available: false })),
        getPearsonCorrelation().catch(() => ({ available: false })),
        getSpearmanCorrelation().catch(() => ({ available: false })),
        getPredictorCorrelationCheck().catch(() => ({ available: false })),
        getDataset().catch(() => ({ available: false })),
      ])

      if (cRes && cRes.available) {
        setCorrAnalysisData(cRes)
        setIsAvailable(true)
      } else if (pRes && pRes.available) {
        setIsAvailable(true)
      } else {
        setIsAvailable(false)
      }

      if (pRes && pRes.available) setPearsonRows(pRes.data || [])
      if (sRes && sRes.available) setSpearmanRows(sRes.data || [])
      if (mcRes && mcRes.available) setPredictorCheckRows(mcRes.data || [])
      if (dataRes && dataRes.available) setDatasetRows(dataRes.data || [])
    } catch (err) {
      setError(err.message || 'Failed to load correlation analysis')
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
        <PageHeader title="Correlation Analysis" subtitle="Loading Pearson and Spearman correlation matrices..." badge="API Data" />
        <LoadingState message="Fetching correlation coefficients and p-values..." />
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-5 sm:p-6 max-w-7xl mx-auto">
        <PageHeader title="Correlation Analysis" subtitle="Error loading data" badge="Error" />
        <ErrorState message={error} onRetry={fetchData} />
      </div>
    )
  }

  // Build matrix helper
  const buildMatrixFromFullResponse = (matrixDict, vars = ALL_VARS) => {
    if (!matrixDict) return null
    return {
      labels: vars,
      matrix: vars.map(v1 => vars.map(v2 => {
        const val = matrixDict[v1]?.[v2]
        return typeof val === 'number' ? val : (v1 === v2 ? 1.0 : null)
      }))
    }
  }

  const buildMatrix = (rows, rKey) => {
    if (!rows || rows.length === 0) return null
    const map = {}
    ALL_VARS.forEach(v1 => {
      map[v1] = {}
      ALL_VARS.forEach(v2 => { map[v1][v2] = v1 === v2 ? 1.0 : null })
    })

    rows.forEach(r => {
      const v1 = r.Variable || r.Variable_1 || r.predictor
      const v2 = r.Variable_2 || 'GDP_Growth'
      const val = parseFloat(r[rKey] ?? r.r ?? r.rho)
      if (v1 && map[v1] && !isNaN(val)) {
        map[v1][v2] = val
        map[v2][v1] = val
      }
    })

    return {
      labels: ALL_VARS,
      matrix: ALL_VARS.map(v1 => ALL_VARS.map(v2 => map[v1][v2]))
    }
  }

  const pearsonMatrix = corrAnalysisData?.pearson_matrix
    ? buildMatrixFromFullResponse(corrAnalysisData.pearson_matrix, corrAnalysisData.variables || ALL_VARS)
    : buildMatrix(pearsonRows, 'Pearson_r')

  const spearmanMatrix = corrAnalysisData?.spearman_matrix
    ? buildMatrixFromFullResponse(corrAnalysisData.spearman_matrix, corrAnalysisData.variables || ALL_VARS)
    : buildMatrix(spearmanRows, 'Spearman_rho')

  // Combined correlation table for GDP_Growth vs Predictors
  const combinedCorrRows = PREDICTORS.map(pred => {
    let rVal = corrAnalysisData?.pearson_matrix?.['GDP_Growth']?.[pred]
    let rhoVal = corrAnalysisData?.spearman_matrix?.['GDP_Growth']?.[pred]
    let pP = corrAnalysisData?.p_values_pearson?.['GDP_Growth']?.[pred]
    let pS = corrAnalysisData?.p_values_spearman?.['GDP_Growth']?.[pred]

    if (rVal === undefined && corrAnalysisData?.pairwise_summary) {
      const pSummary = corrAnalysisData.pairwise_summary.find(
        p => (p.Variable_1 === 'GDP_Growth' && p.Variable_2 === pred) ||
             (p.Variable_1 === pred && p.Variable_2 === 'GDP_Growth')
      )
      if (pSummary) {
        rVal = pSummary.Pearson_r
        rhoVal = pSummary.Spearman_rho
        pP = pSummary.Pearson_p
        pS = pSummary.Spearman_p
      }
    }

    if (rVal === undefined && pearsonRows.length > 0) {
      const gdpRow = pearsonRows.find(r => (r.Variable || r['Unnamed: 0'] || r.predictor) === 'GDP_Growth')
      if (gdpRow && gdpRow[pred] !== undefined) rVal = gdpRow[pred]
    }

    if (rhoVal === undefined && spearmanRows.length > 0) {
      const gdpRow = spearmanRows.find(r => (r.Variable || r['Unnamed: 0'] || r.predictor) === 'GDP_Growth')
      if (gdpRow && gdpRow[pred] !== undefined) rhoVal = gdpRow[pred]
    }

    let direction = 'None'
    if (rVal !== undefined && rVal !== null && !isNaN(rVal)) {
      if (rVal > 0) direction = 'Positive'
      else if (rVal < 0) direction = 'Negative'
      else direction = 'None'
    }

    const pPearsonSig = (pP !== undefined && pP !== null && pP < 0.05)
    const pSpearmanSig = (pS !== undefined && pS !== null && pS < 0.05)

    let sigStr = '—'
    if (pP !== undefined || pS !== undefined) {
      if (pPearsonSig && pSpearmanSig) {
        sigStr = '✓ Both significant'
      } else if (pPearsonSig) {
        sigStr = '✓ Pearson significant'
      } else if (pSpearmanSig) {
        sigStr = '✓ Spearman significant'
      } else {
        sigStr = '— Not significant'
      }
    }

    return {
      predictor: pred,
      r: rVal,
      rho: rhoVal,
      p_pearson: pP,
      p_spearman: pS,
      sig: sigStr,
      direction: direction,
    }
  })

  // Multicollinearity pre-check table (Inter-predictor pairs ONLY, excluding GDP_Growth)
  const interPredictorPairs = []
  for (let i = 0; i < PREDICTORS.length; i++) {
    for (let j = i + 1; j < PREDICTORS.length; j++) {
      const p1 = PREDICTORS[i]
      const p2 = PREDICTORS[j]

      let rVal = corrAnalysisData?.pearson_matrix?.[p1]?.[p2]
      if (rVal === undefined && corrAnalysisData?.pairwise_summary) {
        const pSummary = corrAnalysisData.pairwise_summary.find(
          p => (p.Variable_1 === p1 && p.Variable_2 === p2) ||
               (p.Variable_1 === p2 && p.Variable_2 === p1)
        )
        if (pSummary) rVal = pSummary.Pearson_r
      }
      if (rVal === undefined && pearsonRows.length > 0) {
        const rowObj = pearsonRows.find(r => (r.Variable || r['Unnamed: 0'] || r.predictor) === p1)
        if (rowObj && rowObj[p2] !== undefined) rVal = rowObj[p2]
      }

      if (rVal !== undefined && rVal !== null && !isNaN(rVal)) {
        const absR = Math.abs(rVal)
        const isHigh = absR >= 0.70
        interPredictorPairs.push({
          pair: `${p1} vs ${p2}`,
          r: rVal,
          absR: absR,
          concern: isHigh ? '⚠️ Potential multicollinearity' : '✓ Low concern',
          note: isHigh ? 'Flagged for VIF check (|r| ≥ 0.70)' : 'Acceptable independence (|r| < 0.70)',
        })
      }
    }
  }

  // Sort pairs with highest absolute correlation first
  interPredictorPairs.sort((a, b) => b.absR - a.absR)

  const mcTableRows = interPredictorPairs.map(({ pair, r, concern, note }) => ({
    pair,
    r,
    concern,
    note,
  }))

  // Scatter plot data for selected predictor
  const scatterData = datasetRows.map(d => ({
    x: d[xVar],
    y: d.GDP_Growth,
    year: d.Year,
  })).filter(d => d.x !== undefined && d.y !== undefined)

  const selectedCorrRow = combinedCorrRows.find(r => r.predictor === xVar)

  const years = datasetRows.map(r => r.Year).filter(Boolean)
  const periodSub = years.length ? `${Math.min(...years)}–${Math.max(...years)}` : ''

  return (
    <div className="p-5 sm:p-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between mb-2">
        <PageHeader
          title="Correlation Analysis"
          subtitle="Pearson and Spearman rank correlations between GDP Growth and all predictors."
          badge="α = 0.05"
        />
        <button
          onClick={fetchData}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-600 dark:text-slate-300 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700 rounded-lg transition-colors shadow-sm"
          title="Refresh correlation data"
        >
          <RefreshCw size={13} className={loading ? 'animate-spin' : ''} />
          Refresh
        </button>
      </div>

      {/* Method note */}
      <div className="banner-info mb-5">
        <Info size={14} className="flex-shrink-0 mt-0.5" aria-hidden="true" />
        <span>
          <strong>Both Pearson and Spearman</strong> are reported. Spearman is more robust
          for non-normally distributed variables. Live API outputs from <span className="font-mono text-xs">/api/correlation/pearson</span> and <span className="font-mono text-xs">/api/correlation/spearman</span>.
        </span>
      </div>

      {/* Heatmaps */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 mb-5">
        {pearsonMatrix ? (
          <Heatmap
            title="Pearson Correlation Matrix"
            subtitle="Linear correlation — all variables"
            data={pearsonMatrix}
            type="Pearson"
          />
        ) : (
          <ChartCard title="Pearson Correlation Matrix" subtitle="Linear correlation">
            <EmptyState icon={GitBranch} title="Analysis result not available." message="Pearson correlation data not returned by API." onRefresh={fetchData} />
          </ChartCard>
        )}

        {spearmanMatrix ? (
          <Heatmap
            title="Spearman Rank Correlation Matrix"
            subtitle="Rank-based — robust for non-normal distributions"
            data={spearmanMatrix}
            type="Spearman"
          />
        ) : (
          <ChartCard title="Spearman Correlation Matrix" subtitle="Rank correlation">
            <EmptyState icon={GitBranch} title="Analysis result not available." message="Spearman correlation data not returned by API." onRefresh={fetchData} />
          </ChartCard>
        )}
      </div>

      {/* Combined table */}
      <div className="page-card mb-5">
        <div className="card-header">
          <div>
            <h3 className="card-title">Pearson &amp; Spearman — GDP Growth vs Predictors</h3>
            <p className="card-subtitle">
              India{periodSub ? `, ${periodSub}` : ''} · n = {datasetRows.length} · α = 0.05
            </p>
          </div>
        </div>
        <div className="p-5">
          {!isAvailable || combinedCorrRows.length === 0 ? (
            <EmptyState title="Analysis result not available." message="Correlation results not available." onRefresh={fetchData} />
          ) : (
            <DataTable columns={CORR_COLS} rows={combinedCorrRows} />
          )}
        </div>
      </div>

      {/* Scatter plot */}
      <div className="page-card mb-5">
        <div className="card-header">
          <div>
            <h3 className="card-title">Scatter Plot — GDP Growth vs Predictor</h3>
            <p className="card-subtitle">Select a predictor below to inspect observational relationship</p>
          </div>
        </div>
        <div className="border-b border-slate-100">
          <VarPillSelector items={PREDICTORS} selected={xVar} onChange={setXVar} />
        </div>
        <div className="p-5">
          <ScatterPlot
            title={`GDP Growth vs ${xVar.replace(/_/g, ' ')}`}
            subtitle="Live dataset scatter plot"
            data={scatterData}
            xLabel={xVar.replace(/_/g, ' ')}
            yLabel="GDP Growth"
            r={selectedCorrRow?.r}
            pValue={selectedCorrRow?.p_pearson}
            note="Live data from FastAPI backend"
          />
        </div>
      </div>

      {/* Multicollinearity pre-check */}
      <div className="page-card">
        <div className="card-header">
          <div>
            <h3 className="card-title">Predictor Multicollinearity Pre-Check</h3>
            <p className="card-subtitle">
              Inter-predictor correlations (|r| ≥ 0.7 flagged)
            </p>
          </div>
        </div>
        <div className="p-5">
          {mcTableRows.length === 0 ? (
            <EmptyState title="Analysis result not available." message="Predictor correlation check not returned by backend API." onRefresh={fetchData} />
          ) : (
            <DataTable columns={MC_COLS} rows={mcTableRows} />
          )}
        </div>
      </div>
    </div>
  )
}
