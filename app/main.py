"""
Main FastAPI application for RAG Document Chat
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
import os

from app.config import settings
from app.models import init_db
from app.api.v1.api import api_router

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize database
init_db()

# Create FastAPI app without root_path (we'll handle /rag prefix manually)
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="RAG-powered document chat using Ollama and LEANN. Optimized for Markdown documents.",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json"
)

# Mount static files FIRST (before middleware and routers)
# Note: We don't mount here with root_path because it causes issues
# Static files will be mounted after the app is created without root_path constraint

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router (for direct access)
app.include_router(api_router, prefix="/api/v1")

# Include API router again with /rag prefix (for nginx proxy)
app.include_router(api_router, prefix="/rag/api/v1")

# Include web interface at root (import must be after app creation)
from app.api.v1.endpoints.web import router as web_router
app.include_router(web_router, tags=["Web Interface"])
app.include_router(web_router, prefix="/rag", tags=["Web Interface"])

# Mount static files (for direct access)
static_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
logger.info(f"Static files path: {static_path}")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")
    logger.info("Static files mounted at /static")
    # Also mount with /rag prefix for nginx proxy
    app.mount("/rag/static", StaticFiles(directory=static_path), name="static_rag")
    logger.info("Static files mounted at /rag/static")


# Root endpoints removed - now handled by web router
# Web interface is served at / and /rag


@app.get("/rag/api/v1/openapi.json", include_in_schema=False)
async def rag_openapi():
    """Serve OpenAPI spec for /rag prefix"""
    return app.openapi()


@app.get("/rag/api/v1/docs", include_in_schema=False)
async def rag_docs():
    """Serve Swagger UI for /rag prefix"""
    from fastapi.openapi.docs import get_swagger_ui_html
    return get_swagger_ui_html(
        openapi_url="/rag/api/v1/openapi.json",
        title=f"{settings.app_name} - Swagger UI"
    )


@app.get("/rag/api/v1/redoc", include_in_schema=False)
async def rag_redoc():
    """Serve ReDoc for /rag prefix"""
    from fastapi.openapi.docs import get_redoc_html
    return get_redoc_html(
        openapi_url="/rag/api/v1/openapi.json",
        title=f"{settings.app_name} - ReDoc"
    )


@app.on_event("startup")
async def startup_event():
    """Startup tasks"""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Ollama URL: {settings.ollama_base_url}")
    logger.info(f"Ollama Model: {settings.ollama_model}")
    logger.info(f"LEANN Index Path: {settings.leann_index_path}")
    logger.info(f"Database: {settings.database_url}")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown tasks"""
    logger.info(f"Shutting down {settings.app_name}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=6956,
        reload=settings.debug
    )
