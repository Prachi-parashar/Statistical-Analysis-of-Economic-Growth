import pandas as pd
import numpy as np
from pathlib import Path
from functools import lru_cache
from typing import List, Dict, Any, Tuple

@lru_cache(maxsize=32)
def _read_csv_cached(filepath: str) -> List[Dict[str, Any]]:
    df = pd.read_csv(filepath)
    df = df.replace([np.inf, -np.inf, np.nan], None)
    return df.to_dict(orient="records")

def read_csv_safe(filepath: Path) -> Tuple[bool, str, List[Dict[str, Any]]]:
    if not filepath.exists():
        return False, f"File not found: {filepath.name}", []
    
    try:
        data = _read_csv_cached(str(filepath))
        return True, "", data
    except Exception as e:
        return False, f"Error reading file: {str(e)}", []
