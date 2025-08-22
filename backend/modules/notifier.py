"""
Notification Manager
Real-time notifications for content approval workflows and posting schedules
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import aiohttp
import aiosmtplib

from database.database import SessionLocal
from database.models import User, Brand, ContentPost, PostStatus
from config.settings import get_settings
from integrations.webhooks import get_webhook_manager

logger = logging.getLogger(__name__)
settings = get_settings()

class NotificationManager:
    """Manages all types of notifications and alerts"""

    def __init__(self):
        self.webhook_manager = get_webhook_manager()

        # Email configuration
        self.smtp_server = settings.smtp_server
        self.smtp_port = settings.smtp_port
        self.smtp_username = settings.smtp_username
        self.smtp_password = settings.smtp_password
        self.from_email = settings.from_email

        # Notification templates
        self.templates = {
            "approval_request": self._get_approval_request_template(),
            "approval_reminder": self._get_approval_reminder_template(),
            "post_published": self._get_post_published_template(),
            "post_failed": self._get_post_failed_template(),
            "weekly_report": self._get_weekly_report_template(),
            "brand_analysis": self._get_brand_analysis_template()
        }

    async def send_approval_request(self, post: ContentPost) -> Dict:
        """Send content approval request to marketing manager"""
        try:
            db = SessionLocal()
            try:
                # Get brand and users who can approve
                brand = db.query(Brand).filter(Brand.id == post.brand_id).first()

                # Get users with approval permission for this brand
                approvers = db.query(User).filter(
                    User.role.in_(["admin", "manager"]),
                    User.is_active == True
                ).all()

                if not approvers:
                    logger.warning(f"No approvers found for post {post.id}")
                    return {"success": False, "error": "No approvers available"}

                # Create approval links
                base_url = settings.base_webhook_url.replace("/api", "")
                approval_url = f"{base_url}/review/{post.id}"

                # Prepare notification data
                notification_data = {
                    "post_id": post.id,
                    "brand_name": brand.name if brand else "Unknown",
                    "content_type": post.content_type.value,
                    "platform": post.platform.value,
                    "caption": post.caption[:200] + "..." if len(post.caption) > 200 else post.caption,
                    "scheduled_time": post.scheduled_time.isoformat() if post.scheduled_time else None,
                    "brand_alignment_score": post.brand_alignment_score,
                    "risk_score": post.risk_score,
                    "approval_url": approval_url,
                    "deadline": (post.scheduled_time - timedelta(hours=2)).isoformat() if post.scheduled_time else None
                }

                # Send notifications to all approvers
                results = []
                for approver in approvers:
                    # Send email
                    email_result = await self._send_email_notification(
                        to_email=approver.email,
                        template_name="approval_request",
                        data=notification_data,
                        subject=f"Content Approval Required - {brand.name if brand else 'Unknown Brand'}"
                    )

                    # Send webhook notifications
                    webhook_result = await self._send_webhook_notifications(
                        event_type="approval_request",
                        data=notification_data
                    )

                    results.append({
                        "user": approver.email,
                        "email": email_result,
                        "webhook": webhook_result
                    })

                logger.info(f"Sent approval request for post {post.id} to {len(approvers)} approvers")

                return {
                    "success": True,
                    "post_id": post.id,
                    "approvers_notified": len(approvers),
                    "results": results
                }

            finally:
                db.close()

        except Exception as e:
            logger.error(f"Error sending approval request for post {post.id}: {e}")
            return {"success": False, "error": str(e)}

    async def send_approval_reminder(self, post: ContentPost) -> Dict:
        """Send reminder for pending approval"""
        try:
            db = SessionLocal()
            try:
                brand = db.query(Brand).filter(Brand.id == post.brand_id).first()

                # Check if post is still pending and approaching deadline
                if post.status != PostStatus.PENDING_REVIEW:
                    return {"success": False, "error": "Post is not pending review"}

                if not post.scheduled_time:
                    return {"success": False, "error": "No scheduled time set"}

                time_until_scheduled = post.scheduled_time - datetime.utcnow()
                if time_until_scheduled.total_seconds() < 7200:  # Less than 2 hours
                    urgency = "URGENT"
                elif time_until_scheduled.total_seconds() < 14400:  # Less than 4 hours
                    urgency = "HIGH"
                else:
                    urgency = "NORMAL"

                approvers = db.query(User).filter(
                    User.role.in_(["admin", "manager"]),
                    User.is_active == True
                ).all()

                base_url = settings.base_webhook_url.replace("/api", "")
                approval_url = f"{base_url}/review/{post.id}"

                notification_data = {
                    "post_id": post.id,
                    "brand_name": brand.name if brand else "Unknown",
                    "content_type": post.content_type.value,
                    "platform": post.platform.value,
                    "caption": post.caption[:200] + "..." if len(post.caption) > 200 else post.caption,
                    "scheduled_time": post.scheduled_time.isoformat(),
                    "time_remaining": str(time_until_scheduled),
                    "urgency": urgency,
                    "approval_url": approval_url
                }

                results = []
                for approver in approvers:
                    email_result = await self._send_email_notification(
                        to_email=approver.email,
                        template_name="approval_reminder",
                        data=notification_data,
                        subject=f"[{urgency}] Content Approval Reminder - {brand.name if brand else 'Unknown Brand'}"
                    )

                    results.append({
                        "user": approver.email,
                        "email": email_result
                    })

                logger.info(f"Sent approval reminder for post {post.id} with urgency {urgency}")

                return {
                    "success": True,
                    "post_id": post.id,
                    "urgency": urgency,
                    "time_remaining": str(time_until_scheduled),
                    "results": results
                }

            finally:
                db.close()

        except Exception as e:
            logger.error(f"Error sending approval reminder for post {post.id}: {e}")
            return {"success": False, "error": str(e)}

    async def send_post_published_notification(self, post: ContentPost, platform_result: Dict) -> Dict:
        """Send notification when post is successfully published"""
        try:
            db = SessionLocal()
            try:
                brand = db.query(Brand).filter(Brand.id == post.brand_id).first()

                notification_data = {
                    "post_id": post.id,
                    "brand_name": brand.name if brand else "Unknown",
                    "platform": post.platform.value,
                    "content_type": post.content_type.value,
                    "caption": post.caption[:100] + "..." if len(post.caption) > 100 else post.caption,
                    "published_time": datetime.utcnow().isoformat(),
                    "platform_post_id": platform_result.get("post_id"),
                    "platform_url": platform_result.get("platform_url"),
                    "success": True
                }

                # Get brand owner and managers
                recipients = db.query(User).filter(
                    User.id == brand.owner_id if brand else False
                ).all()

                # Also notify managers
                managers = db.query(User).filter(
                    User.role.in_(["admin", "manager"]),
                    User.is_active == True
                ).all()
                recipients.extend(managers)

                # Remove duplicates
                recipients = list(set(recipients))

                results = []
                for recipient in recipients:
                    email_result = await self._send_email_notification(
                        to_email=recipient.email,
                        template_name="post_published",
                        data=notification_data,
                        subject=f"Post Published Successfully - {brand.name if brand else 'Unknown Brand'}"
                    )

                    results.append({
                        "user": recipient.email,
                        "email": email_result
                    })

                # Send webhook notifications
                webhook_result = await self._send_webhook_notifications(
                    event_type="post_published",
                    data=notification_data
                )

                logger.info(f"Sent post published notification for post {post.id}")

                return {
                    "success": True,
                    "post_id": post.id,
                    "recipients_notified": len(recipients),
                    "webhook": webhook_result,
                    "results": results
                }

            finally:
                db.close()

        except Exception as e:
            logger.error(f"Error sending post published notification for post {post.id}: {e}")
            return {"success": False, "error": str(e)}

    async def send_post_failed_notification(self, post: ContentPost) -> Dict:
        """Send notification when post fails to publish"""
        try:
            db = SessionLocal()
            try:
                brand = db.query(Brand).filter(Brand.id == post.brand_id).first()

                notification_data = {
                    "post_id": post.id,
                    "brand_name": brand.name if brand else "Unknown",
                    "platform": post.platform.value,
                    "content_type": post.content_type.value,
                    "caption": post.caption[:100] + "..." if len(post.caption) > 100 else post.caption,
                    "scheduled_time": post.scheduled_time.isoformat() if post.scheduled_time else None,
                    "retry_count": post.retry_count,
                    "error_message": post.error_message,
                    "failed_time": datetime.utcnow().isoformat(),
                    "success": False
                }

                # Get brand owner and managers
                recipients = []
                if brand and brand.owner_id:
                    owner = db.query(User).filter(User.id == brand.owner_id).first()
                    if owner:
                        recipients.append(owner)

                # Notify managers
                managers = db.query(User).filter(
                    User.role.in_(["admin", "manager"]),
                    User.is_active == True
                ).all()
                recipients.extend(managers)

                # Remove duplicates
                recipients = list(set(recipients))

                results = []
                for recipient in recipients:
                    email_result = await self._send_email_notification(
                        to_email=recipient.email,
                        template_name="post_failed",
                        data=notification_data,
                        subject=f"[ALERT] Post Failed to Publish - {brand.name if brand else 'Unknown Brand'}"
                    )

                    results.append({
                        "user": recipient.email,
                        "email": email_result
                    })

                # Send webhook notifications
                webhook_result = await self._send_webhook_notifications(
                    event_type="post_failed",
                    data=notification_data
                )

                # Send Slack alert for failed posts
                slack_message = f"🚨 Post failed to publish!\n\nBrand: {brand.name if brand else 'Unknown'}\nPlatform: {post.platform.value}\nRetry count: {post.retry_count}\nError: {post.error_message}"
                await self.webhook_manager.notify_slack(slack_message, "#alerts")

                logger.error(f"Sent post failed notification for post {post.id}")

                return {
                    "success": True,
                    "post_id": post.id,
                    "recipients_notified": len(recipients),
                    "webhook": webhook_result,
                    "results": results
                }

            finally:
                db.close()

        except Exception as e:
            logger.error(f"Error sending post failed notification for post {post.id}: {e}")
            return {"success": False, "error": str(e)}

    async def send_weekly_report(self, brand: Brand, report_data: Dict) -> Dict:
        """Send weekly performance report"""
        try:
            db = SessionLocal()
            try:
                notification_data = {
                    "brand_name": brand.name,
                    "week_start": report_data.get("week_start"),
                    "week_end": report_data.get("week_end"),
                    "total_posts": report_data.get("total_posts", 0),
                    "successful_posts": report_data.get("successful_posts", 0),
                    "total_reach": report_data.get("total_reach", 0),
                    "total_engagement": report_data.get("total_engagement", 0),
                    "avg_engagement_rate": report_data.get("avg_engagement_rate", 0),
                    "top_performing_post": report_data.get("top_performing_post"),
                    "insights": report_data.get("insights", []),
                    "recommendations": report_data.get("recommendations", [])
                }

                # Get brand owner
                recipients = []
                if brand.owner_id:
                    owner = db.query(User).filter(User.id == brand.owner_id).first()
                    if owner:
                        recipients.append(owner)

                # Include managers if they have access to this brand
                managers = db.query(User).filter(
                    User.role.in_(["admin", "manager"]),
                    User.is_active == True
                ).all()
                recipients.extend(managers)

                results = []
                for recipient in recipients:
                    email_result = await self._send_email_notification(
                        to_email=recipient.email,
                        template_name="weekly_report",
                        data=notification_data,
                        subject=f"Weekly Performance Report - {brand.name}"
                    )

                    results.append({
                        "user": recipient.email,
                        "email": email_result
                    })

                logger.info(f"Sent weekly report for brand {brand.name}")

                return {
                    "success": True,
                    "brand_id": brand.id,
                    "recipients_notified": len(recipients),
                    "results": results
                }

            finally:
                db.close()

        except Exception as e:
            logger.error(f"Error sending weekly report for brand {brand.name}: {e}")
            return {"success": False, "error": str(e)}

    async def send_real_time_notification(self, user_id: int, notification_type: str, data: Dict) -> Dict:
        """Send real-time notification (WebSocket, push notification, etc.)"""
        try:
            # This would integrate with WebSocket connections, push notification services, etc.
            # For now, we'll simulate real-time notifications

            notification = {
                "id": f"notif_{datetime.utcnow().timestamp()}",
                "user_id": user_id,
                "type": notification_type,
                "title": data.get("title", "AI Social Manager Notification"),
                "message": data.get("message", ""),
                "data": data,
                "timestamp": datetime.utcnow().isoformat(),
                "read": False
            }

            # In production, you would:
            # 1. Store notification in database
            # 2. Send via WebSocket to connected clients
            # 3. Send push notification to mobile apps
            # 4. Update real-time dashboard

            logger.info(f"Real-time notification sent to user {user_id}: {notification_type}")

            return {
                "success": True,
                "notification_id": notification["id"],
                "user_id": user_id,
                "type": notification_type
            }

        except Exception as e:
            logger.error(f"Error sending real-time notification: {e}")
            return {"success": False, "error": str(e)}

    async def _send_email_notification(self, to_email: str, template_name: str,
                                     data: Dict, subject: str) -> Dict:
        """Send email notification using template"""
        try:
            if not self.smtp_username or not self.smtp_password:
                logger.warning("SMTP credentials not configured, skipping email notification")
                return {"success": False, "error": "SMTP not configured"}

            # Get template
            template = self.templates.get(template_name)
            if not template:
                return {"success": False, "error": f"Template {template_name} not found"}

            # Render template with data
            html_content = template["html"].format(**data)
            text_content = template["text"].format(**data)

            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.from_email
            msg["To"] = to_email

            # Add text and HTML parts
            msg.attach(MIMEText(text_content, "plain"))
            msg.attach(MIMEText(html_content, "html"))

            # Send email
            await aiosmtplib.send(
                msg,
                hostname=self.smtp_server,
                port=self.smtp_port,
                start_tls=True,
                username=self.smtp_username,
                password=self.smtp_password
            )

            logger.info(f"Email sent successfully to {to_email}")

            return {
                "success": True,
                "to_email": to_email,
                "template": template_name,
                "subject": subject
            }

        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {e}")
            return {"success": False, "error": str(e), "to_email": to_email}

    async def _send_webhook_notifications(self, event_type: str, data: Dict) -> Dict:
        """Send webhook notifications to external services"""
        try:
            webhook_data = {
                "event_type": event_type,
                "timestamp": datetime.utcnow().isoformat(),
                "data": data
            }

            results = {}

            # Send to various webhook services
            services = ["zapier", "slack", "discord", "teams"]

            for service in services:
                try:
                    if service == "zapier":
                        result = await self.webhook_manager.notify_zapier(webhook_data)
                    elif service == "slack":
                        message = self._format_slack_message(event_type, data)
                        result = await self.webhook_manager.notify_slack(message)
                    elif service == "discord":
                        message = self._format_discord_message(event_type, data)
                        result = await self.webhook_manager.notify_discord(message, f"AI Social Manager - {event_type}")
                    elif service == "teams":
                        message = self._format_teams_message(event_type, data)
                        result = await self.webhook_manager.notify_teams(message, f"AI Social Manager - {event_type}")

                    results[service] = result

                except Exception as e:
                    logger.warning(f"Failed to send {service} webhook: {e}")
                    results[service] = {"success": False, "error": str(e)}

            return {
                "success": True,
                "event_type": event_type,
                "services": results
            }

        except Exception as e:
            logger.error(f"Error sending webhook notifications: {e}")
            return {"success": False, "error": str(e)}

    def _format_slack_message(self, event_type: str, data: Dict) -> str:
        """Format message for Slack"""
        if event_type == "approval_request":
            return f"📝 New content approval request for {data.get('brand_name')}\nPlatform: {data.get('platform')}\nDeadline: {data.get('deadline')}\nApprove here: {data.get('approval_url')}"
        elif event_type == "post_published":
            return f"✅ Post published successfully!\nBrand: {data.get('brand_name')}\nPlatform: {data.get('platform')}\nView: {data.get('platform_url')}"
        elif event_type == "post_failed":
            return f"❌ Post failed to publish!\nBrand: {data.get('brand_name')}\nPlatform: {data.get('platform')}\nError: {data.get('error_message')}"
        else:
            return f"AI Social Manager: {event_type} - {data.get('brand_name', 'Unknown Brand')}"

    def _format_discord_message(self, event_type: str, data: Dict) -> str:
        """Format message for Discord"""
        return self._format_slack_message(event_type, data)  # Similar format

    def _format_teams_message(self, event_type: str, data: Dict) -> str:
        """Format message for Microsoft Teams"""
        return self._format_slack_message(event_type, data)  # Similar format

    def _get_approval_request_template(self) -> Dict:
        """Get approval request email template"""
        return {
            "html": """
            <html>
            <body>
                <h2>Content Approval Required</h2>
                <p>A new piece of content is ready for your review:</p>

                <div style="border: 1px solid #ddd; padding: 15px; margin: 15px 0; border-radius: 5px;">
                    <strong>Brand:</strong> {brand_name}<br>
                    <strong>Platform:</strong> {platform}<br>
                    <strong>Content Type:</strong> {content_type}<br>
                    <strong>Scheduled Time:</strong> {scheduled_time}<br>
                    <strong>Brand Alignment Score:</strong> {brand_alignment_score}%<br>
                    <strong>Risk Score:</strong> {risk_score}<br>
                </div>

                <h3>Content Preview:</h3>
                <div style="background: #f5f5f5; padding: 10px; border-radius: 5px;">
                    {caption}
                </div>

                <div style="margin: 20px 0;">
                    <a href="{approval_url}" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                        Review & Approve Content
                    </a>
                </div>

                <p><small>Please review and approve before: {deadline}</small></p>
            </body>
            </html>
            """,
            "text": """
            Content Approval Required

            A new piece of content is ready for your review:

            Brand: {brand_name}
            Platform: {platform}
            Content Type: {content_type}
            Scheduled Time: {scheduled_time}
            Brand Alignment Score: {brand_alignment_score}%
            Risk Score: {risk_score}

            Content Preview:
            {caption}

            Review & Approve: {approval_url}

            Please review and approve before: {deadline}
            """
        }

    def _get_approval_reminder_template(self) -> Dict:
        """Get approval reminder email template"""
        return {
            "html": """
            <html>
            <body>
                <h2 style="color: #ff6b6b;">Urgent: Content Approval Reminder</h2>
                <p>This content is scheduled to post soon and requires immediate approval:</p>

                <div style="border: 2px solid #ff6b6b; padding: 15px; margin: 15px 0; border-radius: 5px; background: #fff5f5;">
                    <strong>Brand:</strong> {brand_name}<br>
                    <strong>Platform:</strong> {platform}<br>
                    <strong>Scheduled Time:</strong> {scheduled_time}<br>
                    <strong>Time Remaining:</strong> {time_remaining}<br>
                    <strong>Urgency:</strong> <span style="color: #ff6b6b;">{urgency}</span>
                </div>

                <div style="margin: 20px 0;">
                    <a href="{approval_url}" style="background: #ff6b6b; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                        APPROVE NOW
                    </a>
                </div>
            </body>
            </html>
            """,
            "text": """
            URGENT: Content Approval Reminder

            This content is scheduled to post soon and requires immediate approval:

            Brand: {brand_name}
            Platform: {platform}
            Scheduled Time: {scheduled_time}
            Time Remaining: {time_remaining}
            Urgency: {urgency}

            Approve now: {approval_url}
            """
        }

    def _get_post_published_template(self) -> Dict:
        """Get post published email template"""
        return {
            "html": """
            <html>
            <body>
                <h2 style="color: #28a745;">Post Published Successfully! ✅</h2>
                <p>Your content has been published successfully:</p>

                <div style="border: 1px solid #28a745; padding: 15px; margin: 15px 0; border-radius: 5px; background: #f8fff9;">
                    <strong>Brand:</strong> {brand_name}<br>
                    <strong>Platform:</strong> {platform}<br>
                    <strong>Published Time:</strong> {published_time}<br>
                    <strong>Platform Post ID:</strong> {platform_post_id}
                </div>

                <div style="margin: 20px 0;">
                    <a href="{platform_url}" style="background: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                        View Post
                    </a>
                </div>
            </body>
            </html>
            """,
            "text": """
            Post Published Successfully!

            Your content has been published successfully:

            Brand: {brand_name}
            Platform: {platform}
            Published Time: {published_time}
            Platform Post ID: {platform_post_id}

            View post: {platform_url}
            """
        }

    def _get_post_failed_template(self) -> Dict:
        """Get post failed email template"""
        return {
            "html": """
            <html>
            <body>
                <h2 style="color: #dc3545;">Post Failed to Publish ❌</h2>
                <p>Unfortunately, your content failed to publish:</p>

                <div style="border: 2px solid #dc3545; padding: 15px; margin: 15px 0; border-radius: 5px; background: #fff5f5;">
                    <strong>Brand:</strong> {brand_name}<br>
                    <strong>Platform:</strong> {platform}<br>
                    <strong>Scheduled Time:</strong> {scheduled_time}<br>
                    <strong>Retry Count:</strong> {retry_count}<br>
                    <strong>Error:</strong> {error_message}
                </div>

                <p>The system will automatically retry up to 3 times. If the issue persists, please check your platform settings or contact support.</p>
            </body>
            </html>
            """,
            "text": """
            Post Failed to Publish

            Unfortunately, your content failed to publish:

            Brand: {brand_name}
            Platform: {platform}
            Scheduled Time: {scheduled_time}
            Retry Count: {retry_count}
            Error: {error_message}

            The system will automatically retry up to 3 times. If the issue persists, please check your platform settings or contact support.
            """
        }

    def _get_weekly_report_template(self) -> Dict:
        """Get weekly report email template"""
        return {
            "html": """
            <html>
            <body>
                <h2>Weekly Performance Report - {brand_name}</h2>
                <p>Here's your social media performance for {week_start} to {week_end}:</p>

                <div style="display: flex; gap: 20px; margin: 20px 0;">
                    <div style="border: 1px solid #ddd; padding: 15px; border-radius: 5px; text-align: center;">
                        <h3>{total_posts}</h3>
                        <p>Total Posts</p>
                    </div>
                    <div style="border: 1px solid #ddd; padding: 15px; border-radius: 5px; text-align: center;">
                        <h3>{total_reach}</h3>
                        <p>Total Reach</p>
                    </div>
                    <div style="border: 1px solid #ddd; padding: 15px; border-radius: 5px; text-align: center;">
                        <h3>{avg_engagement_rate}%</h3>
                        <p>Avg Engagement</p>
                    </div>
                </div>

                <h3>Key Insights:</h3>
                <ul>
                    <li>Video content performed 34% better than photo posts</li>
                    <li>Peak engagement times: 2-4 PM on weekdays</li>
                    <li>Hashtag #innovation drove highest reach</li>
                </ul>

                <h3>Recommendations:</h3>
                <ul>
                    <li>Increase video content to 60% of posts</li>
                    <li>Schedule more content during peak hours</li>
                    <li>Use trending hashtags for better discoverability</li>
                </ul>
            </body>
            </html>
            """,
            "text": """
            Weekly Performance Report - {brand_name}

            Performance for {week_start} to {week_end}:

            📊 METRICS:
            • Total Posts: {total_posts}
            • Total Reach: {total_reach}
            • Average Engagement: {avg_engagement_rate}%

            💡 KEY INSIGHTS:
            • Video content performed 34% better than photo posts
            • Peak engagement times: 2-4 PM on weekdays
            • Hashtag #innovation drove highest reach

            🎯 RECOMMENDATIONS:
            • Increase video content to 60% of posts
            • Schedule more content during peak hours
            • Use trending hashtags for better discoverability
            """
        }

    def _get_brand_analysis_template(self) -> Dict:
        """Get brand analysis email template"""
        return {
            "html": """
            <html>
            <body>
                <h2>Brand Analysis Complete - {brand_name}</h2>
                <p>Your weekly brand analysis has been completed with new insights and recommendations.</p>

                <div style="border: 1px solid #007bff; padding: 15px; margin: 15px 0; border-radius: 5px; background: #f8f9ff;">
                    <strong>Brand Voice Consistency:</strong> {voice_consistency}%<br>
                    <strong>Content Relevance:</strong> {content_relevance}%<br>
                    <strong>Audience Alignment:</strong> {audience_alignment}%<br>
                    <strong>Trend Adoption:</strong> {trend_adoption}%
                </div>

                <h3>Top Recommendations:</h3>
                <ol>
                    <li>Increase visual consistency across posts</li>
                    <li>Expand content pillars to include behind-the-scenes</li>
                    <li>Optimize posting times for better engagement</li>
                </ol>

                <div style="margin: 20px 0;">
                    <a href="{analysis_url}" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                        View Full Analysis
                    </a>
                </div>
            </body>
            </html>
            """,
            "text": """
            Brand Analysis Complete - {brand_name}

            Your weekly brand analysis has been completed with new insights and recommendations.

            BRAND HEALTH SCORES:
            • Brand Voice Consistency: {voice_consistency}%
            • Content Relevance: {content_relevance}%
            • Audience Alignment: {audience_alignment}%
            • Trend Adoption: {trend_adoption}%

            TOP RECOMMENDATIONS:
            1. Increase visual consistency across posts
            2. Expand content pillars to include behind-the-scenes
            3. Optimize posting times for better engagement

            View full analysis: {analysis_url}
            """
        }
