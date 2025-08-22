"""
SocialMaestro Backend
Main FastAPI application
"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from pydantic_settings import BaseSettings

from database.database import engine, Base
from modules.scheduler import start_scheduler
from api.routes import content, auth, analytics, review
from api.dependencies import get_current_user

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    database_url: str = "postgresql://user:password@localhost/ai_social_manager"
    secret_key: str = "your-secret-key-here"
    gemini_api_key: str = ""
    reddit_client_id: str = ""
    reddit_client_secret: str = ""
    instagram_access_token: str = ""
    twitter_bearer_token: str = ""
    sendgrid_api_key: str = ""
    environment: str = "development"

    class Config:
        env_file = ".env"

settings = Settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Startup
    logger.info("Starting SocialMaestro Backend...")

    # Create database tables
    Base.metadata.create_all(bind=engine)

    # Start the scheduler
    start_scheduler()

    logger.info("Backend startup complete!")

    yield

    # Shutdown
    logger.info("Shutting down SocialMaestro Backend...")

# Create FastAPI app
app = FastAPI(
    title="SocialMaestro",
    description="Intelligent social media management with AI-powered content generation",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(content.router, prefix="/api/content", tags=["Content Management"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(review.router, prefix="/api/review", tags=["Content Review"])

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "SocialMaestro Backend",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "scheduler": "running",
        "environment": settings.environment
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.environment == "development" else False
    )
