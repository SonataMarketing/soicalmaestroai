"""
Scheduler Module - Orchestrates all automated tasks
Daily @ 6 AM: Content Scraping
Daily @ 8 AM & 4 PM: Content Generation
Hourly Check: Approval reminders
Weekly (Monday @ 9 AM): Brand Analysis and Performance Analysis
"""

import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session

from database.database import SessionLocal
from database.models import Brand, ScheduledTask, ContentPost, PostStatus
from modules.scraper import ContentScraper
from modules.brand_analyzer import BrandAnalyzer
from modules.generator import ContentGenerator
from modules.notifier import NotificationManager
from modules.publisher import ContentPublisher
from modules.reporter import PerformanceReporter

logger = logging.getLogger(__name__)

class TaskScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.scraper = ContentScraper()
        self.brand_analyzer = BrandAnalyzer()
        self.generator = ContentGenerator()
        self.notifier = NotificationManager()
        self.publisher = ContentPublisher()
        self.reporter = PerformanceReporter()

    def start(self):
        """Start the scheduler with all configured jobs"""
        try:
            # Daily content scraping at 6 AM
            self.scheduler.add_job(
                func=self._run_content_scraping,
                trigger=CronTrigger(hour=6, minute=0),
                id='daily_content_scraping',
                name='Daily Content Scraping',
                replace_existing=True
            )

            # Daily content generation at 8 AM and 4 PM
            self.scheduler.add_job(
                func=self._run_content_generation,
                trigger=CronTrigger(hour=8, minute=0),
                id='morning_content_generation',
                name='Morning Content Generation',
                replace_existing=True
            )

            self.scheduler.add_job(
                func=self._run_content_generation,
                trigger=CronTrigger(hour=16, minute=0),
                id='evening_content_generation',
                name='Evening Content Generation',
                replace_existing=True
            )

            # Hourly approval reminder checks
            self.scheduler.add_job(
                func=self._check_approval_reminders,
                trigger=IntervalTrigger(hours=1),
                id='approval_reminders',
                name='Approval Reminder Checks',
                replace_existing=True
            )

            # Weekly brand analysis (Monday at 9 AM)
            self.scheduler.add_job(
                func=self._run_brand_analysis,
                trigger=CronTrigger(day_of_week='mon', hour=9, minute=0),
                id='weekly_brand_analysis',
                name='Weekly Brand Analysis',
                replace_existing=True
            )

            # Weekly performance analysis (Monday at 9 AM)
            self.scheduler.add_job(
                func=self._run_performance_analysis,
                trigger=CronTrigger(day_of_week='mon', hour=9, minute=30),
                id='weekly_performance_analysis',
                name='Weekly Performance Analysis',
                replace_existing=True
            )

            # Automated publishing check (every 15 minutes)
            self.scheduler.add_job(
                func=self._check_scheduled_posts,
                trigger=IntervalTrigger(minutes=15),
                id='scheduled_post_check',
                name='Scheduled Post Publishing Check',
                replace_existing=True
            )

            # Retry failed posts (every 2 hours)
            self.scheduler.add_job(
                func=self._retry_failed_posts,
                trigger=IntervalTrigger(hours=2),
                id='retry_failed_posts',
                name='Retry Failed Posts',
                replace_existing=True
            )

            self.scheduler.start()
            logger.info("Task scheduler started successfully")

        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
            raise

    def stop(self):
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Task scheduler stopped")

    async def _run_content_scraping(self):
        """Run content scraping for all active brands"""
        logger.info("Starting daily content scraping")

        db = SessionLocal()
        try:
            brands = db.query(Brand).all()

            for brand in brands:
                try:
                    # Create scheduled task record
                    task = ScheduledTask(
                        task_name="content_scraping",
                        task_type="scraping",
                        brand_id=brand.id,
                        scheduled_time=datetime.utcnow(),
                        status="running",
                        parameters={"brand_keywords": brand.keywords}
                    )
                    db.add(task)
                    db.commit()

                    # Run scraping
                    result = await self.scraper.scrape_for_brand(brand)

                    # Update task status
                    task.status = "completed"
                    task.completed_at = datetime.utcnow()
                    task.result_data = result
                    db.commit()

                    logger.info(f"Content scraping completed for brand {brand.name}")

                except Exception as e:
                    logger.error(f"Content scraping failed for brand {brand.name}: {e}")
                    task.status = "failed"
                    task.error_message = str(e)
                    task.completed_at = datetime.utcnow()
                    db.commit()

        finally:
            db.close()

    async def _run_content_generation(self):
        """Run content generation for all active brands"""
        logger.info("Starting content generation")

        db = SessionLocal()
        try:
            brands = db.query(Brand).all()

            for brand in brands:
                if not brand.auto_posting:
                    continue

                try:
                    # Create scheduled task record
                    task = ScheduledTask(
                        task_name="content_generation",
                        task_type="generation",
                        brand_id=brand.id,
                        scheduled_time=datetime.utcnow(),
                        status="running"
                    )
                    db.add(task)
                    db.commit()

                    # Generate content
                    result = await self.generator.generate_daily_content(brand)

                    # Update task status
                    task.status = "completed"
                    task.completed_at = datetime.utcnow()
                    task.result_data = result
                    db.commit()

                    logger.info(f"Content generation completed for brand {brand.name}")

                except Exception as e:
                    logger.error(f"Content generation failed for brand {brand.name}: {e}")
                    task.status = "failed"
                    task.error_message = str(e)
                    task.completed_at = datetime.utcnow()
                    db.commit()

        finally:
            db.close()

    async def _check_approval_reminders(self):
        """Check for posts that need approval reminders"""
        logger.info("Checking for approval reminders")

        db = SessionLocal()
        try:
            # Find posts pending review that are nearing their scheduled time
            upcoming_posts = db.query(ContentPost).filter(
                ContentPost.status == PostStatus.PENDING_REVIEW,
                ContentPost.scheduled_time <= datetime.utcnow() + timedelta(hours=4),
                ContentPost.scheduled_time > datetime.utcnow()
            ).all()

            for post in upcoming_posts:
                await self.notifier.send_approval_reminder(post)
                logger.info(f"Sent approval reminder for post {post.id}")

        except Exception as e:
            logger.error(f"Failed to check approval reminders: {e}")

        finally:
            db.close()

    async def _run_brand_analysis(self):
        """Run weekly brand analysis for all brands"""
        logger.info("Starting weekly brand analysis")

        db = SessionLocal()
        try:
            brands = db.query(Brand).all()

            for brand in brands:
                try:
                    task = ScheduledTask(
                        task_name="brand_analysis",
                        task_type="analysis",
                        brand_id=brand.id,
                        scheduled_time=datetime.utcnow(),
                        status="running"
                    )
                    db.add(task)
                    db.commit()

                    # Run brand analysis
                    result = await self.brand_analyzer.analyze_brand_weekly(brand)

                    task.status = "completed"
                    task.completed_at = datetime.utcnow()
                    task.result_data = result
                    db.commit()

                    logger.info(f"Brand analysis completed for {brand.name}")

                except Exception as e:
                    logger.error(f"Brand analysis failed for {brand.name}: {e}")
                    task.status = "failed"
                    task.error_message = str(e)
                    task.completed_at = datetime.utcnow()
                    db.commit()

        finally:
            db.close()

    async def _run_performance_analysis(self):
        """Run weekly performance analysis for all brands"""
        logger.info("Starting weekly performance analysis")

        db = SessionLocal()
        try:
            brands = db.query(Brand).all()

            for brand in brands:
                try:
                    task = ScheduledTask(
                        task_name="performance_analysis",
                        task_type="analysis",
                        brand_id=brand.id,
                        scheduled_time=datetime.utcnow(),
                        status="running"
                    )
                    db.add(task)
                    db.commit()

                    # Run performance analysis
                    result = await self.reporter.generate_weekly_report(brand)

                    task.status = "completed"
                    task.completed_at = datetime.utcnow()
                    task.result_data = result
                    db.commit()

                    logger.info(f"Performance analysis completed for {brand.name}")

                except Exception as e:
                    logger.error(f"Performance analysis failed for {brand.name}: {e}")
                    task.status = "failed"
                    task.error_message = str(e)
                    task.completed_at = datetime.utcnow()
                    db.commit()

        finally:
            db.close()

    async def _check_scheduled_posts(self):
        """Check for posts that are scheduled to be published now"""
        logger.info("Checking for scheduled posts to publish")

        db = SessionLocal()
        try:
            # Find posts scheduled for now (within 15-minute window)
            now = datetime.utcnow()
            posts_to_publish = db.query(ContentPost).filter(
                ContentPost.status == PostStatus.SCHEDULED,
                ContentPost.scheduled_time <= now,
                ContentPost.scheduled_time >= now - timedelta(minutes=15)
            ).all()

            for post in posts_to_publish:
                try:
                    # Attempt to publish
                    success = await self.publisher.publish_post(post)

                    if success:
                        post.status = PostStatus.PUBLISHED
                        post.published_time = datetime.utcnow()
                        logger.info(f"Successfully published post {post.id}")
                    else:
                        post.retry_count += 1
                        if post.retry_count >= 3:
                            post.status = PostStatus.FAILED
                            await self.notifier.send_post_failed_notification(post)
                        logger.warning(f"Failed to publish post {post.id}, retry count: {post.retry_count}")

                    db.commit()

                except Exception as e:
                    logger.error(f"Error publishing post {post.id}: {e}")
                    post.retry_count += 1
                    post.error_message = str(e)
                    if post.retry_count >= 3:
                        post.status = PostStatus.FAILED
                        await self.notifier.send_post_failed_notification(post)
                    db.commit()

        finally:
            db.close()

    async def _retry_failed_posts(self):
        """Retry failed posts (up to 3 attempts)"""
        logger.info("Retrying failed posts")

        db = SessionLocal()
        try:
            # Find recently failed posts that haven't exceeded retry limit
            failed_posts = db.query(ContentPost).filter(
                ContentPost.status == PostStatus.FAILED,
                ContentPost.retry_count < 3,
                ContentPost.updated_at >= datetime.utcnow() - timedelta(hours=24)
            ).all()

            for post in failed_posts:
                try:
                    success = await self.publisher.publish_post(post)

                    if success:
                        post.status = PostStatus.PUBLISHED
                        post.published_time = datetime.utcnow()
                        logger.info(f"Successfully republished post {post.id}")
                    else:
                        post.retry_count += 1
                        logger.warning(f"Retry failed for post {post.id}, retry count: {post.retry_count}")

                    db.commit()

                except Exception as e:
                    logger.error(f"Error retrying post {post.id}: {e}")
                    post.retry_count += 1
                    post.error_message = str(e)
                    db.commit()

        finally:
            db.close()

# Global scheduler instance
_scheduler = None

def start_scheduler():
    """Start the global scheduler instance"""
    global _scheduler
    if _scheduler is None:
        _scheduler = TaskScheduler()
        _scheduler.start()
        logger.info("Global scheduler started")

def get_scheduler():
    """Get the global scheduler instance"""
    return _scheduler

def stop_scheduler():
    """Stop the global scheduler instance"""
    global _scheduler
    if _scheduler:
        _scheduler.stop()
        _scheduler = None
        logger.info("Global scheduler stopped")
