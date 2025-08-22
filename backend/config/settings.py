"""
Application settings and configuration
"""

import os
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Application
    app_name: str = Field(default="SocialMaestro", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")

    # Database
    database_url: str = Field(env="DATABASE_URL")
    database_host: str = Field(default="localhost", env="DATABASE_HOST")
    database_port: int = Field(default=5432, env="DATABASE_PORT")
    database_name: str = Field(env="DATABASE_NAME")
    database_user: str = Field(env="DATABASE_USER")
    database_password: str = Field(env="DATABASE_PASSWORD")

    # JWT Authentication
    secret_key: str = Field(env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")

    # OpenAI Configuration
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_org_id: Optional[str] = Field(default=None, env="OPENAI_ORG_ID")
    ai_model: str = Field(default="gpt-4", env="AI_MODEL")
    ai_max_tokens: int = Field(default=2000, env="AI_MAX_TOKENS")
    ai_temperature: float = Field(default=0.7, env="AI_TEMPERATURE")

    # Social Media APIs
    # Instagram
    instagram_app_id: Optional[str] = Field(default=None, env="INSTAGRAM_APP_ID")
    instagram_app_secret: Optional[str] = Field(default=None, env="INSTAGRAM_APP_SECRET")
    instagram_redirect_uri: str = Field(default="http://localhost:8000/auth/instagram/callback", env="INSTAGRAM_REDIRECT_URI")

    # Facebook
    facebook_app_id: Optional[str] = Field(default=None, env="FACEBOOK_APP_ID")
    facebook_app_secret: Optional[str] = Field(default=None, env="FACEBOOK_APP_SECRET")
    facebook_redirect_uri: str = Field(default="http://localhost:8000/auth/facebook/callback", env="FACEBOOK_REDIRECT_URI")

    # Twitter
    twitter_api_key: Optional[str] = Field(default=None, env="TWITTER_API_KEY")
    twitter_api_secret: Optional[str] = Field(default=None, env="TWITTER_API_SECRET")
    twitter_bearer_token: Optional[str] = Field(default=None, env="TWITTER_BEARER_TOKEN")
    twitter_access_token: Optional[str] = Field(default=None, env="TWITTER_ACCESS_TOKEN")
    twitter_access_secret: Optional[str] = Field(default=None, env="TWITTER_ACCESS_SECRET")

    # LinkedIn
    linkedin_client_id: Optional[str] = Field(default=None, env="LINKEDIN_CLIENT_ID")
    linkedin_client_secret: Optional[str] = Field(default=None, env="LINKEDIN_CLIENT_SECRET")
    linkedin_redirect_uri: str = Field(default="http://localhost:8000/auth/linkedin/callback", env="LINKEDIN_REDIRECT_URI")

    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    redis_host: str = Field(default="localhost", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_db: int = Field(default=0, env="REDIS_DB")

    # Email Configuration
    sendgrid_api_key: Optional[str] = Field(default=None, env="SENDGRID_API_KEY")
    from_email: str = Field(default="noreply@socialmaestro.com", env="FROM_EMAIL")
    from_name: str = Field(default="SocialMaestro", env="FROM_NAME")

    # CORS
    cors_origins: List[str] = Field(default=["http://localhost:3000", "http://127.0.0.1:3000"], env="CORS_ORIGINS")

    # File Upload
    upload_dir: str = Field(default="uploads", env="UPLOAD_DIR")
    max_file_size: int = Field(default=10485760, env="MAX_FILE_SIZE")  # 10MB

    # Rate Limiting
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=3600, env="RATE_LIMIT_WINDOW")  # 1 hour

    # Celery Configuration
    celery_broker_url: str = Field(default="redis://localhost:6379/1", env="CELERY_BROKER_URL")
    celery_result_backend: str = Field(default="redis://localhost:6379/2", env="CELERY_RESULT_BACKEND")

    # Content Generation Settings
    default_posting_times: List[str] = Field(default=["09:00", "15:00", "18:00"], env="DEFAULT_POSTING_TIMES")
    max_hashtags_per_post: int = Field(default=15, env="MAX_HASHTAGS_PER_POST")
    content_generation_batch_size: int = Field(default=5, env="CONTENT_GENERATION_BATCH_SIZE")

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL"""
        return self.database_url.replace("postgresql://", "postgresql://")

    @property
    def database_url_async(self) -> str:
        """Get asynchronous database URL"""
        return self.database_url.replace("postgresql://", "postgresql+asyncpg://")

# Create global settings instance
settings = Settings()
