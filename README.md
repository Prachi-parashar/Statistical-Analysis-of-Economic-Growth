<<<<<<< HEAD
# Statistical Analysis of Economic Growth and Its Determinants in India

An econometric and statistical analysis web platform examining India's annual GDP growth (1991–2025) and its macroeconomic determinants using formal statistical inference, interactive visualizations, and automated dynamic PDF report generation.

---

## 1. Project Overview

### Overview & Objective
This project evaluates the empirical relationships between India's economic growth and five key macroeconomic indicators over a 35-year period (1991–2025). The goal is to provide a complete, transparent, and reproducible statistical analysis platform with automated econometric modeling, diagnostics, and dynamic academic report generation.

### Key Features
- **Interactive Dashboard:** Live exploration of descriptive statistics, probability distributions, correlations, and regression models.
- **Rigorous Econometrics:** Simple OLS ($\times 5$), Multiple OLS, HC3 heteroskedasticity-robust standard errors, and full diagnostic suite (Durbin-Watson, Breusch-Pagan, Shapiro-Wilk, Cook's Distance, VIF).
- **Dynamic PDF Report Generation:** True dynamic report compiled via ReportLab reflecting the active dataset and analysis run without hardcoded results.
- **Single Launcher (`app.py`):** One-command startup for both backend and frontend without external shell script dependencies.

### Macroeconomic Variables
| Variable | Description | Unit | Role |
|---|---|---|---|
| **GDP Growth** | Annual percentage growth rate of GDP at market prices | % | **Dependent Variable ($Y$)** |
| **Inflation** | Consumer Price Index (annual variation) | % | Independent Predictor ($X_1$) |
| **FDI Net Inflows** | Foreign Direct Investment net inflows | % of GDP | Independent Predictor ($X_2$) |
| **Exports** | Exports of goods and services | % of GDP | Independent Predictor ($X_3$) |
| **Gross Capital Formation** | Total domestic investment / capital accumulation | % of GDP | Independent Predictor ($X_4$) |
| **Unemployment** | Total unemployment as share of labor force | % | Independent Predictor ($X_5$) |

### Data Source
- **Source:** World Bank World Development Indicators (WDI) API
- **Coverage:** India (`IND`), 1991–2025 ($n=35$ annual observations)
- **Data Integrity:** 100% verified against official World Bank indicators; zero missing values in analysis dataset.

### Statistical Methodology
1. **Descriptive Statistics:** Measures of central tendency, dispersion, quartiles, IQR, skewness, and excess kurtosis.
2. **Distribution & Normality:** Shapiro-Wilk and Anderson-Darling tests, distribution fitting, and empirical probabilities.
3. **Correlation Analysis:** Pearson parametric ($r$) and Spearman non-parametric ($\rho$) correlation matrices with multicollinearity screening.
4. **Regression Modeling:** Five bivariate OLS models, Multiple OLS model, and HC3 robust inference.
5. **Regression Diagnostics:** Autocorrelation (Durbin-Watson), heteroskedasticity (Breusch-Pagan), residual normality (Shapiro-Wilk), influence (Cook's Distance), and multicollinearity (VIF).

### Technology Stack
- **Backend & Statistics:** Python 3.10+, FastAPI, Uvicorn, Pydantic, Requests, pandas, NumPy, SciPy, statsmodels, Matplotlib, Seaborn, ReportLab
- **Frontend UI:** React 18, Vite 5, Tailwind CSS, Recharts, Lucide React

### Architecture & Data Flow
```text
World Bank WDI API
       │
       ▼
Data Ingestion & Cleaning (scripts/collect_data.py)
       │
       ▼
Statistical & Econometric Engine (statsmodels, scipy, pandas)
       │
       ▼
FastAPI REST Backend (http://127.0.0.1:8000)
       ├── API Endpoints ──► React 18 / Vite Frontend (http://localhost:5173)
       └── ReportLab Engine ──► Dynamic Academic PDF Report
```

### Project Structure
```text
Statistical Analysis of Economic Growth/
├── app.py                          # Unified single application launcher
├── requirements.txt                # Curated Python dependencies
├── data/
│   ├── raw/                        # Raw World Bank API downloads & metadata
│   └── cleaned/                    # Cleaned 1991–2025 dataset
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI application
│   │   ├── config.py               # Dynamic path configuration
│   │   ├── schemas.py              # Pydantic v2 schemas
│   │   ├── routers/api.py          # REST API router
│   │   ├── services/data_service.py# Data pipeline service
│   │   └── utils/csv_reader.py     # CSV parsing utility
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/                  # Dashboard, Analysis, Reports, About pages
│   │   ├── components/             # Reusable UI cards, tables, charts
│   │   └── api/apiClient.js        # API service client
│   └── package.json
├── scripts/                        # Standalone statistical & PDF scripts
└── outputs/
    ├── tables/                     # Generated CSV statistical tables
    ├── figures/                    # Generated high-resolution figures
    └── reports/                    # Generated dynamic PDF report
```

---

## 🚀 Setup on a New PC

Follow these step-by-step instructions to set up and run the project on a fresh Windows PC after cloning from GitHub.

### 1. Required Software to Install

Before running the project, install the following tools on your PC:

| Software | Required Version | Purpose | Verification Command |
|---|---|---|---|
| **Git** | Any recent version | Cloning repository from GitHub | `git --version` |
| **Python** | **3.10+** (3.10, 3.11, or 3.12) | Backend API, statistical analysis, PDF generation | `python --version` |
| **Node.js & npm** | **18+** or **20+ (LTS)** | React + Vite frontend development server | `node --version`<br>`npm --version` |

> [!NOTE]
> - When installing Python on Windows, check the box **"Add python.exe to PATH"**.
> - `npm` is bundled automatically with Node.js.
> - No external database (MySQL, PostgreSQL, etc.) is required.

### Summary: What Must Be Installed vs. What Is Included

- **Must Install on Your PC:** Git, Python 3.10+, Node.js (with npm).
- **Already Included in Repository:** Complete backend source, React frontend source, statistical models, data pipeline, dynamic report generator, datasets, `requirements.txt`, and `package.json`.

---

### 2. Step-by-Step Installation & Running

#### Step 1 — Clone the Repository
Open Command Prompt or your preferred terminal:
```text
git clone https://github.com/<your-username>/Statistical-Analysis-of-Economic-Growth.git
cd "Statistical Analysis of Economic Growth"
```

#### Step 2 — Create Python Virtual Environment
Create a clean `.venv` environment in the project root:
```text
python -m venv .venv
```

#### Step 3 — Install Backend Dependencies
Install all required Python packages directly through the virtual environment's executable:
```text
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
```
*(On macOS / Linux, substitute `.venv/bin/python` for `.venv\Scripts\python.exe`)*

#### Step 4 — Install Frontend Dependencies
Navigate to the `frontend` folder and install Node packages:
```text
cd frontend
npm install
cd ..
```

---

## Running the Complete Application

### Recommended

From the project root directory:

```text
.venv\Scripts\python.exe app.py
```

### Alternative (If your virtual environment is already active)

```text
python app.py
```

This single command:
1. Dynamically detects project paths.
2. Launches the **FastAPI Backend** at `http://127.0.0.1:8000`.
3. Launches the **React + Vite Frontend** at `http://localhost:5173`.
4. Automatically opens the application in your default web browser.

---

## Application Access Points

| Service | URL | Description |
|---|---|---|
| **Frontend UI** | [http://localhost:5173](http://localhost:5173) | Web Dashboard & Interactive Analytics |
| **Backend API** | [http://127.0.0.1:8000](http://127.0.0.1:8000) | FastAPI REST Server |
| **API Documentation** | [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) | Interactive Swagger UI Documentation |

---

## Stopping the Application

To stop both backend and frontend servers:
Press **`Ctrl+C`** in the terminal where `app.py` is running. `app.py` cleanly terminates all child processes.

---

## Optional: Standalone Scripts & Verification

To run standalone analysis scripts individually:
```text
.venv\Scripts\python.exe scripts/collect_data.py
.venv\Scripts\python.exe scripts/descriptive_statistics.py
.venv\Scripts\python.exe scripts/probability_distribution_analysis.py
.venv\Scripts\python.exe scripts/correlation_analysis.py
.venv\Scripts\python.exe scripts/regression_analysis.py
.venv\Scripts\python.exe scripts/generate_pdf.py
```

To run the automated validation test suite:
```text
.venv\Scripts\python.exe scripts/validate_report_pipeline.py
```

---

## License & Citation
Academic Research & Demonstration Project. Data sourced from World Bank Open Data.
=======
# Statical-Analysis-of-Economic-growth
>>>>>>> 203d8271f6bf807c6ea79f67701e6ce7692eea6b
