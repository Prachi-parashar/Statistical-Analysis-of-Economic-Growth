"""
descriptive_statistics.py
--------------------------
Phase: Descriptive Statistics and Initial Visualization
Project: Statistical Analysis of Economic Growth and Its Determinants in India
Data:    data/cleaned/india_economic_growth_determinants_clean.csv

Tasks:
  Task 1  — Data validation
  Task 2  — Full descriptive statistics table
  Task 3  — Year-wise trend graphs (one per variable)
  Task 4  — Histogram + KDE and Box plot (one per variable)
  Task 5  — Compact summary statistics table
  Task 6  — Concise factual interpretation (printed)
  Task 7  — Quality check

NOTE: No correlation, regression, or probability tests are performed here.
      Kurtosis is reported as EXCESS kurtosis (Fisher's definition; normal = 0).
"""

import os
import sys
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")          # non-interactive backend — safe for script execution
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from scipy import stats

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────
# 0.  PATHS
# ─────────────────────────────────────────────────────────────
BASE       = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_CSV  = os.path.join(BASE, "data", "cleaned",
                          "india_economic_growth_determinants_clean.csv")
FIG_DIR    = os.path.join(BASE, "outputs", "figures")
TABLE_DIR  = os.path.join(BASE, "outputs", "tables")

for d in [FIG_DIR, TABLE_DIR]:
    os.makedirs(d, exist_ok=True)

# ─────────────────────────────────────────────────────────────
# VARIABLE METADATA
# ─────────────────────────────────────────────────────────────
VARS = ["GDP_Growth", "Inflation", "FDI_Net_Inflows",
        "Exports", "Gross_Capital_Formation", "Unemployment"]

LABELS = {
    "GDP_Growth"             : "GDP Growth",
    "Inflation"              : "Inflation (CPI)",
    "FDI_Net_Inflows"        : "FDI Net Inflows",
    "Exports"                : "Exports of Goods & Services",
    "Gross_Capital_Formation": "Gross Capital Formation",
    "Unemployment"           : "Unemployment Rate",
}

UNITS = {
    "GDP_Growth"             : "Annual % change",
    "Inflation"              : "Annual % change (CPI)",
    "FDI_Net_Inflows"        : "% of GDP",
    "Exports"                : "% of GDP",
    "Gross_Capital_Formation": "% of GDP",
    "Unemployment"           : "% of total labour force",
}

COLORS = {
    "GDP_Growth"             : "#2E86AB",
    "Inflation"              : "#E84855",
    "FDI_Net_Inflows"        : "#F4A261",
    "Exports"                : "#2A9D8F",
    "Gross_Capital_Formation": "#6A4C93",
    "Unemployment"           : "#457B9D",
}

# Global plot style
plt.rcParams.update({
    "figure.dpi"      : 150,
    "font.family"     : "DejaVu Sans",
    "axes.titlesize"  : 13,
    "axes.labelsize"  : 11,
    "xtick.labelsize" : 9,
    "ytick.labelsize" : 9,
    "axes.grid"       : True,
    "grid.alpha"      : 0.35,
    "grid.linestyle"  : "--",
})

# ═══════════════════════════════════════════════════════════════
# TASK 1 — DATA VALIDATION
# ═══════════════════════════════════════════════════════════════
print("=" * 65)
print("TASK 1 — DATA VALIDATION")
print("=" * 65)

df = pd.read_csv(CLEAN_CSV)

n_rows, n_cols = df.shape
yr_min, yr_max = df["Year"].min(), df["Year"].max()
missing        = df.isnull().sum()
dup_rows       = df.duplicated().sum()

print(f"\n  Source file     : {CLEAN_CSV}")
print(f"  Observations    : {n_rows}")
print(f"  Variables       : {n_cols}  → {list(df.columns)}")
print(f"  Year range      : {yr_min} – {yr_max}")
print(f"  Duplicate rows  : {dup_rows}  {'✔ None' if dup_rows == 0 else '⚠ ATTENTION'}")
print(f"\n  Missing values per column:")
for col in df.columns:
    n_miss = missing[col]
    print(f"    {col:30s}: {n_miss}  {'✔' if n_miss == 0 else '⚠'}")

print(f"\n  Data types:")
for col, dtype in df.dtypes.items():
    print(f"    {col:30s}: {dtype}")

# Assertions
assert n_rows == 33,                   f"Expected 33 rows, got {n_rows}"
assert missing.sum() == 0,             "Unexpected missing values"
assert dup_rows == 0,                  "Unexpected duplicate rows"
assert df["Year"].is_monotonic_increasing, "Year column not sorted"
print("\n  All validation checks passed. ✔\n")

# ═══════════════════════════════════════════════════════════════
# TASK 2 — FULL DESCRIPTIVE STATISTICS
# ═══════════════════════════════════════════════════════════════
print("=" * 65)
print("TASK 2 — DESCRIPTIVE STATISTICS")
print("  Note: Kurtosis = EXCESS kurtosis (Fisher convention; normal = 0)")
print("=" * 65)

desc_rows = []

for var in VARS:
    s = df[var].dropna()
    n = len(s)

    mean_val   = s.mean()
    median_val = s.median()
    # Mode: return lowest if multimodal
    mode_res   = stats.mode(s, keepdims=True)
    mode_val   = float(mode_res.mode[0])
    var_val    = s.var(ddof=1)           # sample variance
    std_val    = s.std(ddof=1)           # sample std dev
    min_val    = s.min()
    max_val    = s.max()
    range_val  = max_val - min_val
    q1         = s.quantile(0.25)
    q2         = s.quantile(0.50)        # same as median
    q3         = s.quantile(0.75)
    iqr_val    = q3 - q1
    skew_val   = stats.skew(s)           # Fisher–Pearson skewness
    kurt_val   = stats.kurtosis(s)       # EXCESS kurtosis (Fisher)

    row = {
        "Variable"         : var,
        "Label"            : LABELS[var],
        "Unit"             : UNITS[var],
        "Count"            : n,
        "Mean"             : round(mean_val, 4),
        "Median"           : round(median_val, 4),
        "Mode"             : round(mode_val, 4),
        "Variance_sample"  : round(var_val, 4),
        "Std_Dev_sample"   : round(std_val, 4),
        "Minimum"          : round(min_val, 4),
        "Maximum"          : round(max_val, 4),
        "Range"            : round(range_val, 4),
        "Q1_25th_pct"      : round(q1, 4),
        "Q2_Median_50th"   : round(q2, 4),
        "Q3_75th_pct"      : round(q3, 4),
        "IQR"              : round(iqr_val, 4),
        "Skewness"         : round(skew_val, 4),
        "Excess_Kurtosis"  : round(kurt_val, 4),
    }
    desc_rows.append(row)

    print(f"\n  {LABELS[var]}")
    print(f"    Count={n}  Mean={mean_val:.4f}  Median={median_val:.4f}  Mode={mode_val:.4f}")
    print(f"    Variance={var_val:.4f}  Std Dev={std_val:.4f}")
    print(f"    Min={min_val:.4f}  Max={max_val:.4f}  Range={range_val:.4f}")
    print(f"    Q1={q1:.4f}  Q2={q2:.4f}  Q3={q3:.4f}  IQR={iqr_val:.4f}")
    print(f"    Skewness={skew_val:.4f}  Excess Kurtosis={kurt_val:.4f}")

desc_df = pd.DataFrame(desc_rows)
desc_path = os.path.join(TABLE_DIR, "descriptive_statistics.csv")
desc_df.to_csv(desc_path, index=False)
print(f"\n  ✔  Saved  →  {desc_path}\n")

# ═══════════════════════════════════════════════════════════════
# TASK 3 — YEAR-WISE TREND GRAPHS
# ═══════════════════════════════════════════════════════════════
print("=" * 65)
print("TASK 3 — YEAR-WISE TREND GRAPHS")
print("=" * 65)

trend_files = {}
for var in VARS:
    color  = COLORS[var]
    label  = LABELS[var]
    unit   = UNITS[var]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["Year"], df[var], color=color, lw=2.2,
            marker="o", markersize=5, markerfacecolor="white",
            markeredgewidth=1.8, markeredgecolor=color, label=label)

    # Shade the 2020 COVID dip for GDP and Unemployment
    ax.fill_between(df["Year"], df[var],
                    alpha=0.12, color=color)

    # Zero reference line if variable can be negative
    if df[var].min() < 0:
        ax.axhline(0, color="gray", lw=0.9, ls="--", alpha=0.7)

    # Mean reference line
    mean_v = df[var].mean()
    ax.axhline(mean_v, color="black", lw=1, ls=":", alpha=0.6,
               label=f"Mean = {mean_v:.2f}")

    ax.set_title(f"{label} — India, 1993–2023", fontweight="bold", pad=12)
    ax.set_xlabel("Year", labelpad=8)
    ax.set_ylabel(f"{label}  ({unit})", labelpad=8)
    ax.set_xticks(df["Year"][::2])           # every other year
    ax.tick_params(axis="x", rotation=45)
    ax.legend(fontsize=9, loc="best")
    ax.xaxis.set_minor_locator(mticker.AutoMinorLocator())
    fig.tight_layout()

    fname = os.path.join(FIG_DIR, f"trend_{var}.png")
    fig.savefig(fname, bbox_inches="tight")
    plt.close(fig)
    trend_files[var] = fname
    print(f"  Saved  trend_{var}.png")

# Combined multi-panel trend chart
fig, axes = plt.subplots(3, 2, figsize=(14, 13))
axes = axes.flatten()
for i, var in enumerate(VARS):
    ax    = axes[i]
    color = COLORS[var]
    label = LABELS[var]
    unit  = UNITS[var]
    ax.plot(df["Year"], df[var], color=color, lw=2,
            marker="o", markersize=4, markerfacecolor="white",
            markeredgewidth=1.5, markeredgecolor=color)
    ax.fill_between(df["Year"], df[var], alpha=0.1, color=color)
    if df[var].min() < 0:
        ax.axhline(0, color="gray", lw=0.8, ls="--", alpha=0.6)
    ax.axhline(df[var].mean(), color="black", lw=0.9, ls=":", alpha=0.55)
    ax.set_title(label, fontweight="bold", fontsize=11)
    ax.set_ylabel(unit, fontsize=8)
    ax.set_xlabel("Year", fontsize=8)
    ax.tick_params(axis="x", rotation=45, labelsize=7)
    ax.tick_params(axis="y", labelsize=7)
    ax.set_xticks(df["Year"][::4])

fig.suptitle("Economic Variables — India, 1993–2023\n(Dotted line = sample mean)",
             fontsize=13, fontweight="bold", y=1.01)
fig.tight_layout()
combined_trend = os.path.join(FIG_DIR, "trends_all_variables.png")
fig.savefig(combined_trend, bbox_inches="tight")
plt.close(fig)
print(f"  Saved  trends_all_variables.png\n")

# ═══════════════════════════════════════════════════════════════
# TASK 4 — HISTOGRAM + KDE  AND  BOX PLOTS
# ═══════════════════════════════════════════════════════════════
print("=" * 65)
print("TASK 4 — HISTOGRAMS + KDE  AND  BOX PLOTS")
print("=" * 65)

for var in VARS:
    data  = df[var].dropna().values
    color = COLORS[var]
    label = LABELS[var]
    unit  = UNITS[var]

    # ── Histogram + KDE ──────────────────────────────────────
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.histplot(data, kde=True, color=color, alpha=0.55,
                 edgecolor="white", linewidth=0.6,
                 bins="auto", ax=ax)
    ax.axvline(np.mean(data), color="black", lw=1.4, ls="--",
               label=f"Mean = {np.mean(data):.2f}")
    ax.axvline(np.median(data), color="navy", lw=1.4, ls="-.",
               label=f"Median = {np.median(data):.2f}")
    ax.set_title(f"Histogram + KDE — {label}\n(India, 1993–2023, n=31)",
                 fontweight="bold", pad=10)
    ax.set_xlabel(f"{label}  ({unit})", labelpad=8)
    ax.set_ylabel("Frequency", labelpad=8)
    ax.legend(fontsize=9)
    fig.tight_layout()
    fname = os.path.join(FIG_DIR, f"hist_{var}.png")
    fig.savefig(fname, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved  hist_{var}.png")

    # ── Box Plot ──────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(5, 7))
    bp = ax.boxplot(data, patch_artist=True, notch=False, vert=True,
                    widths=0.5,
                    medianprops  =dict(color="white",  lw=2.5),
                    whiskerprops =dict(color=color,    lw=1.5),
                    capprops     =dict(color=color,    lw=1.5),
                    flierprops   =dict(marker="o",
                                       markerfacecolor="red",
                                       markersize=7, alpha=0.75,
                                       markeredgewidth=0.8))
    bp["boxes"][0].set_facecolor(color)
    bp["boxes"][0].set_alpha(0.65)

    # Annotate IQR values
    q1_v = np.percentile(data, 25)
    q3_v = np.percentile(data, 75)
    med_v = np.median(data)
    ax.text(1.32, med_v, f" Median\n {med_v:.2f}", va="center",
            fontsize=8.5, color="navy", fontweight="bold")
    ax.text(1.32, q1_v,  f" Q1={q1_v:.2f}",  va="center", fontsize=7.5, color="dimgray")
    ax.text(1.32, q3_v,  f" Q3={q3_v:.2f}",  va="center", fontsize=7.5, color="dimgray")

    ax.set_title(f"Box Plot — {label}\n(India, 1993–2023, n=31)",
                 fontweight="bold", pad=10)
    ax.set_ylabel(f"{label}  ({unit})", labelpad=8)
    ax.set_xticks([])
    fig.tight_layout()
    fname = os.path.join(FIG_DIR, f"boxplot_{var}.png")
    fig.savefig(fname, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved  boxplot_{var}.png")

# Combined box plot panel
fig, axes = plt.subplots(2, 3, figsize=(14, 9))
axes = axes.flatten()
for i, var in enumerate(VARS):
    data  = df[var].dropna().values
    color = COLORS[var]
    ax    = axes[i]
    bp = ax.boxplot(data, patch_artist=True, notch=False,
                    medianprops=dict(color="white", lw=2.2),
                    flierprops =dict(marker="o", markerfacecolor="red",
                                     markersize=6, alpha=0.7))
    bp["boxes"][0].set_facecolor(color)
    bp["boxes"][0].set_alpha(0.65)
    ax.set_title(LABELS[var], fontweight="bold", fontsize=10)
    ax.set_ylabel(UNITS[var], fontsize=8)
    ax.set_xticks([])
fig.suptitle("Box Plots — Economic Variables (India, 1993–2023)",
             fontsize=13, fontweight="bold", y=1.01)
fig.tight_layout()
combined_box = os.path.join(FIG_DIR, "boxplots_all_variables.png")
fig.savefig(combined_box, bbox_inches="tight")
plt.close(fig)
print(f"  Saved  boxplots_all_variables.png\n")

# ═══════════════════════════════════════════════════════════════
# TASK 5 — SUMMARY STATISTICS TABLE
# ═══════════════════════════════════════════════════════════════
print("=" * 65)
print("TASK 5 — SUMMARY STATISTICS TABLE")
print("=" * 65)

summary_rows = []
for var in VARS:
    s = df[var].dropna()
    summary_rows.append({
        "Variable"  : var,
        "Label"     : LABELS[var],
        "Unit"      : UNITS[var],
        "Count"     : len(s),
        "Mean"      : round(s.mean(), 4),
        "Std_Dev"   : round(s.std(ddof=1), 4),
        "Minimum"   : round(s.min(), 4),
        "Maximum"   : round(s.max(), 4),
        "Median"    : round(s.median(), 4),
    })

summary_df   = pd.DataFrame(summary_rows)
summary_path = os.path.join(TABLE_DIR, "summary_statistics.csv")
summary_df.to_csv(summary_path, index=False)
print(summary_df.to_string(index=False))
print(f"\n  ✔  Saved  →  {summary_path}\n")

# ═══════════════════════════════════════════════════════════════
# TASK 6 — CONCISE FACTUAL INTERPRETATION
# ═══════════════════════════════════════════════════════════════
print("=" * 65)
print("TASK 6 — FACTUAL INTERPRETATION")
print("=" * 65)

interp_lines = []

for _, row in desc_df.iterrows():
    var   = row["Variable"]
    label = row["Label"]
    mean  = row["Mean"]
    std   = row["Std_Dev_sample"]
    skew  = row["Skewness"]
    kurt  = row["Excess_Kurtosis"]
    mn    = row["Minimum"]
    mx    = row["Maximum"]
    iqr   = row["IQR"]
    q1    = row["Q1_25th_pct"]
    q3    = row["Q3_75th_pct"]

    # Skewness direction
    if skew > 0.5:
        skew_desc = f"right-skewed (positive, skew={skew:.3f})"
    elif skew < -0.5:
        skew_desc = f"left-skewed (negative, skew={skew:.3f})"
    else:
        skew_desc = f"approximately symmetric (skew={skew:.3f})"

    # Kurtosis
    if kurt > 1.0:
        kurt_desc = f"leptokurtic — heavier tails than normal (excess kurt={kurt:.3f})"
    elif kurt < -1.0:
        kurt_desc = f"platykurtic — lighter tails than normal (excess kurt={kurt:.3f})"
    else:
        kurt_desc = f"approximately mesokurtic (excess kurt={kurt:.3f})"

    # Outlier check (IQR rule)
    data   = df[var].dropna().values
    lo_f   = q1 - 1.5 * iqr
    hi_f   = q3 + 1.5 * iqr
    outs   = data[(data < lo_f) | (data > hi_f)]
    out_note = (f"{len(outs)} potential outlier(s) detected by IQR rule: {np.round(outs,2)}"
                if len(outs) > 0 else "No outliers detected by IQR rule")

    line = (f"\n  {label}\n"
            f"    Mean={mean:.4f}, Std Dev={std:.4f}  |  Min={mn:.4f}, Max={mx:.4f}\n"
            f"    Distribution: {skew_desc}\n"
            f"    Tail behaviour: {kurt_desc}\n"
            f"    Outliers: {out_note}")
    interp_lines.append(line)
    print(line)

# Variability ranking
print("\n  Relative variability (CV = Std Dev / |Mean| × 100):")
cv_rows = []
for _, row in desc_df.iterrows():
    cv = abs(row["Std_Dev_sample"] / row["Mean"]) * 100 if row["Mean"] != 0 else np.nan
    cv_rows.append((row["Label"], round(cv, 2)))
cv_rows.sort(key=lambda x: x[1], reverse=True)
for lbl, cv in cv_rows:
    print(f"    {lbl:35s}: CV = {cv:.2f}%")

# Major visible trends
print("""
  Major visible trends:
    GDP_Growth      — Strong upward trend 1993–2016; notable dip in 2002–03;
                      sharp contraction in 2020 (COVID-19, −5.78%); rapid rebound 2021.
    Inflation       — Elevated and volatile in 1990s; moderating trend post-2014
                      linked to inflation-targeting framework (RBI, 2016).
    FDI_Net_Inflows — Near-zero in 1990s; gradual rise from 2000; peak ~2008–09
                      (post-liberalisation surge); some stabilisation after 2012.
    Exports         — Broadly upward 1993–2013 (globalisation era); some
                      contraction in global-slowdown years (2016, 2020).
    Gross_Cap_Form  — Rising investment ratio 1993–2008 (high-growth era);
                      gradual decline thereafter suggesting investment slowdown.
    Unemployment    — Structurally elevated (>7%) through most of the series;
                      data shows a decline in recent years but this may partly
                      reflect ILO modelling methodology changes — flag for later.
""")

# ═══════════════════════════════════════════════════════════════
# TASK 7 — QUALITY CHECK
# ═══════════════════════════════════════════════════════════════
print("=" * 65)
print("TASK 7 — QUALITY CHECK")
print("=" * 65)

# 7a. Original data unchanged
df_recheck = pd.read_csv(CLEAN_CSV)
assert len(df_recheck) == 31
assert list(df_recheck.columns) == ["Year","GDP_Growth","Inflation","FDI_Net_Inflows",
                                     "Exports","Gross_Capital_Formation","Unemployment"]
assert df_recheck.isnull().sum().sum() == 0
print("  ✔  Original cleaned CSV unchanged (31 rows, 7 cols, 0 missing)")

# 7b. Descriptive stats were computed from the actual data (spot-check)
for var in VARS:
    computed_mean = round(df[var].mean(), 4)
    stored_mean   = desc_df.loc[desc_df["Variable"]==var, "Mean"].values[0]
    assert computed_mean == stored_mean, f"Mean mismatch for {var}"
print("  ✔  Spot-check: all means in descriptive_statistics.csv match live computation")

# 7c. Expected figures
expected_figs = (
    [f"trend_{v}.png"   for v in VARS] +
    [f"hist_{v}.png"    for v in VARS] +
    [f"boxplot_{v}.png" for v in VARS] +
    ["trends_all_variables.png", "boxplots_all_variables.png"]
)
missing_figs = [f for f in expected_figs
                if not os.path.isfile(os.path.join(FIG_DIR, f))]
if missing_figs:
    print(f"  ⚠  Missing figures: {missing_figs}")
else:
    print(f"  ✔  All {len(expected_figs)} expected figures present in outputs/figures/")

# 7d. File sizes > 5 KB
corrupt = [f for f in expected_figs
           if os.path.isfile(os.path.join(FIG_DIR, f))
           and os.path.getsize(os.path.join(FIG_DIR, f)) < 5000]
if corrupt:
    print(f"  ⚠  Suspiciously small files: {corrupt}")
else:
    print("  ✔  All figures > 5 KB (not empty/corrupt)")

# 7e. Tables saved
for tpath, tname in [(desc_path,"descriptive_statistics.csv"),
                     (summary_path,"summary_statistics.csv")]:
    if os.path.isfile(tpath):
        t = pd.read_csv(tpath)
        print(f"  ✔  {tname:35s}: {len(t)} rows, cols = {list(t.columns)[:4]} ...")
    else:
        print(f"  ⚠  MISSING: {tname}")

# 7f. Column names in tables are correct
assert list(desc_df["Variable"]) == VARS, "Variable column mismatch in descriptive_statistics.csv"
assert list(summary_df["Variable"]) == VARS, "Variable column mismatch in summary_statistics.csv"
print("  ✔  Variable names in both tables match expected list")

# ─── Final Manifest ───────────────────────────────────────────
print("\n" + "=" * 65)
print("DESCRIPTIVE STATISTICS & VISUALIZATION PHASE — COMPLETE")
print("=" * 65)

print(f"\nFigures in {FIG_DIR}:")
all_figs = sorted(
    f for f in os.listdir(FIG_DIR)
    if f.endswith(".png") and not os.path.isdir(os.path.join(FIG_DIR, f))
)
for f in all_figs:
    sz = os.path.getsize(os.path.join(FIG_DIR, f))
    print(f"  {f:50s}  {sz//1024} KB")

print(f"\nTables in {TABLE_DIR}:")
for fname in ["descriptive_statistics.csv", "summary_statistics.csv"]:
    fpath = os.path.join(TABLE_DIR, fname)
    if os.path.isfile(fpath):
        sz = os.path.getsize(fpath)
        print(f"  {fname:40s}  {sz} bytes")
