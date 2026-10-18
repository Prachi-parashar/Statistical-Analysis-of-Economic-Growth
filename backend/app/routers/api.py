from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from app.schemas import (
    HealthResponse, ProjectInfo, DatasetResponse, 
    GenericTableResponse, DescriptiveStatisticsResponse, DistributionAnalysisResponse,
    CorrelationAnalysisResponse, RegressionAnalysisResponse, RegressionDiagnosticsResponse,
    StatisticalInterpretationsResponse, FiguresResponse, ReportResponse, AnalysisRunResponse
)
from app.services import data_service, statistics_service, analysis_pipeline_service
from app.config import settings


router = APIRouter()

@router.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="ok", version=settings.APP_VERSION)

@router.get("/project", response_model=ProjectInfo, tags=["System"])
async def project_info():
    """Project metadata + live dataset range."""
    ds = data_service.get_dataset()
    min_y = ds.get("min_year") or ds.get("start_year")
    max_y = ds.get("max_year") or ds.get("end_year")
    obs = ds.get("observation_count")
    yr_range = ds.get("year_range")
    return ProjectInfo(
        title="India Economic Growth Determinants",
        description="Statistical Analysis of Economic Growth Determinants in India",
        author="Harshit Tiwari",
        start_year=min_y,
        end_year=max_y,
        min_year=min_y,
        max_year=max_y,
        observation_count=obs,
        year_range=yr_range
    )

@router.get("/dataset", response_model=DatasetResponse, tags=["Data"])
async def get_dataset():
    """Current dataset and metadata."""
    return data_service.get_dataset()

@router.get("/data/live", response_model=DatasetResponse, tags=["Data"])
async def get_live_data():
    """Fetch live data from World Bank API."""
    return data_service.get_live_world_bank_data(force_refresh=False)

@router.post("/data/refresh", response_model=DatasetResponse, tags=["Data"])
async def refresh_live_data():
    """Force a fresh fetch from World Bank API."""
    return data_service.get_live_world_bank_data(force_refresh=True)

@router.post("/analysis/run", response_model=AnalysisRunResponse, tags=["Analysis"])
async def run_analysis():
    """Execute complete analysis pipeline & generate fresh tables, figures, Markdown, and PDF reports."""
    return analysis_pipeline_service.run_analysis_pipeline(force_refresh=True)

@router.get("/analysis/current", response_model=AnalysisRunResponse, tags=["Analysis"])
async def get_current_analysis():
    """Get metadata for the current active analysis run."""
    return analysis_pipeline_service.get_current_analysis_run()


@router.get("/dataset/metadata", response_model=GenericTableResponse, tags=["Data"])
async def get_dataset_metadata():
    """Variable definitions & WB codes."""
    return data_service.get_metadata()

@router.get("/statistics/descriptive", response_model=DescriptiveStatisticsResponse, tags=["Analysis"])
async def get_statistics_descriptive():
    """Calculate dynamic descriptive statistics from live dataset."""
    return statistics_service.calculate_descriptive_statistics()

@router.get("/descriptive-statistics", response_model=DescriptiveStatisticsResponse, tags=["Analysis"])
async def get_descriptive_statistics():
    """Dynamic descriptive statistics (alias)."""
    return statistics_service.calculate_descriptive_statistics()


@router.get("/descriptive-statistics/summary", response_model=GenericTableResponse, tags=["Analysis"])
async def get_summary_statistics():
    """Summary statistics matrix."""
    return data_service.get_generic_table("summary_statistics.csv")

@router.get("/statistics/distribution", response_model=DistributionAnalysisResponse, tags=["Analysis"])
async def get_statistics_distribution():
    """Calculate dynamic distribution and probability analysis from live dataset."""
    return statistics_service.calculate_distribution_analysis()

@router.get("/statistics/correlation", response_model=CorrelationAnalysisResponse, tags=["Analysis"])
async def get_statistics_correlation():
    """Calculate dynamic correlation matrix (Pearson & Spearman) from live dataset."""
    return statistics_service.calculate_correlation_analysis()

@router.get("/statistics/regression", response_model=RegressionAnalysisResponse, tags=["Analysis"])
async def get_statistics_regression():
    """Calculate dynamic multiple linear regression (OLS) from live dataset."""
    return statistics_service.calculate_regression_analysis()

@router.get("/statistics/diagnostics", response_model=RegressionDiagnosticsResponse, tags=["Analysis"])
async def get_statistics_diagnostics():
    """Calculate dynamic regression diagnostics (VIF, Breusch-Pagan, Durbin-Watson, Residuals/QQ plots) from live dataset."""
    return statistics_service.calculate_regression_diagnostics()

@router.get("/statistics/interpretations", response_model=StatisticalInterpretationsResponse, tags=["Analysis"])
async def get_statistics_interpretations():
    """Dynamically generate statistical interpretations based on calculated statistics and econometric model results."""
    return statistics_service.calculate_statistical_interpretations()

@router.get("/probability", response_model=GenericTableResponse, tags=["Analysis"])
async def get_probability():
    """Normality tests + distribution analysis."""
    return data_service.get_generic_table("distribution_analysis.csv")

@router.get("/probability/normality-tests", response_model=GenericTableResponse, tags=["Analysis"])
async def get_normality_tests():
    """Shapiro-Wilk and Anderson-Darling tests."""
    return data_service.get_generic_table("normality_tests.csv")

@router.get("/correlation/pearson", response_model=GenericTableResponse, tags=["Analysis"])
async def get_pearson_correlation():
    """Pearson r + multicollinearity check."""
    return data_service.get_generic_table("pearson_correlation.csv")

@router.get("/correlation/spearman", response_model=GenericTableResponse, tags=["Analysis"])
async def get_spearman_correlation():
    """Spearman rho."""
    return data_service.get_generic_table("spearman_correlation.csv")

@router.get("/correlation/predictor-check", response_model=GenericTableResponse, tags=["Analysis"])
async def get_predictor_correlation_check():
    """Predictor multicollinearity pre-check matrix."""
    return data_service.get_generic_table("predictor_correlation_check.csv")

@router.get("/regression/simple", response_model=GenericTableResponse, tags=["Analysis"])
async def get_simple_regression():
    """5 simple OLS models."""
    res = statistics_service.calculate_simple_regression()
    if res.get("available") and res.get("data"):
        return res
    return data_service.get_generic_table("simple_regression_results.csv")

@router.get("/regression/multiple", response_model=RegressionAnalysisResponse, tags=["Analysis"])
async def get_multiple_regression():
    """Multiple OLS + HC3 robust SE + model statistics."""
    res = statistics_service.calculate_regression_analysis()
    if res.get("available") and res.get("coefficients"):
        return res
    fallback = data_service.get_generic_table("multiple_regression_results.csv")
    return RegressionAnalysisResponse(
        available=fallback.get("available", False),
        reason=fallback.get("reason"),
        coefficients=fallback.get("data"),
        data=fallback.get("data")
    )

@router.get("/regression/robust", response_model=GenericTableResponse, tags=["Analysis"])
async def get_robust_regression():
    """HC3 robust regression results."""
    res = statistics_service.calculate_robust_regression()
    if res.get("available") and res.get("data"):
        return res
    return data_service.get_generic_table("robust_regression_results.csv")

@router.get("/regression/model-comparison", response_model=GenericTableResponse, tags=["Analysis"])
async def get_model_comparison():
    """Model comparison table."""
    res = statistics_service.calculate_model_comparison()
    if res.get("available") and res.get("data"):
        return res
    return data_service.get_generic_table("model_comparison.csv")

@router.get("/diagnostics", response_model=RegressionDiagnosticsResponse, tags=["Analysis"])
async def get_diagnostics():
    """VIF, DW, BP, SW, Cook's D."""
    res = statistics_service.calculate_regression_diagnostics()
    if res.get("available") and res.get("summary_diagnostics"):
        return res
    return data_service.get_generic_table("regression_diagnostics.csv")

@router.get("/diagnostics/vif", response_model=GenericTableResponse, tags=["Analysis"])
async def get_vif_results():
    """Variance Inflation Factors."""
    res = statistics_service.calculate_vif_analysis()
    if res.get("available") and res.get("data"):
        return res
    return data_service.get_generic_table("vif_results.csv")

@router.get("/figures", response_model=FiguresResponse, tags=["Figures"])
async def get_figures():
    """Categorised list of generated PNGs."""
    return data_service.get_figures_list()

@router.get("/figures/{path:path}", tags=["Figures"])
async def serve_figure(path: str):
    """Serve a specific PNG."""
    file_path = settings.FIGURES_DIR / path
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Figure not found")
    return FileResponse(file_path)

@router.get("/report", response_model=ReportResponse, tags=["Report"])
async def report_info():
    """Report availability info."""
    return data_service.get_report_info()

@router.get("/report/pdf", tags=["Report"])
async def serve_report_pdf():
    """Download final PDF."""
    file_path = settings.OUTPUTS_DIR / "final_report.pdf"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="PDF Report not found")
    headers = {
        "Cache-Control": "no-cache, no-store, must-revalidate, max-age=0",
        "Pragma": "no-cache",
        "Expires": "0",
    }
    return FileResponse(
        file_path,
        media_type="application/pdf",
        filename="India_Economic_Growth_Final_Report.pdf",
        headers=headers,
    )

@router.get("/report/md", tags=["Report"])
async def serve_report_md():
    """Download final Markdown."""
    file_path = settings.OUTPUTS_DIR / "final_report.md"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Markdown Report not found")
    headers = {
        "Cache-Control": "no-cache, no-store, must-revalidate, max-age=0",
        "Pragma": "no-cache",
        "Expires": "0",
    }
    return FileResponse(
        file_path,
        media_type="text/markdown",
        filename="India_Economic_Growth_Final_Report.md",
        headers=headers,
    )

@router.get("/tables/json/{filename}", response_model=GenericTableResponse, tags=["Tables"])
async def get_table_json(filename: str):
    """Get JSON content of any output table CSV."""
    return data_service.get_generic_table(filename)

@router.get("/tables/{filename}", tags=["Tables"])
async def serve_table(filename: str):
    """Download a specific CSV/TXT table."""
    file_path = settings.TABLES_DIR / filename
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Table not found")
    return FileResponse(file_path)

@router.get("/analysis/{analysis_id}/report/pdf", tags=["Analysis"])
async def serve_analysis_report_pdf(analysis_id: str):
    """Download analysis-specific PDF report."""
    file_path = settings.OUTPUTS_DIR / "analysis" / analysis_id / "reports" / "final_report.pdf"
    if not file_path.exists():
        file_path = settings.OUTPUTS_DIR / "final_report.pdf"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"PDF Report for analysis {analysis_id} not found")
    headers = {
        "Cache-Control": "no-cache, no-store, must-revalidate, max-age=0",
        "Pragma": "no-cache",
        "Expires": "0",
    }
    return FileResponse(
        file_path,
        media_type="application/pdf",
        filename="India_Economic_Growth_Final_Report.pdf",
        headers=headers,
    )

@router.get("/analysis/{analysis_id}/report/md", tags=["Analysis"])
async def serve_analysis_report_md(analysis_id: str):
    """Download analysis-specific Markdown report."""
    file_path = settings.OUTPUTS_DIR / "analysis" / analysis_id / "reports" / "final_report.md"
    if not file_path.exists():
        file_path = settings.OUTPUTS_DIR / "final_report.md"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Markdown Report for analysis {analysis_id} not found")
    headers = {
        "Cache-Control": "no-cache, no-store, must-revalidate, max-age=0",
        "Pragma": "no-cache",
        "Expires": "0",
    }
    return FileResponse(
        file_path,
        media_type="text/markdown",
        filename="India_Economic_Growth_Final_Report.md",
        headers=headers,
    )

@router.get("/analysis/{analysis_id}/tables/{filename}", tags=["Analysis"])
async def serve_analysis_table(analysis_id: str, filename: str):
    """Download analysis-specific CSV table."""
    file_path = settings.OUTPUTS_DIR / "analysis" / analysis_id / "tables" / filename
    if not file_path.exists():
        file_path = settings.TABLES_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Table {filename} for analysis {analysis_id} not found")
    return FileResponse(file_path)

@router.get("/analysis/{analysis_id}/figures/{path:path}", tags=["Analysis"])
async def serve_analysis_figure(analysis_id: str, path: str):
    """Serve analysis-specific PNG figure."""
    file_path = settings.OUTPUTS_DIR / "analysis" / analysis_id / "figures" / path
    if not file_path.exists():
        file_path = settings.FIGURES_DIR / path
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Figure {path} for analysis {analysis_id} not found")
    return FileResponse(file_path)


