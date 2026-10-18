import { useState, useEffect, useCallback } from 'react'
import {
  FileText,
  Download,
  Table2,
  Image,
  ExternalLink,
  RefreshCw,
  ChevronDown,
  ChevronRight,
} from 'lucide-react'
import PageHeader from '../components/PageHeader.jsx'
import LoadingState from '../components/LoadingState.jsx'
import ErrorState from '../components/ErrorState.jsx'
import EmptyState from '../components/EmptyState.jsx'

import {
  getReportInfo,
  getFigures,
  getReportPdfUrl,
  getReportMdUrl,
  getTableUrl,
  getFigureUrl,
} from '../api/reportApi'

const TABLE_FILES = [
  { title: 'Descriptive Statistics', file: 'descriptive_statistics.csv' },
  { title: 'Summary Statistics Matrix', file: 'summary_statistics.csv' },
  { title: 'Normality Tests', file: 'normality_tests.csv' },
  { title: 'Distribution Analysis', file: 'distribution_analysis.csv' },
  { title: 'Distribution Fitting', file: 'distribution_fitting.csv' },
  { title: 'Empirical Probabilities', file: 'empirical_probabilities.csv' },
  { title: 'Pearson Correlation', file: 'pearson_correlation.csv' },
  { title: 'Spearman Correlation', file: 'spearman_correlation.csv' },
  { title: 'Predictor Correlation Check', file: 'predictor_correlation_check.csv' },
  { title: 'Simple Regression Results', file: 'simple_regression_results.csv' },
  { title: 'Multiple Regression Results', file: 'multiple_regression_results.csv' },
  { title: 'Robust Regression Results', file: 'robust_regression_results.csv' },
  { title: 'VIF Results', file: 'vif_results.csv' },
  { title: 'Regression Diagnostics', file: 'regression_diagnostics.csv' },
  { title: 'Model Comparison', file: 'model_comparison.csv' },
]

export default function Reports() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const [reportInfo, setReportInfo] = useState(null)
  const [figuresCategoryMap, setFiguresCategoryMap] = useState({})
  const [showCsvTables, setShowCsvTables] = useState(false)
  const [showFigures, setShowFigures] = useState(false)

  const fetchData = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const [repRes, figRes] = await Promise.all([
        getReportInfo().catch(() => ({ available: false })),
        getFigures().catch(() => ({ available: false })),
      ])

      setReportInfo(repRes)
      if (figRes && figRes.available && figRes.categories) {
        setFiguresCategoryMap(figRes.categories)
      } else {
        setFiguresCategoryMap({})
      }
    } catch (err) {
      setError(err.message || 'Failed to fetch reports info')
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
        <PageHeader title="Reports & Downloads" subtitle="Loading current analysis artifacts..." badge="API Data" />
        <LoadingState message="Checking current PDF report and figure assets..." />
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-5 sm:p-6 max-w-7xl mx-auto">
        <PageHeader title="Reports & Downloads" subtitle="Error loading data" badge="Error" />
        <ErrorState message={error} onRetry={fetchData} />
      </div>
    )
  }

  // Flatten figures list
  const figureList = []
  Object.entries(figuresCategoryMap).forEach(([cat, files]) => {
    files.forEach(f => {
      figureList.push({ path: `${cat}/${f}`, filename: f, category: cat })
    })
  })

  const startYr = reportInfo?.start_year || 1991
  const endYr = reportInfo?.end_year || 2025
  const obsCount = reportInfo?.observation_count || 35
  const countryName = reportInfo?.country || 'India'
  const sourceName = reportInfo?.source || 'World Bank WDI'

  return (
    <div className="p-5 sm:p-6 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-4 gap-3">
        <PageHeader
          title="Reports &amp; Downloads"
          subtitle="Dynamic generation pipeline — PDF Report, CSV Output Tables & Statistical Charts."
          badge="Live Analysis Run"
        />
        <div className="flex items-center gap-2">
          <button
            onClick={fetchData}
            className="flex items-center gap-1.5 px-3 py-2 text-xs font-medium text-slate-600 dark:text-slate-300 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700 rounded-lg transition-colors shadow-sm"
            title="Refresh current reports and assets"
          >
            <RefreshCw size={13} className={loading ? 'animate-spin' : ''} />
            Refresh
          </button>
        </div>
      </div>

      {/* Metadata Info Banner */}
      <div className="banner-info mb-5 flex items-center justify-between flex-wrap gap-2">
        <div className="flex items-center gap-2">
          <ExternalLink size={14} className="flex-shrink-0 text-primary-600 dark:text-primary-400" aria-hidden="true" />
          <span className="font-semibold text-slate-800 dark:text-slate-100">
            {sourceName} &middot; {countryName} &middot; {startYr}&ndash;{endYr} (n={obsCount})
          </span>
        </div>
        {reportInfo?.analysis_id && (
          <span className="text-xs font-mono bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 px-2 py-0.5 rounded border border-slate-200 dark:border-slate-700">
            ID: {reportInfo.analysis_id}
          </span>
        )}
      </div>

      {/* Final report files */}
      <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-200 mb-3">Final Report Outputs</h3>
      <div className="page-card mb-6 divide-y divide-slate-100 dark:divide-slate-700/70">
        <div className="flex items-center gap-4 p-4 hover:bg-slate-50/80 dark:hover:bg-slate-700/40 transition-colors">
          <div className="w-10 h-10 bg-primary-50 dark:bg-primary-950/60 rounded-xl flex items-center justify-center flex-shrink-0 border border-primary-100 dark:border-primary-800">
            <FileText size={18} className="text-primary-600 dark:text-primary-400" aria-hidden="true" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-0.5">
              <p className="text-sm font-semibold text-slate-800 dark:text-slate-100">Final Report (PDF)</p>
              <span className="badge-sig">ReportLab PDF</span>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mb-0.5">Dynamically generated academic research paper with complete statistical tables, regression OLS models, and econometric diagnostics.</p>
            <p className="text-xs font-mono text-slate-400 dark:text-slate-500">/api/report/pdf</p>
          </div>
          {reportInfo?.pdf_available ? (
            <a
              href={getReportPdfUrl()}
              target="_blank"
              rel="noopener noreferrer"
              download="India_Economic_Growth_Final_Report.pdf"
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-primary-600 hover:bg-primary-700 text-white transition-colors flex-shrink-0 shadow-sm"
            >
              <Download size={12} aria-hidden="true" /> Download PDF
            </a>
          ) : (
            <span className="text-xs text-slate-400 dark:text-slate-500 italic">Not generated yet</span>
          )}
        </div>

        <div className="flex items-center gap-4 p-4 hover:bg-slate-50/80 dark:hover:bg-slate-700/40 transition-colors">
          <div className="w-10 h-10 bg-emerald-50 dark:bg-emerald-950/60 rounded-xl flex items-center justify-center flex-shrink-0 border border-emerald-100 dark:border-emerald-800">
            <FileText size={18} className="text-emerald-600 dark:text-emerald-400" aria-hidden="true" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-0.5">
              <p className="text-sm font-semibold text-slate-800 dark:text-slate-100">Final Report (Markdown)</p>
              <span className="badge-sig">Academic Markdown</span>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mb-0.5">Full academic text and GitHub Flavored Markdown tables matching the exact structure and content of the PDF report.</p>
            <p className="text-xs font-mono text-slate-400 dark:text-slate-500">/api/report/md</p>
          </div>
          {reportInfo?.md_available ? (
            <a
              href={getReportMdUrl()}
              target="_blank"
              rel="noopener noreferrer"
              download="India_Economic_Growth_Final_Report.md"
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-emerald-600 hover:bg-emerald-700 text-white transition-colors flex-shrink-0 shadow-sm"
            >
              <Download size={12} aria-hidden="true" /> Download MD
            </a>
          ) : (
            <span className="text-xs text-slate-400 dark:text-slate-500 italic">Not generated yet</span>
          )}
        </div>
      </div>

      {/* Generated Data Outputs Accordion */}
      <div className="mb-4">
        <button
          type="button"
          onClick={() => setShowCsvTables(prev => !prev)}
          className="w-full flex items-center justify-between p-3.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors text-left shadow-sm group cursor-pointer"
          aria-expanded={showCsvTables}
        >
          <div className="flex items-center gap-2.5">
            <Table2 size={16} className="text-primary-600 dark:text-primary-400 flex-shrink-0" aria-hidden="true" />
            <span className="text-sm font-semibold text-slate-800 dark:text-slate-200">
              Generated Data Outputs ({TABLE_FILES.length} CSV files)
            </span>
          </div>
          <div className="flex items-center gap-2 text-slate-400 group-hover:text-slate-600 dark:group-hover:text-slate-300 transition-colors">
            <span className="text-xs font-medium hidden sm:inline text-slate-500 dark:text-slate-400">
              {showCsvTables ? 'Hide files' : 'Show files'}
            </span>
            {showCsvTables ? <ChevronDown size={16} aria-hidden="true" /> : <ChevronRight size={16} aria-hidden="true" />}
          </div>
        </button>

        {showCsvTables && (
          <div className="page-card mt-2 divide-y divide-slate-100 dark:divide-slate-700/70">
            {TABLE_FILES.map(({ title, file }) => (
              <div key={file} className="flex items-center gap-3 px-4 py-3 hover:bg-slate-50/80 dark:hover:bg-slate-700/40 transition-colors">
                <Table2 size={14} className="text-primary-500 flex-shrink-0" aria-hidden="true" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-slate-700 dark:text-slate-200">{title}</p>
                  <p className="text-xs font-mono text-slate-400 dark:text-slate-500">{file}</p>
                </div>
                <a
                  href={getTableUrl(file)}
                  target="_blank"
                  rel="noopener noreferrer"
                  download={file}
                  className="text-xs px-2.5 py-1 bg-primary-50 hover:bg-primary-100 dark:bg-primary-950/60 dark:hover:bg-primary-900/60 text-primary-700 dark:text-primary-300 rounded-lg flex items-center gap-1 font-medium transition-colors"
                >
                  <Download size={11} aria-hidden="true" /> CSV
                </a>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Generated Statistical Figures Accordion */}
      <div className="mb-6">
        <button
          type="button"
          onClick={() => setShowFigures(prev => !prev)}
          className="w-full flex items-center justify-between p-3.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors text-left shadow-sm group cursor-pointer"
          aria-expanded={showFigures}
        >
          <div className="flex items-center gap-2.5">
            <Image size={16} className="text-primary-600 dark:text-primary-400 flex-shrink-0" aria-hidden="true" />
            <span className="text-sm font-semibold text-slate-800 dark:text-slate-200">
              Generated Statistical Figures ({figureList.length})
            </span>
          </div>
          <div className="flex items-center gap-2 text-slate-400 group-hover:text-slate-600 dark:group-hover:text-slate-300 transition-colors">
            <span className="text-xs font-medium hidden sm:inline text-slate-500 dark:text-slate-400">
              {showFigures ? 'Hide figures' : 'Show figures'}
            </span>
            {showFigures ? <ChevronDown size={16} aria-hidden="true" /> : <ChevronRight size={16} aria-hidden="true" />}
          </div>
        </button>

        {showFigures && (
          <div className="page-card p-4 mt-2">
            {figureList.length === 0 ? (
              <div className="p-5">
                <EmptyState title="No figure files returned by backend API." message="Figures will appear when returned by the backend API." onRefresh={fetchData} />
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {figureList.map(({ path, filename, category }) => {
                  const figUrl = getFigureUrl(path)
                  return (
                    <div key={path} className="border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden bg-white dark:bg-slate-800 shadow-sm hover:shadow-md transition-shadow flex flex-col">
                      <div className="bg-slate-50 dark:bg-slate-900/60 p-2 border-b border-slate-100 dark:border-slate-700/80 flex items-center justify-between">
                        <span className="text-xs font-semibold text-slate-700 dark:text-slate-200 truncate capitalize">{filename.replace(/_/g, ' ').replace('.png', '')}</span>
                        <span className="text-[10px] font-mono uppercase bg-slate-200 dark:bg-slate-700 text-slate-600 dark:text-slate-300 px-1.5 py-0.5 rounded">{category}</span>
                      </div>
                      <div className="p-2 bg-slate-900/5 dark:bg-slate-900/40 flex items-center justify-center min-h-[160px] overflow-hidden">
                        <img
                          src={figUrl}
                          alt={filename}
                          className="max-h-[180px] w-auto object-contain rounded transition-transform hover:scale-105"
                          onError={(e) => {
                            e.target.style.display = 'none'
                          }}
                        />
                      </div>
                      <div className="p-2.5 bg-white dark:bg-slate-800 border-t border-slate-100 dark:border-slate-700/80 mt-auto flex items-center justify-between gap-2">
                        <span className="text-[11px] font-mono text-slate-400 dark:text-slate-500 truncate">{filename}</span>
                        <a
                          href={figUrl}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs px-2.5 py-1 bg-primary-50 hover:bg-primary-100 dark:bg-primary-950/60 dark:hover:bg-primary-900/60 text-primary-700 dark:text-primary-300 rounded-lg flex items-center gap-1 font-semibold transition-colors flex-shrink-0"
                        >
                          <Download size={11} aria-hidden="true" /> View / PNG
                        </a>
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
