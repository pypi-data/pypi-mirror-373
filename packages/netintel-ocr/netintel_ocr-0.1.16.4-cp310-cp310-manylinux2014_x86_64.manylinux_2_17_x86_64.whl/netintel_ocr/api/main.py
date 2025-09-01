"""
FastAPI Application for NetIntel-OCR v0.1.13
Handles all read/write operations, document ingestion, and job management
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager
import os
from typing import Optional

from .routes import documents, search, jobs, health, database
from .middleware.auth import AuthMiddleware
from .middleware.ratelimit import RateLimitMiddleware

# Version info
API_VERSION = "0.1.13"
API_TITLE = "NetIntel-OCR API"
API_DESCRIPTION = """
NetIntel-OCR API v0.1.13

## Features
- 📄 PDF Document Processing with network diagram extraction
- 🔍 Vector Search and Semantic Queries
- 💼 Job Management and Tracking
- 🗄️ Database Operations
- 🔐 Authentication and Authorization
- 📊 Metrics and Monitoring

## Deployment Modes
- **Production**: Full Kubernetes with KEDA scaling (0-50 concurrent PDFs)
- **Small Scale**: Docker Compose with embedded workers (2 concurrent PDFs)
- **Minimal**: Single container mode (1 PDF at a time)
"""

def create_app(embedded_workers: bool = False, max_workers: Optional[int] = None):
    """
    Create and configure the FastAPI application.
    
    Args:
        embedded_workers: Whether to use embedded workers instead of K8s jobs
        max_workers: Maximum number of embedded workers (if enabled)
        
    Returns:
        Configured FastAPI application
    """
    
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """Application lifespan manager"""
        # Startup
        print(f"Starting {API_TITLE} v{API_VERSION}")
        
        # Store worker configuration in app state
        app.state.embedded_workers = embedded_workers
        app.state.max_workers = max_workers or 2
        
        # Initialize connections
        from .services.database import init_database
        from .services.storage import init_storage
        from .services.queue import init_queue
        
        await init_database()
        await init_storage()
        await init_queue()
        
        # Initialize embedded workers if enabled
        if embedded_workers:
            from ..worker.embedded_worker import EmbeddedWorkerConfig, get_worker_pool
            
            config = EmbeddedWorkerConfig(
                max_workers=app.state.max_workers,
                mode="threaded" if app.state.max_workers <= 2 else "process",
                use_local_storage=os.getenv("STORAGE_TYPE") == "local"
            )
            app.state.worker_pool = get_worker_pool(config)
            print(f"Initialized embedded worker pool with {app.state.max_workers} workers")
        
        yield
        
        # Shutdown
        print(f"Shutting down {API_TITLE}")
        
        # Shutdown embedded workers if enabled
        if embedded_workers and hasattr(app.state, "worker_pool"):
            from ..worker.embedded_worker import shutdown_worker_pool
            shutdown_worker_pool()
            print("Shut down embedded worker pool")
        
        from .services.database import close_database
        await close_database()
    
    # Create FastAPI app
    app = FastAPI(
        title=API_TITLE,
        description=API_DESCRIPTION,
        version=API_VERSION,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )
    
    # Configure CORS
    cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add custom middleware
    app.add_middleware(RateLimitMiddleware)
    if os.getenv("AUTH_ENABLED", "true").lower() == "true":
        app.add_middleware(AuthMiddleware)
    
    # Include routers
    app.include_router(health.router, tags=["Health"])
    app.include_router(documents.router, prefix="/api/v1/documents", tags=["Documents"])
    app.include_router(search.router, prefix="/api/v1/search", tags=["Search"])
    app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["Jobs"])
    app.include_router(database.router, prefix="/api/v1/databases", tags=["Database"])
    
    @app.get("/", include_in_schema=False)
    async def root():
        """Redirect to documentation"""
        return RedirectResponse(url="/docs")
    
    @app.get("/api/v1", tags=["API"])
    async def api_info():
        """Get API information"""
        return {
            "name": API_TITLE,
            "version": API_VERSION,
            "status": "operational",
            "endpoints": {
                "documentation": "/docs",
                "openapi": "/openapi.json",
                "health": "/health",
                "api": "/api/v1"
            },
            "worker_mode": "embedded" if embedded_workers else "kubernetes",
            "max_workers": max_workers if embedded_workers else "unlimited"
        }
    
    return app

# Create default app instance
app = create_app()

if __name__ == "__main__":
    import uvicorn
    
    # Configuration from environment
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    workers = int(os.getenv("API_WORKERS", "1"))
    reload = os.getenv("API_RELOAD", "false").lower() == "true"
    
    # Run server
    if workers > 1 and not reload:
        uvicorn.run(
            "netintel_ocr.api.main:app",
            host=host,
            port=port,
            workers=workers,
            log_level="info"
        )
    else:
        uvicorn.run(
            app,
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )