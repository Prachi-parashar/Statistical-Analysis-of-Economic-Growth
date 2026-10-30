import os
import tempfile
from pathlib import Path
from typing import List

def _resolve_dir(env_var: str, local_path: Path, fallback_path: Path) -> Path:
    if os.environ.get(env_var):
        return Path(os.environ[env_var]).resolve()
    if local_path.exists():
        return local_path.resolve()
    return fallback_path.resolve()

def _resolve_writable_outputs_dir(preferred: Path) -> Path:
    try:
        preferred.mkdir(parents=True, exist_ok=True)
        test_file = preferred / ".write_test"
        test_file.write_text("ok", encoding="utf-8")
        test_file.unlink()
        return preferred
    except (OSError, PermissionError):
        tmp_dir = Path(os.environ.get("TMPDIR", tempfile.gettempdir())) / "artha_lens_outputs"
        tmp_dir.mkdir(parents=True, exist_ok=True)
        return tmp_dir

class Settings:
    APP_NAME: str = "India Economic Growth API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "FastAPI backend for Statistical Analysis of India's Economic Growth (ArthaLens)"
    
    # Origins allowed for CORS
    @property
    def FRONTEND_ORIGIN(self) -> List[str]:
        origins = [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:8000",
            "http://127.0.0.1:8000",
        ]
        custom_origins = os.environ.get("CORS_ORIGINS", "")
        if custom_origins:
            for o in custom_origins.split(","):
                cleaned = o.strip()
                if cleaned and cleaned not in origins:
                    origins.append(cleaned)
        return origins

    # Project Paths
    APP_DIR: Path = Path(__file__).resolve().parent
    BACKEND_DIR: Path = APP_DIR.parent
    PROJECT_ROOT: Path = BACKEND_DIR.parent
    
    DATA_DIR: Path = _resolve_dir(
        "DATA_DIR",
        BACKEND_DIR / "data",
        PROJECT_ROOT / "data"
    )
    
    OUTPUTS_DIR: Path = _resolve_dir(
        "OUTPUTS_DIR",
        BACKEND_DIR / "outputs",
        PROJECT_ROOT / "outputs"
    )
    
    TABLES_DIR: Path = OUTPUTS_DIR / "tables"
    FIGURES_DIR: Path = OUTPUTS_DIR / "figures"

    # Writable scratchpad directory for serverless environments (e.g. AWS Lambda / Vercel)
    @property
    def WRITABLE_OUTPUTS_DIR(self) -> Path:
        return _resolve_writable_outputs_dir(self.OUTPUTS_DIR)

    @property
    def WRITABLE_TABLES_DIR(self) -> Path:
        d = self.WRITABLE_OUTPUTS_DIR / "tables"
        d.mkdir(parents=True, exist_ok=True)
        return d

    @property
    def WRITABLE_FIGURES_DIR(self) -> Path:
        d = self.WRITABLE_OUTPUTS_DIR / "figures"
        d.mkdir(parents=True, exist_ok=True)
        return d

settings = Settings()
