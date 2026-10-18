from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.routers import api

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.FRONTEND_ORIGIN,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    """Preload the current analysis run and dataset on server boot."""
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
