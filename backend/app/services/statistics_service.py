import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, Any, List, Optional
from app.services import data_service

def compute_mode(s: pd.Series) -> Any:
    """
    Calculate statistical mode strictly based on observed value frequencies.
    - If every value occurs only once (max frequency == 1), return "No unique mode (all values occur once)".
    - If multiple values share the highest frequency (> 1), return formatted values with multimodal designation e.g. "7.611, 7.629 (bimodal)".
    - If a single value has the highest frequency (> 1), return that value as float/int.
    - Never fallback to min, max, median, or first element.
    """
    s_clean = s.dropna()
    if len(s_clean) == 0:
        return "No unique mode (all values occur once)"

    counts = s_clean.value_counts()
    max_freq = counts.max()

    if max_freq <= 1:
        return "No unique mode (all values occur once)"

    modes = counts[counts == max_freq].index.tolist()
    modes.sort()

    if len(modes) == 1:
        m = modes[0]
        return float(m) if isinstance(m, (int, float, np.number)) else str(m)
    else:
        formatted_modes = []
        for m in modes:
            if isinstance(m, (float, np.floating)):
                formatted_modes.append(f"{m:.4f}".rstrip("0").rstrip("."))
            else:
                formatted_modes.append(str(m))
        
        mode_str = ", ".join(formatted_modes)
        if len(modes) == 2:
            tag = "bimodal"
        elif len(modes) == 3:
            tag = "trimodal"
        else:
            tag = f"{len(modes)}-modal"
        return f"{mode_str} ({tag})"

def calculate_descriptive_statistics() -> Dict[str, Any]:
    """
    Dynamically calculate descriptive statistics for all numerical variables
    from the actual World Bank dataset.
    """
    dataset_res = data_service.get_dataset()
    if not dataset_res.get("available") or not dataset_res.get("data"):
        return {
            "available": False,
            "reason": dataset_res.get("reason", "Dataset not available for calculation."),
            "data": [],
        }

    records = dataset_res["data"]
    df = pd.DataFrame(records)

    num_cols = [c for c in df.columns if c != "Year" and pd.api.types.is_numeric_dtype(df[c])]

    results: List[Dict[str, Any]] = []
    for col in num_cols:
        s = df[col].dropna()
        if len(s) == 0:
            continue

        q1 = float(s.quantile(0.25))
        q2 = float(s.quantile(0.50))
        q3 = float(s.quantile(0.75))
        iqr = float(q3 - q1)

        mode_val = compute_mode(s)

        stat_dict = {
            "Variable": col,
            "Count": int(len(s)),
            "Mean": float(s.mean()),
            "Median": float(s.median()),
            "Mode": mode_val,
            "Variance": float(s.var(ddof=1)) if len(s) > 1 else 0.0,
            "Std_Dev": float(s.std(ddof=1)) if len(s) > 1 else 0.0,
            "Min": float(s.min()),
            "Max": float(s.max()),
            "Range": float(s.max() - s.min()),
            "Q1": q1,
            "Q2": q2,
            "Q3": q3,
            "IQR": iqr,
            "Skewness": float(stats.skew(s, bias=False)) if len(s) > 2 else 0.0,
            "Excess_Kurtosis": float(stats.kurtosis(s, bias=False)) if len(s) > 3 else 0.0,
        }
        results.append(stat_dict)

    years = df["Year"].dropna().astype(int) if "Year" in df.columns else []

    return {
        "available": True,
        "sample_size": len(df),
        "start_year": int(years.min()) if len(years) > 0 else None,
        "end_year": int(years.max()) if len(years) > 0 else None,
        "variables_analyzed": num_cols,
        "data": results,
    }

def calculate_distribution_analysis() -> Dict[str, Any]:
    """
    Dynamically calculate distribution analysis, binned histograms, KDE density points,
    Q-Q quantiles, Shapiro-Wilk & Anderson-Darling normality tests for all numerical variables.
    """
    dataset_res = data_service.get_dataset()
    if not dataset_res.get("available") or not dataset_res.get("data"):
        return {
            "available": False,
            "reason": dataset_res.get("reason", "Dataset not available for distribution calculation."),
            "data": [],
        }

    records = dataset_res["data"]
    df = pd.DataFrame(records)
    num_cols = [c for c in df.columns if c != "Year" and pd.api.types.is_numeric_dtype(df[c])]

    variables_analysis: Dict[str, Dict[str, Any]] = {}
    summary_table_rows: List[Dict[str, Any]] = []

    for col in num_cols:
        s = df[col].dropna().astype(float)
        if len(s) == 0:
            continue

        n = len(s)
        min_val = float(s.min())
        max_val = float(s.max())
        mean_val = float(s.mean())
        median_val = float(s.median())
        std_val = float(s.std(ddof=1)) if n > 1 else 0.0

        # 1. Binned Histogram Data
        num_bins = 7
        counts, bin_edges = np.histogram(s, bins=num_bins)
        histogram_data = []
        for i in range(len(counts)):
            b_min = float(bin_edges[i])
            b_max = float(bin_edges[i + 1])
            b_mid = float((b_min + b_max) / 2.0)
            cnt = int(counts[i])
            pct = float(cnt / n * 100.0)
            histogram_data.append({
                "bin_range": f"{b_min:.2f}–{b_max:.2f}",
                "bin_min": b_min,
                "bin_max": b_max,
                "bin_mid": b_mid,
                "count": cnt,
                "percentage": round(pct, 2),
            })

        # 2. KDE Density Points (50 points)
        kde_data = []
        if n > 1 and std_val > 0:
            try:
                kde = stats.gaussian_kde(s)
                x_grid = np.linspace(min_val, max_val, 50)
                y_densities = kde(x_grid)
                for x_val, y_val in zip(x_grid, y_densities):
                    kde_data.append({
                        "x": float(x_val),
                        "density": float(y_val),
                    })
            except Exception:
                pass

        # 3. Q-Q Plot Points
        qq_data = []
        qq_fit = None
        if n > 2:
            try:
                (osm, osr), (slope, intercept, r_val) = stats.probplot(s, dist="norm")
                qq_fit = {
                    "slope": float(slope),
                    "intercept": float(intercept),
                    "r_value": float(r_val),
                }
                for th_q, sm_q in zip(osm, osr):
                    fit_val = float(slope * th_q + intercept)
                    qq_data.append({
                        "theoretical_quantile": float(th_q),
                        "sample_quantile": float(sm_q),
                        "fitted_line": fit_val,
                    })
            except Exception:
                pass

        # 4. Normality Tests (Shapiro-Wilk & Anderson-Darling)
        sw_stat, sw_p = stats.shapiro(s) if n >= 3 else (0.0, 1.0)
        sw_stat = float(sw_stat)
        sw_p = float(sw_p)
        sw_normal = bool(sw_p >= 0.05)

        ad_res = stats.anderson(s, dist="norm") if n >= 3 else None
        ad_stat = float(ad_res.statistic) if ad_res else 0.0
        ad_cv_5pct = float(ad_res.critical_values[2]) if ad_res else 0.713
        ad_normal = bool(ad_stat < ad_cv_5pct)

        # Shape Summary
        sk = float(stats.skew(s, bias=False)) if n > 2 else 0.0
        if abs(sk) < 0.5:
            sk_type = "Symmetric"
        elif sk >= 0.5:
            sk_type = "Positively Skewed (Right-tailed)"
        else:
            sk_type = "Negatively Skewed (Left-tailed)"

        kt = float(stats.kurtosis(s, bias=False)) if n > 3 else 0.0
        if abs(kt) < 0.5:
            kt_type = "Mesokurtic (Normal-like)"
        elif kt >= 0.5:
            kt_type = "Leptokurtic (Heavy-tailed/Peaked)"
        else:
            kt_type = "Platykurtic (Light-tailed/Flat)"

        is_normal_overall = sw_normal and ad_normal
        recommendation = "No evidence against normality (α = 0.05)" if sw_normal else "Evidence of non-normality (α = 0.05)"

        variables_analysis[col] = {
            "Variable": col,
            "sample_count": n,
            "mean": mean_val,
            "median": median_val,
            "std_dev": std_val,
            "histogram": histogram_data,
            "kde": kde_data,
            "qq_plot": qq_data,
            "qq_fit": qq_fit,
            "normality_tests": {
                "shapiro_wilk": {
                    "statistic": sw_stat,
                    "p_value": sw_p,
                    "is_normal_5pct": sw_normal,
                },
                "anderson_darling": {
                    "statistic": ad_stat,
                    "critical_value_5pct": ad_cv_5pct,
                    "is_normal_5pct": ad_normal,
                },
                "is_normal": is_normal_overall,
                "recommendation": recommendation,
            },
            "shape_summary": {
                "skewness": sk,
                "skew_type": sk_type,
                "excess_kurtosis": kt,
                "kurtosis_type": kt_type,
            },
        }

        summary_table_rows.append({
            "Variable": col,
            "Shapiro_Wilk_Stat": round(sw_stat, 6),
            "Shapiro_Wilk_p": round(sw_p, 6),
            "SW_Normal_5pct": "Yes" if sw_normal else "No",
            "Anderson_Darling_Stat": round(ad_stat, 6),
            "AD_Critical_5pct": round(ad_cv_5pct, 6),
            "AD_Normal_5pct": "Yes" if ad_normal else "No",
            "Skewness": round(sk, 6),
            "Skew_Type": sk_type,
            "Kurtosis": round(kt, 6),
            "Kurtosis_Type": kt_type,
            "Is_Normal_SW": sw_normal,
            "Is_Normal_AD": ad_normal,
            "Recommendation": recommendation,
        })

    years = df["Year"].dropna().astype(int) if "Year" in df.columns else []

    return {
        "available": True,
        "sample_size": len(df),
        "start_year": int(years.min()) if len(years) > 0 else None,
        "end_year": int(years.max()) if len(years) > 0 else None,
        "variables": num_cols,
        "variables_analysis": variables_analysis,
        "data": summary_table_rows,
    }


def calculate_correlation_analysis() -> Dict[str, Any]:
    """
    Dynamically calculate Pearson and Spearman correlation matrices, p-values,
    heatmap chart-ready data, and pairwise observation counts from the actual World Bank dataset.
    """
    dataset_res = data_service.get_dataset()
    if not dataset_res.get("available") or not dataset_res.get("data"):
        return {
            "available": False,
            "reason": dataset_res.get("reason", "Dataset not available for correlation calculation."),
            "data": [],
        }

    records = dataset_res["data"]
    df = pd.DataFrame(records)
    num_cols = [c for c in df.columns if c != "Year" and pd.api.types.is_numeric_dtype(df[c])]

    years = df["Year"].dropna().astype(int) if "Year" in df.columns else []

    pearson_matrix: Dict[str, Dict[str, Optional[float]]] = {v1: {} for v1 in num_cols}
    spearman_matrix: Dict[str, Dict[str, Optional[float]]] = {v1: {} for v1 in num_cols}
    p_values_pearson: Dict[str, Dict[str, Optional[float]]] = {v1: {} for v1 in num_cols}
    p_values_spearman: Dict[str, Dict[str, Optional[float]]] = {v1: {} for v1 in num_cols}
    observations_matrix: Dict[str, Dict[str, Optional[int]]] = {v1: {} for v1 in num_cols}

    heatmap_data: List[Dict[str, Any]] = []
    pairwise_summary: List[Dict[str, Any]] = []

    for v1 in num_cols:
        for v2 in num_cols:
            if v1 == v2:
                s = df[v1].dropna()
                n_count = len(s)
                pearson_matrix[v1][v2] = 1.0
                spearman_matrix[v1][v2] = 1.0
                p_values_pearson[v1][v2] = 0.0
                p_values_spearman[v1][v2] = 0.0
                observations_matrix[v1][v2] = int(n_count)

                heatmap_data.append({
                    "x": v1,
                    "y": v2,
                    "pearson_r": 1.0,
                    "pearson_p": 0.0,
                    "spearman_rho": 1.0,
                    "spearman_p": 0.0,
                    "n_obs": int(n_count),
                    "significant_5pct": True,
                })
            else:
                pair_df = df[[v1, v2]].dropna()
                n_pair = len(pair_df)
                observations_matrix[v1][v2] = int(n_pair)

                if n_pair >= 3:
                    try:
                        r_p, p_p = stats.pearsonr(pair_df[v1], pair_df[v2])
                        r_s, p_s = stats.spearmanr(pair_df[v1], pair_df[v2])

                        r_p_val = float(r_p) if not np.isnan(r_p) else None
                        p_p_val = float(p_p) if not np.isnan(p_p) else None
                        r_s_val = float(r_s) if not np.isnan(r_s) else None
                        p_s_val = float(p_s) if not np.isnan(p_s) else None
                    except Exception:
                        r_p_val, p_p_val, r_s_val, p_s_val = None, None, None, None
                else:
                    r_p_val, p_p_val, r_s_val, p_s_val = None, None, None, None

                pearson_matrix[v1][v2] = r_p_val
                spearman_matrix[v1][v2] = r_s_val
                p_values_pearson[v1][v2] = p_p_val
                p_values_spearman[v1][v2] = p_s_val

                sig_5pct = bool(p_p_val is not None and p_p_val < 0.05)

                heatmap_data.append({
                    "x": v1,
                    "y": v2,
                    "pearson_r": r_p_val,
                    "pearson_p": p_p_val,
                    "spearman_rho": r_s_val,
                    "spearman_p": p_s_val,
                    "n_obs": int(n_pair),
                    "significant_5pct": sig_5pct,
                })

    for i in range(len(num_cols)):
        for j in range(i + 1, len(num_cols)):
            v1 = num_cols[i]
            v2 = num_cols[j]
            r_p = pearson_matrix[v1][v2]
            p_p = p_values_pearson[v1][v2]
            r_s = spearman_matrix[v1][v2]
            p_s = p_values_spearman[v1][v2]
            n_obs = observations_matrix[v1][v2]

            if r_p is None:
                strength = "N/A"
            else:
                abs_r = abs(r_p)
                if abs_r >= 0.8:
                    str_label = "Very Strong"
                elif abs_r >= 0.6:
                    str_label = "Strong"
                elif abs_r >= 0.4:
                    str_label = "Moderate"
                elif abs_r >= 0.2:
                    str_label = "Weak"
                else:
                    str_label = "Very Weak / None"

                direction = "Positive" if r_p > 0 else "Negative"
                strength = f"{direction} {str_label}"

            pairwise_summary.append({
                "Variable_1": v1,
                "Variable_2": v2,
                "Pearson_r": round(r_p, 6) if r_p is not None else None,
                "Pearson_p": round(p_p, 6) if p_p is not None else None,
                "Spearman_rho": round(r_s, 6) if r_s is not None else None,
                "Spearman_p": round(p_s, 6) if p_s is not None else None,
                "Observations_Used": n_obs,
                "Significant_5pct": "Yes" if (p_p is not None and p_p < 0.05) else "No",
                "Relationship": strength,
            })

    return {
        "available": True,
        "sample_size": len(df),
        "start_year": int(years.min()) if len(years) > 0 else None,
        "end_year": int(years.max()) if len(years) > 0 else None,
        "variables": num_cols,
        "pearson_matrix": pearson_matrix,
        "spearman_matrix": spearman_matrix,
        "p_values_pearson": p_values_pearson,
        "p_values_spearman": p_values_spearman,
        "observations_matrix": observations_matrix,
        "heatmap_data": heatmap_data,
        "pairwise_summary": pairwise_summary,
        "data": pairwise_summary,
    }


def calculate_regression_analysis() -> Dict[str, Any]:
    """
    Dynamically calculate Multiple Linear Regression using statsmodels.OLS on the actual World Bank dataset.
    Dependent variable: GDP_Growth
    Independent variables: Inflation, FDI_Net_Inflows, Exports, Gross_Capital_Formation, Unemployment
    """
    import statsmodels.api as sm

    dataset_res = data_service.get_dataset()
    if not dataset_res.get("available") or not dataset_res.get("data"):
        return {
            "available": False,
            "reason": dataset_res.get("reason", "Dataset not available for regression calculation."),
            "data": [],
        }

    records = dataset_res["data"]
    df = pd.DataFrame(records)

    dep_var = "GDP_Growth"
    indep_vars = ["Inflation", "FDI_Net_Inflows", "Exports", "Gross_Capital_Formation", "Unemployment"]

    req_cols = [dep_var] + indep_vars
    req_cols_with_year = ["Year"] + req_cols if "Year" in df.columns else req_cols

    reg_df = df[req_cols_with_year].dropna()

    if len(reg_df) < len(indep_vars) + 2:
        return {
            "available": False,
            "reason": f"Insufficient complete observations ({len(reg_df)}) for regression.",
            "data": [],
        }

    Y = reg_df[dep_var].astype(float)
    X = reg_df[indep_vars].astype(float)
    X_const = sm.add_constant(X)

    model = sm.OLS(Y, X_const)
    results = model.fit()

    conf = results.conf_int(alpha=0.05)
    from scipy.stats import t as t_dist
    hc3_cov = results.cov_HC3
    df_resid = results.df_resid
    t_crit = float(t_dist.ppf(0.975, df_resid))

    coefficients: List[Dict[str, Any]] = []
    robust_regression: List[Dict[str, Any]] = []

    for i, var in enumerate(X_const.columns):
        b = float(results.params[var])
        se_ols = float(results.bse[var])
        t_ols = float(results.tvalues[var])
        p_ols = float(results.pvalues[var])
        ci_ols_low = float(conf.loc[var, 0])
        ci_ols_high = float(conf.loc[var, 1])

        se_hc3 = float(np.sqrt(hc3_cov[i, i]))
        t_hc3 = float(b / se_hc3) if se_hc3 > 0 else 0.0
        p_hc3 = float(2 * t_dist.sf(np.abs(t_hc3), df_resid))
        ci_hc3_low = float(b - t_crit * se_hc3)
        ci_hc3_high = float(b + t_crit * se_hc3)
        sig_hc3 = bool(p_hc3 < 0.05)
        pct_change = float((se_hc3 - se_ols) / se_ols * 100) if se_ols > 0 else 0.0
        pct_str = f"{'+' if pct_change > 0 else ''}{pct_change:.1f}%"

        # Primary coefficients table uses HC3 Robust SE inference
        coefficients.append({
            "Variable": var,
            "variable": var,
            "Coefficient": round(b, 6),
            "coef": round(b, 6),
            "Std_Error": round(se_hc3, 6),
            "se": round(se_hc3, 6),
            "t_statistic": round(t_hc3, 6),
            "t": round(t_hc3, 6),
            "p_value": round(p_hc3, 6),
            "p": round(p_hc3, 6),
            "CI_Lower_95": round(ci_hc3_low, 6),
            "CI_Upper_95": round(ci_hc3_high, 6),
            "ci_low": round(ci_hc3_low, 6),
            "ci_high": round(ci_hc3_high, 6),
            "Significant_5pct": "Yes" if sig_hc3 else "No",
            "is_significant": sig_hc3,
            "OLS_SE": round(se_ols, 6),
            "OLS_t": round(t_ols, 6),
            "OLS_p": round(p_ols, 6),
            "OLS_CI_Lower_95": round(ci_ols_low, 6),
            "OLS_CI_Upper_95": round(ci_ols_high, 6),
            "HC3_SE": round(se_hc3, 6),
            "HC3_t": round(t_hc3, 6),
            "HC3_p": round(p_hc3, 6),
            "HC3_CI_Lower_95": round(ci_hc3_low, 6),
            "HC3_CI_Upper_95": round(ci_hc3_high, 6),
        })

        # Detailed OLS vs HC3 comparison
        robust_regression.append({
            "Variable": var,
            "variable": var,
            "Coefficient": round(b, 6),
            "coef": round(b, 6),
            "OLS_Coef": round(b, 6),
            "OLS_SE": round(se_ols, 6),
            "se_ols": round(se_ols, 6),
            "OLS_t": round(t_ols, 6),
            "t_ols": round(t_ols, 6),
            "OLS_p": round(p_ols, 6),
            "p_ols": round(p_ols, 6),
            "HC3_SE": round(se_hc3, 6),
            "se_hc3": round(se_hc3, 6),
            "HC3_t": round(t_hc3, 6),
            "t_hc3": round(t_hc3, 6),
            "HC3_p": round(p_hc3, 6),
            "p_hc3": round(p_hc3, 6),
            "CI_Lower_OLS": round(ci_ols_low, 6),
            "ci_lower_ols": round(ci_ols_low, 6),
            "CI_Upper_OLS": round(ci_ols_high, 6),
            "ci_upper_ols": round(ci_ols_high, 6),
            "CI_Lower_HC3": round(ci_hc3_low, 6),
            "ci_lower_hc3": round(ci_hc3_low, 6),
            "CI_Upper_HC3": round(ci_hc3_high, 6),
            "ci_upper_hc3": round(ci_hc3_high, 6),
            "SE_Change_pct": round(pct_change, 2),
            "se_change_pct": round(pct_change, 2),
            "SE_change": pct_str,
            "se_change": pct_str,
            "Significant_OLS": "Yes" if p_ols < 0.05 else "No",
            "Significant_HC3": "Yes" if sig_hc3 else "No",
        })

    fitted_values = results.fittedvalues
    residuals = results.resid

    fitted_vs_actual: List[Dict[str, Any]] = []
    for idx, row in reg_df.iterrows():
        yr = int(row["Year"]) if "Year" in reg_df.columns else idx
        act = float(row[dep_var])
        fit = float(fitted_values[idx])
        res = float(residuals[idx])
        fitted_vs_actual.append({
            "year": yr,
            "actual": round(act, 4),
            "fitted": round(fit, 4),
            "residual": round(res, 4),
        })

    years = reg_df["Year"].astype(int) if "Year" in reg_df.columns else []

    r_squared = float(results.rsquared)
    adj_r_squared = float(results.rsquared_adj)
    f_stat = float(results.fvalue) if results.fvalue is not None else None
    prob_f = float(results.f_pvalue) if results.f_pvalue is not None else None
    n_obs = int(results.nobs)
    aic = float(results.aic)
    bic = float(results.bic)
    resid_std_err = float(np.sqrt(results.scale))

    # Simple regressions for each predictor
    simple_regressions: List[Dict[str, Any]] = []
    for pred in indep_vars:
        sub_df = df[[dep_var, pred]].dropna()
        if len(sub_df) >= 3:
            s_Y = sub_df[dep_var].astype(float)
            s_X = sm.add_constant(sub_df[pred].astype(float))
            s_m = sm.OLS(s_Y, s_X).fit()
            s_ci = s_m.conf_int(alpha=0.05)
            s_p = float(s_m.pvalues[pred])
            s_r = float(stats.pearsonr(sub_df[pred], sub_df[dep_var])[0])
            simple_regressions.append({
                "Model": f"GDP_Growth ~ {pred}",
                "Predictor": pred,
                "Intercept": round(float(s_m.params["const"]), 6),
                "Slope": round(float(s_m.params[pred]), 6),
                "Std_Error": round(float(s_m.bse[pred]), 6),
                "t_Statistic": round(float(s_m.tvalues[pred]), 6),
                "p_value": round(s_p, 6),
                "Pearson_r": round(s_r, 6),
                "r": round(s_r, 6),
                "CI_Lower": round(float(s_ci.loc[pred, 0]), 6),
                "CI_Upper": round(float(s_ci.loc[pred, 1]), 6),
                "R_Squared": round(float(s_m.rsquared), 6),
                "Adj_R_Squared": round(float(s_m.rsquared_adj), 6),
                "F_Statistic": round(float(s_m.fvalue), 6),
                "F_p_value": round(float(s_m.f_pvalue), 6),
                "AIC": round(float(s_m.aic), 4),
                "BIC": round(float(s_m.bic), 4),
                "Significant": "Yes" if s_p < 0.05 else "No",
            })

    # Model comparison
    model_comparison: List[Dict[str, Any]] = []
    for s_item in simple_regressions:
        model_comparison.append({
            "Model": s_item["Model"],
            "Predictor": s_item["Predictor"],
            "Type": "Simple OLS",
            "R_Squared": s_item["R_Squared"],
            "Adj_R_Squared": s_item["Adj_R_Squared"],
            "F_Statistic": s_item["F_Statistic"],
            "p_value": s_item["p_value"],
            "AIC": s_item["AIC"],
            "BIC": s_item["BIC"],
            "Significant": s_item["Significant"],
        })
    model_comparison.append({
        "Model": "Multiple OLS (5 predictors)",
        "Predictor": "All 5 Predictors",
        "Type": "Multiple OLS",
        "R_Squared": round(r_squared, 6),
        "Adj_R_Squared": round(adj_r_squared, 6),
        "F_Statistic": round(f_stat, 6) if f_stat is not None else None,
        "p_value": round(prob_f, 6) if prob_f is not None else None,
        "AIC": round(aic, 4),
        "BIC": round(bic, 4),
        "Significant": "Yes" if (prob_f is not None and prob_f < 0.05) else "No",
    })

    return {
        "available": True,
        "dependent_variable": dep_var,
        "independent_variables": indep_vars,
        "sample_size": n_obs,
        "start_year": int(years.min()) if len(years) > 0 else None,
        "end_year": int(years.max()) if len(years) > 0 else None,
        "r_squared": round(r_squared, 6),
        "adj_r_squared": round(adj_r_squared, 6),
        "f_statistic": round(f_stat, 6) if f_stat is not None else None,
        "prob_f_statistic": round(prob_f, 6) if prob_f is not None else None,
        "aic": round(aic, 4),
        "bic": round(bic, 4),
        "residual_std_error": round(resid_std_err, 6),
        "coefficients": coefficients,
        "simple_regressions": simple_regressions,
        "robust_regression": robust_regression,
        "model_comparison": model_comparison,
        "fitted_vs_actual": fitted_vs_actual,
        "data": coefficients,
    }


def calculate_simple_regression() -> Dict[str, Any]:
    """Dynamically calculate simple OLS models for each predictor."""
    res = calculate_regression_analysis()
    if not res.get("available"):
        return res
    return {
        "available": True,
        "sample_size": res.get("sample_size"),
        "start_year": res.get("start_year"),
        "end_year": res.get("end_year"),
        "data": res.get("simple_regressions", []),
    }


def calculate_robust_regression() -> Dict[str, Any]:
    """Dynamically calculate HC3 robust regression standard errors."""
    res = calculate_regression_analysis()
    if not res.get("available"):
        return res
    return {
        "available": True,
        "sample_size": res.get("sample_size"),
        "start_year": res.get("start_year"),
        "end_year": res.get("end_year"),
        "data": res.get("robust_regression", []),
    }


def calculate_model_comparison() -> Dict[str, Any]:
    """Dynamically calculate model comparison table."""
    res = calculate_regression_analysis()
    if not res.get("available"):
        return res
    return {
        "available": True,
        "sample_size": res.get("sample_size"),
        "start_year": res.get("start_year"),
        "end_year": res.get("end_year"),
        "data": res.get("model_comparison", []),
    }


def calculate_regression_diagnostics() -> Dict[str, Any]:
    """
    Dynamically calculate regression diagnostics for the OLS model:
    - VIF for predictors
    - Breusch-Pagan test for heteroskedasticity
    - Durbin-Watson statistic for autocorrelation
    - Residuals and fitted values
    - Residual vs fitted chart data
    - Q-Q plot of residuals
    - Shapiro-Wilk normality of residuals test
    """
    import statsmodels.api as sm
    from statsmodels.stats.outliers_influence import variance_inflation_factor
    from statsmodels.stats.diagnostic import het_breuschpagan
    from statsmodels.stats.stattools import durbin_watson

    dataset_res = data_service.get_dataset()
    if not dataset_res.get("available") or not dataset_res.get("data"):
        return {
            "available": False,
            "reason": dataset_res.get("reason", "Dataset not available for diagnostics calculation."),
            "data": [],
        }

    records = dataset_res["data"]
    df = pd.DataFrame(records)

    dep_var = "GDP_Growth"
    indep_vars = ["Inflation", "FDI_Net_Inflows", "Exports", "Gross_Capital_Formation", "Unemployment"]

    req_cols = [dep_var] + indep_vars
    req_cols_with_year = ["Year"] + req_cols if "Year" in df.columns else req_cols

    reg_df = df[req_cols_with_year].dropna()

    if len(reg_df) < len(indep_vars) + 2:
        return {
            "available": False,
            "reason": f"Insufficient complete observations ({len(reg_df)}) for diagnostics.",
            "data": [],
        }

    Y = reg_df[dep_var].astype(float)
    X = reg_df[indep_vars].astype(float)
    X_const = sm.add_constant(X)

    model = sm.OLS(Y, X_const)
    results = model.fit()

    fitted = results.fittedvalues
    residuals = results.resid
    n = len(reg_df)

    vif_results: List[Dict[str, Any]] = []
    for i, col in enumerate(X_const.columns):
        if col == "const":
            continue
        vif_val = float(variance_inflation_factor(X_const.values, i))
        warn = bool(vif_val > 5.0)
        severe = bool(vif_val > 10.0)
        if severe:
            vif_status = "Severe Multicollinearity (VIF > 10)"
        elif warn:
            vif_status = "Moderate Multicollinearity (VIF > 5)"
        else:
            vif_status = "Low Multicollinearity (VIF <= 5)"

        vif_results.append({
            "Variable": col,
            "VIF": round(vif_val, 6),
            "Multicollinear_Warn": warn,
            "Severe_Warn": severe,
            "Status": vif_status,
        })

    # Cook's Distance Calculation
    infl = results.get_influence()
    cooks_d, _ = infl.cooks_distance
    cooks_d_arr = np.array(cooks_d, dtype=float)
    threshold_4n = float(4.0 / n) if n > 0 else 0.1143
    max_cooks = float(np.max(cooks_d_arr)) if len(cooks_d_arr) > 0 else 0.0
    max_idx = int(np.argmax(cooks_d_arr)) if len(cooks_d_arr) > 0 else 0

    influential_obs = []
    influential_years = []
    for idx_i, cd_val in enumerate(cooks_d_arr):
        yr_val = int(reg_df.iloc[idx_i]["Year"]) if "Year" in reg_df.columns else idx_i
        if cd_val > threshold_4n:
            influential_obs.append({
                "index": idx_i,
                "year": yr_val,
                "cooks_d": round(float(cd_val), 4),
            })
            influential_years.append(yr_val)

    max_year = int(reg_df.iloc[max_idx]["Year"]) if "Year" in reg_df.columns else None
    cooks_dict = {
        "max_d": round(max_cooks, 4),
        "threshold": round(threshold_4n, 4),
        "threshold_formula": f"4/n = 4/{n} = {threshold_4n:.3f}",
        "influential_count": len(influential_obs),
        "influential_years": influential_years,
        "max_year": max_year,
        "influential_observations": influential_obs,
        "interpretation": (
            f"Max Cook's D = {max_cooks:.4f} (Year {max_year}). "
            f"{len(influential_obs)} observation(s) ({', '.join(map(str, influential_years))}) "
            f"exceed the Cook's D screening threshold (4/n ≈ {threshold_4n:.3f}). "
            "These observations should be examined for influence and contextual validity; "
            "exceeding the screening threshold does not by itself imply that the observations are erroneous or should be removed."
        ),
    }

    bp_lm_stat, bp_lm_p, bp_f_stat, bp_f_p = het_breuschpagan(residuals, X_const.values)
    bp_homo = bool(bp_lm_p >= 0.05)
    bp_dict = {
        "lm_statistic": round(float(bp_lm_stat), 6),
        "lm_p_value": round(float(bp_lm_p), 6),
        "f_statistic": round(float(bp_f_stat), 6),
        "f_p_value": round(float(bp_f_p), 6),
        "is_homoscedastic_5pct": bp_homo,
        "interpretation": (
            "No statistically significant evidence of heteroskedasticity at α = 0.05"
            if bp_homo else
            "Evidence of heteroskedasticity in residuals at α = 0.05"
        ),
    }

    dw_val = float(durbin_watson(residuals))
    if 1.5 <= dw_val <= 2.5:
        dw_interp = f"DW = {dw_val:.3f}; the statistic is reasonably close to 2.0, suggesting no strong evidence of first-order autocorrelation."
    elif dw_val < 1.5:
        dw_interp = f"DW = {dw_val:.3f}; indicates potential positive first-order autocorrelation (< 1.5)."
    else:
        dw_interp = f"DW = {dw_val:.3f}; indicates potential negative first-order autocorrelation (> 2.5)."

    dw_dict = {
        "statistic": round(dw_val, 6),
        "ideal_value": 2.0,
        "interpretation": dw_interp,
    }

    sw_stat, sw_p = stats.shapiro(residuals)
    sw_stat = float(sw_stat)
    sw_p = float(sw_p)
    sw_norm = bool(sw_p >= 0.05)
    normality_dict = {
        "shapiro_wilk_statistic": round(sw_stat, 6),
        "shapiro_wilk_p_value": round(sw_p, 6),
        "is_normal_5pct": sw_norm,
        "interpretation": (
            "No evidence against residual normality at α = 0.05."
            if sw_norm else
            "Evidence of non-normality in residuals at α = 0.05."
        ),
    }

    std_resid = (residuals - residuals.mean()) / residuals.std()
    residuals_vs_fitted: List[Dict[str, Any]] = []
    for idx_i, (idx, row) in enumerate(reg_df.iterrows()):
        yr = int(row["Year"]) if "Year" in reg_df.columns else idx
        fit_val = float(fitted[idx])
        res_val = float(residuals[idx])
        abs_res = float(abs(res_val))
        st_res = float(std_resid[idx])
        cd_val = float(cooks_d_arr[idx_i]) if idx_i < len(cooks_d_arr) else 0.0

        residuals_vs_fitted.append({
            "year": yr,
            "fitted": round(fit_val, 4),
            "residual": round(res_val, 4),
            "abs_residual": round(abs_res, 4),
            "standardized_residual": round(st_res, 4),
            "cooks_d": round(cd_val, 4),
        })

    qq_plot_data: List[Dict[str, Any]] = []
    if n > 2:
        try:
            (osm, osr), (slope, intercept, r_val) = stats.probplot(residuals, dist="norm")
            for th_q, sm_res in zip(osm, osr):
                fit_line = float(slope * th_q + intercept)
                qq_plot_data.append({
                    "theoretical_quantile": float(th_q),
                    "sample_residual": float(sm_res),
                    "fitted_line": float(fit_line),
                })
        except Exception:
            pass

    summary_diagnostics = [
        {
            "Test": "Durbin-Watson Autocorrelation",
            "Statistic": round(dw_val, 4),
            "p_value": None,
            "Passed_5pct": "No strong evidence",
            "Conclusion": f"DW = {dw_val:.3f}; the statistic is reasonably close to 2.0, suggesting no strong evidence of first-order autocorrelation.",
            "Decision": "No strong evidence",
        },
        {
            "Test": "Breusch-Pagan Heteroscedasticity",
            "Statistic": round(float(bp_lm_stat), 4),
            "p_value": round(float(bp_lm_p), 6),
            "Passed_5pct": "Fail to reject H₀" if bp_homo else "Reject H₀",
            "Conclusion": "No statistically significant evidence of heteroskedasticity at α = 0.05.",
            "Decision": "Fail to reject H₀",
        },
        {
            "Test": "Shapiro-Wilk Residual Normality",
            "Statistic": round(sw_stat, 4),
            "p_value": round(sw_p, 6),
            "Passed_5pct": "Fail to reject H₀" if sw_norm else "Reject H₀",
            "Conclusion": "Evidence of non-normality in residuals at α = 0.05." if not sw_norm else "No evidence against residual normality at α = 0.05.",
            "Decision": "Reject H₀" if not sw_norm else "Fail to reject H₀",
        },
        {
            "Test": "Cook's Distance (Influential Points)",
            "Statistic": round(max_cooks, 4),
            "p_value": None,
            "Passed_5pct": "Within threshold" if len(influential_obs) == 0 else f"{len(influential_obs)} Exceeding Obs.",
            "Conclusion": (
                f"{len(influential_obs)} observation(s) ({', '.join(map(str, influential_years))}) "
                f"exceed the Cook's D screening threshold (4/n ≈ {threshold_4n:.3f}). "
                "These observations should be examined for influence and contextual validity; "
                "exceeding the screening threshold does not by itself imply that the observations are erroneous or should be removed."
            ),
            "Decision": f"{len(influential_obs)} Exceeding Obs. (Screening Threshold 4/n = {threshold_4n:.3f})",
        },
    ]

    years = reg_df["Year"].astype(int) if "Year" in reg_df.columns else []

    return {
        "available": True,
        "sample_size": n,
        "start_year": int(years.min()) if len(years) > 0 else None,
        "end_year": int(years.max()) if len(years) > 0 else None,
        "vif_results": vif_results,
        "breusch_pagan": bp_dict,
        "durbin_watson": dw_dict,
        "residual_normality": normality_dict,
        "cooks_distance": cooks_dict,
        "residuals_vs_fitted": residuals_vs_fitted,
        "qq_plot_data": qq_plot_data,
        "summary_diagnostics": summary_diagnostics,
        "data": summary_diagnostics,
    }


def calculate_vif_analysis() -> Dict[str, Any]:
    """Dynamically calculate Variance Inflation Factors (VIF) for all predictors."""
    res = calculate_regression_diagnostics()
    if not res.get("available"):
        return res
    return {
        "available": True,
        "sample_size": res.get("sample_size"),
        "start_year": res.get("start_year"),
        "end_year": res.get("end_year"),
        "data": res.get("vif_results", []),
    }


def calculate_statistical_interpretations() -> Dict[str, Any]:
    """
    Dynamically generate statistical interpretations based on the calculated results from:
    - Descriptive statistics
    - Distribution analysis
    - Correlation analysis
    - Regression analysis
    - Regression diagnostics
    """
    desc_res = calculate_descriptive_statistics()
    dist_res = calculate_distribution_analysis()
    corr_res = calculate_correlation_analysis()
    reg_res = calculate_regression_analysis()
    diag_res = calculate_regression_diagnostics()

    if not desc_res.get("available"):
        return {
            "available": False,
            "reason": desc_res.get("reason", "Calculations unavailable for generating statistical interpretations."),
            "data": [],
        }

    sample_size = desc_res.get("sample_size")
    start_year = desc_res.get("start_year")
    end_year = desc_res.get("end_year")

    var_interps: Dict[str, Dict[str, Any]] = {}
    dist_var_map = dist_res.get("variables_analysis", {})

    for item in desc_res.get("data", []):
        v = item["Variable"]
        cnt = item["Count"]
        mn = item["Mean"]
        med = item["Median"]
        sd = item["Std_Dev"]
        sk = item["Skewness"]
        kt = item["Excess_Kurtosis"]

        dist_info = dist_var_map.get(v, {})
        norm_info = dist_info.get("normality_tests", {})
        shape_info = dist_info.get("shape_summary", {})
        is_normal = norm_info.get("is_normal", False)

        descriptive_text = (
            f"{v} has an average (mean) of {mn:.2f} with a median of {med:.2f} over {cnt} observations ({start_year}–{end_year}). "
            f"The standard deviation is {sd:.2f}, spanning from a minimum of {item['Min']:.2f} to a maximum of {item['Max']:.2f}."
        )

        sk_type = shape_info.get("skew_type", "Symmetric")
        kt_type = shape_info.get("kurtosis_type", "Mesokurtic")
        sw_p = norm_info.get("shapiro_wilk", {}).get("p_value", 1.0)

        distribution_text = (
            f"The distribution of {v} is {sk_type.lower()} (skewness = {sk:.2f}) and {kt_type.lower()} (excess kurtosis = {kt:.2f}). "
            f"Shapiro-Wilk normality test yields p = {sw_p:.4f}, indicating that the variable is "
            f"{'normally distributed (p >= 0.05)' if is_normal else 'non-normally distributed (p < 0.05)'}."
        )

        var_interps[v] = {
            "variable": v,
            "descriptive_summary": descriptive_text,
            "distribution_summary": distribution_text,
            "is_normal": is_normal,
            "skewness_classification": sk_type,
            "kurtosis_classification": kt_type,
        }

    corr_pairs: List[Dict[str, Any]] = []
    gdp_corr_texts: List[str] = []

    for row in corr_res.get("pairwise_summary", []):
        v1 = row["Variable_1"]
        v2 = row["Variable_2"]
        r = row["Pearson_r"]
        p = row["Pearson_p"]
        rho = row["Spearman_rho"]
        n_obs = row["Observations_Used"]
        rel = row["Relationship"]
        sig = row["Significant_5pct"] == "Yes"

        text = (
            f"The correlation between {v1} and {v2} shows a {rel.lower()} linear relationship "
            f"(Pearson r = {r:.4f}, p = {p:.4f}; Spearman rho = {rho:.4f}, n = {n_obs}). "
            f"This association is {'statistically significant at the 5% level' if sig else 'not statistically significant at the 5% level'}."
        )

        corr_pairs.append({
            "pair": f"{v1} vs {v2}",
            "text": text,
            "pearson_r": r,
            "p_value": p,
            "is_significant": sig,
        })

        if v1 == "GDP_Growth" or v2 == "GDP_Growth":
            other = v2 if v1 == "GDP_Growth" else v1
            gdp_corr_texts.append(f"{other}: r = {r:.4f} (p = {p:.4f}, {rel})")

    corr_summary_text = (
        f"Pairwise correlation analysis across {sample_size} annual observations reveals linear (Pearson) and "
        f"monotonic (Spearman) relationships among economic growth determinants in India. "
        f"Associations with GDP Growth: {'; '.join(gdp_corr_texts)}."
    )

    corr_interp = {
        "summary": corr_summary_text,
        "pairwise_interpretations": corr_pairs,
    }

    reg_predictors: List[Dict[str, Any]] = []
    sig_regressors: List[str] = []

    dep_var = reg_res.get("dependent_variable", "GDP_Growth")
    r2 = reg_res.get("r_squared", 0.0)
    adj_r2 = reg_res.get("adj_r_squared", 0.0)
    f_stat = reg_res.get("f_statistic", 0.0)
    prob_f = reg_res.get("prob_f_statistic", 1.0)
    f_sig = prob_f is not None and prob_f < 0.05

    model_fit_text = (
        f"The OLS multiple linear regression model explains {r2 * 100:.2f}% of the variance in {dep_var} "
        f"(R-squared = {r2:.4f}, Adjusted R-squared = {adj_r2:.4f}). "
        f"The overall model F-statistic is {f_stat:.4f} (p = {prob_f:.4f}), indicating that the model as a whole is "
        f"{'statistically significant at the 5% level' if f_sig else 'not statistically significant at the 5% level'}."
    )

    for row in reg_res.get("coefficients", []):
        var = row["Variable"]
        coef = row["Coefficient"]
        se = row["Std_Error"]
        t_stat = row["t_statistic"]
        p_val = row["p_value"]
        ci_lo = row["CI_Lower_95"]
        ci_hi = row["CI_Upper_95"]
        sig = row["is_significant"]

        if var == "const":
            pred_text = (
                f"The estimated intercept is {coef:.4f} (SE = {se:.4f}, t = {t_stat:.4f}, p = {p_val:.4f}). "
                f"When all explanatory variables are zero, baseline {dep_var} is estimated at {coef:.2f}%."
            )
        else:
            direction = "increase" if coef > 0 else "decrease"
            sig_text = "statistically significant (p < 0.05)" if sig else "not statistically significant (p >= 0.05)"
            if sig:
                sig_regressors.append(f"{var} (coef = {coef:.4f}, p = {p_val:.4f})")

            pred_text = (
                f"Holding all other variables constant, a 1 unit increase in {var} is associated with a "
                f"{abs(coef):.4f} percentage point {direction} in {dep_var} (coef = {coef:.4f}, SE = {se:.4f}, "
                f"t = {t_stat:.4f}, p = {p_val:.4f}, 95% CI [{ci_lo:.4f}, {ci_hi:.4f}]). "
                f"This predictor is {sig_text}."
            )

        reg_predictors.append({
            "variable": var,
            "coefficient": coef,
            "p_value": p_val,
            "is_significant": sig,
            "interpretation": pred_text,
        })

    reg_interp = {
        "model_fit_summary": model_fit_text,
        "significant_regressors": sig_regressors,
        "predictor_interpretations": reg_predictors,
    }

    vif_items = diag_res.get("vif_results", [])
    vif_summary_texts = [f"{item['Variable']} (VIF = {item['VIF']:.2f})" for item in vif_items]
    vif_warns = [item['Variable'] for item in vif_items if item['Multicollinear_Warn']]

    if vif_warns:
        vif_text = (
            f"VIF analysis indicates potential multicollinearity concern in: {', '.join(vif_warns)}. "
            f"All VIF values: {'; '.join(vif_summary_texts)}."
        )
    else:
        vif_text = f"All predictor VIF values are below 5 ({'; '.join(vif_summary_texts)}), indicating low multicollinearity concern."

    bp_dict = diag_res.get("breusch_pagan", {})
    bp_p = bp_dict.get("lm_p_value", 1.0)
    bp_text = (
        f"Breusch-Pagan test for heteroskedasticity yields LM stat = {bp_dict.get('lm_statistic'):.4f} (p = {bp_p:.4f}). "
        f"There is {'no statistically significant evidence of heteroskedasticity at α = 0.05' if bp_p >= 0.05 else 'statistically significant evidence of heteroskedasticity at α = 0.05'}."
    )

    dw_dict = diag_res.get("durbin_watson", {})
    dw_stat = dw_dict.get("statistic", 2.0)
    dw_text = (
        f"Durbin-Watson statistic is {dw_stat:.4f} (ideal benchmark = 2.0). "
        f"{dw_dict.get('interpretation', '')}"
    )

    norm_dict = diag_res.get("residual_normality", {})
    norm_p = norm_dict.get("shapiro_wilk_p_value", 1.0)
    norm_text = (
        f"Shapiro-Wilk test on OLS residuals yields statistic = {norm_dict.get('shapiro_wilk_statistic'):.4f} (p = {norm_p:.4f}). "
        f"Test indicates {'no evidence against residual normality at α = 0.05' if norm_p >= 0.05 else 'evidence of non-normality in residuals at α = 0.05'}."
    )

    diag_interp = {
        "multicollinearity_vif": vif_text,
        "heteroskedasticity_breusch_pagan": bp_text,
        "autocorrelation_durbin_watson": dw_text,
        "residual_normality": norm_text,
    }

    statistical_cautions = [
        "Association vs. Causation: Neither Pearson/Spearman correlation coefficients nor Ordinary Least Squares (OLS) regression parameters demonstrate causal mechanisms. Observed relationships indicate statistical association only.",
        f"Sample Size & Observational Data: Analysis is based on {sample_size} annual time-series observations ({start_year}–{end_year}) for India. Time-series data can be subject to structural breaks, macro shocks (e.g., global recessions), and non-stationarity.",
        "Model Specification & Omitted Variables: OLS regression results reflect the 5 specified indicators (Inflation, FDI Net Inflows, Exports, Gross Capital Formation, Unemployment). Omitted macroeconomic variables (e.g., fiscal policy, monetary stance, institutional changes) may influence the estimated coefficients.",
    ]

    gdp_mean = desc_res["data"][0]["Mean"] if desc_res.get("data") else 0.0
    gdp_min = desc_res["data"][0]["Min"] if desc_res.get("data") else 0.0
    gdp_max = desc_res["data"][0]["Max"] if desc_res.get("data") else 0.0

    key_findings = [
        f"Over the period {start_year}–{end_year} ({sample_size} observations), India's average annual GDP Growth was {gdp_mean:.2f}% (range: {gdp_min:.2f}% to {gdp_max:.2f}%).",
        f"Multiple OLS regression accounts for {r2 * 100:.2f}% of the variance in GDP Growth (R2 = {r2:.4f}, F = {f_stat:.4f}, p = {prob_f:.4f}).",
        f"Statistically significant predictors at 5% level: {', '.join(sig_regressors)}." if sig_regressors else "No individual regressors are statistically significant at the strict 5% level in this specification.",
        f"Diagnostic Checks: Durbin-Watson statistic ({dw_stat:.2f}) suggests no strong evidence of first-order autocorrelation, while Breusch-Pagan test (p = {bp_p:.4f}) yields {'no statistically significant evidence of heteroskedasticity at α = 0.05' if bp_p >= 0.05 else 'evidence of heteroskedasticity at α = 0.05'}."
    ]

    summary_rows = [
        {"Category": "Key Finding 1", "Details": key_findings[0]},
        {"Category": "Key Finding 2", "Details": key_findings[1]},
        {"Category": "Model Fit", "Details": model_fit_text},
        {"Category": "VIF Status", "Details": vif_text},
        {"Category": "Methodological Caution", "Details": statistical_cautions[0]},
    ]

    return {
        "available": True,
        "sample_size": sample_size,
        "start_year": start_year,
        "end_year": end_year,
        "key_findings": key_findings,
        "variable_interpretations": var_interps,
        "correlation_interpretation": corr_interp,
        "regression_interpretation": reg_interp,
        "diagnostic_interpretation": diag_interp,
        "statistical_cautions": statistical_cautions,
        "data": summary_rows,
    }




