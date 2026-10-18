"""
regression_analysis.py
-----------------------
Phase: Regression Analysis
Project: Statistical Analysis of Economic Growth and Its Determinants in India
Data:    data/cleaned/india_economic_growth_determinants_clean.csv

IMPORTANT NOTES:
  - No causal claims. All language is associative.
  - Original OLS results are NEVER silently replaced by robust results.
  - Outliers/influential points are flagged, NOT removed.
  - Annual time-series; independence of observations cannot be assumed.
"""

import os
import sys
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from scipy import stats
from scipy.stats import shapiro
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.stattools import durbin_watson
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.stattools import jarque_bera as sm_jb
from itertools import combinations

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────
# 0.  PATHS & CONFIG
# ─────────────────────────────────────────────────────────────
BASE      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_CSV = os.path.join(BASE, "data", "cleaned",
                         "india_economic_growth_determinants_clean.csv")
TABLE_DIR = os.path.join(BASE, "outputs", "tables")
SIMP_DIR  = os.path.join(BASE, "outputs", "figures", "regression", "simple")
DIAG_DIR  = os.path.join(BASE, "outputs", "figures", "regression", "diagnostics")

for d in [TABLE_DIR, SIMP_DIR, DIAG_DIR]:
    os.makedirs(d, exist_ok=True)

ALPHA      = 0.05
PREDICTORS = ["Inflation", "FDI_Net_Inflows",
              "Exports", "Gross_Capital_Formation", "Unemployment"]
LABELS = {
    "GDP_Growth"             : "GDP Growth",
    "Inflation"              : "Inflation (CPI)",
    "FDI_Net_Inflows"        : "FDI Net Inflows",
    "Exports"                : "Exports",
    "Gross_Capital_Formation": "Gross Capital Formation",
    "Unemployment"           : "Unemployment",
}
UNITS = {
    "GDP_Growth"             : "Annual % change",
    "Inflation"              : "Annual % change",
    "FDI_Net_Inflows"        : "% of GDP",
    "Exports"                : "% of GDP",
    "Gross_Capital_Formation": "% of GDP",
    "Unemployment"           : "% of labour force",
}
COLORS = {
    "Inflation"              : "#E84855",
    "FDI_Net_Inflows"        : "#F4A261",
    "Exports"                : "#2A9D8F",
    "Gross_Capital_Formation": "#6A4C93",
    "Unemployment"           : "#457B9D",
}
plt.rcParams.update({
    "figure.dpi"    : 150, "font.family": "DejaVu Sans",
    "axes.titlesize": 12,  "axes.labelsize": 10,
    "xtick.labelsize": 8,  "ytick.labelsize": 8,
    "axes.grid": True,     "grid.alpha": 0.3, "grid.linestyle": "--",
})

# ─────────────────────────────────────────────────────────────
# 1.  LOAD & VALIDATE
# ─────────────────────────────────────────────────────────────
df = pd.read_csv(CLEAN_CSV)
N  = len(df)
assert N >= 30, f"Expected at least 30 observations, got {N}"
assert df[["GDP_Growth"] + PREDICTORS].isnull().sum().sum() == 0
print(f"Data loaded: {N} obs  |  {df['Year'].min()}–{df['Year'].max()}")
print(f"n/k ratio: {N}/{len(PREDICTORS)} = {N/len(PREDICTORS):.1f}  "
      f"({'adequate' if N/len(PREDICTORS)>=6 else 'small'})\n")

y = df["GDP_Growth"].values


# ═══════════════════════════════════════════════════════════════
# TASK 1 — FIVE SIMPLE OLS REGRESSIONS
# ═══════════════════════════════════════════════════════════════
print("="*65); print("TASK 1 — SIMPLE LINEAR REGRESSIONS"); print("="*65)

simple_rows  = []
simple_models = {}

for pred in PREDICTORS:
    x   = df[pred].values
    Xc  = sm.add_constant(x)
    mdl = sm.OLS(y, Xc).fit()
    simple_models[pred] = mdl
    ci  = mdl.conf_int()
    sig = "Yes" if mdl.pvalues[1] < ALPHA else "No"

    simple_rows.append({
        "Model"          : f"GDP_Growth ~ {pred}",
        "Predictor"      : pred,
        "Intercept"      : round(mdl.params[0], 4),
        "SE_Intercept"   : round(mdl.bse[0], 4),
        "t_Intercept"    : round(mdl.tvalues[0], 4),
        "p_Intercept"    : round(mdl.pvalues[0], 4),
        "Slope"          : round(mdl.params[1], 4),
        "SE_Slope"       : round(mdl.bse[1], 4),
        "t_Slope"        : round(mdl.tvalues[1], 4),
        "p_Slope"        : round(mdl.pvalues[1], 4),
        "CI_low_95"      : round(ci[0][1], 4),
        "CI_high_95"     : round(ci[1][1], 4),
        "R2"             : round(mdl.rsquared, 4),
        "Adj_R2"         : round(mdl.rsquared_adj, 4),
        "F_statistic"    : round(mdl.fvalue, 4),
        "F_p_value"      : round(mdl.f_pvalue, 4),
        "n"              : N,
        "AIC"            : round(mdl.aic, 4),
        "BIC"            : round(mdl.bic, 4),
        "Slope_Sig_0.05" : sig,
    })
    print(f"\n  GDP_Growth ~ {pred}")
    print(f"    Intercept: {mdl.params[0]:+.4f} (SE={mdl.bse[0]:.4f}, t={mdl.tvalues[0]:.4f}, p={mdl.pvalues[0]:.4f})")
    print(f"    Slope    : {mdl.params[1]:+.4f} (SE={mdl.bse[1]:.4f}, t={mdl.tvalues[1]:.4f}, p={mdl.pvalues[1]:.4f}) Sig={sig}")
    print(f"    95% CI slope: [{ci[0][1]:.4f}, {ci[1][1]:.4f}]")
    print(f"    R²={mdl.rsquared:.4f}  Adj R²={mdl.rsquared_adj:.4f}  F={mdl.fvalue:.4f}  F-p={mdl.f_pvalue:.4f}")

simple_df = pd.DataFrame(simple_rows)
simp_path = os.path.join(TABLE_DIR, "simple_regression_results.csv")
simple_df.to_csv(simp_path, index=False)
print(f"\n  ✔  Saved  →  {simp_path}\n")


# ═══════════════════════════════════════════════════════════════
# TASK 2 — SIMPLE REGRESSION SCATTER PLOTS
# ═══════════════════════════════════════════════════════════════
print("="*65); print("TASK 2 — SIMPLE REGRESSION PLOTS"); print("="*65)

for pred in PREDICTORS:
    mdl   = simple_models[pred]
    x     = df[pred].values
    coef  = mdl.params[1]
    inter = mdl.params[0]
    r2    = mdl.rsquared
    p_sl  = mdl.pvalues[1]
    sig_tag = "p < 0.05" if p_sl < ALPHA else f"p = {p_sl:.3f}"

    fig, ax = plt.subplots(figsize=(7, 5))
    dec_colors = ["#FF6B6B" if yr < 2000 else
                  "#4ECDC4" if yr < 2010 else "#45B7D1"
                  for yr in df["Year"]]
    ax.scatter(x, y, c=dec_colors, s=60, alpha=0.85,
               edgecolors="white", linewidths=0.6, zorder=3)
    x_line = np.linspace(x.min()-0.05*(x.max()-x.min()),
                          x.max()+0.05*(x.max()-x.min()), 300)
    ls = "-" if p_sl < ALPHA else "--"
    ax.plot(x_line, inter + coef*x_line, "k", lw=2, ls=ls, zorder=2,
            label=f"OLS: Ŷ = {inter:.2f} {coef:+.2f}X")
    eq_text = f"Ŷ = {inter:.3f} {coef:+.3f}X\nR² = {r2:.4f}  ({sig_tag})"
    ax.text(0.04, 0.97, eq_text, transform=ax.transAxes, fontsize=8.5,
            va="top", ha="left",
            bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
                      edgecolor="gray", alpha=0.85))
    patches = [mpatches.Patch(color="#FF6B6B", label="1993–1999"),
               mpatches.Patch(color="#4ECDC4", label="2000–2009"),
               mpatches.Patch(color="#45B7D1", label="2010–2023")]
    ax.legend(handles=patches, fontsize=7.5, loc="lower right")
    ax.set_title(f"Simple OLS: GDP Growth ~ {LABELS[pred]}\n(India, 1993–2023, n=31)",
                 fontweight="bold", pad=10)
    ax.set_xlabel(f"{LABELS[pred]}  ({UNITS[pred]})", labelpad=8)
    ax.set_ylabel(f"GDP Growth  ({UNITS['GDP_Growth']})", labelpad=8)
    fig.tight_layout()
    fname = os.path.join(SIMP_DIR, f"simple_reg_GDP_vs_{pred}.png")
    fig.savefig(fname, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved  simple_reg_GDP_vs_{pred}.png")
print()


# ═══════════════════════════════════════════════════════════════
# TASK 3 — MULTIPLE OLS REGRESSION
# ═══════════════════════════════════════════════════════════════
print("="*65); print("TASK 3 — MULTIPLE OLS REGRESSION"); print("="*65)

print("\n  Pre-estimation checks:")
print(f"    n={N}, k={len(PREDICTORS)}, n/k={N/len(PREDICTORS):.1f}")
print(f"    Missing: {df[['GDP_Growth']+PREDICTORS].isnull().sum().sum()}")
print("    Predictor |r|:")
from scipy.stats import pearsonr
for v1, v2 in combinations(PREDICTORS, 2):
    r, _ = pearsonr(df[v1].values, df[v2].values)
    flag = " ⚠ HIGH" if abs(r) >= 0.7 else ""
    print(f"      {v1:25s} vs {v2:25s}: r={r:+.4f}{flag}")

X_multi   = sm.add_constant(df[PREDICTORS])
multi_mdl = sm.OLS(df["GDP_Growth"], X_multi).fit()
ci_multi  = multi_mdl.conf_int()

print(f"\n  R²={multi_mdl.rsquared:.4f}  Adj R²={multi_mdl.rsquared_adj:.4f}")
print(f"  F={multi_mdl.fvalue:.4f}  F-p={multi_mdl.f_pvalue:.4f}")
print(f"  AIC={multi_mdl.aic:.4f}  BIC={multi_mdl.bic:.4f}  n={int(multi_mdl.nobs)}")
print("\n  Coefficients:")
multi_rows = []
for var in multi_mdl.params.index:
    coef = multi_mdl.params[var]
    se   = multi_mdl.bse[var]
    t    = multi_mdl.tvalues[var]
    p    = multi_mdl.pvalues[var]
    lo   = ci_multi.loc[var, 0]
    hi   = ci_multi.loc[var, 1]
    sig  = "*" if p < ALPHA else ""
    print(f"    {var:25s}: β={coef:+.4f} SE={se:.4f} t={t:+.4f} p={p:.4f}{sig} CI=[{lo:.4f},{hi:.4f}]")
    multi_rows.append({
        "Variable": var, "Coefficient": round(coef,4), "Std_Error": round(se,4),
        "t_statistic": round(t,4), "p_value": round(p,4),
        "CI_low_95": round(lo,4), "CI_high_95": round(hi,4),
        "Significant": "Yes" if p < ALPHA else "No",
    })

multi_rows_df = pd.DataFrame(multi_rows)
model_stats = pd.DataFrame([
    {"Variable":"--- MODEL STATS ---","Coefficient":np.nan,"Std_Error":np.nan,
     "t_statistic":np.nan,"p_value":np.nan,"CI_low_95":np.nan,"CI_high_95":np.nan,"Significant":np.nan},
    {"Variable":"R2","Coefficient":round(multi_mdl.rsquared,4),"Std_Error":np.nan,
     "t_statistic":np.nan,"p_value":np.nan,"CI_low_95":np.nan,"CI_high_95":np.nan,"Significant":np.nan},
    {"Variable":"Adj_R2","Coefficient":round(multi_mdl.rsquared_adj,4),"Std_Error":np.nan,
     "t_statistic":np.nan,"p_value":np.nan,"CI_low_95":np.nan,"CI_high_95":np.nan,"Significant":np.nan},
    {"Variable":"F_statistic","Coefficient":round(multi_mdl.fvalue,4),"Std_Error":np.nan,
     "t_statistic":np.nan,"p_value":round(multi_mdl.f_pvalue,4),"CI_low_95":np.nan,"CI_high_95":np.nan,"Significant":np.nan},
    {"Variable":"AIC","Coefficient":round(multi_mdl.aic,4),"Std_Error":np.nan,
     "t_statistic":np.nan,"p_value":np.nan,"CI_low_95":np.nan,"CI_high_95":np.nan,"Significant":np.nan},
    {"Variable":"BIC","Coefficient":round(multi_mdl.bic,4),"Std_Error":np.nan,
     "t_statistic":np.nan,"p_value":np.nan,"CI_low_95":np.nan,"CI_high_95":np.nan,"Significant":np.nan},
    {"Variable":"n","Coefficient":int(multi_mdl.nobs),"Std_Error":np.nan,
     "t_statistic":np.nan,"p_value":np.nan,"CI_low_95":np.nan,"CI_high_95":np.nan,"Significant":np.nan},
])
pd.concat([multi_rows_df, model_stats], ignore_index=True).to_csv(
    os.path.join(TABLE_DIR, "multiple_regression_results.csv"), index=False)
print(f"\n  ✔  Saved  →  {os.path.join(TABLE_DIR,'multiple_regression_results.csv')}")

summary_path = os.path.join(TABLE_DIR, "multiple_regression_summary.txt")
with open(summary_path, "w") as f:
    f.write("MULTIPLE OLS REGRESSION SUMMARY\n")
    f.write("Project: Statistical Analysis of Economic Growth and Its Determinants in India\n")
    f.write(f"Period: {df['Year'].min()}-{df['Year'].max()}  |  n={N}\n")
    f.write("="*65+"\n\n")
    f.write(str(multi_mdl.summary()))
    f.write("\n\nNOTE: Observational annual time-series. No causal claims warranted.\n")
print(f"  ✔  Saved  →  {summary_path}\n")


# ═══════════════════════════════════════════════════════════════
# TASK 4 — COEFFICIENT INTERPRETATION (printed)
# ═══════════════════════════════════════════════════════════════
print("="*65); print("TASK 4 — COEFFICIENT INTERPRETATION"); print("="*65)
for pred in PREDICTORS:
    coef = multi_mdl.params[pred]
    p    = multi_mdl.pvalues[pred]
    lo   = ci_multi.loc[pred, 0]
    hi   = ci_multi.loc[pred, 1]
    sig  = "statistically significant (p < 0.05)" if p < ALPHA else f"NOT statistically significant (p={p:.4f})"
    dirn = "positive" if coef > 0 else "negative"
    print(f"\n  {LABELS[pred]}:  β={coef:+.4f}  [{sig}]")
    print(f"    A one-unit increase in {LABELS[pred]} is associated with an estimated")
    print(f"    {dirn} change of {abs(coef):.4f} pp in GDP Growth, holding other variables constant.")
    print(f"    95% CI: [{lo:.4f}, {hi:.4f}]")
print()


# ═══════════════════════════════════════════════════════════════
# TASK 5 — VIF
# ═══════════════════════════════════════════════════════════════
print("="*65); print("TASK 5 — VARIANCE INFLATION FACTORS (VIF)"); print("="*65)
X_vif = sm.add_constant(df[PREDICTORS])
vif_rows = []
for i, col in enumerate(X_vif.columns):
    if col == "const": continue
    v = variance_inflation_factor(X_vif.values, i)
    flag = ("FLAG — severe" if v > 10 else
            "Moderate"      if v > 5  else "Acceptable")
    note = ("VIF>10: consider addressing multicollinearity before interpreting coefficients"
            if v > 10 else
            "VIF 5-10: moderate; monitor in regression" if v > 5 else
            "VIF<5: low concern")
    vif_rows.append({"Variable":col,"VIF":round(v,4),"Flag":flag,"Note":note})
    print(f"  {col:25s}: VIF={v:.4f}  [{flag}]")

vif_df = pd.DataFrame(vif_rows)
vif_path = os.path.join(TABLE_DIR, "vif_results.csv")
vif_df.to_csv(vif_path, index=False)
print(f"\n  ✔  Saved  →  {vif_path}\n")


# ═══════════════════════════════════════════════════════════════
# TASK 6 — REGRESSION DIAGNOSTICS
# ═══════════════════════════════════════════════════════════════
print("="*65); print("TASK 6 — REGRESSION DIAGNOSTICS"); print("="*65)

fitted    = multi_mdl.fittedvalues.values
residuals = multi_mdl.resid.values
influence = multi_mdl.get_influence()
std_resid = influence.resid_studentized_internal
cooks_d   = influence.cooks_distance[0]
leverage  = influence.hat_matrix_diag
cook_thresh = 4.0 / N

# 6a. Residuals vs Fitted
fig, ax = plt.subplots(figsize=(8.5, 5))
ax.scatter(fitted, residuals, color="#2E86AB", s=55, alpha=0.8,
           edgecolors="white", lw=0.5)
ax.axhline(0, color="red", lw=1.5, ls="--", alpha=0.8)
lowess = sm.nonparametric.lowess(residuals, fitted, frac=0.6)
ax.plot(lowess[:,0], lowess[:,1], color="darkorange", lw=1.8, label="LOWESS")
# Annotate year labels on large residuals
thresh_resid = np.percentile(np.abs(residuals), 90)
for i, yr in enumerate(df["Year"].values):
    if abs(residuals[i]) >= thresh_resid:
        ax.annotate(str(yr), xy=(fitted[i], residuals[i]),
                    xytext=(5,5), textcoords="offset points", fontsize=7, color="navy")
# Internal margins
y_min, y_max = residuals.min(), residuals.max()
y_padding = (y_max - y_min) * 0.10
ax.set_ylim(y_min - y_padding, y_max + y_padding)

fig.suptitle("Residuals vs Fitted Values", fontsize=12.5, fontweight="bold", y=0.98)
ax.set_title("Evaluates linearity and constancy of error variance across predicted GDP Growth", fontsize=9.2, color="#334155", pad=8)
ax.set_xlabel("Fitted Values", labelpad=8)
ax.set_ylabel("Residuals", labelpad=8)
ax.legend(fontsize=9)
plt.subplots_adjust(top=0.88, bottom=0.12, left=0.10, right=0.95)
fig.savefig(os.path.join(DIAG_DIR, "diag_residuals_vs_fitted.png"), bbox_inches="tight")
plt.close(fig); print("  Saved  diag_residuals_vs_fitted.png")

# 6b. Q-Q Plot
fig, ax = plt.subplots(figsize=(6,6))
(osm, osr), (slope_qq, intercept_qq, r_qq) = stats.probplot(residuals, dist="norm")
ax.plot(osm, osr, "o", color="#2E86AB", alpha=0.75, markersize=6, label="Residuals")
ax.plot(osm, slope_qq*np.array(osm)+intercept_qq, "k--", lw=1.5,
        label=f"Normal ref (r={r_qq:.3f})")
ax.set_title("Q-Q Plot of Residuals\n(Multiple OLS, India 1993–2023)", fontweight="bold")
ax.set_xlabel("Theoretical Quantiles", labelpad=8)
ax.set_ylabel("Sample Quantiles (Residuals)", labelpad=8)
ax.legend(fontsize=9)
fig.tight_layout()
fig.savefig(os.path.join(DIAG_DIR, "diag_qq_residuals.png"), bbox_inches="tight")
plt.close(fig); print("  Saved  diag_qq_residuals.png")

# 6c. Histogram of residuals
fig, ax = plt.subplots(figsize=(7,5))
sns.histplot(residuals, kde=True, color="#2E86AB", alpha=0.55,
             edgecolor="white", lw=0.6, bins="auto", ax=ax)
ax.axvline(0, color="red", lw=1.5, ls="--", alpha=0.8)
ax.set_title("Histogram of Residuals\n(Multiple OLS, India 1993–2023)", fontweight="bold")
ax.set_xlabel("Residuals", labelpad=8)
ax.set_ylabel("Frequency", labelpad=8)
fig.tight_layout()
fig.savefig(os.path.join(DIAG_DIR, "diag_hist_residuals.png"), bbox_inches="tight")
plt.close(fig); print("  Saved  diag_hist_residuals.png")

# 6d. Scale-Location
fig, ax = plt.subplots(figsize=(7,5))
sqrt_abs = np.sqrt(np.abs(std_resid))
ax.scatter(fitted, sqrt_abs, color="#E84855", s=55, alpha=0.8,
           edgecolors="white", lw=0.5)
lowess2 = sm.nonparametric.lowess(sqrt_abs, fitted, frac=0.6)
ax.plot(lowess2[:,0], lowess2[:,1], color="darkorange", lw=1.8, label="LOWESS")
ax.set_title("Scale-Location Plot\n(√|Std Residuals| vs Fitted, India 1993–2023)",
             fontweight="bold")
ax.set_xlabel("Fitted Values", labelpad=8)
ax.set_ylabel("√|Standardised Residuals|", labelpad=8)
ax.legend(fontsize=9)
fig.tight_layout()
fig.savefig(os.path.join(DIAG_DIR, "diag_scale_location.png"), bbox_inches="tight")
plt.close(fig); print("  Saved  diag_scale_location.png")

# 6e. Cook's Distance
fig, ax = plt.subplots(figsize=(8.5, 5))
ax.stem(df["Year"].values, cooks_d,
        linefmt="C0-", markerfmt="C0o", basefmt="k-")
ax.axhline(cook_thresh, color="red", lw=1.5, ls="--",
           label=f"Threshold 4/n ≈ {cook_thresh:.3f}")
max_cd = np.max(cooks_d)
ax.set_ylim(-0.03, max_cd * 1.16)
for i, yr in enumerate(df["Year"].values):
    if cooks_d[i] > cook_thresh:
        ax.annotate(str(yr), xy=(yr, cooks_d[i]),
                    xytext=(0, 8), textcoords="offset points",
                    fontsize=8, color="red", ha="center")
fig.suptitle("Cook's Distance — Influential Observations", fontsize=12.5, fontweight="bold", y=0.98)
ax.set_title(f"Influence check: observations exceeding the Cook's D screening threshold 4/n ≈ {cook_thresh:.3f}", fontsize=9.2, color="#334155", pad=8)
ax.set_xlabel("Year", labelpad=8)
ax.set_ylabel("Cook's Distance", labelpad=8)
ax.legend(fontsize=9)
plt.subplots_adjust(top=0.88, bottom=0.12, left=0.10, right=0.95)
fig.savefig(os.path.join(DIAG_DIR, "diag_cooks_distance.png"), bbox_inches="tight")
plt.close(fig); print("  Saved  diag_cooks_distance.png")

# ── Statistical tests ────────────────────────────────────────
dw_stat  = durbin_watson(residuals)
bp_lm, bp_p, bp_f, bp_fp = het_breuschpagan(residuals, X_multi.values)
jb_stat, jb_p, jb_sk, jb_ku = sm_jb(residuals)
sw_stat, sw_p = shapiro(residuals)
n_influential = int((cooks_d > cook_thresh).sum())
influential_yrs = df["Year"].values[cooks_d > cook_thresh].tolist()

print(f"\n  Durbin-Watson       : {dw_stat:.4f}  "
      f"({'≈ no autocorrelation' if 1.5<dw_stat<2.5 else '⚠ autocorrelation'})")
print(f"  Breusch-Pagan       : stat={bp_lm:.4f}  p={bp_p:.4f}  "
      f"({'Heteroskedasticity' if bp_p<ALPHA else 'No significant heteroskedasticity'})")
print(f"  Jarque-Bera         : stat={jb_stat:.4f}  p={jb_p:.4f}  "
      f"({'Non-normal residuals' if jb_p<ALPHA else 'Approx normal'})")
print(f"  Shapiro-Wilk (resid): W={sw_stat:.4f}  p={sw_p:.4f}  "
      f"({'Non-normal' if sw_p<ALPHA else 'Cannot reject normality'})")
print(f"  Cook's D > {cook_thresh:.3f}       : {n_influential} obs  {influential_yrs}")

diag_rows = [
    {"Test":"Durbin-Watson","Statistic":round(dw_stat,4),"p_value":np.nan,
     "Decision":"≈ No autocorrelation" if 1.5<dw_stat<2.5 else "⚠ Possible autocorrelation",
     "Notes":"Values near 2 indicate no first-order autocorrelation"},
    {"Test":"Breusch-Pagan (heteroskedasticity)","Statistic":round(bp_lm,4),
     "p_value":round(bp_p,4),
     "Decision":"Heteroskedasticity present" if bp_p<ALPHA else "No significant heteroskedasticity",
     "Notes":"LM test for constant error variance"},
    {"Test":"Jarque-Bera (residual normality)","Statistic":round(jb_stat,4),
     "p_value":round(jb_p,4),
     "Decision":"Non-normal residuals" if jb_p<ALPHA else "Residuals approximately normal",
     "Notes":"Tests skewness and kurtosis jointly"},
    {"Test":"Shapiro-Wilk (residual normality)","Statistic":round(sw_stat,4),
     "p_value":round(sw_p,4),
     "Decision":"Non-normal residuals" if sw_p<ALPHA else "Cannot reject normality of residuals",
     "Notes":"Preferred for small samples (n<50)"},
    {"Test":"Cook's Distance influential obs","Statistic":round(float(np.max(cooks_d)),4),
     "p_value":np.nan,
     "Decision":f"{n_influential} influential point(s): {influential_yrs}" if n_influential>0 else "None",
     "Notes":f"Threshold=4/n={cook_thresh:.4f}; influential points NOT removed"},
]
pd.DataFrame(diag_rows).to_csv(os.path.join(TABLE_DIR,"regression_diagnostics.csv"), index=False)
print(f"\n  ✔  Saved  →  {os.path.join(TABLE_DIR,'regression_diagnostics.csv')}\n")


# ═══════════════════════════════════════════════════════════════
# TASK 7 — ROBUST STANDARD ERRORS (HC3)
# ═══════════════════════════════════════════════════════════════
print("="*65); print("TASK 7 — ROBUST SE (HC3) + INFLUENTIAL OBSERVATIONS"); print("="*65)

# Compute HC3 robust SE directly from the HC3 covariance matrix
# This avoids the statsmodels version-dependent get_robustcov_results API
from scipy.stats import t as t_dist
hc3_cov   = multi_mdl.cov_HC3                       # HC3 covariance matrix (numpy array)
param_idx = {name: i for i, name in enumerate(multi_mdl.params.index)}
df_resid  = multi_mdl.df_resid

print("\n  [ORIGINAL OLS]")
for p in PREDICTORS:
    print(f"    {p:25s}: β={multi_mdl.params[p]:+.4f}  SE={multi_mdl.bse[p]:.4f}  p={multi_mdl.pvalues[p]:.4f}")

print("\n  [HC3 ROBUST SE]")
rob_rows = []
for pred in PREDICTORS:
    idx    = param_idx[pred]
    b      = multi_mdl.params[pred]
    se_ols = multi_mdl.bse[pred]
    se_r   = float(np.sqrt(hc3_cov[idx, idx]))
    t_r    = float(b / se_r)
    p_r    = float(2 * t_dist.sf(np.abs(t_r), df_resid))
    t_crit = float(t_dist.ppf(0.975, df_resid))
    lo_r   = float(b - t_crit * se_r)
    hi_r   = float(b + t_crit * se_r)
    chg    = "SE↑" if se_r > se_ols else "SE↓"
    print(f"    {pred:25s}: β={b:+.4f}  SE(HC3)={se_r:.4f}  p={p_r:.4f}  [{chg}]")
    rob_rows.append({
        "Variable":pred, "Coef":round(b,4),
        "SE_OLS":round(se_ols,4), "SE_HC3":round(se_r,4),
        "t_HC3":round(t_r,4), "p_HC3":round(p_r,4),
        "CI_low_HC3":round(lo_r,4), "CI_high_HC3":round(hi_r,4),
        "SE_change":chg,
    })

pd.DataFrame(rob_rows).to_csv(
    os.path.join(TABLE_DIR,"robust_regression_results.csv"), index=False)
print(f"\n  ✔  Saved  →  {os.path.join(TABLE_DIR,'robust_regression_results.csv')}")

print(f"\n  Influential observations (Cook's D > {cook_thresh:.4f}):")
if n_influential == 0:
    print("    None detected.")
else:
    for i, yr in enumerate(df["Year"].values):
        if cooks_d[i] > cook_thresh:
            gdpg = df.loc[df["Year"]==yr,"GDP_Growth"].values[0]
            print(f"    Year {yr}: Cook's D={cooks_d[i]:.4f}  Leverage={leverage[i]:.4f}  GDP_Growth={gdpg:.4f}%")
    print("    ⚠  Flagged only — NOT removed. Require substantive investigation.")
print()


# ═══════════════════════════════════════════════════════════════
# TASK 8 — MODEL COMPARISON TABLE
# ═══════════════════════════════════════════════════════════════
print("="*65); print("TASK 8 — MODEL COMPARISON"); print("="*65)

comp_rows = []
for pred in PREDICTORS:
    m = simple_models[pred]
    comp_rows.append({
        "Model":f"Simple: GDP ~ {pred}","Type":"Simple OLS",
        "R2":round(m.rsquared,4),"Adj_R2":round(m.rsquared_adj,4),
        "F_statistic":round(m.fvalue,4),"F_p_value":round(m.f_pvalue,4),
        "AIC":round(m.aic,4),"BIC":round(m.bic,4),"n":int(m.nobs),"k":1,
    })
comp_rows.append({
    "Model":"Multiple OLS (5 predictors)","Type":"Multiple OLS",
    "R2":round(multi_mdl.rsquared,4),"Adj_R2":round(multi_mdl.rsquared_adj,4),
    "F_statistic":round(multi_mdl.fvalue,4),"F_p_value":round(multi_mdl.f_pvalue,4),
    "AIC":round(multi_mdl.aic,4),"BIC":round(multi_mdl.bic,4),
    "n":int(multi_mdl.nobs),"k":5,
})
comp_df = pd.DataFrame(comp_rows)
comp_path = os.path.join(TABLE_DIR,"model_comparison.csv")
comp_df.to_csv(comp_path, index=False)

print(f"\n  {'Model':42s} {'R²':>6} {'AdjR²':>7} {'F':>8} {'F-p':>8} {'AIC':>9}")
print("  "+"-"*85)
for _, row in comp_df.iterrows():
    print(f"  {row['Model']:42s} {row['R2']:>6.4f} {row['Adj_R2']:>7.4f} "
          f"{row['F_statistic']:>8.4f} {row['F_p_value']:>8.4f} {row['AIC']:>9.2f}")
print(f"\n  ✔  Saved  →  {comp_path}\n")


# ═══════════════════════════════════════════════════════════════
# TASK 9 — FINAL INTERPRETATION
# ═══════════════════════════════════════════════════════════════
print("="*65); print("TASK 9 — FINAL REGRESSION INTERPRETATION"); print("="*65)

print(f"""
  MULTIPLE OLS MODEL SUMMARY
  ---------------------------
  R²      = {multi_mdl.rsquared:.4f}  ({multi_mdl.rsquared*100:.1f}% of variance in GDP Growth explained)
  Adj R²  = {multi_mdl.rsquared_adj:.4f}
  F-stat  = {multi_mdl.fvalue:.4f}  (p = {multi_mdl.f_pvalue:.4f})
  Overall model {'is' if multi_mdl.f_pvalue<ALPHA else 'is NOT'} statistically significant at α=0.05.

  COEFFICIENT DIRECTIONS (holding other variables constant):""")
for pred in PREDICTORS:
    coef = multi_mdl.params[pred]
    p    = multi_mdl.pvalues[pred]
    sig  = "SIG *" if p < ALPHA else "not sig"
    dirn = "positive" if coef > 0 else "negative"
    print(f"    {LABELS[pred]:30s}: β={coef:+.4f}  ({dirn})  [{sig}]")

print(f"""
  VIF SUMMARY:""")
for _, row in vif_df.iterrows():
    print(f"    {row['Variable']:25s}: VIF={row['VIF']:.4f}  [{row['Flag']}]")

print(f"""
  DIAGNOSTIC SUMMARY:
    Heteroskedasticity (BP): p={bp_p:.4f}  → {'Present ⚠' if bp_p<ALPHA else 'Not detected'}
    Autocorrelation (DW)   : {dw_stat:.4f}  → {'Concern ⚠' if not (1.5<dw_stat<2.5) else 'No concern'}
    Residual normality (SW): p={sw_p:.4f}  → {'Non-normal ⚠' if sw_p<ALPHA else 'Cannot reject normality'}
    Influential obs         : {n_influential} ({influential_yrs if n_influential>0 else 'none'})

  LIMITATIONS (must be stated):
    1. n=31 annual observations — sample is small relative to 5 predictors.
    2. Annual time-series; OLS independence assumption may not hold.
    3. Endogeneity possible (GDP growth may influence FDI, Exports, GCF).
    4. Omitted variables: human capital, governance, monetary policy, etc.
    5. Structural breaks: 1991 liberalisation, 2008 GFC, COVID-19 2020.
    6. Correlation/association ≠ causation. No causal inference is made.
""")


# ═══════════════════════════════════════════════════════════════
# TASK 10 — QUALITY CHECK
# ═══════════════════════════════════════════════════════════════
print("="*65); print("TASK 10 — QUALITY CHECK"); print("="*65)

df_chk = pd.read_csv(CLEAN_CSV)
assert len(df_chk)==31 and df_chk.isnull().sum().sum()==0
print("  ✔  Original CSV unchanged (31 rows, 0 missing)")

for pred in PREDICTORS:
    stored = simple_df.loc[simple_df["Predictor"]==pred,"R2"].values[0]
    assert stored == round(simple_models[pred].rsquared,4)
print("  ✔  Simple model R² values match stored CSV")

assert all(0<=r<=1 for r in simple_df["R2"])
assert all(0<=p<=1 for p in simple_df["p_Slope"])
assert 0 <= multi_mdl.rsquared <= 1
assert 0 <= multi_mdl.f_pvalue <= 1
print("  ✔  All R² in [0,1] and p-values in [0,1]")

assert all(vif_df["VIF"] > 0)
print("  ✔  All VIF values positive")

assert 0 <= dw_stat <= 4
assert 0 <= bp_p <= 1
print(f"  ✔  DW={dw_stat:.4f} in [0,4]  BP-p={bp_p:.4f} in [0,1]")

expected_tables = [
    "simple_regression_results.csv",
    "multiple_regression_results.csv",
    "multiple_regression_summary.txt",
    "vif_results.csv",
    "regression_diagnostics.csv",
    "robust_regression_results.csv",
    "model_comparison.csv",
]
expected_figs_simp = [f"simple_reg_GDP_vs_{p}.png" for p in PREDICTORS]
expected_figs_diag = ["diag_residuals_vs_fitted.png","diag_qq_residuals.png",
                      "diag_hist_residuals.png","diag_scale_location.png",
                      "diag_cooks_distance.png"]

all_ok = True
for fname in expected_tables:
    path = os.path.join(TABLE_DIR, fname)
    if not os.path.isfile(path) or os.path.getsize(path) < 50:
        print(f"  ⚠  MISSING/EMPTY: {fname}"); all_ok=False
for fname in expected_figs_simp:
    path = os.path.join(SIMP_DIR, fname)
    if not os.path.isfile(path) or os.path.getsize(path) < 5000:
        print(f"  ⚠  MISSING/EMPTY: {fname}"); all_ok=False
for fname in expected_figs_diag:
    path = os.path.join(DIAG_DIR, fname)
    if not os.path.isfile(path) or os.path.getsize(path) < 5000:
        print(f"  ⚠  MISSING/EMPTY: {fname}"); all_ok=False

if all_ok:
    print(f"  ✔  All {len(expected_tables)} tables and "
          f"{len(expected_figs_simp)+len(expected_figs_diag)} figures present and non-empty")

# ─── FINAL MANIFEST ──────────────────────────────────────────
print("\n"+"="*65)
print("REGRESSION ANALYSIS PHASE — COMPLETE")
print("="*65)
print(f"\nTables ({TABLE_DIR}):")
for fname in expected_tables:
    fp = os.path.join(TABLE_DIR, fname)
    if os.path.isfile(fp):
        print(f"  {fname:45s}  {os.path.getsize(fp):6d} bytes")
print(f"\nSimple regression figures ({SIMP_DIR}):")
for fname in expected_figs_simp:
    fp = os.path.join(SIMP_DIR, fname)
    if os.path.isfile(fp):
        print(f"  {fname:50s}  {os.path.getsize(fp)//1024:4d} KB")
print(f"\nDiagnostic figures ({DIAG_DIR}):")
for fname in expected_figs_diag:
    fp = os.path.join(DIAG_DIR, fname)
    if os.path.isfile(fp):
        print(f"  {fname:50s}  {os.path.getsize(fp)//1024:4d} KB")
