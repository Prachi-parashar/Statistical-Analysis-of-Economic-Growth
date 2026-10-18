from pydantic import BaseModel, ConfigDict
from typing import Any, Optional, List, Dict

class HealthResponse(BaseModel):
    status: str
    version: str

class YearRangeDetails(BaseModel):
    start: Optional[int] = None
    end: Optional[int] = None
    range_str: Optional[str] = None

class ProjectInfo(BaseModel):
    title: str
    description: str
    author: str
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    min_year: Optional[int] = None
    max_year: Optional[int] = None
    observation_count: Optional[int] = None
    year_range: Optional[YearRangeDetails] = None

class DatasetRecord(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    Year: int
    GDP_Growth: Optional[float] = None
    Inflation: Optional[float] = None
    FDI_Net_Inflows: Optional[float] = None
    Exports: Optional[float] = None
    Gross_Capital_Formation: Optional[float] = None
    Unemployment: Optional[float] = None

class DatasetResponse(BaseModel):
    available: bool = True
    reason: Optional[str] = None
    source: Optional[str] = None
    country: Optional[str] = None
    country_code: Optional[str] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    min_year: Optional[int] = None
    max_year: Optional[int] = None
    fetched_at: Optional[str] = None
    observation_count: Optional[int] = None
    missing_values: Optional[Dict[str, int]] = None
    year_range: Optional[YearRangeDetails] = None
    data: Optional[List[Dict[str, Any]]] = None
    total_records: Optional[int] = None

class GenericTableResponse(BaseModel):
    available: bool
    reason: Optional[str] = None
    data: Optional[List[Dict[str, Any]]] = None

class DescriptiveStatisticsResponse(BaseModel):
    available: bool = True
    reason: Optional[str] = None
    sample_size: Optional[int] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    variables_analyzed: Optional[List[str]] = None
    data: Optional[List[Dict[str, Any]]] = None

class DistributionAnalysisResponse(BaseModel):
    available: bool = True
    reason: Optional[str] = None
    sample_size: Optional[int] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    variables: Optional[List[str]] = None
    variables_analysis: Optional[Dict[str, Any]] = None
    data: Optional[List[Dict[str, Any]]] = None

class CorrelationAnalysisResponse(BaseModel):
    available: bool = True
    reason: Optional[str] = None
    sample_size: Optional[int] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    variables: Optional[List[str]] = None
    pearson_matrix: Optional[Dict[str, Dict[str, Optional[float]]]] = None
    spearman_matrix: Optional[Dict[str, Dict[str, Optional[float]]]] = None
    p_values_pearson: Optional[Dict[str, Dict[str, Optional[float]]]] = None
    p_values_spearman: Optional[Dict[str, Dict[str, Optional[float]]]] = None
    observations_matrix: Optional[Dict[str, Dict[str, Optional[int]]]] = None
    heatmap_data: Optional[List[Dict[str, Any]]] = None
    pairwise_summary: Optional[List[Dict[str, Any]]] = None
    data: Optional[List[Dict[str, Any]]] = None

class RegressionAnalysisResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    available: bool = True
    reason: Optional[str] = None
    dependent_variable: Optional[str] = "GDP_Growth"
    independent_variables: Optional[List[str]] = None
    sample_size: Optional[int] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    r_squared: Optional[float] = None
    adj_r_squared: Optional[float] = None
    f_statistic: Optional[float] = None
    prob_f_statistic: Optional[float] = None
    aic: Optional[float] = None
    bic: Optional[float] = None
    residual_std_error: Optional[float] = None
    coefficients: Optional[List[Dict[str, Any]]] = None
    simple_regressions: Optional[List[Dict[str, Any]]] = None
    robust_regression: Optional[List[Dict[str, Any]]] = None
    model_comparison: Optional[List[Dict[str, Any]]] = None
    fitted_vs_actual: Optional[List[Dict[str, Any]]] = None
    data: Optional[List[Dict[str, Any]]] = None

class RegressionDiagnosticsResponse(BaseModel):
    available: bool = True
    reason: Optional[str] = None
    sample_size: Optional[int] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    vif_results: Optional[List[Dict[str, Any]]] = None
    breusch_pagan: Optional[Dict[str, Any]] = None
    durbin_watson: Optional[Dict[str, Any]] = None
    residual_normality: Optional[Dict[str, Any]] = None
    cooks_distance: Optional[Dict[str, Any]] = None
    residuals_vs_fitted: Optional[List[Dict[str, Any]]] = None
    qq_plot_data: Optional[List[Dict[str, Any]]] = None
    summary_diagnostics: Optional[List[Dict[str, Any]]] = None
    data: Optional[List[Dict[str, Any]]] = None

class StatisticalInterpretationsResponse(BaseModel):
    available: bool = True
    reason: Optional[str] = None
    sample_size: Optional[int] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    key_findings: Optional[List[str]] = None
    variable_interpretations: Optional[Dict[str, Dict[str, Any]]] = None
    correlation_interpretation: Optional[Dict[str, Any]] = None
    regression_interpretation: Optional[Dict[str, Any]] = None
    diagnostic_interpretation: Optional[Dict[str, Any]] = None
    statistical_cautions: Optional[List[str]] = None
    data: Optional[List[Dict[str, Any]]] = None


class FiguresResponse(BaseModel):
    available: bool
    reason: Optional[str] = None
    categories: Optional[Dict[str, List[str]]] = None

class ReportResponse(BaseModel):
    available: bool
    reason: Optional[str] = None
    analysis_id: Optional[str] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    observation_count: Optional[int] = None
    source: Optional[str] = None
    country: Optional[str] = None
    pdf_available: bool = False
    md_available: bool = False

class AnalysisRunResponse(BaseModel):
    success: bool = True
    analysis_id: Optional[str] = None
    source: Optional[str] = None
    country: Optional[str] = None
    country_code: Optional[str] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    observation_count: Optional[int] = None
    fetched_at: Optional[str] = None
    dataset_hash: Optional[str] = None
    reports: Optional[Dict[str, Any]] = None
    tables: Optional[List[str]] = None
    figures: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None
