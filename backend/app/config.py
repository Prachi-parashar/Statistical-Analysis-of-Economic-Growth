import os
from pathlib import Path

class Settings:
    APP_NAME: str = "India Economic Growth API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "FastAPI backend for Statistical Analysis of India's Economic Growth"
    
    FRONTEND_ORIGIN: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # Project Paths
    APP_DIR: Path = Path(__file__).resolve().parent
    BACKEND_DIR: Path = APP_DIR.parent
    PROJECT_ROOT: Path = BACKEND_DIR.parent
    
    DATA_DIR: Path = PROJECT_ROOT / "data"
    OUTPUTS_DIR: Path = PROJECT_ROOT / "outputs"
    TABLES_DIR: Path = OUTPUTS_DIR / "tables"
    FIGURES_DIR: Path = OUTPUTS_DIR / "figures"

settings = Settings()
