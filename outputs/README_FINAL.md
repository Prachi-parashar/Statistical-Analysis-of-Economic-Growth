# README — Statistical Analysis of Economic Growth and Its Determinants in India

## Project Title
**Statistical Analysis of Economic Growth and Its Determinants in India**

## Overview
A complete Statistics / Data Analysis college project analysing the association between
India's annual GDP growth and five macroeconomic variables: Inflation, FDI Net Inflows,
Exports, Gross Capital Formation, and Unemployment.

## Dataset
| Item | Detail |
|---|---|
| Source | World Bank World Development Indicators (WDI) |
| API | https://api.worldbank.org/v2/country/IND/indicator/{code} |
| Country | India (IND) |
| Period | 1993–2023 |
| Observations | 31 annual |
| Variables | 6 (1 dependent + 5 independent) |
| Missing values | 0 (in cleaned dataset) |

## Project Folder Structure
```
Statistical Analysis of Economic Growth/
├── data/
│   ├── raw/                          ← original downloaded + metadata
│   ├── cleaned/                      ← analysis-ready dataset
│   └── external/
├── scripts/                          ← all Python analysis scripts
│   ├── collect_data.py
│   ├── descriptive_statistics.py
│   ├── probability_distribution_analysis.py
│   ├── correlation_analysis.py
│   └── regression_analysis.py
├── outputs/
│   ├── tables/                       ← all CSV result tables
│   ├── final_tables/                 ← curated final tables
│   ├── figures/                      ← all generated figures
│   │   ├── probability_distributions/
│   │   ├── correlation/
│   │   └── regression/
│   │       ├── simple/
│   │       └── diagnostics/
│   ├── final_figures/                ← curated final figures
│   ├── final_report.md               ← complete academic report (Markdown)
│   ├── final_report.pdf              ← complete academic report (PDF)
│   └── README_FINAL.md               ← this file
├── requirements.txt
└── notebooks/
```

## How to Reproduce the Analysis

Install dependencies:
```bash
pip install -r requirements.txt
```

Run scripts in order:
```bash
python scripts/collect_data.py
python scripts/descriptive_statistics.py
python scripts/probability_distribution_analysis.py
python scripts/correlation_analysis.py
python scripts/regression_analysis.py
```

## Main Output Files

| File | Description |
|---|---|
| `outputs/final_report.md` | Complete academic report |
| `outputs/final_report.pdf` | PDF version of the report |
| `data/cleaned/india_economic_growth_determinants_clean.csv` | Analysis dataset |
| `outputs/final_tables/` | All key result tables |
| `outputs/final_figures/` | Selected publication-quality figures |
| `outputs/tables/multiple_regression_summary.txt` | Full statsmodels OLS output |

## Key Results (Summary)
- Average GDP Growth: **6.24%** (1993–2023, n=31)
- Only significant correlation: **Spearman ρ(GCF, GDP) = +0.382, p = 0.034**
- Multiple OLS R² = **0.318**, Adj. R² = **0.182**
- Significant predictors (OLS): **GCF** (β=+0.356, p=0.033), **FDI** (β=−2.114, p=0.029)
- Both lose significance under **HC3 robust SE**
- No heteroskedasticity (BP p=0.131), DW=1.855 (no autocorrelation concern)
- Non-normal residuals (SW p=0.008), influential obs: **2020** (COVID), **2023**

## Important Notes
- All results are **associative**, not causal
- Data sourced exclusively from the **World Bank WDI** — no fabricated values
- Limitations include: small sample (n=31), potential endogeneity, omitted variables,
  structural breaks, and the influential 2020 COVID-19 observation
