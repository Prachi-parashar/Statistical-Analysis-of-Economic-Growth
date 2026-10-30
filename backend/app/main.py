import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.routers import api

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Enable CORS for local development and all Vercel domains (*.vercel.app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.FRONTEND_ORIGIN,
    allow_origin_regex=r"^https:\/\/.*\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["System"])
async def root_ping():
    """Root ping endpoint."""
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "api_prefix": "/api"
    }

@app.get("/health", tags=["System"])
async def root_health_check():
    """Top-level health check endpoint."""
    return {"status": "ok", "version": settings.APP_VERSION}

@app.on_event("startup")
def startup_event():
    """Preload current analysis run metadata on startup."""
    try:
        from app.services import analysis_pipeline_service
        analysis_pipeline_service.get_current_analysis_run()
    except Exception as exc:
        print(f"Startup notice: preloading analysis failed: {exc}")

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"available": False, "reason": str(exc)},
    )

app.include_router(api.router, prefix="/api")
