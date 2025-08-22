"""
SocialMaestro Settings and Configuration
Centralized configuration for all API keys, database, and service settings
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # Application
    app_name: str = "SocialMaestro"
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=True, env="DEBUG")
    secret_key: str = Field(..., env="SECRET_KEY")

    # Database
    database_url: str = Field(..., env="DATABASE_URL")

    # Authentication & Security
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    algorithm: str = Field(default="HS256", env="ALGORITHM")

    # AI Services
    gemini_api_key: str = Field(..., env="GEMINI_API_KEY")
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")

    # Social Media APIs - Instagram
    instagram_app_id: str = Field(..., env="INSTAGRAM_APP_ID")
    instagram_app_secret: str = Field(..., env="INSTAGRAM_APP_SECRET")
    instagram_access_token: Optional[str] = Field(default=None, env="INSTAGRAM_ACCESS_TOKEN")
    instagram_business_account_id: Optional[str] = Field(default=None, env="INSTAGRAM_BUSINESS_ACCOUNT_ID")

    # Social Media APIs - Reddit
    reddit_client_id: str = Field(..., env="REDDIT_CLIENT_ID")
    reddit_client_secret: str = Field(..., env="REDDIT_CLIENT_SECRET")
    reddit_user_agent: str = Field(default="SocialMaestro v1.0", env="REDDIT_USER_AGENT")

    # Social Media APIs - Twitter
    twitter_api_key: Optional[str] = Field(default=None, env="TWITTER_API_KEY")
    twitter_api_secret: Optional[str] = Field(default=None, env="TWITTER_API_SECRET")
    twitter_access_token: Optional[str] = Field(default=None, env="TWITTER_ACCESS_TOKEN")
    twitter_access_token_secret: Optional[str] = Field(default=None, env="TWITTER_ACCESS_TOKEN_SECRET")
    twitter_bearer_token: Optional[str] = Field(default=None, env="TWITTER_BEARER_TOKEN")

    # Social Media APIs - LinkedIn
    linkedin_client_id: Optional[str] = Field(default=None, env="LINKEDIN_CLIENT_ID")
    linkedin_client_secret: Optional[str] = Field(default=None, env="LINKEDIN_CLIENT_SECRET")
    linkedin_access_token: Optional[str] = Field(default=None, env="LINKEDIN_ACCESS_TOKEN")

    # Social Media APIs - Facebook
    facebook_app_id: Optional[str] = Field(default=None, env="FACEBOOK_APP_ID")
    facebook_app_secret: Optional[str] = Field(default=None, env="FACEBOOK_APP_SECRET")
    facebook_access_token: Optional[str] = Field(default=None, env="FACEBOOK_ACCESS_TOKEN")
    facebook_page_id: Optional[str] = Field(default=None, env="FACEBOOK_PAGE_ID")

    # Email & Notifications
    sendgrid_api_key: Optional[str] = Field(default=None, env="SENDGRID_API_KEY")
    smtp_server: str = Field(default="smtp.gmail.com", env="SMTP_SERVER")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_username: Optional[str] = Field(default=None, env="SMTP_USERNAME")
    smtp_password: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    from_email: str = Field(default="noreply@socialmaestro.com", env="FROM_EMAIL")

    # Webhooks
    webhook_secret: str = Field(..., env="WEBHOOK_SECRET")
    base_webhook_url: str = Field(..., env="BASE_WEBHOOK_URL")

    # Redis (for caching and queues)
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")

    # File Storage
    upload_directory: str = Field(default="uploads", env="UPLOAD_DIRECTORY")
    max_file_size: int = Field(default=10485760, env="MAX_FILE_SIZE")  # 10MB
    allowed_file_extensions: List[str] = Field(
        default=["jpg", "jpeg", "png", "gif", "mp4", "mov", "pdf"],
        env="ALLOWED_FILE_EXTENSIONS"
    )

    # Rate Limiting
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=3600, env="RATE_LIMIT_WINDOW")  # 1 hour

    # Scheduler Settings
    scheduler_timezone: str = Field(default="UTC", env="SCHEDULER_TIMEZONE")
    max_retry_attempts: int = Field(default=3, env="MAX_RETRY_ATTEMPTS")

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: Optional[str] = Field(default=None, env="LOG_FILE")

    # CORS
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "https://your-frontend-domain.com"],
        env="ALLOWED_ORIGINS"
    )

    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
_settings = None

def get_settings() -> Settings:
    """Get application settings singleton"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

# Environment-specific configurations
def get_database_url() -> str:
    """Get database URL with fallback for different environments"""
    settings = get_settings()

    if settings.environment == "test":
        return settings.database_url.replace("/ai_social_manager", "/ai_social_manager_test")

    return settings.database_url

def is_production() -> bool:
    """Check if running in production environment"""
    return get_settings().environment == "production"

def is_development() -> bool:
    """Check if running in development environment"""
    return get_settings().environment == "development"
