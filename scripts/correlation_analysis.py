"""
correlation_analysis.py
------------------------
Phase: Correlation Analysis
Project: Statistical Analysis of Economic Growth and Its Determinants in India
Data:    data/cleaned/india_economic_growth_determinants_clean.csv

Tasks:
  Task 1  — Pearson correlation (GDP_Growth vs predictors + full matrix)
  Task 2  — Spearman correlation (same)
  Task 3  — Dual heatmap (Pearson + Spearman side-by-side)
  Task 4  — Significance testing at alpha = 0.05
  Task 5  — Scatter plots with OLS trend lines
  Task 6  — Multicollinearity pre-check among predictors
  Task 7  — Concise factual interpretation (printed)
  Task 8  — Quality check

IMPORTANT:
  - No regression performed here.
  - Correlation ≠ causation. All language is associative, not causal.
  - Both Pearson and Spearman reported to account for non-normality found
    in the distribution analysis phase (GDP_Growth, Unemployment strongly
    non-normal; Spearman is rank-based and more robust in that case).
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
from scipy.stats import pearsonr, spearmanr
from itertools import combinations

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────
# 0.  PATHS & CONSTANTS
# ─────────────────────────────────────────────────────────────
BASE      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_CSV = os.path.join(BASE, "data", "cleaned",
                         "india_economic_growth_determinants_clean.csv")
FIG_DIR   = os.path.join(BASE, "outputs", "figures")
CORR_DIR  = os.path.join(BASE, "outputs", "figures", "correlation")
TABLE_DIR = os.path.join(BASE, "outputs", "tables")

for d in [CORR_DIR, TABLE_DIR]:
    os.makedirs(d, exist_ok=True)

ALPHA = 0.05

VARS = ["GDP_Growth", "Inflation", "FDI_Net_Inflows",
        "Exports", "Gross_Capital_Formation", "Unemployment"]

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
    "figure.dpi"     : 150,
    "font.family"    : "DejaVu Sans",
    "axes.titlesize" : 12,
    "axes.labelsize" : 10,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "axes.grid"      : True,
    "grid.alpha"     : 0.3,
    "grid.linestyle" : "--",
})

# ─────────────────────────────────────────────────────────────
# 1.  LOAD & VALIDATE DATA
# ─────────────────────────────────────────────────────────────
df = pd.read_csv(CLEAN_CSV)
N  = len(df)

assert N == 31,                          f"Expected 31 rows, got {N}"
assert df[VARS].isnull().sum().sum() == 0, "Unexpected missing values"
assert df.duplicated().sum() == 0,         "Unexpected duplicate rows"

print(f"Data loaded: {N} observations, years {df['Year'].min()}–{df['Year'].max()}")
print(f"All validation checks passed.\n")

# ═══════════════════════════════════════════════════════════════
# HELPER — build full correlation matrix with p-values
# ═══════════════════════════════════════════════════════════════
def full_corr_matrix(data: pd.DataFrame, method: str) -> (pd.DataFrame, pd.DataFrame):
    """
    Returns (r_matrix, p_matrix) DataFrames for all pairs in data.
    method: 'pearson' | 'spearman'
    """
    cols = data.columns.tolist()
    r_mat = pd.DataFrame(np.nan, index=cols, columns=cols)
    p_mat = pd.DataFrame(np.nan, index=cols, columns=cols)
    for c1 in cols:
        for c2 in cols:
            if c1 == c2:
                r_mat.loc[c1, c2] = 1.0
                p_mat.loc[c1, c2] = np.nan
            else:
                x, y = data[c1].values, data[c2].values
                if method == "pearson":
                    r, p = pearsonr(x, y)
                else:
                    r, p = spearmanr(x, y)
                r_mat.loc[c1, c2] = round(r, 4)
                p_mat.loc[c1, c2] = round(p, 4)
    return r_mat, p_mat


# ═══════════════════════════════════════════════════════════════
# TASK 1 — PEARSON CORRELATION
# ═══════════════════════════════════════════════════════════════
print("=" * 65)
print("TASK 1 — PEARSON CORRELATION")
print("=" * 65)

pearson_r_mat, pearson_p_mat = full_corr_matrix(df[VARS], "pearson")

# GDP_Growth vs each predictor
pearson_rows = []
for pred in PREDICTORS:
    r, p = pearsonr(df["GDP_Growth"].values, df[pred].values)
    sig  = "Significant"   if p < ALPHA else "Not significant"
    pearson_rows.append({
        "Variable_X"        : "GDP_Growth",
        "Variable_Y"        : pred,
        "Pearson_r"         : round(r, 4),
        "p_value"           : round(p, 4),
        "n"                 : N,
        "Significant_0.05"  : sig,
        "Direction"         : ("Positive" if r > 0 else "Negative"),
        "Strength"          : ("Strong"   if abs(r) >= 0.6
                                else "Moderate" if abs(r) >= 0.3
                                else "Weak"),
    })
    print(f"  GDP_Growth vs {pred:25s}: r={r:+.4f}  p={p:.4f}  [{sig}]")

pearson_df = pd.DataFrame(pearson_rows)
pearson_path = os.path.join(TABLE_DIR, "pearson_correlation.csv")

# Also append the full matrix as a separate section
with open(pearson_path, "w", newline="") as f:
    f.write("# GDP_Growth vs Predictors\n")
pearson_df.to_csv(pearson_path, index=False, mode="a")
with open(pearson_path, "a", newline="") as f:
    f.write("\n# Full Pearson Correlation Matrix\n")
pearson_r_mat.to_csv(pearson_path, mode="a")

print(f"\n  Full Pearson matrix:\n{pearson_r_mat.to_string()}")
print(f"\n  ✔  Saved  →  {pearson_path}\n")


# ═══════════════════════════════════════════════════════════════
# TASK 2 — SPEARMAN CORRELATION
# ═══════════════════════════════════════════════════════════════
print("=" * 65)
print("TASK 2 — SPEARMAN CORRELATION")
print("=" * 65)

spearman_r_mat, spearman_p_mat = full_corr_matrix(df[VARS], "spearman")

spearman_rows = []
for pred in PREDICTORS:
    rho, p = spearmanr(df["GDP_Growth"].values, df[pred].values)
    sig    = "Significant"   if p < ALPHA else "Not significant"
    spearman_rows.append({
        "Variable_X"        : "GDP_Growth",
        "Variable_Y"        : pred,
        "Spearman_rho"      : round(rho, 4),
        "p_value"           : round(p, 4),
        "n"                 : N,
        "Significant_0.05"  : sig,
        "Direction"         : ("Positive" if rho > 0 else "Negative"),
        "Strength"          : ("Strong"   if abs(rho) >= 0.6
                                else "Moderate" if abs(rho) >= 0.3
                                else "Weak"),
    })
    print(f"  GDP_Growth vs {pred:25s}: rho={rho:+.4f}  p={p:.4f}  [{sig}]")

spearman_df = pd.DataFrame(spearman_rows)
spearman_path = os.path.join(TABLE_DIR, "spearman_correlation.csv")

with open(spearman_path, "w", newline="") as f:
    f.write("# GDP_Growth vs Predictors\n")
spearman_df.to_csv(spearman_path, index=False, mode="a")
with open(spearman_path, "a", newline="") as f:
    f.write("\n# Full Spearman Correlation Matrix\n")
spearman_r_mat.to_csv(spearman_path, mode="a")

print(f"\n  Full Spearman matrix:\n{spearman_r_mat.to_string()}")
print(f"\n  ✔  Saved  →  {spearman_path}\n")


# ═══════════════════════════════════════════════════════════════
# TASK 3 — HEATMAPS
# ═══════════════════════════════════════════════════════════════
print("=" * 65)
print("TASK 3 — CORRELATION HEATMAPS")
print("=" * 65)

def draw_heatmap(r_mat: pd.DataFrame, p_mat: pd.DataFrame,
                 title: str, ax, alpha: float = 0.05):
    """Draw annotated heatmap; asterisk marks p < alpha."""
    r_vals = r_mat.astype(float)
    mask   = np.zeros_like(r_vals, dtype=bool)  # show all cells

    annot_labels = pd.DataFrame("", index=r_mat.index, columns=r_mat.columns)
    for c1 in r_mat.index:
        for c2 in r_mat.columns:
            r_v = r_vals.loc[c1, c2]
            if c1 == c2:
                annot_labels.loc[c1, c2] = "1.00"
            else:
                p_v = p_mat.loc[c1, c2]
                star = "*" if (not np.isnan(p_v) and p_v < alpha) else ""
                annot_labels.loc[c1, c2] = f"{r_v:.2f}{star}"

    short_labels = [LABELS[v] for v in r_mat.index]
    sns.heatmap(
        r_vals,
        ax=ax,
        annot=annot_labels,
        fmt="",
        cmap="RdYlGn",
        vmin=-1, vmax=1,
        center=0,
        linewidths=0.5,
        linecolor="white",
        xticklabels=short_labels,
        yticklabels=short_labels,
        annot_kws={"size": 9},
        cbar_kws={"shrink": 0.8, "label": "Correlation coefficient"},
    )
    ax.set_title(title, fontweight="bold", pad=10)
    ax.tick_params(axis="x", rotation=40, labelsize=8)
    ax.tick_params(axis="y", rotation=0,  labelsize=8)

# Side-by-side Pearson + Spearman
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
draw_heatmap(pearson_r_mat,  pearson_p_mat,
             "Pearson Correlation Matrix\n(* = p < 0.05, India 1993–2023, n=31)",
             axes[0])
draw_heatmap(spearman_r_mat, spearman_p_mat,
             "Spearman Rank Correlation Matrix\n(* = p < 0.05, India 1993–2023, n=31)",
             axes[1])
fig.suptitle("Correlation Analysis — Economic Variables, India 1993–2023",
             fontsize=13, fontweight="bold", y=1.02)
fig.tight_layout()
heatmap_path = os.path.join(FIG_DIR, "correlation_heatmap.png")
fig.savefig(heatmap_path, bbox_inches="tight")
plt.close(fig)
print(f"  ✔  Saved  →  {heatmap_path}")

# Individual Pearson heatmap (larger, for report)
fig, ax = plt.subplots(figsize=(9, 7))
draw_heatmap(pearson_r_mat, pearson_p_mat,
             "Pearson Correlation Matrix\n(* = p < 0.05,  India 1993–2023, n=31)", ax)
fig.tight_layout()
fig.savefig(os.path.join(FIG_DIR, "pearson_heatmap.png"), bbox_inches="tight")
plt.close(fig)
print(f"  ✔  Saved  →  pearson_heatmap.png")

# Individual Spearman heatmap
fig, ax = plt.subplots(figsize=(9, 7))
draw_heatmap(spearman_r_mat, spearman_p_mat,
             "Spearman Rank Correlation Matrix\n(* = p < 0.05,  India 1993–2023, n=31)", ax)
fig.tight_layout()
fig.savefig(os.path.join(FIG_DIR, "spearman_heatmap.png"), bbox_inches="tight")
plt.close(fig)
print(f"  ✔  Saved  →  spearman_heatmap.png\n")


# ═══════════════════════════════════════════════════════════════
# TASK 4 — SIGNIFICANCE SUMMARY (printed inline)
# ═══════════════════════════════════════════════════════════════
print("=" * 65)
print("TASK 4 — SIGNIFICANCE SUMMARY  (alpha = 0.05)")
print("=" * 65)
print(f"\n  {'Pair':45s} {'Pearson r':>10} {'p':>7} {'Spearman rho':>13} {'p':>7}  Sig?")
print("  " + "-" * 95)
for pred in PREDICTORS:
    p_row = pearson_df[pearson_df["Variable_Y"] == pred].iloc[0]
    s_row = spearman_df[spearman_df["Variable_Y"] == pred].iloc[0]
    pair  = f"GDP_Growth vs {pred}"
    sig_p = "*" if p_row["p_value"] < ALPHA else " "
    sig_s = "*" if s_row["p_value"] < ALPHA else " "
    both_sig = "BOTH SIG" if (p_row["p_value"] < ALPHA and s_row["p_value"] < ALPHA) else \
               ("PEARSON ONLY" if p_row["p_value"] < ALPHA else
               ("SPEARMAN ONLY" if s_row["p_value"] < ALPHA else "NOT SIG"))
    print(f"  {pair:45s} {p_row['Pearson_r']:>+10.4f} {p_row['p_value']:>7.4f}"
          f" {s_row['Spearman_rho']:>+13.4f} {s_row['p_value']:>7.4f}  {both_sig}")
print()


# ═══════════════════════════════════════════════════════════════
# TASK 5 — SCATTER PLOTS  (GDP_Growth vs each predictor)
# ═══════════════════════════════════════════════════════════════
print("=" * 65)
print("TASK 5 — SCATTER PLOTS")
print("=" * 65)

for pred in PREDICTORS:
    x     = df[pred].values
    y     = df["GDP_Growth"].values
    color = COLORS[pred]

    r_p, p_p   = pearsonr(x, y)
    rho_s, p_s = spearmanr(x, y)
    sig_tag    = "p < 0.05" if p_p < ALPHA else "p ≥ 0.05"

    fig, ax = plt.subplots(figsize=(7, 5))

    # Scatter points coloured by decade
    decade_colors = []
    for yr in df["Year"]:
        if yr < 2000:
            decade_colors.append("#FF6B6B")
        elif yr < 2010:
            decade_colors.append("#4ECDC4")
        else:
            decade_colors.append("#45B7D1")

    sc = ax.scatter(x, y, c=decade_colors, s=60, alpha=0.85,
                    edgecolors="white", linewidths=0.6, zorder=3)

    # OLS trend line
    slope, intercept, _, _, _ = stats.linregress(x, y)
    x_line = np.linspace(x.min() - 0.05 * (x.max()-x.min()),
                          x.max() + 0.05 * (x.max()-x.min()), 300)
    y_line = slope * x_line + intercept
    ls     = "-" if p_p < ALPHA else "--"
    ax.plot(x_line, y_line, color="black", lw=1.8, ls=ls, alpha=0.75,
            label=f"OLS trend  (slope={slope:.3f})")

    # Annotate a few notable years
    notable = {2020: "2020\n(COVID)", 1998: "1998", 2008: "2008\n(GFC)"}
    for idx, row in df.iterrows():
        yr = int(row["Year"])
        if yr in notable:
            ax.annotate(notable[yr],
                        xy=(row[pred], row["GDP_Growth"]),
                        xytext=(8, 6), textcoords="offset points",
                        fontsize=7, color="dimgray",
                        arrowprops=dict(arrowstyle="-", color="gray", lw=0.8))

    # Legend for decades
    patches = [
        mpatches.Patch(color="#FF6B6B", label="1993–1999"),
        mpatches.Patch(color="#4ECDC4", label="2000–2009"),
        mpatches.Patch(color="#45B7D1", label="2010–2023"),
    ]
    ax.legend(handles=patches + [plt.Line2D([0],[0], color="black", lw=1.8, ls=ls,
              label=f"OLS trend (slope={slope:.3f})")],
              fontsize=7.5, loc="best")

    ax.set_title(
        f"GDP Growth  vs  {LABELS[pred]}\n"
        f"Pearson r = {r_p:+.4f} ({sig_tag})  |  Spearman ρ = {rho_s:+.4f}",
        fontweight="bold", pad=10, fontsize=11)
    ax.set_xlabel(f"{LABELS[pred]}  ({UNITS[pred]})", labelpad=8)
    ax.set_ylabel(f"GDP Growth  ({UNITS['GDP_Growth']})", labelpad=8)
    fig.tight_layout()

    fname = os.path.join(CORR_DIR, f"scatter_GDP_Growth_vs_{pred}.png")
    fig.savefig(fname, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved  scatter_GDP_Growth_vs_{pred}.png")

# Combined 2×3 scatter panel
fig, axes = plt.subplots(2, 3, figsize=(15, 10))
axes_flat = axes.flatten()
for i, pred in enumerate(PREDICTORS):
    ax    = axes_flat[i]
    x     = df[pred].values
    y     = df["GDP_Growth"].values
    color = COLORS[pred]
    r_p, p_p = pearsonr(x, y)
    ax.scatter(x, y, color=color, s=45, alpha=0.75, edgecolors="white", lw=0.5)
    slope, intercept, _, _, _ = stats.linregress(x, y)
    x_line = np.linspace(x.min(), x.max(), 200)
    ls = "-" if p_p < ALPHA else "--"
    ax.plot(x_line, slope * x_line + intercept,
            color="black", lw=1.5, ls=ls)
    ax.set_title(f"vs {LABELS[pred]}\nr={r_p:+.3f} ({'*' if p_p < ALPHA else 'ns'})",
                 fontsize=9, fontweight="bold")
    ax.set_xlabel(UNITS[pred], fontsize=7)
    ax.set_ylabel("GDP Growth (%)" if i % 3 == 0 else "", fontsize=7)

axes_flat[-1].set_visible(False)
fig.suptitle("GDP Growth vs All Predictors  (India, 1993–2023)\n"
             "Solid line = OLS trend (p < 0.05);  Dashed = not significant",
             fontsize=12, fontweight="bold", y=1.01)
fig.tight_layout()
fig.savefig(os.path.join(CORR_DIR, "scatter_GDP_Growth_all_predictors.png"),
            bbox_inches="tight")
plt.close(fig)
print(f"  Saved  scatter_GDP_Growth_all_predictors.png\n")


# ═══════════════════════════════════════════════════════════════
# TASK 6 — MULTICOLLINEARITY PRE-CHECK
# ═══════════════════════════════════════════════════════════════
print("=" * 65)
print("TASK 6 — MULTICOLLINEARITY PRE-CHECK (among predictors)")
print("=" * 65)

mc_rows = []
for v1, v2 in combinations(PREDICTORS, 2):
    r_p, p_p   = pearsonr(df[v1].values, df[v2].values)
    rho_s, p_s = spearmanr(df[v1].values, df[v2].values)
    concern    = "FLAG" if abs(r_p) >= 0.7 else ("Monitor" if abs(r_p) >= 0.5 else "Low")
    mc_rows.append({
        "Variable_1"         : v1,
        "Variable_2"         : v2,
        "Pearson_r"          : round(r_p, 4),
        "Pearson_p"          : round(p_p, 4),
        "Spearman_rho"       : round(rho_s, 4),
        "Spearman_p"         : round(p_s, 4),
        "Abs_Pearson_r"      : round(abs(r_p), 4),
        "Multicollinearity"  : concern,
        "Note"               : ("High correlation — potential multicollinearity; check VIF in regression"
                                 if concern == "FLAG"
                                 else ("Moderate — monitor in regression"
                                       if concern == "Monitor"
                                       else "Low concern")),
    })
    print(f"  {v1:25s} vs {v2:25s}:  r={r_p:+.4f}  [{concern}]")

mc_df   = pd.DataFrame(mc_rows).sort_values("Abs_Pearson_r", ascending=False)
mc_path = os.path.join(TABLE_DIR, "predictor_correlation_check.csv")
mc_df.to_csv(mc_path, index=False)
print(f"\n  ✔  Saved  →  {mc_path}\n")

# Predictor-to-predictor heatmap
# Build a fresh label map for the renamed index so draw_heatmap can look up correctly
pred_r = pearson_r_mat.loc[PREDICTORS, PREDICTORS].copy()
pred_p = pearson_p_mat.loc[PREDICTORS, PREDICTORS].copy()

# Rename axes for display
pred_r_labeled = pred_r.rename(index=LABELS, columns=LABELS)
pred_p_labeled = pred_p.rename(index=LABELS, columns=LABELS)

# Temporarily override LABELS dict with identity mapping for renamed matrix
_orig_labels = LABELS.copy()
for v in pred_r_labeled.index:
    LABELS[v] = v    # identity — already renamed

fig, ax = plt.subplots(figsize=(7, 6))
draw_heatmap(pred_r_labeled, pred_p_labeled,
             "Predictor–Predictor Pearson Correlation\n(* = p < 0.05, India 1993–2023)",
             ax)
LABELS.update(_orig_labels)   # restore original LABELS
fig.tight_layout()
fig.savefig(os.path.join(FIG_DIR, "predictor_correlation_heatmap.png"),
            bbox_inches="tight")
plt.close(fig)
print(f"  ✔  Saved  →  predictor_correlation_heatmap.png")


# ═══════════════════════════════════════════════════════════════
# TASK 7 — FACTUAL INTERPRETATION
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 65)
print("TASK 7 — FACTUAL INTERPRETATION")
print("=" * 65)

print("""
  1. DIRECTION AND STRENGTH OF RELATIONSHIPS WITH GDP_GROWTH
  -----------------------------------------------------------""")
for pred in PREDICTORS:
    p_row = pearson_df[pearson_df["Variable_Y"] == pred].iloc[0]
    s_row = spearman_df[spearman_df["Variable_Y"] == pred].iloc[0]
    diff  = abs(p_row["Pearson_r"] - s_row["Spearman_rho"])
    nl_note = ("Pearson and Spearman differ notably (|Δ|={:.3f}) — "
               "possible non-linear/monotonic relationship; Spearman preferred "
               "given non-normality of variables.".format(diff)
               if diff > 0.1 else
               "Pearson and Spearman broadly agree — "
               "relationship appears reasonably linear.")
    print(f"\n  {LABELS[pred]}")
    print(f"    Pearson  r   = {p_row['Pearson_r']:+.4f}  "
          f"({'significant' if p_row['Significant_0.05']=='Significant' else 'NOT significant'} at α=0.05)")
    print(f"    Spearman ρ   = {s_row['Spearman_rho']:+.4f}  "
          f"({'significant' if s_row['Significant_0.05']=='Significant' else 'NOT significant'} at α=0.05)")
    print(f"    Direction    : {p_row['Direction']},  Strength (Pearson): {p_row['Strength']}")
    print(f"    P vs S note  : {nl_note}")

print("""
  2. MULTICOLLINEARITY AMONG PREDICTORS
  --------------------------------------""")
flagged = mc_df[mc_df["Multicollinearity"] != "Low concern"]
if flagged.empty:
    print("  No predictor pairs exceed |r| = 0.5. Low multicollinearity concern overall.")
else:
    for _, row in flagged.iterrows():
        print(f"  {row['Variable_1']} ↔ {row['Variable_2']}: "
              f"r={row['Pearson_r']:+.4f}  [{row['Multicollinearity']}]")
        print(f"    → {row['Note']}")

print("""
  3. IMPLICATIONS FOR REGRESSION
  --------------------------------
  - Spearman should be considered the more reliable measure for GDP_Growth
    and Unemployment given their strongly non-normal distributions
    (confirmed in distribution analysis phase).
  - Significant Pearson and Spearman pairs provide initial evidence of
    linear/monotonic association but do NOT establish causation.
  - Predictor pairs flagged above should have VIF computed in regression.
  - The 2020 COVID outlier (GDP_Growth = -5.78%) may exert undue influence
    on OLS estimates; leverage/influence diagnostics will be needed.
""")


# ═══════════════════════════════════════════════════════════════
# TASK 8 — QUALITY CHECK
# ═══════════════════════════════════════════════════════════════
print("=" * 65)
print("TASK 8 — QUALITY CHECK")
print("=" * 65)

# 8a. Data unchanged
df_chk = pd.read_csv(CLEAN_CSV)
assert len(df_chk) == 31
assert df_chk.isnull().sum().sum() == 0
print("  ✔  Original cleaned CSV unchanged (31 rows, 0 missing)")

# 8b. Coefficients in [-1, +1]
for pred in PREDICTORS:
    r_v   = pearson_df.loc[pearson_df["Variable_Y"]==pred, "Pearson_r"].values[0]
    rho_v = spearman_df.loc[spearman_df["Variable_Y"]==pred, "Spearman_rho"].values[0]
    assert -1.0 <= r_v   <= 1.0, f"Pearson r out of range for {pred}: {r_v}"
    assert -1.0 <= rho_v <= 1.0, f"Spearman rho out of range for {pred}: {rho_v}"
print("  ✔  All Pearson r and Spearman rho values within [-1, +1]")

# 8c. p-values in [0, 1]
for pred in PREDICTORS:
    p_v = pearson_df.loc[pearson_df["Variable_Y"]==pred, "p_value"].values[0]
    s_v = spearman_df.loc[spearman_df["Variable_Y"]==pred, "p_value"].values[0]
    assert 0.0 <= p_v <= 1.0, f"Pearson p-value invalid for {pred}: {p_v}"
    assert 0.0 <= s_v <= 1.0, f"Spearman p-value invalid for {pred}: {s_v}"
print("  ✔  All p-values within [0, 1]")

# 8d. Spot-check one correlation manually
r_check, _ = pearsonr(df["GDP_Growth"].values, df["Inflation"].values)
stored_r   = pearson_df.loc[pearson_df["Variable_Y"]=="Inflation", "Pearson_r"].values[0]
assert round(r_check, 4) == stored_r, "Spot-check mismatch!"
print(f"  ✔  Spot-check: Pearson r (GDP_Growth vs Inflation) = {stored_r}  (verified)")

# 8e. All expected files exist
expected_tables = [
    os.path.join(TABLE_DIR, "pearson_correlation.csv"),
    os.path.join(TABLE_DIR, "spearman_correlation.csv"),
    os.path.join(TABLE_DIR, "predictor_correlation_check.csv"),
]
expected_figs = [
    os.path.join(FIG_DIR,  "correlation_heatmap.png"),
    os.path.join(FIG_DIR,  "pearson_heatmap.png"),
    os.path.join(FIG_DIR,  "spearman_heatmap.png"),
    os.path.join(FIG_DIR,  "predictor_correlation_heatmap.png"),
    os.path.join(CORR_DIR, "scatter_GDP_Growth_all_predictors.png"),
] + [os.path.join(CORR_DIR, f"scatter_GDP_Growth_vs_{p}.png") for p in PREDICTORS]

all_ok = True
for path in expected_tables + expected_figs:
    exists = os.path.isfile(path)
    size   = os.path.getsize(path) if exists else 0
    if not exists or size < 100:
        print(f"  ⚠  MISSING or empty: {os.path.basename(path)}")
        all_ok = False
if all_ok:
    print(f"  ✔  All {len(expected_tables)} tables and {len(expected_figs)} figures present and non-empty")

# 8f. No missing values used
print(f"  ✔  All correlations computed on n={N} complete observations (no imputation)")

# ─── Final Manifest ───────────────────────────────────────────
print("\n" + "=" * 65)
print("CORRELATION ANALYSIS PHASE — COMPLETE")
print("=" * 65)

print(f"\nTables in {TABLE_DIR}:")
for fname in ["pearson_correlation.csv","spearman_correlation.csv",
              "predictor_correlation_check.csv"]:
    fp = os.path.join(TABLE_DIR, fname)
    if os.path.isfile(fp):
        print(f"  {fname:40s}  {os.path.getsize(fp):6d} bytes")

print(f"\nFigures:")
all_fig_files = (
    [os.path.join(FIG_DIR,  f) for f in
     ["correlation_heatmap.png","pearson_heatmap.png",
      "spearman_heatmap.png","predictor_correlation_heatmap.png"]] +
    [os.path.join(CORR_DIR, f) for f in
     [f"scatter_GDP_Growth_vs_{p}.png" for p in PREDICTORS] +
     ["scatter_GDP_Growth_all_predictors.png"]]
)
for fp in all_fig_files:
    if os.path.isfile(fp):
        print(f"  {os.path.basename(fp):55s}  {os.path.getsize(fp)//1024:4d} KB")
