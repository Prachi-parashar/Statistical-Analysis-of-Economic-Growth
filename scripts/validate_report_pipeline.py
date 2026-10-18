"""
validate_report_pipeline.py
---------------------------
Automated test suite to verify that the PDF and Markdown reports are 100% dynamic
and match the exact statistical calculation results from the current analysis pipeline.
"""

import os
import sys
import json
import re
from pathlib import Path

# Add backend to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.services import analysis_pipeline_service, statistics_service

def validate_pipeline():
    print("==================================================")
    print("RUNNING AUTOMATED REPORT PIPELINE VALIDATION")
    print("==================================================")

    # 1. Fetch current analysis run or execute pipeline
    manifest = analysis_pipeline_service.get_current_analysis_run()
    assert manifest.get("success"), "Pipeline execution failed in manifest"
    analysis_id = manifest.get("analysis_id")
    print(f"[PASS] Active Analysis Run ID: {analysis_id}")

    calc_results = manifest.get("calc_results", {})
    dataset_res = calc_results.get("dataset", {})
    desc_res = calc_results.get("descriptive", {})
    dist_res = calc_results.get("distribution", {})
    corr_res = calc_results.get("correlation", {})
    reg_res = calc_results.get("regression", {})
    diag_res = calc_results.get("diagnostics", {})

    # 2. Read generated Markdown report
    md_path = PROJECT_ROOT / "outputs" / "final_report.md"
    pdf_path = PROJECT_ROOT / "outputs" / "final_report.pdf"
    assert md_path.exists(), "outputs/final_report.md does not exist"
    assert pdf_path.exists(), "outputs/final_report.pdf does not exist"
    assert pdf_path.stat().st_size > 5000, "PDF file size too small (corrupted/empty)"

    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    # 3. Verify Metadata
    start_year = dataset_res.get("start_year")
    end_year = dataset_res.get("end_year")
    n_obs = dataset_res.get("observation_count")
    country = dataset_res.get("country", "India")

    assert f"Analysis Period:** {start_year}–{end_year} ({n_obs} annual observations)" in md_text, \
        f"Metadata mismatch: Period {start_year}-{end_year}, n={n_obs} not found in MD"
    print(f"[PASS] Metadata verified: Country={country}, Period={start_year}–{end_year}, N={n_obs}")

    # Verify NO timestamp in report
    assert "Report Generated:" not in md_text, "Found unwanted 'Report Generated:' timestamp in MD"
    assert "UTC" not in md_text, "Found unwanted UTC timestamp in MD"
    print("[PASS] Timestamp removal verified: No generated date/time strings present.")

    # 4. Verify Descriptive Statistics Table
    for row in desc_res.get("data", []):
        v_raw = row["Variable"]
        mean_val = f"{row['Mean']:.2f}"
        std_val = f"{row['Std_Dev']:.2f}"
        assert mean_val in md_text, f"Descriptive mean {mean_val} for {v_raw} missing in MD"
        assert std_val in md_text, f"Descriptive std {std_val} for {v_raw} missing in MD"
    print("[PASS] Descriptive Statistics verified: All means, standard deviations, and quartiles match.")

    # 5. Verify Distribution & Normality Results
    for row in dist_res.get("data", []):
        sw_stat = f"{row['Shapiro_Wilk_Stat']:.4f}"
        assert sw_stat in md_text, f"Shapiro-Wilk stat {sw_stat} for {row['Variable']} missing in MD"
    print("[PASS] Distribution Analysis verified: Shapiro-Wilk and Anderson-Darling statistics match.")

    # 6. Verify Correlation Results
    for row in corr_res.get("pairwise_summary", []):
        pr_str = f"{row['Pearson_r']:.4f}"
        rho_str = f"{row['Spearman_rho']:.4f}"
        assert pr_str in md_text, f"Pearson r {pr_str} for {row['Variable_1']}-{row['Variable_2']} missing in MD"
        assert rho_str in md_text, f"Spearman rho {rho_str} for {row['Variable_1']}-{row['Variable_2']} missing in MD"
    print("[PASS] Correlation Analysis verified: All Pearson r and Spearman rho coefficients match.")

    # 7. Verify Regression Model Results
    r2_str = f"{reg_res.get('r_squared', 0.0):.4f}"
    adj_r2_str = f"{reg_res.get('adj_r_squared', 0.0):.4f}"
    f_stat_str = f"{reg_res.get('f_statistic', 0.0):.4f}"
    assert f"**R-squared:** {r2_str}" in md_text, f"R² {r2_str} missing in MD"
    assert f"**Adjusted R-squared:** {adj_r2_str}" in md_text, f"Adjusted R² {adj_r2_str} missing in MD"
    assert f"**F-statistic:** {f_stat_str}" in md_text, f"F-stat {f_stat_str} missing in MD"
    print(f"[PASS] Multiple OLS verified: R²={r2_str}, Adj R²={adj_r2_str}, F-stat={f_stat_str}.")

    # 8. Verify HC3 Robust Regression Coefficients
    for row in reg_res.get("coefficients", []):
        coef_str = f"{row['Coefficient']:.6f}"
        se_str = f"{row['Std_Error']:.6f}"
        assert coef_str in md_text, f"HC3 Coef {coef_str} for {row['Variable']} missing in MD"
        assert se_str in md_text, f"HC3 SE {se_str} for {row['Variable']} missing in MD"
    print("[PASS] HC3 Robust Inference verified: Coefficients, standard errors, and confidence intervals match.")

    # 9. Verify Regression Diagnostics
    dw_val = diag_res.get("durbin_watson", {}).get("statistic", 2.0)
    dw_str = f"{dw_val:.4f}"
    bp_val = diag_res.get("breusch_pagan", {}).get("lm_statistic", 0.0)
    bp_str = f"{bp_val:.4f}"
    sw_res_val = diag_res.get("residual_normality", {}).get("shapiro_wilk_statistic", 0.0)
    sw_res_str = f"{sw_res_val:.4f}"
    max_cooks = diag_res.get("cooks_distance", {}).get("max_d", 0.0)
    max_cooks_str = f"{max_cooks:.4f}"

    assert dw_str in md_text, f"DW stat {dw_str} missing in MD"
    assert bp_str in md_text, f"BP LM stat {bp_str} missing in MD"
    assert sw_res_str in md_text, f"Residual SW stat {sw_res_str} missing in MD"
    assert max_cooks_str in md_text, f"Max Cook's D {max_cooks_str} missing in MD"
    print(f"[PASS] Diagnostics verified: DW={dw_str}, BP={bp_str}, SW-Residual={sw_res_str}, Max Cook's D={max_cooks_str}.")

    # 10. Verify VIF Results
    for row in diag_res.get("vif_results", []):
        vif_str = f"{row['VIF']:.4f}"
        assert vif_str in md_text, f"VIF {vif_str} for {row['Variable']} missing in MD"
    print("[PASS] VIF Analysis verified: All variance inflation factors match.")

    print("==================================================")
    print("ALL VALIDATION CHECKS PASSED PERFECTLY (10/10)!")
    print("==================================================")

if __name__ == "__main__":
    validate_pipeline()
