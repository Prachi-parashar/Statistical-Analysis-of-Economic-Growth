import requests
import hashlib
import pandas as pd
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
from typing import Tuple, Dict, Any, Optional

COUNTRY_CODE = "IND"
COUNTRY_NAME = "India"
DEFAULT_START_YEAR = 1991

INDICATORS = {
    "GDP_Growth": "NY.GDP.MKTP.KD.ZG",
    "Inflation": "FP.CPI.TOTL.ZG",
    "FDI_Net_Inflows": "BX.KLT.DINV.WD.GD.ZS",
    "Exports": "NE.EXP.GNFS.ZS",
    "Gross_Capital_Formation": "NE.GDI.TOTL.ZS",
    "Unemployment": "SL.UEM.TOTL.ZS",
}

def compute_dataset_hash(df: pd.DataFrame) -> str:
    """Compute deterministic SHA-256 fingerprint of dataset content."""
    csv_bytes = df.to_csv(index=False, float_format="%.6f").encode("utf-8")
    return hashlib.sha256(csv_bytes).hexdigest()[:16]

def fetch_indicator_data(name: str, code: str, start_year: int, end_year: Optional[int] = None, timeout: int = 25) -> Tuple[str, Dict[int, Optional[float]]]:
    """Fetch single indicator time series directly from World Bank REST API v2."""
    current_year = datetime.now().year
    date_range = f"{start_year}:{end_year}" if end_year else f"{start_year}:{current_year}"
    url = f"https://api.worldbank.org/v2/country/{COUNTRY_CODE}/indicator/{code}?date={date_range}&format=json&per_page=1000"
    
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        json_data = response.json()
    except Exception as exc:
        raise RuntimeError(f"World Bank API request failed for {name} ({code}): {str(exc)}") from exc
        
    if not isinstance(json_data, list) or len(json_data) < 2 or not json_data[1]:
        raise RuntimeError(f"No valid data returned by World Bank API for indicator {name} ({code}).")
        
    records: Dict[int, Optional[float]] = {}
    for entry in json_data[1]:
        try:
            yr = int(entry["date"])
            val = entry["value"]
            records[yr] = float(val) if val is not None else None
        except (ValueError, TypeError):
            continue
            
    return name, records

def fetch_world_bank_data(start_year: int = DEFAULT_START_YEAR, end_year: Optional[int] = None) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Fetch real macroeconomic data for India directly from World Bank API.
    Determines the latest available common year dynamically without hardcoding.
    Returns clean pandas DataFrame and metadata dictionary.
    """
    with ThreadPoolExecutor(max_workers=len(INDICATORS)) as executor:
        futures = [
            executor.submit(fetch_indicator_data, name, code, start_year, end_year)
            for name, code in INDICATORS.items()
        ]
        results = [f.result() for f in futures]
        
    data_by_year: Dict[int, Dict[str, Optional[float]]] = {}
    for name, records in results:
        for yr, val in records.items():
            if yr not in data_by_year:
                data_by_year[yr] = {}
            data_by_year[yr][name] = val
            
    if not data_by_year:
        raise RuntimeError("Failed to extract any observations from World Bank API responses.")
        
    df = pd.DataFrame.from_dict(data_by_year, orient="index").sort_index()
    df.index.name = "Year"
    df = df.reset_index()
    
    cols = ["Year", "GDP_Growth", "Inflation", "FDI_Net_Inflows", "Exports", "Gross_Capital_Formation", "Unemployment"]
    df = df.reindex(columns=cols)
    df = df[df["Year"] >= start_year].copy()
    
    actual_start_year = int(df["Year"].min()) if not df.empty else start_year
    actual_end_year = int(df["Year"].max()) if not df.empty else start_year
    
    missing_dict = {col: int(df[col].isnull().sum()) for col in cols if col != "Year"}
    d_hash = compute_dataset_hash(df)
    
    metadata = {
        "source": "World Bank World Development Indicators (WDI)",
        "country": COUNTRY_NAME,
        "country_code": COUNTRY_CODE,
        "start_year": actual_start_year,
        "end_year": actual_end_year,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "observation_count": len(df),
        "missing_values": missing_dict,
        "dataset_hash": d_hash,
    }
    
    return df, metadata
