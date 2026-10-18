import { useState, useEffect } from 'react'
import { BookOpen, Database, Target, Layers, ExternalLink, AlertTriangle } from 'lucide-react'
import PageHeader from '../components/PageHeader.jsx'
import { getReportInfo } from '../api/reportApi'
import { getDataset } from '../api/datasetApi'

const VARIABLES = [
  { name: 'GDP_Growth',              role: 'Dependent',   unit: 'Annual % change',       code: 'NY.GDP.MKTP.KD.ZG',     description: 'Annual % growth of GDP at constant local currency' },
  { name: 'Inflation',               role: 'Independent', unit: 'Annual % change',       code: 'FP.CPI.TOTL.ZG',        description: 'Consumer Price Index annual % change' },
  { name: 'FDI_Net_Inflows',         role: 'Independent', unit: '% of GDP',              code: 'BX.KLT.DINV.WD.GD.ZS',  description: 'Foreign direct investment net inflows as % of GDP' },
  { name: 'Exports',                 role: 'Independent', unit: '% of GDP',              code: 'NE.EXP.GNFS.ZS',        description: 'Exports of goods and services as % of GDP' },
  { name: 'Gross_Capital_Formation', role: 'Independent', unit: '% of GDP',              code: 'NE.GDI.TOTL.ZS',        description: 'Gross capital formation as % of GDP' },
  { name: 'Unemployment',            role: 'Independent', unit: '% of total labour force', code: 'SL.UEM.TOTL.ZS',      description: 'Unemployment rate — ILO modelled estimate' },
]

const METHODS = [
  { phase: 'Descriptive Statistics',   script: 'statistics_service.py',                tools: 'Mean, median, mode, variance, std dev, IQR, skewness, excess kurtosis'                              },
  { phase: 'Distribution Analysis',    script: 'statistics_service.py',                tools: 'Shapiro-Wilk, Anderson-Darling, Histogram+KDE, Q-Q plots, distribution fitting, empirical probabilities' },
  { phase: 'Correlation Analysis',     script: 'statistics_service.py',                tools: 'Pearson product-moment, Spearman rank, multicollinearity pre-check (all predictor pairs)'           },
  { phase: 'Regression Analysis',      script: 'statistics_service.py',                tools: 'Simple OLS (×5), Multiple OLS, HC3 robust standard errors'                                          },
  { phase: 'Regression Diagnostics',   script: 'statistics_service.py',                tools: 'Durbin-Watson, Breusch-Pagan, Shapiro-Wilk (residuals), Jarque-Bera, VIF, Cook\'s Distance, leverage/influence diagnostics' },
]

function Section({ icon: Icon, title, children }) {
  return (
    <div className="page-card mb-5">
      <div className="card-header">
        <div className="flex items-center gap-2.5">
          <Icon size={16} className="text-primary-600 dark:text-primary-400 flex-shrink-0" aria-hidden="true" />
          <h3 className="card-title">{title}</h3>
        </div>
      </div>
      <div className="p-5">{children}</div>
    </div>
  )
}

export default function About() {
  const [info, setInfo] = useState({ startYear: 1991, endYear: 2025, obs: 35 })

  useEffect(() => {
    Promise.all([
      getReportInfo().catch(() => null),
      getDataset().catch(() => null),
    ]).then(([rep, data]) => {
      if (rep && rep.start_year && rep.end_year) {
        setInfo({
          startYear: rep.start_year,
          endYear: rep.end_year,
          obs: rep.observation_count || 35
        })
      } else if (data && data.data && data.data.length > 0) {
        const yrs = data.data.map(d => d.Year).filter(Boolean)
        setInfo({
          startYear: Math.min(...yrs),
          endYear: Math.max(...yrs),
          obs: data.data.length
        })
      }
    })
  }, [])

  const sourceMeta = [
    { label: 'Source',         value: 'World Bank World Development Indicators (WDI)'     },
    { label: 'Country',        value: 'India (ISO code: IND)'                             },
    { label: 'Period',         value: `${info.startYear}–${info.endYear} (${info.obs} annual observations)` },
    { label: 'Access method',  value: 'World Bank REST API v2'                            },
    { label: 'Missing values', value: '0 (cleaned dataset)'                               },
    { label: 'Duplicates',     value: '0'                                                  },
  ]

  return (
    <div className="p-5 sm:p-6 max-w-5xl mx-auto">
      <PageHeader
        title="About"
        subtitle="Background, objectives, data source, variables, and statistical methods."
      />

      <Section icon={BookOpen} title="Overview">
        <div className="space-y-4">
          <div className="bg-primary-50 dark:bg-primary-950/60 border border-primary-100 dark:border-primary-800 rounded-xl p-4">
            <p className="text-sm font-semibold text-primary-800 dark:text-primary-200 leading-relaxed">
              Statistical Analysis of Economic Growth and Its Determinants in India
            </p>
          </div>
          <div>
            <p className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-1.5">Objective</p>
            <p className="text-sm text-slate-700 dark:text-slate-200 leading-relaxed">
              To analyze India’s annual GDP growth and its relationship with five key macroeconomic indicators—Inflation, FDI Net Inflows, Exports, Gross Capital Formation, and Unemployment—using annual secondary data from the World Bank for 1991–2025. The analysis combines descriptive statistics, distribution and normality analysis, Pearson and Spearman correlation, simple and multiple regression, and econometric diagnostic tests to identify patterns, associations, and potential model limitations. The findings describe statistical relationships in the data and do not establish causal effects.
            </p>
          </div>
          <div className="flex items-start gap-2.5 p-3 bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800/80 rounded-xl">
            <AlertTriangle size={14} className="text-amber-600 dark:text-amber-400 flex-shrink-0 mt-0.5" aria-hidden="true" />
            <p className="text-xs text-amber-700 dark:text-amber-300 leading-relaxed">
              <strong>Important:</strong> This is an observational study based on 35 annual secondary observations. Statistical associations do not establish causation. Results should be interpreted with awareness of the relatively small sample size, potential omitted-variable bias, possible structural changes associated with major economic events, and the limitations of annual time-series data.
            </p>
          </div>
        </div>
      </Section>

      <Section icon={Database} title="Data Source">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 mb-4">
          {sourceMeta.map(({ label, value }) => (
            <div key={label} className="bg-slate-50 dark:bg-slate-700/40 rounded-xl p-3 border border-slate-100 dark:border-slate-700/50">
              <p className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-1">{label}</p>
              <p className="text-sm font-medium text-slate-800 dark:text-slate-100">{value}</p>
            </div>
          ))}
        </div>
        <div className="flex items-center gap-2">
          <ExternalLink size={13} className="text-primary-600 dark:text-primary-400 flex-shrink-0" aria-hidden="true" />
          <a
            href="https://databank.worldbank.org/source/world-development-indicators"
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs text-primary-600 dark:text-primary-400 hover:underline focus-visible:outline-none
                       focus-visible:ring-2 focus-visible:ring-primary-400 rounded"
          >
            World Bank DataBank — World Development Indicators
          </a>
        </div>
      </Section>

      <Section icon={Layers} title="Variables">
        <div className="space-y-2">
          {VARIABLES.map((v) => (
            <div
              key={v.name}
              className="flex flex-col sm:flex-row sm:items-center sm:justify-between
                         bg-slate-50 dark:bg-slate-700/40 rounded-xl px-4 py-3 gap-2 border border-slate-100 dark:border-slate-700/50"
            >
              <div className="min-w-0">
                <div className="flex items-center gap-2 mb-0.5 flex-wrap">
                  <span className="font-mono text-sm font-semibold text-slate-700 dark:text-slate-200">{v.name}</span>
                  <span className={`text-xs px-1.5 py-0.5 rounded font-semibold ${
                    v.role === 'Dependent'
                      ? 'bg-primary-100 text-primary-700 dark:bg-primary-950/80 dark:text-primary-300'
                      : 'bg-slate-200 text-slate-600 dark:bg-slate-700 dark:text-slate-300'
                  }`}>
                    {v.role}
                  </span>
                </div>
                <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">{v.description}</p>
              </div>
              <div className="text-right flex-shrink-0">
                <p className="text-xs font-semibold text-slate-600 dark:text-slate-300">{v.unit}</p>
                <p className="text-xs font-mono text-slate-400 dark:text-slate-500 mt-0.5">{v.code}</p>
              </div>
            </div>
          ))}
        </div>
      </Section>

      <Section icon={Target} title="Statistical Methods">
        <div className="space-y-3 mb-4">
          {METHODS.map(({ phase, tools, script }) => (
            <div key={phase} className="border border-slate-200 dark:border-slate-700/80 rounded-xl p-4 bg-white dark:bg-slate-800">
              <div className="flex items-center justify-between mb-2 gap-2">
                <p className="text-sm font-semibold text-slate-800 dark:text-slate-100">{phase}</p>
                <span className="text-xs font-mono text-slate-400 dark:text-slate-400 bg-slate-100 dark:bg-slate-900/60 px-2 py-0.5
                                 rounded whitespace-nowrap flex-shrink-0">
                  {script}
                </span>
              </div>
              <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">{tools}</p>
            </div>
          ))}
        </div>
        <div className="bg-slate-50 dark:bg-slate-700/40 rounded-xl p-3 border border-slate-100 dark:border-slate-700/50">
          <p className="text-xs font-semibold text-slate-600 dark:text-slate-300 mb-1.5">Software &amp; Libraries</p>
          <div className="flex flex-wrap gap-1.5">
            {['Python 3.10+', 'FastAPI', 'Uvicorn', 'Pydantic', 'Requests', 'pandas', 'NumPy', 'SciPy', 'statsmodels', 'Matplotlib', 'Seaborn', 'ReportLab'].map((lib) => (
              <span key={lib} className="text-xs font-mono bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700
                                         text-slate-600 dark:text-slate-300 px-2 py-0.5 rounded">
                {lib}
              </span>
            ))}
          </div>
        </div>
      </Section>
    </div>
  )
}
