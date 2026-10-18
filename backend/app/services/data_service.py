from pathlib import Path
from typing import Dict, Any, List, Optional
import numpy as np

from app.config import settings
from app.utils.csv_reader import read_csv_safe
from app.services import world_bank_service

_cached_dataset_response: Optional[Dict[str, Any]] = None

def get_live_world_bank_data(force_refresh: bool = False) -> Dict[str, Any]:
    """Fetch live data from World Bank API and return dataset with full metadata."""
    global _cached_dataset_response
    if _cached_dataset_response is not None and not force_refresh:
        return _cached_dataset_response

    # If no cached dataset exists yet, attempt to synchronize from current analysis run
    if not force_refresh:
        try:
            from app.services import analysis_pipeline_service
            run = analysis_pipeline_service.get_current_analysis_run()
            if run and run.get("success") and "calc_results" in run and "dataset" in run["calc_results"]:
                _cached_dataset_response = run["calc_results"]["dataset"]
                return _cached_dataset_response
        except Exception:
            pass

    try:
        df, metadata = world_bank_service.fetch_world_bank_data(start_year=1991)
        records = df.replace([np.inf, -np.inf, np.nan], None).to_dict(orient="records")
        import pandas as pd
        years = df["Year"].dropna().astype(int) if "Year" in df.columns else pd.Series(dtype=int)
        min_y = int(years.min()) if len(years) > 0 else metadata.get("start_year")
        max_y = int(years.max()) if len(years) > 0 else metadata.get("end_year")
        obs_count = int(len(years)) if len(years) > 0 else metadata.get("observation_count", len(records))

        year_range_info = {
            "start": min_y,
            "end": max_y,
            "range_str": f"{min_y}–{max_y}" if min_y and max_y else None
        } if min_y and max_y else None

        response = {
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
        _cached_dataset_response = response
        return response
    except Exception as exc:
        if _cached_dataset_response is not None and not force_refresh:
            return _cached_dataset_response
        return {
            "available": False,
            "reason": f"Failed to fetch live World Bank data: {str(exc)}",
            "source": "World Bank World Development Indicators (WDI)",
            "country": "India",
            "country_code": "IND",
            "data": [],
        }

def set_cached_dataset_response(response: Dict[str, Any]) -> None:
    """Set the unified dataset cache."""
    global _cached_dataset_response
    _cached_dataset_response = response

def clear_dataset_cache() -> None:
    """Clear the cached dataset response."""
    global _cached_dataset_response
    _cached_dataset_response = None

def get_dataset(force_refresh: bool = False) -> Dict[str, Any]:
    """Return dataset and metadata."""
    return get_live_world_bank_data(force_refresh=force_refresh)

def get_metadata() -> Dict[str, Any]:
    file_path = settings.DATA_DIR / "raw" / "dataset_metadata.csv"
    success, reason, data = read_csv_safe(file_path)
    if not success:
        return {"available": False, "reason": reason}
    return {"available": True, "data": data}

def get_generic_table(filename: str) -> Dict[str, Any]:
    file_path = settings.TABLES_DIR / filename
    success, reason, data = read_csv_safe(file_path)
    if not success:
        return {"available": False, "reason": reason}
    return {"available": True, "data": data}

def get_figures_list() -> Dict[str, Any]:
    from app.services import analysis_pipeline_service
    current_run = analysis_pipeline_service.get_current_analysis_run()
    
    categories = {}
    if settings.FIGURES_DIR.exists():
        for subdir in settings.FIGURES_DIR.iterdir():
            if subdir.is_dir():
                png_files = [f.name for f in subdir.glob("*.png")]
                if png_files:
                    categories[subdir.name] = png_files
                    
    if not categories and current_run.get("success"):
        fig_items = current_run.get("figures", [])
        for item in fig_items:
            cat = item.get("category", "general")
            fname = item.get("filename")
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(fname)

    return {
        "available": len(categories) > 0,
        "analysis_id": current_run.get("analysis_id"),
        "categories": categories
    }

def get_report_info() -> Dict[str, Any]:
    from app.services import analysis_pipeline_service
    current_run = analysis_pipeline_service.get_current_analysis_run()
    
    pdf_path = settings.OUTPUTS_DIR / "final_report.pdf"
    md_path = settings.OUTPUTS_DIR / "final_report.md"
    
    available = current_run.get("success", False) or pdf_path.exists() or md_path.exists()
    return {
        "available": available,
        "reason": "Reports not found" if not available else None,
        "analysis_id": current_run.get("analysis_id"),
        "start_year": current_run.get("start_year"),
        "end_year": current_run.get("end_year"),
        "observation_count": current_run.get("observation_count"),
        "source": current_run.get("source"),
        "country": current_run.get("country"),
        "pdf_available": pdf_path.exists(),
        "md_available": md_path.exists()
    }
