"""
collect_data.py
---------------
Data Collection and Dataset Preparation
Project: Statistical Analysis of Economic Growth and Its Determinants in India
Source:  World Bank World Development Indicators (WDI) API
Author:  Auto-generated for academic project
Date:    2026

Variables fetched for India (country code: IND):
  - GDP Growth (annual %)               -> NY.GDP.MKTP.KD.ZG
  - Inflation, consumer prices (ann %)  -> FP.CPI.TOTL.ZG
  - FDI net inflows (% of GDP)          -> BX.KLT.DINV.WD.GD.ZS
  - Exports of goods & services (% GDP) -> NE.EXP.GNFS.ZS
  - Gross capital formation (% of GDP)  -> NE.GDI.TOTL.ZS
  - Unemployment, total (% labor force) -> SL.UEM.TOTL.ZS

NOTE: No statistics are computed here. Only data collection, saving, cleaning,
      metadata creation, and integrity verification.
"""

import os
import sys
import requests
import pandas as pd
from datetime import datetime

# ─────────────────────────────────────────────
# 0. PATHS
# ─────────────────────────────────────────────
BASE_DIR     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR      = os.path.join(BASE_DIR, "data", "raw")
CLEANED_DIR  = os.path.join(BASE_DIR, "data", "cleaned")

RAW_FILE     = os.path.join(RAW_DIR,     "india_economic_growth_determinants_raw.csv")
CLEAN_FILE   = os.path.join(CLEANED_DIR, "india_economic_growth_determinants_clean.csv")
META_FILE    = os.path.join(RAW_DIR,     "dataset_metadata.csv")

for d in [RAW_DIR, CLEANED_DIR]:
    os.makedirs(d, exist_ok=True)

# ─────────────────────────────────────────────
# 1. WORLD BANK WDI INDICATOR MAP
# ─────────────────────────────────────────────
INDICATORS = {
    "GDP_Growth"             : "NY.GDP.MKTP.KD.ZG",
    "Inflation"              : "FP.CPI.TOTL.ZG",
    "FDI_Net_Inflows"        : "BX.KLT.DINV.WD.GD.ZS",
    "Exports"                : "NE.EXP.GNFS.ZS",
    "Gross_Capital_Formation": "NE.GDI.TOTL.ZS",
    "Unemployment"           : "SL.UEM.TOTL.ZS",
}

COUNTRY  = "IND"
START_YR = 1991   # post-liberalisation era, maximises usable data
END_YR   = 2023   # latest confirmed WDI annual data

WB_API   = "https://api.worldbank.org/v2/country/{country}/indicator/{indicator}"
WB_BASE  = "https://data.worldbank.org/indicator/{indicator}?locations=IN"

# ─────────────────────────────────────────────
# 2. FETCH FUNCTION  (World Bank JSON API v2)
# ─────────────────────────────────────────────
def fetch_wb_series(indicator_code: str, country: str,
                    start: int, end: int) -> dict:
    """
    Fetch annual data for one WDI indicator via the World Bank REST API.
    Returns {year: value} dict. Raises on HTTP or API errors.
    """
    url = WB_API.format(country=country, indicator=indicator_code)
    params = {
        "format"   : "json",
        "per_page" : 500,          # more than enough for annual data
        "mrv"      : end - start + 1,
        "date"     : f"{start}:{end}",
    }
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()

    payload = resp.json()
    # WB JSON v2: [metadata_dict, [data_records]]
    if not isinstance(payload, list) or len(payload) < 2:
        raise ValueError(f"Unexpected API response structure for {indicator_code}")

    records = payload[1]
    if records is None:
        raise ValueError(f"No records returned for {indicator_code}. "
                         "Check the indicator code or date range.")

    series = {}
    for rec in records:
        year_str = rec.get("date", "")
        value    = rec.get("value")
        if year_str.isdigit():
            series[int(year_str)] = value   # None stays None (missing)
    return series


# ─────────────────────────────────────────────
# 3. FETCH ALL INDICATORS
# ─────────────────────────────────────────────
print("=" * 60)
print("DATA COLLECTION — World Bank WDI API")
print(f"Country : India ({COUNTRY})")
print(f"Period  : {START_YR}–{END_YR}")
print("=" * 60)

all_series = {}
fetch_errors = []

for col_name, wb_code in INDICATORS.items():
    print(f"  Fetching  {col_name:30s} [{wb_code}] ...", end=" ", flush=True)
    try:
        series = fetch_wb_series(wb_code, COUNTRY, START_YR, END_YR)
        if not series:
            raise ValueError("Empty series returned")
        all_series[col_name] = series
        non_null = sum(1 for v in series.values() if v is not None)
        print(f"OK  ({non_null} non-null values over {len(series)} years)")
    except Exception as e:
        print(f"ERROR: {e}")
        fetch_errors.append((col_name, wb_code, str(e)))

if fetch_errors:
    print("\n⚠  FETCH ERRORS — the following indicators could not be retrieved:")
    for col, code, err in fetch_errors:
        print(f"   {col} ({code}): {err}")
    print("\nHalting. Please check connectivity or indicator codes before proceeding.")
    sys.exit(1)

print("\nAll indicators fetched successfully.\n")

# ─────────────────────────────────────────────
# 4. BUILD RAW DATAFRAME
# ─────────────────────────────────────────────
years = list(range(START_YR, END_YR + 1))
raw_data = {"Year": years}

for col_name in INDICATORS.keys():
    series = all_series[col_name]
    raw_data[col_name] = [series.get(y, None) for y in years]

raw_df = pd.DataFrame(raw_data)
raw_df["Year"] = raw_df["Year"].astype(int)

# ─────────────────────────────────────────────
# 5. SAVE RAW FILE (unmodified source values)
# ─────────────────────────────────────────────
raw_df.to_csv(RAW_FILE, index=False)
print(f"✔  Raw dataset saved  →  {RAW_FILE}")
print(f"   Shape: {raw_df.shape[0]} rows × {raw_df.shape[1]} columns\n")

# ─────────────────────────────────────────────
# 6. CLEANING STEPS  (transparent, documented)
# ─────────────────────────────────────────────
print("-" * 60)
print("CLEANING")
print("-" * 60)

clean_df = raw_df.copy()

# 6a. Correct data types
clean_df["Year"] = clean_df["Year"].astype(int)
numeric_cols = [c for c in clean_df.columns if c != "Year"]
for col in numeric_cols:
    clean_df[col] = pd.to_numeric(clean_df[col], errors="coerce")
print("  [6a] Data types enforced: Year→int, all indicators→float64")

# 6b. Sort by Year
clean_df.sort_values("Year", inplace=True)
clean_df.reset_index(drop=True, inplace=True)
print("  [6b] Sorted ascending by Year")

# 6c. Remove exact duplicate year rows (keep first)
dup_count = clean_df.duplicated(subset=["Year"]).sum()
if dup_count > 0:
    clean_df.drop_duplicates(subset=["Year"], keep="first", inplace=True)
    print(f"  [6c] Removed {dup_count} duplicate year row(s)")
else:
    print("  [6c] No duplicate year rows found")

# 6d. Identify and document missing values — do NOT impute or delete
missing_summary = clean_df[numeric_cols].isnull().sum()
total_missing   = missing_summary.sum()
print(f"  [6d] Missing value audit:")
for col, cnt in missing_summary.items():
    status = f"{cnt} missing" if cnt > 0 else "complete"
    print(f"       {col:30s}: {status}")
print(f"       Total missing cells: {total_missing}")
print("       NOTE: Missing values are retained as NaN — NOT imputed.")

# 6e. Restrict to rows where ALL key variables have at least a Year value
#     (rows where Year itself is null would be invalid — none expected here)
null_year = clean_df["Year"].isnull().sum()
if null_year > 0:
    clean_df.dropna(subset=["Year"], inplace=True)
    print(f"  [6e] Dropped {null_year} rows with null Year")
else:
    print("  [6e] No null Year values — all rows retained")

# 6f. Standardise column names (already set correctly via INDICATORS dict)
print(f"  [6f] Column names: {list(clean_df.columns)}")

# ─────────────────────────────────────────────
# 7. SAVE CLEANED FILE
# ─────────────────────────────────────────────
clean_df.to_csv(CLEAN_FILE, index=False)
print(f"\n✔  Cleaned dataset saved  →  {CLEAN_FILE}")
print(f"   Shape: {clean_df.shape[0]} rows × {clean_df.shape[1]} columns\n")

# ─────────────────────────────────────────────
# 8. METADATA FILE
# ─────────────────────────────────────────────
metadata = [
    {
        "Column_Name"       : "Year",
        "Variable_Definition": "Calendar year of observation",
        "Unit"              : "Year (YYYY)",
        "Source"            : "World Bank WDI",
        "Source_URL"        : "https://databank.worldbank.org/source/world-development-indicators",
        "WB_Indicator_Code" : "N/A",
        "Data_Period"       : f"{START_YR}–{END_YR}",
        "Notes"             : "Index variable; all series aligned to calendar year",
    },
    {
        "Column_Name"       : "GDP_Growth",
        "Variable_Definition": "Annual percentage growth rate of GDP at market prices based on constant local currency",
        "Unit"              : "Annual % change",
        "Source"            : "World Bank WDI",
        "Source_URL"        : WB_BASE.format(indicator="NY.GDP.MKTP.KD.ZG"),
        "WB_Indicator_Code" : "NY.GDP.MKTP.KD.ZG",
        "Data_Period"       : f"{START_YR}–{END_YR}",
        "Notes"             : "Dependent variable",
    },
    {
        "Column_Name"       : "Inflation",
        "Variable_Definition": "Inflation as measured by the consumer price index (CPI); annual % change",
        "Unit"              : "Annual % change",
        "Source"            : "World Bank WDI",
        "Source_URL"        : WB_BASE.format(indicator="FP.CPI.TOTL.ZG"),
        "WB_Indicator_Code" : "FP.CPI.TOTL.ZG",
        "Data_Period"       : f"{START_YR}–{END_YR}",
        "Notes"             : "Independent variable",
    },
    {
        "Column_Name"       : "FDI_Net_Inflows",
        "Variable_Definition": "Foreign direct investment net inflows as a share of GDP",
        "Unit"              : "% of GDP",
        "Source"            : "World Bank WDI",
        "Source_URL"        : WB_BASE.format(indicator="BX.KLT.DINV.WD.GD.ZS"),
        "WB_Indicator_Code" : "BX.KLT.DINV.WD.GD.ZS",
        "Data_Period"       : f"{START_YR}–{END_YR}",
        "Notes"             : "Independent variable",
    },
    {
        "Column_Name"       : "Exports",
        "Variable_Definition": "Exports of goods and services as a share of GDP",
        "Unit"              : "% of GDP",
        "Source"            : "World Bank WDI",
        "Source_URL"        : WB_BASE.format(indicator="NE.EXP.GNFS.ZS"),
        "WB_Indicator_Code" : "NE.EXP.GNFS.ZS",
        "Data_Period"       : f"{START_YR}–{END_YR}",
        "Notes"             : "Independent variable",
    },
    {
        "Column_Name"       : "Gross_Capital_Formation",
        "Variable_Definition": "Gross capital formation (formerly gross domestic investment) as a share of GDP",
        "Unit"              : "% of GDP",
        "Source"            : "World Bank WDI",
        "Source_URL"        : WB_BASE.format(indicator="NE.GDI.TOTL.ZS"),
        "WB_Indicator_Code" : "NE.GDI.TOTL.ZS",
        "Data_Period"       : f"{START_YR}–{END_YR}",
        "Notes"             : "Independent variable",
    },
    {
        "Column_Name"       : "Unemployment",
        "Variable_Definition": "Unemployment as % of total labour force (national estimate, ILO modelled)",
        "Unit"              : "% of total labour force",
        "Source"            : "World Bank WDI",
        "Source_URL"        : WB_BASE.format(indicator="SL.UEM.TOTL.ZS"),
        "WB_Indicator_Code" : "SL.UEM.TOTL.ZS",
        "Data_Period"       : f"{START_YR}–{END_YR}",
        "Notes"             : "Independent variable; ILO modelled estimates used where survey data gaps exist",
    },
]

meta_df = pd.DataFrame(metadata)
meta_df.to_csv(META_FILE, index=False)
print(f"✔  Metadata file saved   →  {META_FILE}\n")

# ─────────────────────────────────────────────
# 9. VERIFICATION REPORT
# ─────────────────────────────────────────────
print("=" * 60)
print("VERIFICATION REPORT")
print("=" * 60)

# 9a. Shape
n_obs = clean_df.shape[0]
n_col = clean_df.shape[1]
print(f"\n  Observations  : {n_obs}")
print(f"  Columns       : {n_col}  →  {list(clean_df.columns)}")

# 9b. Year range
yr_min = clean_df["Year"].min()
yr_max = clean_df["Year"].max()
print(f"  Year range    : {yr_min} – {yr_max}")

# 9c. Duplicate rows
dup_rows = clean_df.duplicated().sum()
print(f"  Duplicate rows: {dup_rows}  {'⚠ ATTENTION' if dup_rows > 0 else '✔ None'}")

# 9d. Missing values
print(f"\n  Missing values by column:")
for col in clean_df.columns:
    n_miss = clean_df[col].isnull().sum()
    pct    = round(n_miss / n_obs * 100, 1)
    flag   = "  ⚠" if n_miss > 0 else "  ✔"
    print(f"    {col:30s}: {n_miss:2d} missing  ({pct}%){flag}")

# 9e. Data types
print(f"\n  Data types:")
for col, dtype in clean_df.dtypes.items():
    print(f"    {col:30s}: {dtype}")

# 9f. Value range sanity checks
print(f"\n  Value range sanity checks:")
expected_ranges = {
    "GDP_Growth"             : (-20,  20),
    "Inflation"              : (-5,   30),
    "FDI_Net_Inflows"        : (-2,   10),
    "Exports"                : (0,    60),
    "Gross_Capital_Formation": (10,   60),
    "Unemployment"           : (0,    20),
}
for col, (lo, hi) in expected_ranges.items():
    series = clean_df[col].dropna()
    if series.empty:
        print(f"    {col:30s}: No data to check  ⚠")
        continue
    mn  = round(series.min(), 3)
    mx  = round(series.max(), 3)
    out = series[(series < lo) | (series > hi)]
    flag = f"  ⚠ {len(out)} value(s) outside [{lo}, {hi}]" if not out.empty else "  ✔ within expected range"
    print(f"    {col:30s}: min={mn:8.3f}  max={mx:8.3f}{flag}")

# 9g. Compatibility check — all annual, same Year column
print(f"\n  Temporal alignment : All variables share the same 'Year' column  ✔")
print(f"  Observation unit   : Annual (one row per calendar year)          ✔")

print("\n" + "=" * 60)
print("DATA COLLECTION AND PREPARATION COMPLETE")
print("=" * 60)
print(f"\nFiles written:")
print(f"  1. {RAW_FILE}")
print(f"  2. {CLEAN_FILE}")
print(f"  3. {META_FILE}")
print(f"\nScript completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
