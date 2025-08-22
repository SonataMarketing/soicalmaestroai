"""
SocialMaestro Backend API
FastAPI application with authentication, social media integrations, and AI features
"""

import logging
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from config.settings import settings
from database.database import check_database_connection, get_db_health
from api.routes import auth, content
from auth.security import SecurityHeaders

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log") if not settings.debug else logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info(f"🚀 Starting {settings.app_name} v{settings.app_version}")

    # Check database connection
    if check_database_connection():
        logger.info("✅ Database connection successful")
    else:
        logger.error("❌ Database connection failed")

    yield

    # Shutdown
    logger.info("👋 Shutting down SocialMaestro")

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="AI-powered social media management platform",
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Add security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)

    # Add security headers
    security_headers = SecurityHeaders.get_security_headers()
    for header, value in security_headers.items():
        response.headers[header] = value

    return response

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add trusted host middleware for production
if not settings.debug:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "*.socialmaestro.com"]
    )

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.app_name} API",
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs" if settings.debug else "disabled_in_production"
    }

# Health check endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2024-08-22T20:47:00Z",
        "version": settings.app_version,
        "environment": "development" if settings.debug else "production"
    }

@app.get("/health/database")
async def database_health():
    """Database health check"""
    return get_db_health()

@app.get("/health/detailed")
async def detailed_health():
    """Detailed health check"""
    db_health = get_db_health()

    return {
        "api": {
            "status": "healthy",
            "version": settings.app_version
        },
        "database": db_health,
        "environment": {
            "debug": settings.debug,
            "cors_origins": settings.cors_origins
        }
    }

# Include API routers
app.include_router(
    auth.router,
    prefix="/api/auth",
    tags=["Authentication"],
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
    }
)

app.include_router(
    content.router,
    prefix="/api/content",
    tags=["Content Management"],
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
    }
)

# Global exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler"""
    logger.warning(f"HTTP {exc.status_code}: {exc.detail} - {request.url}")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code,
            "timestamp": "2024-08-22T20:47:00Z"
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """General exception handler"""
    logger.error(f"Unhandled exception: {str(exc)} - {request.url}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Internal server error" if not settings.debug else str(exc),
            "status_code": 500,
            "timestamp": "2024-08-22T20:47:00Z"
        }
    )

# API information endpoint
@app.get("/api/info")
async def api_info():
    """API information and endpoints"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "endpoints": {
            "authentication": "/api/auth",
            "content": "/api/content",
            "health": "/health",
            "docs": "/docs" if settings.debug else None
        },
        "features": {
            "authentication": "JWT-based with refresh tokens",
            "authorization": "Role-based access control",
            "content_management": "AI-powered content generation",
            "social_media": "Multi-platform posting",
            "analytics": "Performance tracking"
        }
    }

if __name__ == "__main__":
    # Development server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info" if not settings.debug else "debug",
        access_log=settings.debug
    )
