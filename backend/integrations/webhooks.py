"""
Webhook Integrations
Automatic posting to social media platforms via webhooks and API integrations
"""

import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
import aiohttp
import json
from urllib.parse import urlencode

from config.settings import get_settings
from integrations.instagram import InstagramAPI
from integrations.twitter import TwitterAPI
from integrations.linkedin import LinkedInAPI
from integrations.facebook import FacebookAPI

logger = logging.getLogger(__name__)
settings = get_settings()

class WebhookManager:
    """Manages webhook integrations for social media posting"""

    def __init__(self):
        # Initialize social media APIs
        self.instagram = InstagramAPI()
        self.twitter = TwitterAPI()
        self.linkedin = LinkedInAPI()
        self.facebook = FacebookAPI()

        # Webhook endpoints
        self.webhook_endpoints = {
            "zapier": settings.base_webhook_url + "/zapier",
            "ifttt": settings.base_webhook_url + "/ifttt",
            "buffer": settings.base_webhook_url + "/buffer",
            "hootsuite": settings.base_webhook_url + "/hootsuite",
            "custom": settings.base_webhook_url + "/custom"
        }

    async def post_to_platform(self, platform: str, content_data: Dict) -> Dict:
        """Post content to specified social media platform"""
        try:
            platform = platform.lower()

            if platform == "instagram":
                return await self._post_to_instagram(content_data)
            elif platform == "twitter":
                return await self._post_to_twitter(content_data)
            elif platform == "linkedin":
                return await self._post_to_linkedin(content_data)
            elif platform == "facebook":
                return await self._post_to_facebook(content_data)
            else:
                return {"error": f"Unsupported platform: {platform}", "success": False}

        except Exception as e:
            logger.error(f"Error posting to {platform}: {e}")
            return {"error": str(e), "success": False}

    async def _post_to_instagram(self, content_data: Dict) -> Dict:
        """Post content to Instagram"""
        try:
            if not self.instagram.is_configured():
                return {"error": "Instagram not configured", "success": False}

            content_type = content_data.get("content_type", "photo")
            caption = content_data.get("caption", "")
            media_url = content_data.get("media_url", "")

            if not media_url:
                return {"error": "Media URL required for Instagram", "success": False}

            if content_type == "video":
                result = await self.instagram.post_video(media_url, caption)
            else:
                result = await self.instagram.post_photo(media_url, caption)

            if result.get("success"):
                return {
                    "success": True,
                    "platform": "instagram",
                    "post_id": result.get("post_id"),
                    "platform_url": f"https://www.instagram.com/p/{result.get('post_id')}/" if result.get("post_id") else None
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error posting to Instagram: {e}")
            return {"error": str(e), "success": False}

    async def _post_to_twitter(self, content_data: Dict) -> Dict:
        """Post content to Twitter"""
        try:
            if not self.twitter.is_configured():
                return {"error": "Twitter not configured", "success": False}

            text = content_data.get("caption", "")
            media_url = content_data.get("media_url")

            if media_url:
                result = await self.twitter.post_with_media(text, media_url)
            else:
                result = await self.twitter.post_tweet(text)

            if result.get("success"):
                tweet_id = result.get("tweet_id")
                return {
                    "success": True,
                    "platform": "twitter",
                    "post_id": tweet_id,
                    "platform_url": f"https://twitter.com/user/status/{tweet_id}" if tweet_id else None
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error posting to Twitter: {e}")
            return {"error": str(e), "success": False}

    async def _post_to_linkedin(self, content_data: Dict) -> Dict:
        """Post content to LinkedIn"""
        try:
            if not self.linkedin.is_configured():
                return {"error": "LinkedIn not configured", "success": False}

            text = content_data.get("caption", "")
            media_url = content_data.get("media_url")

            if media_url:
                result = await self.linkedin.post_with_media(text, media_url)
            else:
                result = await self.linkedin.post_text(text)

            if result.get("success"):
                return {
                    "success": True,
                    "platform": "linkedin",
                    "post_id": result.get("post_id"),
                    "platform_url": result.get("post_url")
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error posting to LinkedIn: {e}")
            return {"error": str(e), "success": False}

    async def _post_to_facebook(self, content_data: Dict) -> Dict:
        """Post content to Facebook"""
        try:
            if not self.facebook.is_configured():
                return {"error": "Facebook not configured", "success": False}

            message = content_data.get("caption", "")
            media_url = content_data.get("media_url")

            if media_url:
                result = await self.facebook.post_with_media(message, media_url)
            else:
                result = await self.facebook.post_text(message)

            if result.get("success"):
                return {
                    "success": True,
                    "platform": "facebook",
                    "post_id": result.get("post_id"),
                    "platform_url": result.get("post_url")
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error posting to Facebook: {e}")
            return {"error": str(e), "success": False}

    async def post_to_multiple_platforms(self, platforms: List[str], content_data: Dict) -> Dict:
        """Post content to multiple platforms simultaneously"""
        results = {}
        tasks = []

        for platform in platforms:
            task = asyncio.create_task(
                self.post_to_platform(platform, content_data),
                name=f"post_to_{platform}"
            )
            tasks.append((platform, task))

        # Wait for all posts to complete
        for platform, task in tasks:
            try:
                result = await task
                results[platform] = result
            except Exception as e:
                logger.error(f"Error posting to {platform}: {e}")
                results[platform] = {"error": str(e), "success": False}

        # Calculate overall success
        successful_posts = [p for p, r in results.items() if r.get("success")]
        failed_posts = [p for p, r in results.items() if not r.get("success")]

        return {
            "overall_success": len(successful_posts) > 0,
            "successful_platforms": successful_posts,
            "failed_platforms": failed_posts,
            "results": results,
            "success_rate": len(successful_posts) / len(platforms) if platforms else 0
        }

    async def send_webhook_notification(self, webhook_url: str, data: Dict, headers: Dict = None) -> Dict:
        """Send webhook notification to external service"""
        try:
            default_headers = {
                "Content-Type": "application/json",
                "User-Agent": "SocialMaestro Webhook v1.0"
            }

            if headers:
                default_headers.update(headers)

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    webhook_url,
                    json=data,
                    headers=default_headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    response_text = await response.text()

                    return {
                        "success": response.status < 400,
                        "status_code": response.status,
                        "response": response_text,
                        "webhook_url": webhook_url
                    }

        except asyncio.TimeoutError:
            logger.error(f"Webhook timeout: {webhook_url}")
            return {"success": False, "error": "Timeout", "webhook_url": webhook_url}
        except Exception as e:
            logger.error(f"Webhook error for {webhook_url}: {e}")
            return {"success": False, "error": str(e), "webhook_url": webhook_url}

    async def notify_zapier(self, trigger_data: Dict) -> Dict:
        """Send notification to Zapier webhook"""
        zapier_webhook = settings.zapier_webhook_url if hasattr(settings, 'zapier_webhook_url') else None

        if not zapier_webhook:
            return {"success": False, "error": "Zapier webhook not configured"}

        # Format data for Zapier
        zapier_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": trigger_data.get("event_type", "content_posted"),
            "platform": trigger_data.get("platform"),
            "post_id": trigger_data.get("post_id"),
            "content": trigger_data.get("content", ""),
            "success": trigger_data.get("success", False),
            "brand_id": trigger_data.get("brand_id"),
            "scheduled_time": trigger_data.get("scheduled_time"),
            "published_time": trigger_data.get("published_time")
        }

        return await self.send_webhook_notification(zapier_webhook, zapier_data)

    async def notify_ifttt(self, trigger_data: Dict) -> Dict:
        """Send notification to IFTTT webhook"""
        ifttt_webhook = settings.ifttt_webhook_url if hasattr(settings, 'ifttt_webhook_url') else None

        if not ifttt_webhook:
            return {"success": False, "error": "IFTTT webhook not configured"}

        # IFTTT uses specific format
        ifttt_data = {
            "value1": trigger_data.get("platform", ""),
            "value2": trigger_data.get("content", "")[:100],  # Truncate for IFTTT
            "value3": "success" if trigger_data.get("success") else "failed"
        }

        return await self.send_webhook_notification(ifttt_webhook, ifttt_data)

    async def notify_slack(self, message: str, channel: str = None) -> Dict:
        """Send notification to Slack"""
        slack_webhook = settings.slack_webhook_url if hasattr(settings, 'slack_webhook_url') else None

        if not slack_webhook:
            return {"success": False, "error": "Slack webhook not configured"}

        slack_data = {
            "text": message,
            "channel": channel or "#social-media",
            "username": "AI Social Manager",
            "icon_emoji": ":robot_face:"
        }

        return await self.send_webhook_notification(slack_webhook, slack_data)

    async def notify_discord(self, message: str, title: str = "AI Social Manager") -> Dict:
        """Send notification to Discord"""
        discord_webhook = settings.discord_webhook_url if hasattr(settings, 'discord_webhook_url') else None

        if not discord_webhook:
            return {"success": False, "error": "Discord webhook not configured"}

        discord_data = {
            "embeds": [{
                "title": title,
                "description": message,
                "color": 5814783,  # Blue color
                "timestamp": datetime.utcnow().isoformat()
            }]
        }

        return await self.send_webhook_notification(discord_webhook, discord_data)

    async def notify_teams(self, message: str, title: str = "AI Social Manager") -> Dict:
        """Send notification to Microsoft Teams"""
        teams_webhook = settings.teams_webhook_url if hasattr(settings, 'teams_webhook_url') else None

        if not teams_webhook:
            return {"success": False, "error": "Teams webhook not configured"}

        teams_data = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "summary": title,
            "themeColor": "0078D4",
            "sections": [{
                "activityTitle": title,
                "activitySubtitle": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                "text": message
            }]
        }

        return await self.send_webhook_notification(teams_webhook, teams_data)

    async def schedule_webhook_post(self, platform: str, content_data: Dict,
                                  scheduled_time: datetime, webhook_url: str = None) -> Dict:
        """Schedule a webhook-triggered post"""
        try:
            # This would integrate with a task queue like Celery or APScheduler
            # For now, we'll simulate the scheduling

            scheduled_data = {
                "platform": platform,
                "content_data": content_data,
                "scheduled_time": scheduled_time.isoformat(),
                "webhook_url": webhook_url,
                "status": "scheduled"
            }

            # In production, you'd store this in a database and use a scheduler
            logger.info(f"Scheduled webhook post for {platform} at {scheduled_time}")

            return {"success": True, "scheduled_id": f"webhook_{datetime.utcnow().timestamp()}"}

        except Exception as e:
            logger.error(f"Error scheduling webhook post: {e}")
            return {"success": False, "error": str(e)}

    async def handle_webhook_response(self, platform: str, response_data: Dict) -> Dict:
        """Handle response from social media platform webhook"""
        try:
            # Parse platform-specific response formats
            if platform == "instagram":
                return await self._handle_instagram_webhook(response_data)
            elif platform == "twitter":
                return await self._handle_twitter_webhook(response_data)
            elif platform == "linkedin":
                return await self._handle_linkedin_webhook(response_data)
            elif platform == "facebook":
                return await self._handle_facebook_webhook(response_data)
            else:
                return {"success": False, "error": f"Unsupported platform: {platform}"}

        except Exception as e:
            logger.error(f"Error handling webhook response for {platform}: {e}")
            return {"success": False, "error": str(e)}

    async def _handle_instagram_webhook(self, data: Dict) -> Dict:
        """Handle Instagram webhook response"""
        # Instagram webhook format varies, implement based on their docs
        return {
            "success": True,
            "platform": "instagram",
            "data": data
        }

    async def _handle_twitter_webhook(self, data: Dict) -> Dict:
        """Handle Twitter webhook response"""
        # Twitter webhook format
        return {
            "success": True,
            "platform": "twitter",
            "data": data
        }

    async def _handle_linkedin_webhook(self, data: Dict) -> Dict:
        """Handle LinkedIn webhook response"""
        # LinkedIn webhook format
        return {
            "success": True,
            "platform": "linkedin",
            "data": data
        }

    async def _handle_facebook_webhook(self, data: Dict) -> Dict:
        """Handle Facebook webhook response"""
        # Facebook webhook format
        return {
            "success": True,
            "platform": "facebook",
            "data": data
        }

    async def validate_webhook_signature(self, payload: bytes, signature: str, secret: str) -> bool:
        """Validate webhook signature for security"""
        import hmac
        import hashlib

        try:
            expected_signature = hmac.new(
                secret.encode(),
                payload,
                hashlib.sha256
            ).hexdigest()

            # Remove 'sha256=' prefix if present
            if signature.startswith('sha256='):
                signature = signature[7:]

            return hmac.compare_digest(expected_signature, signature)

        except Exception as e:
            logger.error(f"Error validating webhook signature: {e}")
            return False

    def get_webhook_endpoints(self) -> Dict[str, str]:
        """Get all configured webhook endpoints"""
        return self.webhook_endpoints.copy()

    async def test_webhook_connection(self, webhook_url: str) -> Dict:
        """Test webhook connection"""
        test_data = {
            "test": True,
            "timestamp": datetime.utcnow().isoformat(),
            "message": "AI Social Manager webhook test"
        }

        result = await self.send_webhook_notification(webhook_url, test_data)

        return {
            "webhook_url": webhook_url,
            "connection_successful": result.get("success", False),
            "response_status": result.get("status_code"),
            "test_timestamp": datetime.utcnow().isoformat()
        }

    async def get_platform_status(self) -> Dict:
        """Get status of all social media platform integrations"""
        return {
            "instagram": {
                "configured": self.instagram.is_configured(),
                "status": "active" if self.instagram.is_configured() else "not_configured"
            },
            "twitter": {
                "configured": self.twitter.is_configured(),
                "status": "active" if self.twitter.is_configured() else "not_configured"
            },
            "linkedin": {
                "configured": self.linkedin.is_configured(),
                "status": "active" if self.linkedin.is_configured() else "not_configured"
            },
            "facebook": {
                "configured": self.facebook.is_configured(),
                "status": "active" if self.facebook.is_configured() else "not_configured"
            }
        }

# Global webhook manager instance
_webhook_manager = None

def get_webhook_manager() -> WebhookManager:
    """Get global webhook manager instance"""
    global _webhook_manager
    if _webhook_manager is None:
        _webhook_manager = WebhookManager()
    return _webhook_manager
