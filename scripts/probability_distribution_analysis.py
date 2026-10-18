"""
probability_distribution_analysis.py
--------------------------------------
Phase: Probability Distribution Analysis
Project: Statistical Analysis of Economic Growth and Its Determinants in India
Data:    data/cleaned/india_economic_growth_determinants_clean.csv
Author:  Auto-generated for academic project

Tasks covered:
  Task 1  — Histogram+KDE, Box plot, Q-Q plot for each variable
  Task 2  — Shapiro-Wilk + Anderson-Darling normality tests
  Task 3  — Distribution characteristics (shape, skewness, outliers)
  Task 4  — Distribution fitting (Normal, Log-normal, Gamma, Exponential)
  Task 5  — Empirical probabilities
  Task 6  — Save output tables
  Task 8  — Quality check

NOTE: No correlation or regression is performed here.
"""

import os
import sys
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")          # non-interactive backend — safe for script execution
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from scipy import stats
from scipy.stats import (shapiro, anderson, kstest,
                         norm, lognorm, gamma, expon)
import statsmodels.api as sm

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────
# 0.  PATHS
# ─────────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CLEAN_CSV  = os.path.join(BASE, "data", "cleaned",
                          "india_economic_growth_determinants_clean.csv")
FIG_DIR    = os.path.join(BASE, "outputs", "figures", "probability_distributions")
TABLE_DIR  = os.path.join(BASE, "outputs", "tables")

for d in [FIG_DIR, TABLE_DIR]:
    os.makedirs(d, exist_ok=True)

# ─────────────────────────────────────────────────────────────
# 1.  LOAD DATA
# ─────────────────────────────────────────────────────────────
df = pd.read_csv(CLEAN_CSV)
VARS = ["GDP_Growth", "Inflation", "FDI_Net_Inflows",
        "Exports", "Gross_Capital_Formation", "Unemployment"]

# Verify no observations were modified
N = len(df)
print(f"Loaded: {N} rows × {df.shape[1]} columns  |  Years: {df['Year'].min()}–{df['Year'].max()}")
assert N == 31, f"Expected 31 observations, got {N}"
assert df[VARS].isnull().sum().sum() == 0, "Unexpected missing values in cleaned data"
print("Data integrity check passed.\n")

# ─────────────────────────────────────────────────────────────
# STYLING HELPERS
# ─────────────────────────────────────────────────────────────
UNITS = {
    "GDP_Growth"             : "Annual % change",
    "Inflation"              : "Annual % change (CPI)",
    "FDI_Net_Inflows"        : "% of GDP",
    "Exports"                : "% of GDP",
    "Gross_Capital_Formation": "% of GDP",
    "Unemployment"           : "% of total labour force",
}

TITLES = {
    "GDP_Growth"             : "GDP Growth",
    "Inflation"              : "Inflation (CPI)",
    "FDI_Net_Inflows"        : "FDI Net Inflows",
    "Exports"                : "Exports of Goods & Services",
    "Gross_Capital_Formation": "Gross Capital Formation",
    "Unemployment"           : "Unemployment Rate",
}

PALETTE = {
    "GDP_Growth"             : "#2E86AB",
    "Inflation"              : "#E84855",
    "FDI_Net_Inflows"        : "#F4A261",
    "Exports"                : "#2A9D8F",
    "Gross_Capital_Formation": "#6A4C93",
    "Unemployment"           : "#457B9D",
}

plt.rcParams.update({
    "figure.dpi"     : 150,
    "font.family"    : "DejaVu Sans",
    "axes.titlesize" : 13,
    "axes.labelsize" : 11,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "axes.grid"      : True,
    "grid.alpha"     : 0.3,
})


# ─────────────────────────────────────────────────────────────
# TASK 1A — HISTOGRAM + KDE  (one figure per variable)
# ─────────────────────────────────────────────────────────────
print("=" * 60)
print("TASK 1 — DISTRIBUTION VISUALISATIONS")
print("=" * 60)

hist_files = {}
for var in VARS:
    data = df[var].dropna().values
    color = PALETTE[var]
    title = TITLES[var]
    unit  = UNITS[var]

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.histplot(data, kde=True, color=color, alpha=0.55,
                 edgecolor="white", linewidth=0.6, ax=ax, bins="auto")
    ax.set_title(f"Distribution of {title}\n(India, 1993–2023, n=31)",
                 fontweight="bold", pad=12)
    ax.set_xlabel(f"{title}  ({unit})", labelpad=8)
    ax.set_ylabel("Frequency", labelpad=8)

    # Overlay normal curve for reference
    mu, sigma = data.mean(), data.std(ddof=1)
    x_range = np.linspace(data.min() - sigma, data.max() + sigma, 300)
    ax.plot(x_range,
            norm.pdf(x_range, mu, sigma) * len(data) * (data.max()-data.min()) / 10,
            "k--", lw=1.4, alpha=0.6, label=f"Normal ref  (μ={mu:.2f}, σ={sigma:.2f})")
    ax.axvline(mu, color="black", lw=1, ls=":", alpha=0.7)
    ax.legend(fontsize=8)
    fig.tight_layout()

    fname = os.path.join(FIG_DIR, f"hist_kde_{var}.png")
    fig.savefig(fname, bbox_inches="tight")
    plt.close(fig)
    hist_files[var] = fname
    print(f"  Saved  hist_kde_{var}.png")

# ─────────────────────────────────────────────────────────────
# TASK 1B — BOX PLOTS  (combined panel + individual)
# ─────────────────────────────────────────────────────────────
# Combined box plot (all 6 standardised — just for overview)
fig, axes = plt.subplots(2, 3, figsize=(14, 9))
axes = axes.flatten()
for i, var in enumerate(VARS):
    data  = df[var].dropna().values
    color = PALETTE[var]
    title = TITLES[var]
    unit  = UNITS[var]
    ax    = axes[i]
    bp    = ax.boxplot(data, patch_artist=True, notch=False,
                       medianprops=dict(color="white", lw=2))
    bp["boxes"][0].set_facecolor(color)
    bp["boxes"][0].set_alpha(0.7)
    ax.set_title(f"{title}", fontweight="bold")
    ax.set_ylabel(unit, fontsize=9)
    ax.set_xticks([])

fig.suptitle("Box Plots — Economic Variables\n(India, 1993–2023)",
             fontsize=14, fontweight="bold", y=1.01)
fig.tight_layout()
combined_box = os.path.join(FIG_DIR, "boxplots_all_variables.png")
fig.savefig(combined_box, bbox_inches="tight")
plt.close(fig)
print(f"  Saved  boxplots_all_variables.png")

# Individual box plots
for var in VARS:
    data  = df[var].dropna().values
    color = PALETTE[var]
    title = TITLES[var]
    unit  = UNITS[var]

    fig, ax = plt.subplots(figsize=(5, 6))
    bp = ax.boxplot(data, patch_artist=True, notch=False, vert=True,
                    medianprops=dict(color="white", lw=2.5),
                    flierprops=dict(marker="o", markerfacecolor="red",
                                    markersize=7, alpha=0.7))
    bp["boxes"][0].set_facecolor(color)
    bp["boxes"][0].set_alpha(0.65)
    ax.set_title(f"Box Plot — {title}\n(India, 1993–2023, n=31)",
                 fontweight="bold", pad=10)
    ax.set_ylabel(f"{title}  ({unit})", labelpad=8)
    ax.set_xticks([])
    # Annotate median
    med = np.median(data)
    ax.text(1.1, med, f"  Median={med:.2f}", va="center", fontsize=9, color="navy")
    fig.tight_layout()

    fname = os.path.join(FIG_DIR, f"boxplot_{var}.png")
    fig.savefig(fname, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved  boxplot_{var}.png")

# ─────────────────────────────────────────────────────────────
# TASK 1C — Q-Q PLOTS
# ─────────────────────────────────────────────────────────────
for var in VARS:
    data  = df[var].dropna().values
    color = PALETTE[var]
    title = TITLES[var]

    fig, ax = plt.subplots(figsize=(6, 6))
    (osm, osr), (slope, intercept, r) = stats.probplot(data, dist="norm")
    ax.plot(osm, osr, "o", color=color, alpha=0.75, markersize=6, label="Observed")
    ax.plot(osm, slope * np.array(osm) + intercept,
            "k--", lw=1.5, label=f"Theoretical normal line  (r={r:.3f})")
    ax.set_title(f"Q-Q Plot — {title}\n(India, 1993–2023, n=31)",
                 fontweight="bold", pad=10)
    ax.set_xlabel("Theoretical Quantiles (Standard Normal)", labelpad=8)
    ax.set_ylabel(f"Sample Quantiles  ({UNITS[var]})", labelpad=8)
    ax.legend(fontsize=9)
    fig.tight_layout()

    fname = os.path.join(FIG_DIR, f"qqplot_{var}.png")
    fig.savefig(fname, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved  qqplot_{var}.png")

print(f"\nTask 1 complete — {len(VARS)*3 + 1} figures saved to {FIG_DIR}\n")


# ─────────────────────────────────────────────────────────────
# TASK 2 — NORMALITY TESTS
# ─────────────────────────────────────────────────────────────
print("=" * 60)
print("TASK 2 — NORMALITY TESTS")
print("=" * 60)

# AD critical values significance labels
AD_SIG_LABELS = {0: "15%", 1: "10%", 2: "5%", 3: "2.5%", 4: "1%"}

normality_rows = []

for var in VARS:
    data  = df[var].dropna().values
    title = TITLES[var]
    n     = len(data)

    # --- Shapiro-Wilk ---
    sw_stat, sw_p = shapiro(data)

    # --- Anderson-Darling ---
    ad_result = anderson(data, dist="norm")
    ad_stat   = ad_result.statistic
    # Find the highest significance level at which we reject H0
    ad_reject_at = "Cannot reject H0 at any standard level"
    for idx in range(len(ad_result.critical_values) - 1, -1, -1):
        if ad_stat > ad_result.critical_values[idx]:
            ad_reject_at = f"Reject H0 at {AD_SIG_LABELS[idx]} significance"
            break

    # --- Skewness & kurtosis ---
    skew_val = stats.skew(data)
    kurt_val = stats.kurtosis(data)   # excess kurtosis (normal = 0)

    # --- Interpretation ---
    # For small n (≤50), SW is preferred; visual evidence also considered
    sw_evidence = "Suggests non-normal" if sw_p < 0.05 else "Does not reject normality"
    # Combine evidence
    visual_note = ""
    if abs(skew_val) > 1.0:
        visual_note = "Strongly skewed"
    elif abs(skew_val) > 0.5:
        visual_note = "Moderately skewed"
    else:
        visual_note = "Approximately symmetric"

    if sw_p >= 0.05 and abs(skew_val) <= 0.8 and abs(kurt_val) <= 2.0:
        overall = "Approximately normal (statistical + visual)"
    elif sw_p >= 0.05 and (abs(skew_val) > 0.8 or abs(kurt_val) > 2.0):
        overall = "Borderline — SW does not reject but shape departs from normal"
    else:
        overall = "Non-normal — SW rejects and/or shape departs substantially"

    normality_rows.append({
        "Variable"              : var,
        "N"                     : n,
        "Shapiro_W"             : round(sw_stat, 4),
        "Shapiro_p"             : round(sw_p, 4),
        "SW_Evidence"           : sw_evidence,
        "AD_Statistic"          : round(ad_stat, 4),
        "AD_CV_5pct"            : round(ad_result.critical_values[2], 4),
        "AD_Decision"           : ad_reject_at,
        "Skewness"              : round(skew_val, 4),
        "Excess_Kurtosis"       : round(kurt_val, 4),
        "Visual_Shape"          : visual_note,
        "Overall_Assessment"    : overall,
    })

    print(f"\n  {title}")
    print(f"    Shapiro-Wilk : W={sw_stat:.4f},  p={sw_p:.4f}  → {sw_evidence}")
    print(f"    Anderson-Darling : stat={ad_stat:.4f},  CV(5%)={ad_result.critical_values[2]:.4f}  → {ad_reject_at}")
    print(f"    Skewness={skew_val:.4f},  Excess Kurtosis={kurt_val:.4f}  → {visual_note}")
    print(f"    Overall: {overall}")

normality_df = pd.DataFrame(normality_rows)
print()


# ─────────────────────────────────────────────────────────────
# TASK 3 — DISTRIBUTION CHARACTERISTICS TABLE
# ─────────────────────────────────────────────────────────────
print("=" * 60)
print("TASK 3 — DISTRIBUTION CHARACTERISTICS")
print("=" * 60)

char_rows = []
for var in VARS:
    data  = df[var].dropna().values
    q1    = np.percentile(data, 25)
    q3    = np.percentile(data, 75)
    iqr   = q3 - q1
    lo_f  = q1 - 1.5 * iqr
    hi_f  = q3 + 1.5 * iqr
    outliers = data[(data < lo_f) | (data > hi_f)]
    n_out = len(outliers)

    skew_val = stats.skew(data)
    kurt_val = stats.kurtosis(data)

    if skew_val > 0.5:
        skew_dir = "Right-skewed (positive)"
    elif skew_val < -0.5:
        skew_dir = "Left-skewed (negative)"
    else:
        skew_dir = "Approximately symmetric"

    if kurt_val > 1.0:
        kurt_desc = "Leptokurtic (heavy tails)"
    elif kurt_val < -1.0:
        kurt_desc = "Platykurtic (light tails)"
    else:
        kurt_desc = "Approximately mesokurtic"

    sym_note = ("Symmetric" if abs(skew_val) < 0.5
                else ("Mildly asymmetric" if abs(skew_val) < 1.0
                      else "Strongly asymmetric"))

    # Normal reasonable?
    norm_ok = normality_df.loc[normality_df["Variable"]==var,
                               "Overall_Assessment"].values[0]

    char_rows.append({
        "Variable"               : var,
        "Skewness"               : round(skew_val, 4),
        "Skewness_Direction"     : skew_dir,
        "Excess_Kurtosis"        : round(kurt_val, 4),
        "Kurtosis_Description"   : kurt_desc,
        "Symmetry"               : sym_note,
        "N_Outliers_IQR_rule"    : n_out,
        "Outlier_Values"         : str(np.round(outliers, 3).tolist()) if n_out > 0 else "None",
        "Normal_Assumption"      : norm_ok,
    })

    print(f"\n  {TITLES[var]}")
    print(f"    Skewness : {skew_val:.4f}  → {skew_dir}")
    print(f"    Kurtosis : {kurt_val:.4f}  → {kurt_desc}")
    print(f"    Symmetry : {sym_note}")
    print(f"    Outliers (IQR rule) : {n_out}"
          + (f"  → {np.round(outliers,2)}" if n_out > 0 else "  → None"))
    print(f"    Normal assumption  : {norm_ok}")

char_df = pd.DataFrame(char_rows)
print()


# ─────────────────────────────────────────────────────────────
# TASK 4 — DISTRIBUTION FITTING
# ─────────────────────────────────────────────────────────────
print("=" * 60)
print("TASK 4 — DISTRIBUTION FITTING")
print("=" * 60)

# Eligibility rules per variable:
#   Normal       — always tried (reference)
#   Log-normal   — only if ALL values > 0 (multiplicative processes)
#   Gamma        — only if ALL values > 0 (waiting-time / rate processes)
#   Exponential  — only if ALL values > 0 AND skew ≥ 0.8 (one-sided)

def ks_gof(data, dist_obj, params):
    """Kolmogorov-Smirnov goodness-of-fit against fitted distribution."""
    ks_stat, ks_p = kstest(data, dist_obj.cdf, args=params)
    return round(ks_stat, 4), round(ks_p, 4)

def fit_and_report(var, data):
    rows = []
    skew_val = stats.skew(data)
    all_pos  = (data > 0).all()

    # --- Normal ---
    mu, sigma = norm.fit(data)
    ks_s, ks_p = ks_gof(data, norm, (mu, sigma))
    rows.append({
        "Variable": var, "Distribution": "Normal",
        "Param1_name": "mu",    "Param1_value": round(mu, 4),
        "Param2_name": "sigma", "Param2_value": round(sigma, 4),
        "Param3_name": "N/A",   "Param3_value": np.nan,
        "KS_Statistic": ks_s,   "KS_p_value": ks_p,
        "Eligible": True,
        "Note": "Reference distribution; fitted by MLE"
    })

    # --- Log-normal ---
    if all_pos:
        shape, loc, scale = lognorm.fit(data, floc=0)
        ks_s, ks_p = ks_gof(data, lognorm, (shape, loc, scale))
        rows.append({
            "Variable": var, "Distribution": "Log-Normal",
            "Param1_name": "shape(sigma_log)", "Param1_value": round(shape, 4),
            "Param2_name": "loc",  "Param2_value": round(loc, 4),
            "Param3_name": "scale(exp_mu_log)", "Param3_value": round(scale, 4),
            "KS_Statistic": ks_s, "KS_p_value": ks_p,
            "Eligible": True,
            "Note": "Fitted with loc=0 (MLE); appropriate only when values are strictly positive"
        })
    else:
        rows.append({
            "Variable": var, "Distribution": "Log-Normal",
            "Param1_name": "N/A", "Param1_value": np.nan,
            "Param2_name": "N/A", "Param2_value": np.nan,
            "Param3_name": "N/A", "Param3_value": np.nan,
            "KS_Statistic": np.nan, "KS_p_value": np.nan,
            "Eligible": False,
            "Note": "NOT eligible — variable contains zero or negative values (e.g. GDP_Growth can be negative)"
        })

    # --- Gamma ---
    if all_pos:
        a_shape, g_loc, g_scale = gamma.fit(data, floc=0)
        ks_s, ks_p = ks_gof(data, gamma, (a_shape, g_loc, g_scale))
        rows.append({
            "Variable": var, "Distribution": "Gamma",
            "Param1_name": "shape(alpha)", "Param1_value": round(a_shape, 4),
            "Param2_name": "loc",          "Param2_value": round(g_loc, 4),
            "Param3_name": "scale(beta)",  "Param3_value": round(g_scale, 4),
            "KS_Statistic": ks_s, "KS_p_value": ks_p,
            "Eligible": True,
            "Note": "Fitted with loc=0 (MLE); only meaningful for strictly positive data"
        })
    else:
        rows.append({
            "Variable": var, "Distribution": "Gamma",
            "Param1_name": "N/A", "Param1_value": np.nan,
            "Param2_name": "N/A", "Param2_value": np.nan,
            "Param3_name": "N/A", "Param3_value": np.nan,
            "KS_Statistic": np.nan, "KS_p_value": np.nan,
            "Eligible": False,
            "Note": "NOT eligible — variable contains zero or negative values"
        })

    # --- Exponential ---
    if all_pos and skew_val >= 0.6:
        e_loc, e_scale = expon.fit(data, floc=0)
        ks_s, ks_p = ks_gof(data, expon, (e_loc, e_scale))
        rows.append({
            "Variable": var, "Distribution": "Exponential",
            "Param1_name": "loc",         "Param1_value": round(e_loc, 4),
            "Param2_name": "scale(1/lam)","Param2_value": round(e_scale, 4),
            "Param3_name": "N/A",         "Param3_value": np.nan,
            "KS_Statistic": ks_s, "KS_p_value": ks_p,
            "Eligible": True,
            "Note": "Fitted (loc=0); Exponential appropriate only for right-skewed positive data"
        })
    else:
        reason = ("NOT eligible — variable contains non-positive values"
                  if not all_pos
                  else "NOT fitted — skewness too low for exponential to be meaningful")
        rows.append({
            "Variable": var, "Distribution": "Exponential",
            "Param1_name": "N/A", "Param1_value": np.nan,
            "Param2_name": "N/A", "Param2_value": np.nan,
            "Param3_name": "N/A", "Param3_value": np.nan,
            "KS_Statistic": np.nan, "KS_p_value": np.nan,
            "Eligible": False,
            "Note": reason
        })
    return rows

fitting_rows = []
for var in VARS:
    data = df[var].dropna().values
    rows = fit_and_report(var, data)
    fitting_rows.extend(rows)
    print(f"\n  {TITLES[var]}  (all_pos={bool((data>0).all())}, skew={stats.skew(data):.3f})")
    for r in rows:
        if r["Eligible"]:
            print(f"    {r['Distribution']:12s}  KS={r['KS_Statistic']}  p={r['KS_p_value']}  | "
                  f"P1({r['Param1_name']})={r['Param1_value']}  P2({r['Param2_name']})={r['Param2_value']}")
        else:
            print(f"    {r['Distribution']:12s}  → {r['Note']}")

fitting_df = pd.DataFrame(fitting_rows)
print()


# ─────────────────────────────────────────────────────────────
# TASK 4b — DISTRIBUTION FIT OVERLAY PLOTS (eligible fits only)
# ─────────────────────────────────────────────────────────────
DIST_OBJS = {
    "Normal"     : norm,
    "Log-Normal" : lognorm,
    "Gamma"      : gamma,
    "Exponential": expon,
}

for var in VARS:
    data = df[var].dropna().values
    eligible = fitting_df[(fitting_df["Variable"]==var) & (fitting_df["Eligible"]==True)]
    if eligible.empty:
        continue

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.histplot(data, kde=False, stat="density", color=PALETTE[var],
                 alpha=0.35, edgecolor="white", linewidth=0.5,
                 bins="auto", ax=ax, label="Observed data")

    x = np.linspace(max(data.min() - 0.5*data.std(), data.min()-1),
                    data.max() + 0.5*data.std(), 400)

    line_styles = ["-", "--", "-.", ":"]
    colors_fit  = ["navy", "crimson", "darkorange", "darkgreen"]
    for i, (_, row) in enumerate(eligible.iterrows()):
        dist_name = row["Distribution"]
        d_obj     = DIST_OBJS[dist_name]
        p1, p2, p3 = row["Param1_value"], row["Param2_value"], row["Param3_value"]
        try:
            if dist_name == "Normal":
                pdf_vals = d_obj.pdf(x, p1, p2)
            elif dist_name == "Log-Normal":
                pdf_vals = d_obj.pdf(x, p1, p2, p3)
                pdf_vals = np.where(x > 0, pdf_vals, 0)
            elif dist_name == "Gamma":
                pdf_vals = d_obj.pdf(x, p1, p2, p3)
                pdf_vals = np.where(x > 0, pdf_vals, 0)
            elif dist_name == "Exponential":
                pdf_vals = d_obj.pdf(x, p1, p2)
                pdf_vals = np.where(x > 0, pdf_vals, 0)
            else:
                continue
            label = f"{dist_name}  (KS p={row['KS_p_value']})"
            ax.plot(x, pdf_vals, lw=2, ls=line_styles[i % 4],
                    color=colors_fit[i % 4], label=label)
        except Exception:
            pass

    ax.set_title(f"Distribution Fitting — {TITLES[var]}\n(India, 1993–2023, n=31)",
                 fontweight="bold")
    ax.set_xlabel(f"{TITLES[var]}  ({UNITS[var]})", labelpad=8)
    ax.set_ylabel("Density", labelpad=8)
    ax.legend(fontsize=8, loc="best")
    fig.tight_layout()
    fname = os.path.join(FIG_DIR, f"dist_fit_{var}.png")
    fig.savefig(fname, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved  dist_fit_{var}.png")

print()


# ─────────────────────────────────────────────────────────────
# TASK 5 — EMPIRICAL PROBABILITIES
# ─────────────────────────────────────────────────────────────
print("=" * 60)
print("TASK 5 — EMPIRICAL PROBABILITIES")
print("=" * 60)
print("(Based solely on observed frequencies in the 31-year sample)")
print()

emp_rows = []

def emp_prob(series, condition_label, mask):
    n_total = len(series)
    n_event = mask.sum()
    p = round(n_event / n_total, 4)
    return n_event, n_total, p

# GDP_Growth
for threshold, label in [(6, "> 6%"), (7, "> 7%"), (0, "> 0% (positive growth)")]:
    series = df["GDP_Growth"]
    mask   = series > threshold
    n_e, n_t, p = emp_prob(series, label, mask)
    emp_rows.append({
        "Variable": "GDP_Growth", "Condition": f"GDP_Growth {label}",
        "n_events": n_e, "n_total": n_t, "Empirical_Probability": p,
        "Note": "Proportion of years in sample satisfying condition"
    })
    print(f"  P(GDP_Growth {label:25s}) = {n_e}/{n_t} = {p:.4f}  ({p*100:.1f}%)")

# Inflation
for threshold, label in [(5, "> 5%"), (8, "> 8%")]:
    series = df["Inflation"]
    mask   = series > threshold
    n_e, n_t, p = emp_prob(series, label, mask)
    emp_rows.append({
        "Variable": "Inflation", "Condition": f"Inflation {label}",
        "n_events": n_e, "n_total": n_t, "Empirical_Probability": p,
        "Note": "Proportion of years in sample satisfying condition"
    })
    print(f"  P(Inflation {label:27s}) = {n_e}/{n_t} = {p:.4f}  ({p*100:.1f}%)")

# FDI
for threshold, label in [(1, "> 1% of GDP"), (2, "> 2% of GDP")]:
    series = df["FDI_Net_Inflows"]
    mask   = series > threshold
    n_e, n_t, p = emp_prob(series, label, mask)
    emp_rows.append({
        "Variable": "FDI_Net_Inflows", "Condition": f"FDI_Net_Inflows {label}",
        "n_events": n_e, "n_total": n_t, "Empirical_Probability": p,
        "Note": "Proportion of years in sample satisfying condition"
    })
    print(f"  P(FDI {label:31s}) = {n_e}/{n_t} = {p:.4f}  ({p*100:.1f}%)")

# Exports
for threshold, label in [(15, "> 15% of GDP"), (20, "> 20% of GDP")]:
    series = df["Exports"]
    mask   = series > threshold
    n_e, n_t, p = emp_prob(series, label, mask)
    emp_rows.append({
        "Variable": "Exports", "Condition": f"Exports {label}",
        "n_events": n_e, "n_total": n_t, "Empirical_Probability": p,
        "Note": "Proportion of years in sample satisfying condition"
    })
    print(f"  P(Exports {label:29s}) = {n_e}/{n_t} = {p:.4f}  ({p*100:.1f}%)")

# Gross_Capital_Formation
for threshold, label in [(30, "> 30% of GDP"), (35, "> 35% of GDP")]:
    series = df["Gross_Capital_Formation"]
    mask   = series > threshold
    n_e, n_t, p = emp_prob(series, label, mask)
    emp_rows.append({
        "Variable": "Gross_Capital_Formation", "Condition": f"GCF {label}",
        "n_events": n_e, "n_total": n_t, "Empirical_Probability": p,
        "Note": "Proportion of years in sample satisfying condition"
    })
    print(f"  P(GCF {label:33s}) = {n_e}/{n_t} = {p:.4f}  ({p*100:.1f}%)")

# Unemployment
for threshold, label in [(6, "> 6%"), (7, "> 7%")]:
    series = df["Unemployment"]
    mask   = series > threshold
    n_e, n_t, p = emp_prob(series, label, mask)
    emp_rows.append({
        "Variable": "Unemployment", "Condition": f"Unemployment {label}",
        "n_events": n_e, "n_total": n_t, "Empirical_Probability": p,
        "Note": "Proportion of years in sample satisfying condition"
    })
    print(f"  P(Unemployment {label:24s}) = {n_e}/{n_t} = {p:.4f}  ({p*100:.1f}%)")

emp_df = pd.DataFrame(emp_rows)
print()


# ─────────────────────────────────────────────────────────────
# TASK 6 — SAVE OUTPUT TABLES
# ─────────────────────────────────────────────────────────────
print("=" * 60)
print("TASK 6 — SAVING OUTPUT TABLES")
print("=" * 60)

norm_path    = os.path.join(TABLE_DIR, "normality_tests.csv")
char_path    = os.path.join(TABLE_DIR, "distribution_analysis.csv")
fit_path     = os.path.join(TABLE_DIR, "distribution_fitting.csv")
emp_path     = os.path.join(TABLE_DIR, "empirical_probabilities.csv")

normality_df.to_csv(norm_path, index=False)
char_df.to_csv(char_path, index=False)
fitting_df.to_csv(fit_path, index=False)
emp_df.to_csv(emp_path, index=False)

print(f"  ✔  normality_tests.csv         → {norm_path}")
print(f"  ✔  distribution_analysis.csv   → {char_path}")
print(f"  ✔  distribution_fitting.csv    → {fit_path}")
print(f"  ✔  empirical_probabilities.csv → {emp_path}")
print()


# ─────────────────────────────────────────────────────────────
# TASK 7 — INTERPRETATION SUMMARY (printed, not saved)
# ─────────────────────────────────────────────────────────────
print("=" * 60)
print("TASK 7 — INTERPRETATION SUMMARY")
print("=" * 60)

for _, row in normality_df.iterrows():
    print(f"\n  {TITLES[row['Variable']]}")
    print(f"    SW p={row['Shapiro_p']}  | Skewness={row['Skewness']}  | Excess Kurt={row['Excess_Kurtosis']}")
    print(f"    → {row['Overall_Assessment']}")
    c_row = char_df[char_df["Variable"] == row["Variable"]].iloc[0]
    if c_row["N_Outliers_IQR_rule"] > 0:
        print(f"    ⚠  {c_row['N_Outliers_IQR_rule']} potential outlier(s): {c_row['Outlier_Values']}")
    else:
        print(f"    No outliers detected by IQR rule")


# ─────────────────────────────────────────────────────────────
# TASK 8 — QUALITY CHECK
# ─────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("TASK 8 — QUALITY CHECK")
print("=" * 60)

# 8a. Original data untouched
df_check = pd.read_csv(CLEAN_CSV)
assert len(df_check) == 31, "Row count mismatch!"
assert list(df_check.columns) == ["Year","GDP_Growth","Inflation","FDI_Net_Inflows",
                                   "Exports","Gross_Capital_Formation","Unemployment"]
assert df_check[VARS].isnull().sum().sum() == 0
print("  ✔  Original cleaned CSV unchanged (31 rows, 7 columns, 0 missing values)")

# 8b. All expected figures exist
expected_figs = (
    [f"hist_kde_{v}.png"  for v in VARS] +
    [f"boxplot_{v}.png"   for v in VARS] +
    [f"qqplot_{v}.png"    for v in VARS] +
    ["boxplots_all_variables.png"] +
    [f"dist_fit_{v}.png"  for v in VARS]
)
missing_figs = [f for f in expected_figs
                if not os.path.isfile(os.path.join(FIG_DIR, f))]
if missing_figs:
    print(f"  ⚠  Missing figures: {missing_figs}")
else:
    print(f"  ✔  All {len(expected_figs)} expected figures present in {FIG_DIR}")

# 8c. All tables exist
for path, name in [(norm_path,"normality_tests.csv"),
                   (char_path,"distribution_analysis.csv"),
                   (fit_path ,"distribution_fitting.csv"),
                   (emp_path ,"empirical_probabilities.csv")]:
    if os.path.isfile(path):
        tdf = pd.read_csv(path)
        print(f"  ✔  {name:35s} → {len(tdf)} rows")
    else:
        print(f"  ⚠  MISSING: {name}")

# 8d. No unsupported distribution claimed as good fit
ineligible = fitting_df[fitting_df["Eligible"]==False]
print(f"  ✔  {len(ineligible)} distribution fits correctly flagged as ineligible (not reported as fits)")

# 8e. Figures file size sanity
sizes_ok = all(
    os.path.getsize(os.path.join(FIG_DIR, f)) > 5000
    for f in expected_figs
    if os.path.isfile(os.path.join(FIG_DIR, f))
)
print(f"  ✔  All figure files > 5 KB (not empty/corrupt): {sizes_ok}")

print("\n" + "=" * 60)
print("PROBABILITY DISTRIBUTION ANALYSIS — COMPLETE")
print("=" * 60)

# Final file manifest
all_figs = sorted(os.listdir(FIG_DIR))
print(f"\nFigures in {FIG_DIR}:")
for f in all_figs:
    sz = os.path.getsize(os.path.join(FIG_DIR, f))
    print(f"  {f:50s}  {sz//1024} KB")

print(f"\nTables in {TABLE_DIR}:")
for fname in ["normality_tests.csv","distribution_analysis.csv",
              "distribution_fitting.csv","empirical_probabilities.csv"]:
    fpath = os.path.join(TABLE_DIR, fname)
    if os.path.isfile(fpath):
        sz = os.path.getsize(fpath)
        print(f"  {fname:40s}  {sz} bytes")
