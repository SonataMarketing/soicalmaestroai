"""
Content Management API Routes
AI content generation, social media posting, and content management
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from database.database import get_db
from database.models import User, Brand, ContentPost, SocialAccount, PostStatus, PostType, Platform
from api.dependencies import get_current_user
from modules.ai_content_generator import ai_generator
from integrations.instagram import instagram_api
from integrations.twitter import twitter_api
from integrations.facebook import facebook_api
from integrations.linkedin import linkedin_api

logger = logging.getLogger(__name__)
router = APIRouter()

# Pydantic models for requests/responses
class ContentGenerationRequest(BaseModel):
    brand_id: int
    platform: str = Field(..., regex="^(instagram|twitter|linkedin|facebook)$")
    content_type: str = Field(..., regex="^(photo|video|text|carousel)$")
    topic: Optional[str] = None
    additional_context: Optional[str] = None

class ContentResponse(BaseModel):
    id: int
    title: Optional[str]
    caption: str
    content_type: str
    platform: str
    status: str
    brand_alignment_score: float
    created_at: datetime
    scheduled_time: Optional[datetime]
    published_time: Optional[datetime]

    class Config:
        from_attributes = True

class SocialMediaPostRequest(BaseModel):
    content_id: int
    social_account_id: int
    scheduled_time: Optional[datetime] = None

class HashtagGenerationRequest(BaseModel):
    content: str
    platform: str
    brand_id: int
    target_count: int = Field(default=10, ge=1, le=30)

class ContentIdeasRequest(BaseModel):
    brand_id: int
    platform: str
    count: int = Field(default=5, ge=1, le=10)

class ContentOptimizationRequest(BaseModel):
    content: str
    source_platform: str
    target_platform: str
    brand_id: int

class BrandVoiceAnalysisRequest(BaseModel):
    brand_id: int
    sample_content: List[str] = Field(..., max_items=10)

# Content Generation Endpoints
@router.post("/generate", response_model=Dict)
async def generate_content(
    request: ContentGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate AI-powered content for social media"""

    # Get brand information
    brand = db.query(Brand).filter(
        Brand.id == request.brand_id,
        Brand.owner_id == current_user.id
    ).first()

    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found"
        )

    # Prepare brand context for AI
    brand_context = {
        "name": brand.name,
        "description": brand.description,
        "industry": brand.industry,
        "target_audience": brand.target_audience,
        "keywords": brand.keywords or [],
        "style_guide": brand.style_guide or {},
        "content_pillars": brand.content_pillars or []
    }

    # Generate content using AI
    result = ai_generator.generate_caption(
        brand_context=brand_context,
        content_type=request.content_type,
        platform=request.platform,
        topic=request.topic,
        additional_context=request.additional_context
    )

    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content generation failed: {result['error']}"
        )

    # Save generated content to database
    content_post = ContentPost(
        title=f"{request.platform.title()} {request.content_type} - {datetime.now().strftime('%Y%m%d_%H%M')}",
        caption=result["content"]["caption"],
        content_type=PostType[request.content_type.upper()],
        platform=Platform[request.platform.upper()],
        brand_id=brand.id,
        status=PostStatus.DRAFT,
        created_by_ai=True,
        brand_alignment_score=85.0,  # This could be calculated by AI
        created_at=datetime.utcnow()
    )

    db.add(content_post)
    db.commit()
    db.refresh(content_post)

    return {
        "success": True,
        "content_id": content_post.id,
        "generated_content": result["content"],
        "ai_usage": result.get("usage", {}),
        "brand_alignment_score": content_post.brand_alignment_score
    }

@router.post("/generate/hashtags")
async def generate_hashtags(
    request: HashtagGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate relevant hashtags for content"""

    # Get brand information
    brand = db.query(Brand).filter(
        Brand.id == request.brand_id,
        Brand.owner_id == current_user.id
    ).first()

    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found"
        )

    brand_context = {
        "name": brand.name,
        "industry": brand.industry,
        "target_audience": brand.target_audience
    }

    hashtags = ai_generator.generate_hashtags(
        content=request.content,
        platform=request.platform,
        brand_context=brand_context,
        target_count=request.target_count
    )

    return {
        "success": True,
        "hashtags": hashtags,
        "count": len(hashtags),
        "platform": request.platform
    }

@router.post("/generate/ideas")
async def generate_content_ideas(
    request: ContentIdeasRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate content ideas for a brand"""

    # Get brand information
    brand = db.query(Brand).filter(
        Brand.id == request.brand_id,
        Brand.owner_id == current_user.id
    ).first()

    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found"
        )

    brand_context = {
        "name": brand.name,
        "description": brand.description,
        "industry": brand.industry,
        "target_audience": brand.target_audience,
        "content_pillars": brand.content_pillars or []
    }

    ideas = ai_generator.generate_content_ideas(
        brand_context=brand_context,
        platform=request.platform,
        count=request.count
    )

    return {
        "success": True,
        "ideas": ideas,
        "count": len(ideas),
        "platform": request.platform,
        "brand": brand.name
    }

@router.post("/optimize")
async def optimize_content(
    request: ContentOptimizationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Optimize content for different platforms"""

    # Get brand information
    brand = db.query(Brand).filter(
        Brand.id == request.brand_id,
        Brand.owner_id == current_user.id
    ).first()

    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found"
        )

    brand_context = {
        "name": brand.name,
        "industry": brand.industry,
        "style_guide": brand.style_guide or {}
    }

    result = ai_generator.optimize_content_for_platform(
        content=request.content,
        source_platform=request.source_platform,
        target_platform=request.target_platform,
        brand_context=brand_context
    )

    return result

@router.post("/analyze/brand-voice")
async def analyze_brand_voice(
    request: BrandVoiceAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze and define brand voice from sample content"""

    # Get brand information
    brand = db.query(Brand).filter(
        Brand.id == request.brand_id,
        Brand.owner_id == current_user.id
    ).first()

    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found"
        )

    brand_context = {
        "name": brand.name,
        "industry": brand.industry
    }

    result = ai_generator.analyze_brand_voice(
        brand_context=brand_context,
        sample_content=request.sample_content
    )

    # Update brand with analyzed voice if successful
    if result.get("success") and "analysis" in result:
        brand.style_guide = brand.style_guide or {}
        brand.style_guide.update(result["analysis"])
        db.commit()

    return result

# Content Management Endpoints
@router.get("/", response_model=List[ContentResponse])
async def list_content(
    brand_id: Optional[int] = None,
    platform: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 25,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List user's content with filtering options"""

    # Base query for user's brands
    query = db.query(ContentPost).join(Brand).filter(Brand.owner_id == current_user.id)

    # Apply filters
    if brand_id:
        query = query.filter(ContentPost.brand_id == brand_id)

    if platform:
        try:
            platform_enum = Platform[platform.upper()]
            query = query.filter(ContentPost.platform == platform_enum)
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid platform: {platform}"
            )

    if status:
        try:
            status_enum = PostStatus[status.upper()]
            query = query.filter(ContentPost.status == status_enum)
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status}"
            )

    # Order by creation date (newest first) and apply pagination
    content_posts = query.order_by(ContentPost.created_at.desc()).offset(offset).limit(limit).all()

    return content_posts

@router.get("/{content_id}")
async def get_content(
    content_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific content by ID"""

    content_post = db.query(ContentPost).join(Brand).filter(
        ContentPost.id == content_id,
        Brand.owner_id == current_user.id
    ).first()

    if not content_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )

    return content_post

@router.put("/{content_id}")
async def update_content(
    content_id: int,
    caption: Optional[str] = None,
    title: Optional[str] = None,
    scheduled_time: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update content"""

    content_post = db.query(ContentPost).join(Brand).filter(
        ContentPost.id == content_id,
        Brand.owner_id == current_user.id
    ).first()

    if not content_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )

    # Update fields
    if caption is not None:
        content_post.caption = caption

    if title is not None:
        content_post.title = title

    if scheduled_time is not None:
        content_post.scheduled_time = scheduled_time
        if content_post.status == PostStatus.DRAFT:
            content_post.status = PostStatus.SCHEDULED

    content_post.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(content_post)

    return content_post

@router.delete("/{content_id}")
async def delete_content(
    content_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete content"""

    content_post = db.query(ContentPost).join(Brand).filter(
        ContentPost.id == content_id,
        Brand.owner_id == current_user.id
    ).first()

    if not content_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )

    db.delete(content_post)
    db.commit()

    return {"message": "Content deleted successfully"}

# Social Media Posting Endpoints
@router.post("/{content_id}/publish")
async def publish_content(
    content_id: int,
    social_account_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Publish content to social media platform"""

    # Get content
    content_post = db.query(ContentPost).join(Brand).filter(
        ContentPost.id == content_id,
        Brand.owner_id == current_user.id
    ).first()

    if not content_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )

    # Get social account
    social_account = db.query(SocialAccount).join(Brand).filter(
        SocialAccount.id == social_account_id,
        Brand.owner_id == current_user.id
    ).first()

    if not social_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Social account not found"
        )

    # Verify platform compatibility
    if content_post.platform.value != social_account.platform.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content platform doesn't match social account platform"
        )

    # Publish immediately or schedule
    if content_post.scheduled_time and content_post.scheduled_time > datetime.utcnow():
        # Schedule for later
        background_tasks.add_task(
            _schedule_publish_task,
            content_post,
            social_account,
            db
        )

        content_post.status = PostStatus.SCHEDULED
        message = f"Content scheduled for {content_post.scheduled_time}"
    else:
        # Publish now
        result = await _publish_to_platform(content_post, social_account)

        if result.get("success"):
            content_post.status = PostStatus.PUBLISHED
            content_post.published_time = datetime.utcnow()
            message = "Content published successfully"
        else:
            content_post.status = PostStatus.FAILED
            content_post.error_message = result.get("error", "Unknown error")
            message = f"Publishing failed: {result.get('error')}"

    db.commit()

    return {
        "success": content_post.status == PostStatus.PUBLISHED or content_post.status == PostStatus.SCHEDULED,
        "message": message,
        "status": content_post.status.value,
        "content_id": content_post.id
    }

async def _publish_to_platform(content_post: ContentPost, social_account: SocialAccount) -> Dict:
    """Publish content to specific social media platform"""

    platform = social_account.platform.value
    caption = content_post.caption
    access_token = social_account.access_token

    if platform == "instagram":
        if content_post.image_url:
            return instagram_api.post_photo(
                access_token=access_token,
                image_url=content_post.image_url,
                caption=caption
            )
        else:
            return {"error": "Instagram requires image for posts"}

    elif platform == "twitter":
        if content_post.image_url:
            return twitter_api.post_tweet_with_media(
                text=caption,
                media_url=content_post.image_url
            )
        else:
            return twitter_api.post_tweet(caption)

    elif platform == "facebook":
        return facebook_api.post_to_page(
            page_id=social_account.username,  # Assuming username stores page ID
            page_access_token=access_token,
            message=caption,
            image_url=content_post.image_url
        )

    elif platform == "linkedin":
        return linkedin_api.post_to_profile(
            access_token=access_token,
            text=caption,
            image_url=content_post.image_url
        )

    else:
        return {"error": f"Unsupported platform: {platform}"}

def _schedule_publish_task(content_post: ContentPost, social_account: SocialAccount, db: Session):
    """Background task for scheduled publishing"""
    # In a real implementation, this would be handled by a task queue like Celery
    # For now, this is a placeholder for the scheduling logic
    logger.info(f"Scheduled publishing task created for content {content_post.id}")

# Analytics Endpoints
@router.get("/{content_id}/analytics")
async def get_content_analytics(
    content_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get analytics for published content"""

    content_post = db.query(ContentPost).join(Brand).filter(
        ContentPost.id == content_id,
        Brand.owner_id == current_user.id
    ).first()

    if not content_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )

    if content_post.status != PostStatus.PUBLISHED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Analytics only available for published content"
        )

    # Return stored analytics data
    analytics = {
        "content_id": content_post.id,
        "platform": content_post.platform.value,
        "published_time": content_post.published_time,
        "engagement": {
            "likes": content_post.likes_count,
            "comments": content_post.comments_count,
            "shares": content_post.shares_count,
            "reach": content_post.reach,
            "impressions": content_post.impressions
        },
        "engagement_rate": content_post.actual_engagement_rate,
        "brand_alignment_score": content_post.brand_alignment_score
    }

    return analytics

# Platform Health Checks
@router.get("/platforms/status")
async def get_platforms_status():
    """Get status of all social media platform integrations"""

    status_checks = {
        "instagram": instagram_api.is_configured(),
        "twitter": twitter_api.is_configured(),
        "facebook": facebook_api.is_configured(),
        "linkedin": linkedin_api.is_configured() if 'linkedin_api' in globals() else False,
        "ai_generator": ai_generator._is_configured()
    }

    return {
        "platforms": status_checks,
        "all_configured": all(status_checks.values()),
        "configured_count": sum(status_checks.values())
    }
