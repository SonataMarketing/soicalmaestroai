"""
Database models for AI Social Media Manager
"""

from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.database import Base

class PostStatus(PyEnum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"

class PostType(PyEnum):
    PHOTO = "photo"
    VIDEO = "video"
    TEXT = "text"

class Platform(PyEnum):
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="manager")  # admin, manager, viewer
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    brands = relationship("Brand", back_populates="owner")
    reviews = relationship("ContentReview", back_populates="reviewer")

class Brand(Base):
    __tablename__ = "brands"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    website_url = Column(String)
    description = Column(Text)
    industry = Column(String)
    target_audience = Column(Text)
    keywords = Column(JSON)  # List of brand keywords

    # Brand style guide (AI-generated)
    style_guide = Column(JSON)  # Tone, voice, personality traits
    color_palette = Column(JSON)  # Brand colors
    typography = Column(JSON)  # Font preferences
    content_pillars = Column(JSON)  # Content themes

    # Settings
    posting_frequency = Column(Integer, default=2)  # Posts per day
    posting_times = Column(JSON)  # Preferred posting times
    auto_posting = Column(Boolean, default=False)

    # Metadata
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    owner = relationship("User", back_populates="brands")
    social_accounts = relationship("SocialAccount", back_populates="brand")
    content_posts = relationship("ContentPost", back_populates="brand")
    scraped_content = relationship("ScrapedContent", back_populates="brand")

class SocialAccount(Base):
    __tablename__ = "social_accounts"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(Enum(Platform), nullable=False)
    username = Column(String, nullable=False)
    access_token = Column(String)  # Encrypted
    refresh_token = Column(String)  # Encrypted
    is_active = Column(Boolean, default=True)
    follower_count = Column(Integer, default=0)

    # Metadata
    brand_id = Column(Integer, ForeignKey("brands.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    brand = relationship("Brand", back_populates="social_accounts")

class ScrapedContent(Base):
    __tablename__ = "scraped_content"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(Enum(Platform), nullable=False)
    post_url = Column(String, nullable=False)
    content_text = Column(Text)
    hashtags = Column(JSON)  # List of hashtags

    # Engagement metrics
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)

    # AI Analysis
    relevance_score = Column(Float, default=0.0)  # 0-100
    sentiment_score = Column(Float, default=0.0)  # -1 to 1
    trending_keywords = Column(JSON)

    # Metadata
    brand_id = Column(Integer, ForeignKey("brands.id"))
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    brand = relationship("Brand", back_populates="scraped_content")

class ContentPost(Base):
    __tablename__ = "content_posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    caption = Column(Text, nullable=False)
    content_type = Column(Enum(PostType), nullable=False)
    platform = Column(Enum(Platform), nullable=False)

    # Media
    image_url = Column(String)
    video_url = Column(String)
    thumbnail_url = Column(String)
    media_description = Column(Text)  # Alt text or description

    # Scheduling
    scheduled_time = Column(DateTime(timezone=True))
    published_time = Column(DateTime(timezone=True))
    status = Column(Enum(PostStatus), default=PostStatus.DRAFT)

    # AI Scores
    brand_alignment_score = Column(Float, default=0.0)  # 0-100
    engagement_prediction = Column(Float, default=0.0)  # Predicted engagement rate
    risk_score = Column(String, default="low")  # low, medium, high

    # Performance (after publishing)
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    reach = Column(Integer, default=0)
    impressions = Column(Integer, default=0)
    actual_engagement_rate = Column(Float, default=0.0)

    # Metadata
    brand_id = Column(Integer, ForeignKey("brands.id"))
    created_by_ai = Column(Boolean, default=False)
    retry_count = Column(Integer, default=0)
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    brand = relationship("Brand", back_populates="content_posts")
    reviews = relationship("ContentReview", back_populates="post")

class ContentReview(Base):
    __tablename__ = "content_reviews"

    id = Column(Integer, primary_key=True, index=True)
    decision = Column(String)  # approve, reject, edit
    feedback = Column(Text)
    suggested_changes = Column(Text)

    # Metadata
    post_id = Column(Integer, ForeignKey("content_posts.id"))
    reviewer_id = Column(Integer, ForeignKey("users.id"))
    reviewed_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    post = relationship("ContentPost", back_populates="reviews")
    reviewer = relationship("User", back_populates="reviews")

class ScheduledTask(Base):
    __tablename__ = "scheduled_tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_name = Column(String, nullable=False)
    task_type = Column(String, nullable=False)  # scraping, generation, analysis
    parameters = Column(JSON)
    status = Column(String, default="pending")  # pending, running, completed, failed

    # Timing
    scheduled_time = Column(DateTime(timezone=True), nullable=False)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))

    # Results
    result_data = Column(JSON)
    error_message = Column(Text)

    # Metadata
    brand_id = Column(Integer, ForeignKey("brands.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class PerformanceMetric(Base):
    __tablename__ = "performance_metrics"

    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String, nullable=False)
    metric_value = Column(Float, nullable=False)
    metric_date = Column(DateTime(timezone=True), nullable=False)
    platform = Column(Enum(Platform))

    # Aggregation period
    period_type = Column(String, default="daily")  # daily, weekly, monthly

    # Metadata
    brand_id = Column(Integer, ForeignKey("brands.id"))
    post_id = Column(Integer, ForeignKey("content_posts.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AIInsight(Base):
    __tablename__ = "ai_insights"

    id = Column(Integer, primary_key=True, index=True)
    insight_type = Column(String, nullable=False)  # performance, optimization, trend
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    recommendation = Column(Text)
    confidence_score = Column(Float, default=0.0)  # 0-1
    potential_impact = Column(String)  # low, medium, high

    # Data backing the insight
    supporting_data = Column(JSON)

    # Status
    is_acted_upon = Column(Boolean, default=False)
    action_taken = Column(Text)

    # Metadata
    brand_id = Column(Integer, ForeignKey("brands.id"))
    generated_at = Column(DateTime(timezone=True), server_default=func.now())

class CachedContent(Base):
    __tablename__ = "cached_content"

    id = Column(Integer, primary_key=True, index=True)
    cache_key = Column(String, unique=True, nullable=False)
    content_data = Column(JSON, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    accessed_count = Column(Integer, default=0)
    last_accessed = Column(DateTime(timezone=True))
