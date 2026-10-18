import os
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from pathlib import Path
from scipy import stats
from typing import Dict, Any, List

def generate_all_figures(df: pd.DataFrame, calc_results: Dict[str, Any], figures_dir: Path) -> List[Dict[str, str]]:
    """
    Programmatically generate statistical charts for the current analysis run
    using matplotlib and seaborn. Save to figures_dir.
    """
    figures_dir.mkdir(parents=True, exist_ok=True)
    
    ts_dir = figures_dir / "time_series"
    dist_dir = figures_dir / "distributions"
    corr_dir = figures_dir / "correlation"
    reg_dir = figures_dir / "regression"
    diag_dir = figures_dir / "diagnostics"

    for d in [ts_dir, dist_dir, corr_dir, reg_dir, diag_dir]:
        d.mkdir(parents=True, exist_ok=True)

    sns.set_theme(style="whitegrid", palette="muted")
    plt.rcParams.update({"font.family": "sans-serif", "figure.autolayout": True})

    generated_files: List[Dict[str, str]] = []

    # 1. Time Series Charts
    num_cols = [c for c in df.columns if c != "Year" and pd.api.types.is_numeric_dtype(df[c])]
    years = df["Year"].astype(int) if "Year" in df.columns else np.arange(len(df))

    for col in num_cols:
        s = df[col].dropna()
        if len(s) == 0:
            continue
        
        plt.figure(figsize=(9, 4.5), dpi=150)
        plt.plot(years.loc[s.index], s, marker="o", color="#1565c0", linewidth=2.0, markersize=5, label=col)
        plt.axhline(s.mean(), color="#d32f2f", linestyle="--", linewidth=1.2, label=f"Mean ({s.mean():.2f})")
        
        plt.title(f"Time Series Trend: {col} (India)", fontsize=13, fontweight="bold", pad=12)
        plt.xlabel("Year", fontsize=10, labelpad=8)
        plt.ylabel(col, fontsize=10, labelpad=8)
        plt.legend(loc="upper right", frameon=True, facecolor="white", framealpha=0.9)
        plt.grid(True, linestyle=":", alpha=0.6)
        
        fname = f"{col.lower()}_over_time.png"
        fpath = ts_dir / fname
        plt.savefig(fpath, bbox_inches="tight")
        plt.close()
        
        generated_files.append({"category": "time_series", "filename": fname, "path": f"time_series/{fname}"})

    # 2. Distribution Histograms + KDE & Normal Q-Q Plots for all variables
    for col in num_cols:
        s = df[col].dropna()
        if len(s) == 0:
            continue

        # A. Distribution Histogram + KDE
        plt.figure(figsize=(8, 4.5), dpi=150)
        sns.histplot(s, kde=True, bins=7, color="#2e7d32", stat="density", edgecolor="white", alpha=0.6)
        plt.axvline(s.mean(), color="#b71c1c", linestyle="--", linewidth=1.5, label=f"Mean ({s.mean():.2f})")
        plt.axvline(s.median(), color="#0d47a1", linestyle=":", linewidth=1.5, label=f"Median ({s.median():.2f})")

        plt.title(f"Distribution & Kernel Density: {col}", fontsize=13, fontweight="bold", pad=12)
        plt.xlabel(col, fontsize=10, labelpad=8)
        plt.ylabel("Density", fontsize=10, labelpad=8)
        plt.legend(loc="upper right", frameon=True)
        plt.grid(True, linestyle=":", alpha=0.6)

        fname_hist = f"{col.lower()}_distribution.png"
        fpath_hist = dist_dir / fname_hist
        plt.savefig(fpath_hist, bbox_inches="tight")
        plt.close()

        generated_files.append({"category": "distributions", "filename": fname_hist, "path": f"distributions/{fname_hist}"})

        # B. Normal Q-Q Plot for variable
        if len(s) > 2:
            (osm, osr), (slope, intercept, r_val) = stats.probplot(s, dist="norm")
            plt.figure(figsize=(7, 5), dpi=150)
            plt.scatter(osm, osr, color="#1565c0", alpha=0.85, s=35, label="Observed Sample Quantiles")
            
            x_line = np.array([min(osm), max(osm)])
            y_line = slope * x_line + intercept
            plt.plot(x_line, y_line, color="#c62828", linestyle="--", linewidth=1.8, label=f"Normal Fit Line (r = {r_val:.3f})")

            plt.title(f"Normal Q-Q Plot: {col} (India, n={len(s)})", fontsize=13, fontweight="bold", pad=12)
            plt.xlabel("Theoretical Quantiles (Standard Normal)", fontsize=10, labelpad=8)
            plt.ylabel("Sample Quantiles (Observed Data)", fontsize=10, labelpad=8)
            plt.legend(loc="upper left", frameon=True)
            plt.grid(True, linestyle=":", alpha=0.6)

            fname_qq = f"qqplot_{col}.png"
            fpath_qq = dist_dir / fname_qq
            plt.savefig(fpath_qq, bbox_inches="tight")
            plt.close()

            generated_files.append({"category": "distributions", "filename": fname_qq, "path": f"distributions/{fname_qq}"})

    # B1. Combined 2x3 Histograms with Normal & KDE Curves
    fig, axes = plt.subplots(2, 3, figsize=(13, 7.5), dpi=150)
    axes = axes.flatten()
    for idx, col in enumerate(num_cols[:6]):
        ax = axes[idx]
        s = df[col].dropna()
        sns.histplot(s, kde=True, bins=7, color="#2e7d32", stat="density", edgecolor="white", alpha=0.55, ax=ax)
        # Overlay fitted normal curve
        mu_s, std_s = s.mean(), s.std()
        x_norm = np.linspace(s.min() - 0.5*std_s, s.max() + 0.5*std_s, 100)
        ax.plot(x_norm, stats.norm.pdf(x_norm, mu_s, std_s), color="#c62828", linestyle="--", linewidth=1.5, label="Normal Curve")
        ax.axvline(mu_s, color="#b71c1c", linestyle=":", linewidth=1.2, label=f"Mean ({mu_s:.2f})")
        ax.set_title(col, fontsize=10.5, fontweight="bold", pad=6)
        ax.set_xlabel(col, fontsize=8.5)
        ax.set_ylabel("Density", fontsize=8.5)
        ax.legend(loc="upper right", fontsize=7.5, frameon=True)
        ax.grid(True, linestyle=":", alpha=0.6)
    plt.suptitle("Frequency Distributions & Fitted Normal Density Curves (India, 1991–2025)", fontsize=13, fontweight="bold", y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    hist_all_p = dist_dir / "histograms_all_variables.png"
    plt.savefig(hist_all_p, bbox_inches="tight")
    plt.close()
    generated_files.append({"category": "distributions", "filename": "histograms_all_variables.png", "path": "distributions/histograms_all_variables.png"})

    # B2. Combined 2x3 Normal Q-Q Plots
    fig, axes = plt.subplots(2, 3, figsize=(13, 7.5), dpi=150)
    axes = axes.flatten()
    for idx, col in enumerate(num_cols[:6]):
        ax = axes[idx]
        s = df[col].dropna()
        if len(s) > 2:
            (osm, osr), (slope, intercept, r_val) = stats.probplot(s, dist="norm")
            ax.scatter(osm, osr, color="#1565c0", alpha=0.8, s=25, label="Sample Quantiles")
            x_line = np.array([min(osm), max(osm)])
            ax.plot(x_line, slope * x_line + intercept, color="#c62828", linestyle="--", linewidth=1.5, label=f"Fit (r={r_val:.3f})")
            ax.set_title(f"Q-Q: {col}", fontsize=10.5, fontweight="bold", pad=6)
            ax.set_xlabel("Theoretical Quantiles", fontsize=8.5)
            ax.set_ylabel("Sample Quantiles", fontsize=8.5)
            ax.legend(loc="upper left", fontsize=7.5, frameon=True)
            ax.grid(True, linestyle=":", alpha=0.6)
    plt.suptitle("Normal Quantile-Quantile (Q-Q) Plots across Study Series (n = 35)", fontsize=13, fontweight="bold", y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    qq_all_p = dist_dir / "qq_plots_all_variables.png"
    plt.savefig(qq_all_p, bbox_inches="tight")
    plt.close()
    generated_files.append({"category": "distributions", "filename": "qq_plots_all_variables.png", "path": "distributions/qq_plots_all_variables.png"})

    # C. Boxplots for all variables (2x3 panel)
    fig, axes = plt.subplots(2, 3, figsize=(12, 7), dpi=150)
    axes = axes.flatten()
    for idx, col in enumerate(num_cols[:6]):
        ax = axes[idx]
        s = df[col].dropna()
        sns.boxplot(y=s, ax=ax, color="#90caf9", width=0.4, fliersize=4,
                    boxprops=dict(edgecolor="#0d47a1", linewidth=1.5),
                    whiskerprops=dict(color="#0d47a1", linewidth=1.2),
                    capprops=dict(color="#0d47a1", linewidth=1.2),
                    medianprops=dict(color="#b71c1c", linewidth=2.0))
        # Annotate mean as a diamond
        ax.scatter([0], [s.mean()], color="#2e7d32", marker="D", s=45, zorder=4, label=f"Mean: {s.mean():.2f}")
        ax.set_title(f"{col}", fontsize=11, fontweight="bold", pad=8)
        ax.set_ylabel(col, fontsize=9)
        ax.legend(loc="upper right", fontsize=8)
        ax.grid(True, linestyle=":", alpha=0.6)
    plt.suptitle("Boxplots & Outlier Identification across Study Variables (India, 1991–2025)", fontsize=13, fontweight="bold", y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    box_path = dist_dir / "boxplots_all_variables.png"
    plt.savefig(box_path, bbox_inches="tight")
    plt.close()
    generated_files.append({"category": "distributions", "filename": "boxplots_all_variables.png", "path": "distributions/boxplots_all_variables.png"})

    # D. Multi-panel Time Series Trend Chart (2x3 panel)
    fig, axes = plt.subplots(2, 3, figsize=(13, 7.5), dpi=150)
    axes = axes.flatten()
    for idx, col in enumerate(num_cols[:6]):
        ax = axes[idx]
        s = df[col].dropna()
        ax.plot(years.loc[s.index], s, marker="o", markersize=3.5, linewidth=1.6, color="#1565c0", label=col)
        ax.axhline(s.mean(), color="#d32f2f", linestyle="--", linewidth=1.1, label=f"Mean ({s.mean():.2f})")
        ax.set_title(col, fontsize=11, fontweight="bold", pad=6)
        ax.set_xlabel("Year", fontsize=8.5)
        ax.set_ylabel(col, fontsize=8.5)
        ax.legend(loc="upper right", fontsize=7.5, frameon=True)
        ax.grid(True, linestyle=":", alpha=0.6)
    plt.suptitle("Annual Macroeconomic Indicator Trends in India (1991–2025)", fontsize=13, fontweight="bold", y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    trends_path = ts_dir / "all_variables_trends.png"
    plt.savefig(trends_path, bbox_inches="tight")
    plt.close()
    generated_files.append({"category": "time_series", "filename": "all_variables_trends.png", "path": "time_series/all_variables_trends.png"})

    # 3. Correlation Heatmaps (Pearson & Spearman)
    corr_res = calc_results.get("correlation", {})
    p_mat = corr_res.get("pearson_matrix", {})
    if p_mat and len(p_mat) > 0:
        corr_df = pd.DataFrame(p_mat)
        plt.figure(figsize=(8, 6.5), dpi=150)
        sns.heatmap(corr_df, annot=True, fmt=".3f", cmap="vlag", vmin=-1.0, vmax=1.0,
                    linewidths=0.8, cbar_kws={"shrink": 0.8}, square=True)
        plt.title("Pearson Linear Correlation Matrix Heatmap (n=35)", fontsize=13, fontweight="bold", pad=12)
        plt.xticks(rotation=30, ha="right", fontsize=9)
        plt.yticks(rotation=0, fontsize=9)
        plt.savefig(corr_dir / "correlation_heatmap.png", bbox_inches="tight")
        plt.savefig(corr_dir / "correlation_heatmap_pearson.png", bbox_inches="tight")
        plt.close()
        generated_files.append({"category": "correlation", "filename": "correlation_heatmap.png", "path": "correlation/correlation_heatmap.png"})
        generated_files.append({"category": "correlation", "filename": "correlation_heatmap_pearson.png", "path": "correlation/correlation_heatmap_pearson.png"})

    s_mat = corr_res.get("spearman_matrix", {})
    if s_mat and len(s_mat) > 0:
        scorr_df = pd.DataFrame(s_mat)
        plt.figure(figsize=(8, 6.5), dpi=150)
        sns.heatmap(scorr_df, annot=True, fmt=".3f", cmap="vlag", vmin=-1.0, vmax=1.0,
                    linewidths=0.8, cbar_kws={"shrink": 0.8}, square=True)
        plt.title("Spearman Rank Correlation Matrix Heatmap (n=35)", fontsize=13, fontweight="bold", pad=12)
        plt.xticks(rotation=30, ha="right", fontsize=9)
        plt.yticks(rotation=0, fontsize=9)
        plt.savefig(corr_dir / "correlation_heatmap_spearman.png", bbox_inches="tight")
        plt.close()
        generated_files.append({"category": "correlation", "filename": "correlation_heatmap_spearman.png", "path": "correlation/correlation_heatmap_spearman.png"})

    # 4. Simple Regressions (5 scatter plots with fitted lines)
    reg_res = calc_results.get("regression", {})
    simples = reg_res.get("simple_regressions", [])
    simple_dir = reg_dir / "simple"
    simple_dir.mkdir(parents=True, exist_ok=True)

    fig_pan, axes_pan = plt.subplots(2, 3, figsize=(13.5, 8), dpi=150)
    axes_pan = axes_pan.flatten()

    for idx, s_info in enumerate(simples):
        pred = s_info.get("Predictor")
        if not pred or pred not in df.columns:
            continue
        sub_df = df[["GDP_Growth", pred]].dropna()
        x_vals = sub_df[pred]
        y_vals = sub_df["GDP_Growth"]
        slope = s_info.get("Slope", 0.0)
        intercept = s_info.get("Intercept", 0.0)
        r2_val = s_info.get("R_Squared", 0.0)
        p_val = s_info.get("p_value", 1.0)

        # Single plot
        plt.figure(figsize=(7, 4.8), dpi=150)
        plt.scatter(x_vals, y_vals, color="#1565c0", alpha=0.8, s=40, label="Observed (Annual)")
        x_seq = np.linspace(x_vals.min(), x_vals.max(), 100)
        plt.plot(x_seq, intercept + slope * x_seq, color="#c62828", linestyle="--", linewidth=1.8,
                 label=f"Fit: y = {slope:.3f}x + {intercept:.2f}\n(R² = {r2_val:.3f}, p = {p_val:.3f})")
        plt.title(f"Simple OLS: GDP Growth vs {pred}", fontsize=12, fontweight="bold", pad=10)
        plt.xlabel(pred, fontsize=10, labelpad=8)
        plt.ylabel("GDP Growth (%)", fontsize=10, labelpad=8)
        plt.legend(loc="best", frameon=True)
        plt.grid(True, linestyle=":", alpha=0.6)
        s_fname = f"simple_reg_{pred}.png"
        plt.savefig(reg_dir / s_fname, bbox_inches="tight")
        plt.savefig(simple_dir / f"simple_reg_GDP_Growth_vs_{pred}.png", bbox_inches="tight")
        plt.close()
        generated_files.append({"category": "regression", "filename": s_fname, "path": f"regression/{s_fname}"})

        # Subplot in 2x3 panel
        if idx < 5:
            ax_p = axes_pan[idx]
            ax_p.scatter(x_vals, y_vals, color="#1565c0", alpha=0.75, s=30)
            ax_p.plot(x_seq, intercept + slope * x_seq, color="#c62828", linestyle="--", linewidth=1.6)
            ax_p.set_title(f"vs {pred}\n(R² = {r2_val:.3f}, p = {p_val:.3f})", fontsize=10, fontweight="bold")
            ax_p.set_xlabel(pred, fontsize=8.5)
            ax_p.set_ylabel("GDP Growth (%)", fontsize=8.5)
            ax_p.grid(True, linestyle=":", alpha=0.6)

    # Clean up empty 6th subplot
    if len(axes_pan) > 5:
        axes_pan[5].axis("off")
    fig_pan.suptitle("Simple Linear Regression Models for GDP Growth (India, 1991–2025)", fontsize=13, fontweight="bold", y=0.98)
    fig_pan.tight_layout(rect=[0, 0, 1, 0.95])
    fig_pan.savefig(reg_dir / "simple_regressions_panel.png", bbox_inches="tight")
    plt.close(fig_pan)
    generated_files.append({"category": "regression", "filename": "simple_regressions_panel.png", "path": "regression/simple_regressions_panel.png"})

    # 5. Multiple OLS Regression Charts & Diagnostics
    fv_act = reg_res.get("fitted_vs_actual", [])
    if fv_act and len(fv_act) > 0:
        f_df = pd.DataFrame(fv_act)
        
        # A. Actual vs Fitted Time Series
        plt.figure(figsize=(9, 4.5), dpi=150)
        plt.plot(f_df["year"], f_df["actual"], marker="o", color="#1565c0", label="Actual GDP Growth", linewidth=2.0)
        plt.plot(f_df["year"], f_df["fitted"], marker="s", color="#e65100", linestyle="--", label="OLS Fitted Values", linewidth=2.0)
        
        plt.title("Multiple OLS Regression: Actual vs Fitted GDP Growth (1991–2025)", fontsize=13, fontweight="bold", pad=12)
        plt.xlabel("Year", fontsize=10, labelpad=8)
        plt.ylabel("GDP Growth (%)", fontsize=10, labelpad=8)
        plt.legend(loc="upper right", frameon=True)
        plt.grid(True, linestyle=":", alpha=0.6)

        fname_act = "regression_actual_vs_fitted.png"
        fpath_act = reg_dir / fname_act
        plt.savefig(fpath_act, bbox_inches="tight")
        plt.close()

        generated_files.append({"category": "regression", "filename": fname_act, "path": f"regression/{fname_act}"})

        # B. Residuals vs Fitted Scatter Plot
        fig, ax = plt.subplots(figsize=(8.5, 5), dpi=150)
        ax.scatter(f_df["fitted"], f_df["residual"], color="#6a1b9a", alpha=0.8, edgecolors="none", s=40)
        ax.axhline(0, color="#d32f2f", linestyle="--", linewidth=1.5)

        y_min, y_max = f_df["residual"].min(), f_df["residual"].max()
        y_padding = (y_max - y_min) * 0.10 if y_max != y_min else 1.0
        ax.set_ylim(y_min - y_padding, y_max + y_padding)

        fig.suptitle("Residuals vs Fitted Values", fontsize=12.5, fontweight="bold", y=0.98)
        ax.set_title("Evaluates linearity and constancy of error variance across predicted GDP Growth", fontsize=9.2, color="#334155", pad=8)
        ax.set_xlabel("Fitted GDP Growth (%)", fontsize=10, labelpad=8)
        ax.set_ylabel("Residuals", fontsize=10, labelpad=8)
        ax.grid(True, linestyle=":", alpha=0.6)
        plt.subplots_adjust(top=0.88, bottom=0.12, left=0.10, right=0.95)

        fname_res = "regression_residual_vs_fitted.png"
        fpath_res = reg_dir / fname_res
        plt.savefig(fpath_res, bbox_inches="tight")
        plt.savefig(diag_dir / "residual_vs_fitted.png", bbox_inches="tight")
        plt.savefig(diag_dir / "diag_residuals_vs_fitted.png", bbox_inches="tight")
        plt.close()

        generated_files.append({"category": "regression", "filename": fname_res, "path": f"regression/{fname_res}"})
        generated_files.append({"category": "diagnostics", "filename": "residual_vs_fitted.png", "path": "diagnostics/residual_vs_fitted.png"})

        # C. Normal Q-Q Plot of Residuals
        diag_res = calc_results.get("diagnostics", {})
        qq_data = diag_res.get("qq_plot_data", [])
        if qq_data and len(qq_data) > 0:
            qq_df = pd.DataFrame(qq_data)
            plt.figure(figsize=(7, 5), dpi=150)
            plt.scatter(qq_df["theoretical_quantile"], qq_df["sample_residual"], color="#0277bd", alpha=0.8, label="Sample Residuals")
            plt.plot(qq_df["theoretical_quantile"], qq_df["fitted_line"], color="#c62828", linestyle="--", linewidth=1.8, label="Normal Line")

            plt.title("Regression Diagnostics: Normal Q-Q Plot of Residuals", fontsize=13, fontweight="bold", pad=12)
            plt.xlabel("Theoretical Quantiles", fontsize=10, labelpad=8)
            plt.ylabel("Sample Residuals", fontsize=10, labelpad=8)
            plt.legend(loc="upper left", frameon=True)
            plt.grid(True, linestyle=":", alpha=0.6)

            fname_qq = "regression_qq_plot.png"
            fpath_qq = reg_dir / fname_qq
            plt.savefig(fpath_qq, bbox_inches="tight")
            plt.savefig(diag_dir / "diag_qq_residuals.png", bbox_inches="tight")
            plt.close()

            generated_files.append({"category": "regression", "filename": fname_qq, "path": f"regression/{fname_qq}"})
            generated_files.append({"category": "diagnostics", "filename": "diag_qq_residuals.png", "path": "diagnostics/diag_qq_residuals.png"})

        # D. Residual Distribution Histogram with Normal Curve
        res_series = f_df["residual"].dropna()
        plt.figure(figsize=(7.5, 4.8), dpi=150)
        sns.histplot(res_series, kde=True, bins=8, color="#00838f", stat="density", edgecolor="white", alpha=0.6)
        # Overlay fitted normal curve
        mu_r, std_r = res_series.mean(), res_series.std()
        x_norm = np.linspace(res_series.min() - 1, res_series.max() + 1, 100)
        plt.plot(x_norm, stats.norm.pdf(x_norm, mu_r, std_r), color="#c62828", linestyle="--", linewidth=1.8,
                 label=f"Fitted Normal (μ={mu_r:.2f}, σ={std_r:.2f})")
        plt.axvline(0, color="#d32f2f", linestyle=":", linewidth=1.2, label="Zero Reference")
        plt.title("Regression Diagnostics: Residual Distribution vs Normal Curve", fontsize=12.5, fontweight="bold", pad=10)
        plt.xlabel("Residual Value", fontsize=10, labelpad=8)
        plt.ylabel("Density", fontsize=10, labelpad=8)
        plt.legend(loc="upper left", frameon=True)
        plt.grid(True, linestyle=":", alpha=0.6)
        plt.savefig(diag_dir / "diag_residual_distribution.png", bbox_inches="tight")
        plt.close()
        generated_files.append({"category": "diagnostics", "filename": "diag_residual_distribution.png", "path": "diagnostics/diag_residual_distribution.png"})

        # E. Cook's Distance Plot
        cd_info = diag_res.get("cooks_distance", {})
        rv_fit = diag_res.get("residuals_vs_fitted", [])
        if rv_fit and len(rv_fit) > 0:
            cd_df = pd.DataFrame(rv_fit)
            if "cooks_d" in cd_df.columns:
                thresh_val = float(cd_info.get("threshold", 4.0 / len(cd_df)))
                fig, ax = plt.subplots(figsize=(8.5, 5), dpi=150)
                markerline, stemlines, baseline = ax.stem(
                    cd_df["year"], cd_df["cooks_d"],
                    linefmt="#1565c0", markerfmt="o", basefmt=" "
                )
                plt.setp(markerline, markersize=5, color="#1565c0")
                plt.setp(stemlines, linewidth=1.4, color="#1565c0", alpha=0.7)
                ax.axhline(thresh_val, color="#d32f2f", linestyle="--", linewidth=1.5,
                           label=f"Screening Threshold 4/n ≈ {thresh_val:.3f}")
                max_cd = cd_df["cooks_d"].max()
                ax.set_ylim(-0.03, max_cd * 1.16)
                for _, row_cd in cd_df.iterrows():
                    if row_cd["cooks_d"] > thresh_val:
                        ax.scatter([row_cd["year"]], [row_cd["cooks_d"]], color="#d32f2f", s=50, zorder=5)
                        ax.annotate(
                            f"{int(row_cd['year'])} ({row_cd['cooks_d']:.3f})",
                            (row_cd["year"], row_cd["cooks_d"]),
                            textcoords="offset points", xytext=(0, 7), ha="center",
                            fontsize=8.5, fontweight="bold", color="#b71c1c"
                        )
                fig.suptitle("Cook's Distance — Influential Observations", fontsize=12.5, fontweight="bold", y=0.98)
                ax.set_title(f"Influence check: observations exceeding the Cook's D screening threshold 4/n ≈ {thresh_val:.3f}", fontsize=9.2, color="#334155", pad=8)
                ax.set_xlabel("Year", fontsize=10, labelpad=8)
                ax.set_ylabel("Cook's Distance (D)", fontsize=10, labelpad=8)
                ax.legend(loc="upper left", frameon=True)
                ax.grid(True, linestyle=":", alpha=0.6)
                plt.subplots_adjust(top=0.88, bottom=0.12, left=0.10, right=0.95)

                fname_cd = "cooks_distance.png"
                plt.savefig(diag_dir / fname_cd, bbox_inches="tight")
                plt.savefig(diag_dir / "diag_cooks_distance.png", bbox_inches="tight")
                plt.savefig(reg_dir / fname_cd, bbox_inches="tight")
                plt.close()

                generated_files.append({"category": "diagnostics", "filename": fname_cd, "path": f"diagnostics/{fname_cd}"})
                generated_files.append({"category": "regression", "filename": fname_cd, "path": f"regression/{fname_cd}"})

        # F. Variance Inflation Factor (VIF) Bar Chart
        vif_data = diag_res.get("vif_results", [])
        if vif_data and len(vif_data) > 0:
            v_df = pd.DataFrame(vif_data)
            plt.figure(figsize=(7.5, 4.2), dpi=150)
            bar_colors = ["#d32f2f" if v > 5 else "#1565c0" for v in v_df["VIF"]]
            y_pos = np.arange(len(v_df))
            plt.barh(y_pos, v_df["VIF"], color=bar_colors, alpha=0.85, height=0.55, edgecolor="#0d47a1")
            plt.yticks(y_pos, v_df["Variable"], fontsize=9.5)
            plt.axvline(5.0, color="#f57c00", linestyle="--", linewidth=1.5, label="Moderate Threshold (VIF = 5)")
            plt.axvline(10.0, color="#d32f2f", linestyle=":", linewidth=1.5, label="Severe Threshold (VIF = 10)")
            for i, v in enumerate(v_df["VIF"]):
                plt.text(v + 0.1, i, f"{v:.2f}", va="center", fontsize=9, fontweight="bold")
            plt.title("Multicollinearity Diagnostics: Variance Inflation Factors (VIF)", fontsize=12, fontweight="bold", pad=10)
            plt.xlabel("Variance Inflation Factor (VIF)", fontsize=10, labelpad=8)
            plt.xlim(0, max(max(v_df["VIF"]) + 1.2, 11))
            plt.legend(loc="lower right", frameon=True)
            plt.grid(True, linestyle=":", alpha=0.6)
            plt.savefig(diag_dir / "vif_chart.png", bbox_inches="tight")
            plt.close()
            generated_files.append({"category": "diagnostics", "filename": "vif_chart.png", "path": "diagnostics/vif_chart.png"})

    return generated_files
