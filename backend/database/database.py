"""
Database configuration and session management
"""

import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from config.settings import settings

# Create database engine with proper configuration
engine = create_engine(
    settings.database_url_sync,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    poolclass=QueuePool,
    echo=settings.debug,  # Log SQL queries in debug mode
    connect_args={
        "check_same_thread": False,  # SQLite compatibility
        "options": "-c timezone=utc"  # Set timezone for PostgreSQL
    } if "sqlite" in settings.database_url else {"options": "-c timezone=utc"}
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

# Create base class for models
Base = declarative_base()

# Metadata for migrations
metadata = MetaData()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all tables in the database"""
    from database.models import (
        User, Brand, SocialAccount, ScrapedContent,
        ContentPost, ContentReview, ScheduledTask,
        PerformanceMetric, AIInsight, CachedContent
    )

    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
        return True
    except Exception as e:
        print(f"❌ Error creating database tables: {str(e)}")
        return False

def drop_tables():
    """Drop all tables in the database (use with caution!)"""
    try:
        Base.metadata.drop_all(bind=engine)
        print("✅ Database tables dropped successfully")
        return True
    except Exception as e:
        print(f"❌ Error dropping database tables: {str(e)}")
        return False

def init_database():
    """Initialize database with tables and basic data"""
    try:
        # Create tables
        create_tables()

        # Create upload directory if it doesn't exist
        os.makedirs(settings.upload_dir, exist_ok=True)

        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Error initializing database: {str(e)}")
        return False

def check_database_connection():
    """Check if database connection is working"""
    try:
        with engine.connect() as connection:
            result = connection.execute("SELECT 1")
            result.fetchone()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

# Connection health check function
def get_db_health():
    """Get database health status"""
    try:
        with engine.connect() as connection:
            result = connection.execute("SELECT 1")
            result.fetchone()
        return {
            "status": "healthy",
            "database": settings.database_name,
            "host": settings.database_host,
            "port": settings.database_port
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "database": settings.database_name,
            "host": settings.database_host,
            "port": settings.database_port
        }
