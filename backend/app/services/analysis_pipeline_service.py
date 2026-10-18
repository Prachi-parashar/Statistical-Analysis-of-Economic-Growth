import os
import json
import datetime
import threading
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Optional

from app.config import settings
from app.services import world_bank_service, data_service, statistics_service, figure_generator, report_generator

_CURRENT_ANALYSIS_RUN: Optional[Dict[str, Any]] = None
_PIPELINE_LOCK = threading.RLock()

def get_current_analysis_id() -> Optional[str]:
    run = get_current_analysis_run()
    if run and run.get("success"):
        return run.get("analysis_id")
    return None

def run_analysis_pipeline(force_refresh: bool = True) -> Dict[str, Any]:
    """
    Execute the complete dynamic analysis & report generation pipeline:
    1. Fetch live World Bank WDI data
    2. Synchronize single source of truth in data_service
    3. Run descriptive statistics
    4. Run distribution analysis
    5. Run correlation analysis
    6. Run regression analysis
    7. Run regression diagnostics
    8. Generate statistical interpretations
    9. Generate CSV output tables
    10. Generate statistical figure charts (PNG)
    11. Generate Markdown report (final_report.md)
    12. Generate PDF report (final_report.pdf)
    13. Save analysis manifest and current state
    """
    global _CURRENT_ANALYSIS_RUN

    with _PIPELINE_LOCK:
        if not force_refresh:
            if _CURRENT_ANALYSIS_RUN is not None and _CURRENT_ANALYSIS_RUN.get("success"):
                if "calc_results" in _CURRENT_ANALYSIS_RUN and "dataset" in _CURRENT_ANALYSIS_RUN["calc_results"]:
                    data_service.set_cached_dataset_response(_CURRENT_ANALYSIS_RUN["calc_results"]["dataset"])
                return _CURRENT_ANALYSIS_RUN

            current_manifest_file = settings.OUTPUTS_DIR / "current_analysis.json"
            if current_manifest_file.exists():
                try:
                    with open(current_manifest_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if data.get("success"):
                            _CURRENT_ANALYSIS_RUN = data
                            if "calc_results" in data and "dataset" in data["calc_results"]:
                                data_service.set_cached_dataset_response(data["calc_results"]["dataset"])
                            return data
                except Exception:
                    pass
        return _execute_pipeline_locked(force_refresh=force_refresh)

def _execute_pipeline_locked(force_refresh: bool = True) -> Dict[str, Any]:
    global _CURRENT_ANALYSIS_RUN
    try:
        # Step 1: Fetch live data & compute fingerprint
        df, metadata = world_bank_service.fetch_world_bank_data(start_year=1991)
        records = df.replace([np.inf, -np.inf, np.nan], None).to_dict(orient="records")
        years = df["Year"].dropna().astype(int) if "Year" in df.columns else pd.Series(dtype=int)
        min_y = int(years.min()) if len(years) > 0 else metadata.get("start_year")
        max_y = int(years.max()) if len(years) > 0 else metadata.get("end_year")
        obs_count = int(len(years)) if len(years) > 0 else metadata.get("observation_count", len(records))

        year_range_info = {
            "start": min_y,
            "end": max_y,
            "range_str": f"{min_y}–{max_y}" if min_y and max_y else None
        } if min_y and max_y else None

        dataset_res = {
            "available": True,
            "source": metadata["source"],
            "country": metadata["country"],
            "country_code": metadata["country_code"],
            "start_year": min_y,
            "end_year": max_y,
            "min_year": min_y,
            "max_year": max_y,
            "year_range": year_range_info,
            "fetched_at": metadata["fetched_at"],
            "observation_count": obs_count,
            "missing_values": metadata["missing_values"],
            "dataset_hash": metadata.get("dataset_hash"),
            "data": records,
            "total_records": len(records),
        }

        # Synchronize single source of truth in data_service cache
        data_service.set_cached_dataset_response(dataset_res)

        # Check and log data fetch audit information
        prev_hash = None
        if _CURRENT_ANALYSIS_RUN and "dataset_hash" in _CURRENT_ANALYSIS_RUN:
            prev_hash = _CURRENT_ANALYSIS_RUN.get("dataset_hash")
        elif (settings.OUTPUTS_DIR / "current_analysis.json").exists():
            try:
                with open(settings.OUTPUTS_DIR / "current_analysis.json", "r", encoding="utf-8") as f:
                    prev_manifest = json.load(f)
                    prev_hash = prev_manifest.get("dataset_hash")
            except Exception:
                pass

        print("----------------------------------------")
        print("WORLD BANK DATA FETCH")
        print("----------------------------------------")
        print(f"Source: {metadata.get('source')}")
        print(f"Country: {metadata.get('country')} ({metadata.get('country_code')})")
        print(f"Requested period: 1991–latest")
        print(f"Actual latest available year: {metadata.get('end_year')}")
        print(f"Observations: {metadata.get('observation_count')}")
        print(f"Missing values: {metadata.get('missing_values')}")
        print(f"Force refresh: {force_refresh}")
        print("Cache bypassed: True")
        print(f"Dataset hash: {metadata.get('dataset_hash')}")
        if prev_hash:
            if prev_hash == metadata.get("dataset_hash"):
                print("World Bank data unchanged; identical analysis results are expected.")
            else:
                print("World Bank data changed; analysis results should be recalculated.")
        print("----------------------------------------")

        # Step 2: Run all statistical calculations from the active dataset
        desc_res = statistics_service.calculate_descriptive_statistics()
        dist_res = statistics_service.calculate_distribution_analysis()
        corr_res = statistics_service.calculate_correlation_analysis()
        reg_res = statistics_service.calculate_regression_analysis()
        diag_res = statistics_service.calculate_regression_diagnostics()
        interp_res = statistics_service.calculate_statistical_interpretations()

        calc_results = {
            "dataset": dataset_res,
            "descriptive": desc_res,
            "distribution": dist_res,
            "correlation": corr_res,
            "regression": reg_res,
            "diagnostics": diag_res,
            "interpretations": interp_res,
        }

        # Step 3: Analysis ID & Directory Setup
        now_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d_%H%M%S")
        analysis_id = f"run_{metadata['start_year']}_{metadata['end_year']}_{now_str}"

        analysis_dir = settings.OUTPUTS_DIR / "analysis" / analysis_id
        dataset_dir = analysis_dir / "dataset"
        tables_dir = analysis_dir / "tables"
        figures_dir = analysis_dir / "figures"
        reports_dir = analysis_dir / "reports"

        for d in [dataset_dir, tables_dir, figures_dir, reports_dir]:
            d.mkdir(parents=True, exist_ok=True)

        # Step 4: Write CSV Output Tables
        df.to_csv(dataset_dir / "dataset.csv", index=False)
        df.to_csv(tables_dir / "dataset.csv", index=False)

        pd.DataFrame(desc_res.get("data", [])).to_csv(tables_dir / "descriptive_statistics.csv", index=False)
        pd.DataFrame(desc_res.get("data", [])).to_csv(tables_dir / "summary_statistics.csv", index=False)
        pd.DataFrame(dist_res.get("data", [])).to_csv(tables_dir / "normality_tests.csv", index=False)
        pd.DataFrame(dist_res.get("data", [])).to_csv(tables_dir / "distribution_analysis.csv", index=False)
        pd.DataFrame(dist_res.get("data", [])).to_csv(tables_dir / "distribution_fitting.csv", index=False)
        pd.DataFrame(dist_res.get("data", [])).to_csv(tables_dir / "empirical_probabilities.csv", index=False)

        # Correlation matrices
        p_df = pd.DataFrame(corr_res.get("pearson_matrix", {}))
        s_df = pd.DataFrame(corr_res.get("spearman_matrix", {}))
        p_df.to_csv(tables_dir / "pearson_correlation.csv")
        s_df.to_csv(tables_dir / "spearman_correlation.csv")
        p_df.to_csv(tables_dir / "predictor_correlation_check.csv")

        # Regression & Diagnostics tables
        pd.DataFrame(reg_res.get("simple_regressions", [])).to_csv(tables_dir / "simple_regression_results.csv", index=False)
        pd.DataFrame(reg_res.get("coefficients", [])).to_csv(tables_dir / "multiple_regression_results.csv", index=False)
        pd.DataFrame(reg_res.get("robust_regression", [])).to_csv(tables_dir / "robust_regression_results.csv", index=False)
        pd.DataFrame(diag_res.get("vif_results", [])).to_csv(tables_dir / "vif_results.csv", index=False)
        pd.DataFrame(diag_res.get("summary_diagnostics", [])).to_csv(tables_dir / "regression_diagnostics.csv", index=False)
        pd.DataFrame(reg_res.get("model_comparison", [])).to_csv(tables_dir / "model_comparison.csv", index=False)

        # Mirror tables to global tables directory
        settings.TABLES_DIR.mkdir(parents=True, exist_ok=True)
        for t_file in tables_dir.glob("*.csv"):
            with open(t_file, "r", encoding="utf-8") as rf:
                with open(settings.TABLES_DIR / t_file.name, "w", encoding="utf-8") as wf:
                    wf.write(rf.read())

        # Step 5: Generate Figures
        generated_figures = figure_generator.generate_all_figures(df, calc_results, figures_dir)
        
        # Mirror figures to global figures directory
        settings.FIGURES_DIR.mkdir(parents=True, exist_ok=True)
        for fig_item in generated_figures:
            src_p = figures_dir / fig_item["path"]
            dst_p = settings.FIGURES_DIR / fig_item["path"]
            dst_p.parent.mkdir(parents=True, exist_ok=True)
            if src_p.exists():
                with open(src_p, "rb") as rf:
                    with open(dst_p, "wb") as wf:
                        wf.write(rf.read())

        # Step 6: Generate Markdown & PDF Reports from THIS exact run
        output_md_path = reports_dir / "final_report.md"
        output_pdf_path = reports_dir / "final_report.pdf"

        report_generator.generate_markdown_report(calc_results, output_md_path)
        report_generator.generate_pdf_report(calc_results, output_pdf_path, metadata, figures_dir=figures_dir)

        # Mirror reports to root outputs folder
        with open(output_md_path, "r", encoding="utf-8") as rf:
            with open(settings.OUTPUTS_DIR / "final_report.md", "w", encoding="utf-8") as wf:
                wf.write(rf.read())

        with open(output_pdf_path, "rb") as rf:
            with open(settings.OUTPUTS_DIR / "final_report.pdf", "wb") as wf:
                wf.write(rf.read())

        # Build list of table files for response
        table_files_list = [f.name for f in tables_dir.glob("*.csv")]

        run_manifest = {
            "success": True,
            "analysis_id": analysis_id,
            "source": metadata["source"],
            "country": metadata["country"],
            "country_code": metadata["country_code"],
            "start_year": metadata["start_year"],
            "end_year": metadata["end_year"],
            "observation_count": metadata["observation_count"],
            "dataset_hash": metadata.get("dataset_hash"),
            "fetched_at": metadata["fetched_at"],
            "reports": {
                "pdf_available": True,
                "md_available": True,
                "pdf_url": f"/api/analysis/{analysis_id}/report/pdf",
                "md_url": f"/api/analysis/{analysis_id}/report/md",
            },
            "tables": table_files_list,
            "figures": generated_figures,
            "calc_results": calc_results,
        }

        # Save manifest inside analysis directory and set as current
        with open(analysis_dir / "manifest.json", "w", encoding="utf-8") as f:
            json.dump(run_manifest, f, indent=2, default=str)

        with open(settings.OUTPUTS_DIR / "current_analysis.json", "w", encoding="utf-8") as f:
            json.dump(run_manifest, f, indent=2, default=str)

        _CURRENT_ANALYSIS_RUN = run_manifest
        return run_manifest

    except Exception as exc:
        err_res = {
            "success": False,
            "stage": "pipeline",
            "error": f"Analysis pipeline execution failed: {str(exc)}",
        }
        return err_res


def get_current_analysis_run() -> Dict[str, Any]:
    global _CURRENT_ANALYSIS_RUN
    if _CURRENT_ANALYSIS_RUN is not None and _CURRENT_ANALYSIS_RUN.get("success"):
        return _CURRENT_ANALYSIS_RUN
    
    with _PIPELINE_LOCK:
        if _CURRENT_ANALYSIS_RUN is not None and _CURRENT_ANALYSIS_RUN.get("success"):
            return _CURRENT_ANALYSIS_RUN

        current_manifest_file = settings.OUTPUTS_DIR / "current_analysis.json"
        if current_manifest_file.exists():
            try:
                with open(current_manifest_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data.get("success"):
                        _CURRENT_ANALYSIS_RUN = data
                        if "calc_results" in data and "dataset" in data["calc_results"]:
                            data_service.set_cached_dataset_response(data["calc_results"]["dataset"])
                        return data
            except Exception:
                pass
                
        # Auto-run pipeline if no active analysis run exists yet
        return run_analysis_pipeline(force_refresh=False)
