"""
Main FastAPI Application

Production-ready backend for Data Analyst Depth Portal.
"""

import logging
import time
from datetime import datetime
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
import redis

from app.config import settings
from app.database import engine, Base, init_db
from app.core.exceptions import AppException
from app.api import auth
from app.api import dashboard, datasets

logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting Data Analyst Depth Portal...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    
    # Initialize database tables (for development)
    # In production, use Alembic migrations instead
    if settings.is_development:
        try:
            init_db()
            logger.info("Database tables initialized")
        except Exception as e:
            logger.warning(f"Database initialization skipped: {e}")
    
    # Test Redis connection (optional)
    try:
        redis_client = redis.from_url(settings.redis_url)
        redis_client.ping()
        logger.info("Redis connection successful")
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Data Analyst Depth Portal...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="AI-Powered Data Analysis Platform - Production Backend",
    version=settings.app_version,
    docs_url="/api/docs" if settings.debug else None,
    redoc_url="/api/redoc" if settings.debug else None,
    openapi_url="/api/openapi.json" if settings.debug else None,
    lifespan=lifespan,
)

# Add rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"],
)

# Gzip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses."""
    start_time = time.time()
    
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    if not settings.is_development:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    # Request timing
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Metrics
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    REQUEST_DURATION.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(process_time)
    
    return response


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Handle custom application exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "error": exc.to_dict(),
            "timestamp": datetime.utcnow().isoformat(),
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": exc.detail,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.exception(f"Unexpected error: {exc}")
    
    if settings.debug:
        detail = str(exc)
    else:
        detail = "An unexpected error occurred"
    
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "error": {
                "code": "INTERNAL_ERROR",
                "message": detail,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    )


# Health check endpoint
@app.get("/api/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns system health status including:
    - Database connectivity
    - Redis connectivity
    - External API status
    """
    components = {}
    overall_healthy = True
    
    # Check database
    try:
        from app.database import engine
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        components["database"] = {"status": "healthy"}
    except Exception as e:
        components["database"] = {"status": "unhealthy", "message": str(e)}
        overall_healthy = False
    
    # Check Redis
    try:
        redis_client = redis.from_url(settings.redis_url)
        redis_client.ping()
        components["redis"] = {"status": "healthy"}
    except Exception as e:
        components["redis"] = {"status": "unhealthy", "message": str(e)}
        # Redis is optional, don't mark as unhealthy
    
    # Check Gemini API key
    if settings.google_api_key:
        components["gemini_api"] = {"status": "configured"}
    else:
        components["gemini_api"] = {"status": "not_configured"}
    
    return {
        "status": "healthy" if overall_healthy else "unhealthy",
        "message": "All systems operational" if overall_healthy else "Some systems are experiencing issues",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.app_version,
        "environment": settings.environment,
        "components": components,
    }


# Prometheus metrics endpoint
@app.get("/api/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


# Include API routers
app.include_router(auth.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(datasets.router, prefix="/api")

# TODO: Include other routers after they're converted to use database
# app.include_router(analytics.router, prefix="/api")
# app.include_router(reports.router, prefix="/api")
# app.include_router(settings_routes.router, prefix="/api")
# app.include_router(workspaces.router, prefix="/api")
# app.include_router(explorer.router, prefix="/api")


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint redirect to API docs."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/api/docs",
        "health": "/api/health",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.is_development,
        log_level=settings.log_level.lower(),
    )
