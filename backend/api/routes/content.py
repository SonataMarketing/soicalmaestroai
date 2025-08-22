"""
Content Management API Routes
Complete CRUD operations for content, scheduling, and platform integrations
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from pydantic import BaseModel, Field

from database.database import get_db
from database.models import (
    ContentPost, Brand, User, PostStatus, PostType, Platform,
    ScrapedContent, ContentReview
)
from api.dependencies import (
    get_current_user, require_permission, RequirePermission,
    verify_brand_access, validate_content_ownership,
    get_pagination_params, PaginationParams, get_filter_params,
    FilterParams, audit_log
)
from modules.generator import ContentGenerator
from modules.scraper import ContentScraper
from modules.notifier import NotificationManager
from integrations.webhooks import get_webhook_manager

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
generator = ContentGenerator()
scraper = ContentScraper()
notifier = NotificationManager()
webhook_manager = get_webhook_manager()

# Pydantic models
class ContentCreate(BaseModel):
    title: Optional[str] = None
    caption: str = Field(..., min_length=1, max_length=5000)
    content_type: PostType
    platform: Platform
    scheduled_time: Optional[datetime] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    media_description: Optional[str] = None
    brand_id: int

class ContentUpdate(BaseModel):
    title: Optional[str] = None
    caption: Optional[str] = Field(None, min_length=1, max_length=5000)
    scheduled_time: Optional[datetime] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    media_description: Optional[str] = None
    status: Optional[PostStatus] = None

class ContentResponse(BaseModel):
    id: int
    title: Optional[str]
    caption: str
    content_type: PostType
    platform: Platform
    scheduled_time: Optional[datetime]
    published_time: Optional[datetime]
    status: PostStatus
    brand_alignment_score: float
    risk_score: str
    image_url: Optional[str]
    video_url: Optional[str]
    brand_id: int
    created_by_ai: bool
    created_at: datetime
    updated_at: Optional[datetime]

    # Engagement metrics
    likes_count: int = 0
    comments_count: int = 0
    shares_count: int = 0
    reach: int = 0
    actual_engagement_rate: float = 0.0

    class Config:
        from_attributes = True

class ContentGenerate(BaseModel):
    brand_id: int
    content_type: Optional[PostType] = None
    platform: Optional[Platform] = None
    inspiration_keywords: Optional[List[str]] = None
    custom_prompt: Optional[str] = None

class ContentApproval(BaseModel):
    decision: str = Field(..., regex="^(approve|reject|request_changes)$")
    feedback: Optional[str] = None
    suggested_changes: Optional[str] = None

class BulkAction(BaseModel):
    content_ids: List[int]
    action: str = Field(..., regex="^(approve|reject|delete|schedule|publish)$")
    scheduled_time: Optional[datetime] = None

class ScrapingRequest(BaseModel):
    brand_id: int
    keywords: Optional[List[str]] = None
    platforms: Optional[List[str]] = ["instagram", "reddit"]
    limit: Optional[int] = Field(default=50, le=100)

# Content CRUD Operations

@router.get("/content", response_model=List[ContentResponse])
async def list_content(
    pagination: PaginationParams = Depends(get_pagination_params),
    filters: FilterParams = Depends(get_filter_params),
    brand_id: Optional[int] = Query(None),
    status: Optional[PostStatus] = Query(None),
    platform: Optional[Platform] = Query(None),
    content_type: Optional[PostType] = Query(None),
    current_user: User = RequirePermission.view_brands,
    db: Session = Depends(get_db)
):
    """List content with filtering and pagination"""

    query = db.query(ContentPost)

    # Apply brand access filter
    from api.dependencies import get_brand_access_filter
    brand_filter = get_brand_access_filter(current_user)
    if brand_filter is not None:
        query = query.join(Brand).filter(brand_filter)

    # Apply filters
    if brand_id:
        # Verify user has access to this brand
        await verify_brand_access(brand_id, current_user, db)
        query = query.filter(ContentPost.brand_id == brand_id)

    if status:
        query = query.filter(ContentPost.status == status)

    if platform:
        query = query.filter(ContentPost.platform == platform)

    if content_type:
        query = query.filter(ContentPost.content_type == content_type)

    if filters.start_date:
        start_date = datetime.fromisoformat(filters.start_date)
        query = query.filter(ContentPost.created_at >= start_date)

    if filters.end_date:
        end_date = datetime.fromisoformat(filters.end_date)
        query = query.filter(ContentPost.created_at <= end_date)

    # Order by creation time (newest first)
    query = query.order_by(desc(ContentPost.created_at))

    # Apply pagination
    content = query.offset(pagination.skip).limit(pagination.limit).all()

    return content

@router.get("/content/{content_id}", response_model=ContentResponse)
async def get_content(
    content_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific content by ID"""

    content = await validate_content_ownership(content_id, current_user, db)
    return content

@router.post("/content", response_model=ContentResponse, status_code=status.HTTP_201_CREATED)
async def create_content(
    content_data: ContentCreate,
    background_tasks: BackgroundTasks,
    current_user: User = RequirePermission.create_content,
    db: Session = Depends(get_db),
    _audit: dict = Depends(audit_log("create", "content"))
):
    """Create new content"""

    # Verify user has access to the brand
    brand = await verify_brand_access(content_data.brand_id, current_user, db)

    # Create content post
    content = ContentPost(
        title=content_data.title,
        caption=content_data.caption,
        content_type=content_data.content_type,
        platform=content_data.platform,
        scheduled_time=content_data.scheduled_time,
        image_url=content_data.image_url,
        video_url=content_data.video_url,
        media_description=content_data.media_description,
        brand_id=content_data.brand_id,
        status=PostStatus.DRAFT,
        created_by_ai=False,
        created_at=datetime.utcnow()
    )

    # Calculate brand alignment score
    if brand.style_guide:
        content.brand_alignment_score = await generator.calculate_brand_alignment_score(
            content_data.caption, brand
        )

    # Set risk score based on alignment
    if content.brand_alignment_score >= 90:
        content.risk_score = "low"
    elif content.brand_alignment_score >= 75:
        content.risk_score = "medium"
    else:
        content.risk_score = "high"

    db.add(content)
    db.commit()
    db.refresh(content)

    logger.info(f"Content created: {content.id} by user {current_user.id}")

    return content

@router.put("/content/{content_id}", response_model=ContentResponse)
async def update_content(
    content_id: int,
    content_update: ContentUpdate,
    background_tasks: BackgroundTasks,
    current_user: User = RequirePermission.edit_content,
    db: Session = Depends(get_db),
    _audit: dict = Depends(audit_log("update", "content"))
):
    """Update existing content"""

    content = await validate_content_ownership(content_id, current_user, db)

    # Update fields
    if content_update.title is not None:
        content.title = content_update.title

    if content_update.caption is not None:
        content.caption = content_update.caption

        # Recalculate brand alignment if caption changed
        brand = db.query(Brand).filter(Brand.id == content.brand_id).first()
        if brand and brand.style_guide:
            content.brand_alignment_score = await generator.calculate_brand_alignment_score(
                content_update.caption, brand
            )

    if content_update.scheduled_time is not None:
        content.scheduled_time = content_update.scheduled_time

    if content_update.image_url is not None:
        content.image_url = content_update.image_url

    if content_update.video_url is not None:
        content.video_url = content_update.video_url

    if content_update.media_description is not None:
        content.media_description = content_update.media_description

    if content_update.status is not None:
        old_status = content.status
        content.status = content_update.status

        # Send notifications on status change
        if old_status != content_update.status:
            if content_update.status == PostStatus.PENDING_REVIEW:
                background_tasks.add_task(notifier.send_approval_request, content)
            elif content_update.status == PostStatus.SCHEDULED:
                # Schedule for publishing
                background_tasks.add_task(schedule_content_publication, content)

    content.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(content)

    logger.info(f"Content updated: {content.id} by user {current_user.id}")

    return content

@router.delete("/content/{content_id}")
async def delete_content(
    content_id: int,
    current_user: User = RequirePermission.delete_content,
    db: Session = Depends(get_db),
    _audit: dict = Depends(audit_log("delete", "content"))
):
    """Delete content"""

    content = await validate_content_ownership(content_id, current_user, db)

    # Don't allow deletion of published content
    if content.status == PostStatus.PUBLISHED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete published content"
        )

    db.delete(content)
    db.commit()

    logger.info(f"Content deleted: {content_id} by user {current_user.id}")

    return {"message": "Content deleted successfully"}

# AI Content Generation

@router.post("/content/generate", response_model=List[ContentResponse])
async def generate_content(
    generate_request: ContentGenerate,
    background_tasks: BackgroundTasks,
    current_user: User = RequirePermission.create_content,
    db: Session = Depends(get_db),
    _audit: dict = Depends(audit_log("generate", "content"))
):
    """Generate AI content for a brand"""

    # Verify user has access to the brand
    brand = await verify_brand_access(generate_request.brand_id, current_user, db)

    try:
        # Generate content using AI
        if generate_request.custom_prompt:
            # Custom content generation
            suggestions = await generator.get_content_suggestions(brand, count=1)
            # This would use the custom prompt - simplified for now
            generated_content = suggestions[:1]
        else:
            # Standard daily content generation
            result = await generator.generate_daily_content(brand)

            if result.get("errors"):
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Content generation failed: {result['errors']}"
                )

            # Get the generated posts from database
            generated_posts = []
            for post_info in result.get("posts_generated", []):
                post = db.query(ContentPost).filter(ContentPost.id == post_info["post_id"]).first()
                if post:
                    generated_posts.append(post)

            return generated_posts

    except Exception as e:
        logger.error(f"Content generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content generation failed: {str(e)}"
        )

@router.post("/content/{content_id}/regenerate", response_model=ContentResponse)
async def regenerate_content(
    content_id: int,
    feedback: str = None,
    current_user: User = RequirePermission.edit_content,
    db: Session = Depends(get_db),
    _audit: dict = Depends(audit_log("regenerate", "content"))
):
    """Regenerate content with feedback"""

    content = await validate_content_ownership(content_id, current_user, db)

    if not content.created_by_ai:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only regenerate AI-created content"
        )

    # Regenerate content
    updated_content = await generator.regenerate_post(content_id, feedback or "")

    if not updated_content:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to regenerate content"
        )

    logger.info(f"Content regenerated: {content_id} by user {current_user.id}")

    return updated_content

# Content Approval Workflow

@router.post("/content/{content_id}/approve")
async def approve_content(
    content_id: int,
    approval: ContentApproval,
    background_tasks: BackgroundTasks,
    current_user: User = RequirePermission.approve_content,
    db: Session = Depends(get_db),
    _audit: dict = Depends(audit_log("approve", "content"))
):
    """Approve or reject content"""

    content = await validate_content_ownership(content_id, current_user, db)

    if content.status != PostStatus.PENDING_REVIEW:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content is not pending review"
        )

    # Create review record
    review = ContentReview(
        post_id=content_id,
        reviewer_id=current_user.id,
        decision=approval.decision,
        feedback=approval.feedback,
        suggested_changes=approval.suggested_changes,
        reviewed_at=datetime.utcnow()
    )
    db.add(review)

    # Update content status
    if approval.decision == "approve":
        content.status = PostStatus.APPROVED
        if content.scheduled_time:
            content.status = PostStatus.SCHEDULED
            background_tasks.add_task(schedule_content_publication, content)
    elif approval.decision == "reject":
        content.status = PostStatus.REJECTED
    elif approval.decision == "request_changes":
        content.status = PostStatus.DRAFT
        # Could trigger regeneration here

    content.updated_at = datetime.utcnow()
    db.commit()

    logger.info(f"Content {approval.decision}d: {content_id} by user {current_user.id}")

    return {
        "message": f"Content {approval.decision}d successfully",
        "content_id": content_id,
        "new_status": content.status.value
    }

@router.get("/content/{content_id}/reviews")
async def get_content_reviews(
    content_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get review history for content"""

    content = await validate_content_ownership(content_id, current_user, db)

    reviews = db.query(ContentReview).filter(
        ContentReview.post_id == content_id
    ).order_by(desc(ContentReview.reviewed_at)).all()

    return reviews

# Content Publishing

@router.post("/content/{content_id}/publish")
async def publish_content_now(
    content_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = RequirePermission.publish_content,
    db: Session = Depends(get_db),
    _audit: dict = Depends(audit_log("publish", "content"))
):
    """Publish content immediately"""

    content = await validate_content_ownership(content_id, current_user, db)

    if content.status not in [PostStatus.APPROVED, PostStatus.SCHEDULED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content must be approved before publishing"
        )

    # Publish to platform
    background_tasks.add_task(publish_content_to_platform, content)

    return {
        "message": "Content publishing initiated",
        "content_id": content_id
    }

async def publish_content_to_platform(content: ContentPost):
    """Background task to publish content to social media platform"""
    db = SessionLocal()
    try:
        # Prepare content data for publishing
        content_data = {
            "caption": content.caption,
            "content_type": content.content_type.value,
            "media_url": content.image_url or content.video_url
        }

        # Publish to platform
        result = await webhook_manager.post_to_platform(
            content.platform.value, content_data
        )

        if result.get("success"):
            # Update content status
            content.status = PostStatus.PUBLISHED
            content.published_time = datetime.utcnow()

            # Send success notification
            await notifier.send_post_published_notification(content, result)
        else:
            # Handle failure
            content.retry_count += 1
            content.error_message = result.get("error", "Unknown error")

            if content.retry_count >= 3:
                content.status = PostStatus.FAILED
                await notifier.send_post_failed_notification(content)

        db.commit()

    except Exception as e:
        logger.error(f"Error publishing content {content.id}: {e}")
        content.retry_count += 1
        content.error_message = str(e)

        if content.retry_count >= 3:
            content.status = PostStatus.FAILED
            await notifier.send_post_failed_notification(content)

        db.commit()
    finally:
        db.close()

async def schedule_content_publication(content: ContentPost):
    """Background task to schedule content for future publication"""
    # This would integrate with APScheduler or similar
    logger.info(f"Scheduled content {content.id} for publication at {content.scheduled_time}")

# Bulk Operations

@router.post("/content/bulk-action")
async def bulk_content_action(
    bulk_action: BulkAction,
    background_tasks: BackgroundTasks,
    current_user: User = RequirePermission.edit_content,
    db: Session = Depends(get_db),
    _audit: dict = Depends(audit_log("bulk_action", "content"))
):
    """Perform bulk action on multiple content items"""

    # Validate all content IDs belong to user's accessible brands
    content_items = []
    for content_id in bulk_action.content_ids:
        content = await validate_content_ownership(content_id, current_user, db)
        content_items.append(content)

    results = []

    for content in content_items:
        try:
            if bulk_action.action == "approve":
                if current_user.role not in ["admin", "manager"]:
                    results.append({"content_id": content.id, "success": False, "error": "Insufficient permissions"})
                    continue

                content.status = PostStatus.APPROVED
                if content.scheduled_time:
                    content.status = PostStatus.SCHEDULED
                    background_tasks.add_task(schedule_content_publication, content)

            elif bulk_action.action == "reject":
                if current_user.role not in ["admin", "manager"]:
                    results.append({"content_id": content.id, "success": False, "error": "Insufficient permissions"})
                    continue

                content.status = PostStatus.REJECTED

            elif bulk_action.action == "delete":
                if content.status == PostStatus.PUBLISHED:
                    results.append({"content_id": content.id, "success": False, "error": "Cannot delete published content"})
                    continue

                db.delete(content)

            elif bulk_action.action == "schedule":
                if not bulk_action.scheduled_time:
                    results.append({"content_id": content.id, "success": False, "error": "Scheduled time required"})
                    continue

                content.scheduled_time = bulk_action.scheduled_time
                if content.status == PostStatus.APPROVED:
                    content.status = PostStatus.SCHEDULED
                    background_tasks.add_task(schedule_content_publication, content)

            elif bulk_action.action == "publish":
                if content.status not in [PostStatus.APPROVED, PostStatus.SCHEDULED]:
                    results.append({"content_id": content.id, "success": False, "error": "Content must be approved"})
                    continue

                background_tasks.add_task(publish_content_to_platform, content)

            content.updated_at = datetime.utcnow()
            results.append({"content_id": content.id, "success": True})

        except Exception as e:
            results.append({"content_id": content.id, "success": False, "error": str(e)})

    db.commit()

    logger.info(f"Bulk action {bulk_action.action} performed on {len(bulk_action.content_ids)} items by user {current_user.id}")

    return {
        "action": bulk_action.action,
        "total_items": len(bulk_action.content_ids),
        "successful": len([r for r in results if r["success"]]),
        "failed": len([r for r in results if not r["success"]]),
        "results": results
    }

# Content Discovery & Scraping

@router.post("/content/scrape")
async def scrape_content(
    scraping_request: ScrapingRequest,
    background_tasks: BackgroundTasks,
    current_user: User = RequirePermission.view_brands,
    db: Session = Depends(get_db),
    _audit: dict = Depends(audit_log("scrape", "content"))
):
    """Scrape trending content for brand inspiration"""

    # Verify user has access to the brand
    brand = await verify_brand_access(scraping_request.brand_id, current_user, db)

    # Start background scraping task
    background_tasks.add_task(
        run_content_scraping,
        brand,
        scraping_request.keywords or brand.keywords,
        scraping_request.platforms,
        scraping_request.limit
    )

    return {
        "message": "Content scraping initiated",
        "brand_id": scraping_request.brand_id,
        "estimated_completion": "2-5 minutes"
    }

async def run_content_scraping(brand: Brand, keywords: List[str], platforms: List[str], limit: int):
    """Background task for content scraping"""
    try:
        result = await scraper.scrape_for_brand(brand)
        logger.info(f"Content scraping completed for brand {brand.id}: {result.get('total_scraped', 0)} items")
    except Exception as e:
        logger.error(f"Content scraping failed for brand {brand.id}: {e}")

@router.get("/content/scraped")
async def get_scraped_content(
    brand_id: int,
    pagination: PaginationParams = Depends(get_pagination_params),
    min_relevance: float = Query(70.0, ge=0.0, le=100.0),
    platform: Optional[str] = Query(None),
    current_user: User = RequirePermission.view_brands,
    db: Session = Depends(get_db)
):
    """Get scraped content for inspiration"""

    # Verify user has access to the brand
    await verify_brand_access(brand_id, current_user, db)

    query = db.query(ScrapedContent).filter(
        ScrapedContent.brand_id == brand_id,
        ScrapedContent.relevance_score >= min_relevance
    )

    if platform:
        query = query.filter(ScrapedContent.platform == platform)

    query = query.order_by(desc(ScrapedContent.relevance_score), desc(ScrapedContent.scraped_at))

    scraped_content = query.offset(pagination.skip).limit(pagination.limit).all()

    return scraped_content

# Analytics & Insights

@router.get("/content/analytics")
async def get_content_analytics(
    brand_id: Optional[int] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    platform: Optional[Platform] = Query(None),
    current_user: User = RequirePermission.view_analytics,
    db: Session = Depends(get_db)
):
    """Get content performance analytics"""

    query = db.query(ContentPost).filter(ContentPost.status == PostStatus.PUBLISHED)

    # Apply brand access filter
    from api.dependencies import get_brand_access_filter
    brand_filter = get_brand_access_filter(current_user)
    if brand_filter is not None:
        query = query.join(Brand).filter(brand_filter)

    if brand_id:
        await verify_brand_access(brand_id, current_user, db)
        query = query.filter(ContentPost.brand_id == brand_id)

    if platform:
        query = query.filter(ContentPost.platform == platform)

    if start_date:
        start = datetime.fromisoformat(start_date)
        query = query.filter(ContentPost.published_time >= start)

    if end_date:
        end = datetime.fromisoformat(end_date)
        query = query.filter(ContentPost.published_time <= end)

    posts = query.all()

    # Calculate analytics
    total_posts = len(posts)
    total_likes = sum(post.likes_count for post in posts)
    total_comments = sum(post.comments_count for post in posts)
    total_shares = sum(post.shares_count for post in posts)
    total_reach = sum(post.reach for post in posts)

    avg_engagement_rate = sum(post.actual_engagement_rate for post in posts) / total_posts if total_posts > 0 else 0

    # Platform breakdown
    platform_stats = {}
    for post in posts:
        platform_name = post.platform.value
        if platform_name not in platform_stats:
            platform_stats[platform_name] = {
                "posts": 0,
                "likes": 0,
                "comments": 0,
                "shares": 0,
                "reach": 0
            }

        platform_stats[platform_name]["posts"] += 1
        platform_stats[platform_name]["likes"] += post.likes_count
        platform_stats[platform_name]["comments"] += post.comments_count
        platform_stats[platform_name]["shares"] += post.shares_count
        platform_stats[platform_name]["reach"] += post.reach

    # Content type performance
    content_type_stats = {}
    for post in posts:
        content_type = post.content_type.value
        if content_type not in content_type_stats:
            content_type_stats[content_type] = {
                "posts": 0,
                "avg_engagement": 0,
                "total_engagement": 0
            }

        content_type_stats[content_type]["posts"] += 1
        content_type_stats[content_type]["total_engagement"] += post.actual_engagement_rate

    # Calculate averages
    for content_type in content_type_stats:
        posts_count = content_type_stats[content_type]["posts"]
        if posts_count > 0:
            content_type_stats[content_type]["avg_engagement"] = content_type_stats[content_type]["total_engagement"] / posts_count

    return {
        "summary": {
            "total_posts": total_posts,
            "total_likes": total_likes,
            "total_comments": total_comments,
            "total_shares": total_shares,
            "total_reach": total_reach,
            "avg_engagement_rate": round(avg_engagement_rate, 2)
        },
        "platform_breakdown": platform_stats,
        "content_type_performance": content_type_stats,
        "period": {
            "start_date": start_date,
            "end_date": end_date
        }
    }

@router.get("/content/queue-status")
async def get_queue_status(
    current_user: User = RequirePermission.view_brands,
    db: Session = Depends(get_db)
):
    """Get status of content queue"""

    # Apply brand access filter
    from api.dependencies import get_brand_access_filter
    brand_filter = get_brand_access_filter(current_user)

    query = db.query(ContentPost)
    if brand_filter is not None:
        query = query.join(Brand).filter(brand_filter)

    # Count by status
    status_counts = {}
    for status in PostStatus:
        count = query.filter(ContentPost.status == status).count()
        status_counts[status.value] = count

    # Upcoming scheduled posts
    upcoming_posts = query.filter(
        ContentPost.status == PostStatus.SCHEDULED,
        ContentPost.scheduled_time >= datetime.utcnow(),
        ContentPost.scheduled_time <= datetime.utcnow() + timedelta(days=7)
    ).order_by(ContentPost.scheduled_time).limit(10).all()

    # Pending approvals nearing deadline
    urgent_approvals = query.filter(
        ContentPost.status == PostStatus.PENDING_REVIEW,
        ContentPost.scheduled_time <= datetime.utcnow() + timedelta(hours=4)
    ).order_by(ContentPost.scheduled_time).all()

    return {
        "status_counts": status_counts,
        "upcoming_posts": len(upcoming_posts),
        "urgent_approvals": len(urgent_approvals),
        "next_scheduled": upcoming_posts[0].scheduled_time.isoformat() if upcoming_posts else None
    }
