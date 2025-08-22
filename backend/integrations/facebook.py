"""
Facebook API Integration
Real API integration using Facebook Graph API for posting and analytics
"""

import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
import aiohttp
import json
from urllib.parse import urlencode

from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class FacebookAPI:
    """Facebook Graph API client"""

    def __init__(self):
        self.app_id = settings.facebook_app_id
        self.app_secret = settings.facebook_app_secret
        self.access_token = settings.facebook_access_token
        self.page_id = settings.facebook_page_id
        self.base_url = "https://graph.facebook.com/v18.0"

    async def get_auth_url(self, redirect_uri: str, state: str = None) -> str:
        """Generate Facebook authorization URL"""
        params = {
            "client_id": self.app_id,
            "redirect_uri": redirect_uri,
            "scope": "pages_manage_posts,pages_read_engagement,pages_show_list,public_profile",
            "response_type": "code",
            "state": state or "facebook_auth"
        }

        auth_url = f"https://www.facebook.com/v18.0/dialog/oauth?{urlencode(params)}"
        return auth_url

    async def exchange_code_for_token(self, code: str, redirect_uri: str) -> Dict:
        """Exchange authorization code for access token"""
        try:
            params = {
                "client_id": self.app_id,
                "client_secret": self.app_secret,
                "redirect_uri": redirect_uri,
                "code": code
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/oauth/access_token",
                    params=params
                ) as response:
                    result = await response.json()

                    if response.status == 200:
                        # Get long-lived token
                        long_lived_token = await self.get_long_lived_token(result["access_token"])
                        return long_lived_token
                    else:
                        logger.error(f"Failed to exchange code for token: {result}")
                        return {"error": result}

        except Exception as e:
            logger.error(f"Error exchanging code for token: {e}")
            return {"error": str(e)}

    async def get_long_lived_token(self, short_token: str) -> Dict:
        """Convert short-lived token to long-lived token"""
        try:
            params = {
                "grant_type": "fb_exchange_token",
                "client_id": self.app_id,
                "client_secret": self.app_secret,
                "fb_exchange_token": short_token
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/oauth/access_token",
                    params=params
                ) as response:
                    result = await response.json()

                    if response.status == 200:
                        return {
                            "access_token": result["access_token"],
                            "token_type": result.get("token_type", "bearer"),
                            "expires_in": result.get("expires_in", 5183944)  # ~60 days
                        }
                    else:
                        logger.error(f"Failed to get long-lived token: {result}")
                        return {"error": result}

        except Exception as e:
            logger.error(f"Error getting long-lived token: {e}")
            return {"error": str(e)}

    async def get_user_pages(self, access_token: str = None) -> List[Dict]:
        """Get Facebook pages managed by the user"""
        token = access_token or self.access_token

        try:
            params = {
                "access_token": token,
                "fields": "id,name,category,access_token,fan_count,picture"
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/me/accounts",
                    params=params
                ) as response:
                    result = await response.json()

                    if response.status == 200:
                        return result.get("data", [])
                    else:
                        logger.error(f"Failed to get user pages: {result}")
                        return []

        except Exception as e:
            logger.error(f"Error getting user pages: {e}")
            return []

    async def post_text(self, message: str, page_access_token: str = None) -> Dict:
        """Post text-only message to Facebook page"""
        try:
            if not self.page_id:
                return {"error": "Facebook page not configured", "success": False}

            token = page_access_token or self.access_token

            data = {
                "message": message,
                "access_token": token
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/{self.page_id}/feed",
                    data=data
                ) as response:
                    result = await response.json()

                    if response.status == 200:
                        post_id = result.get("id")
                        return {
                            "success": True,
                            "post_id": post_id,
                            "post_url": f"https://www.facebook.com/{post_id}" if post_id else None
                        }
                    else:
                        logger.error(f"Failed to post to Facebook: {result}")
                        return {"error": result, "success": False}

        except Exception as e:
            logger.error(f"Error posting to Facebook: {e}")
            return {"error": str(e), "success": False}

    async def post_with_media(self, message: str, media_url: str, page_access_token: str = None) -> Dict:
        """Post message with media to Facebook page"""
        try:
            if not self.page_id:
                return {"error": "Facebook page not configured", "success": False}

            token = page_access_token or self.access_token

            # Determine if it's a photo or video based on URL
            is_video = any(ext in media_url.lower() for ext in ['.mp4', '.mov', '.avi', '.mkv'])

            if is_video:
                return await self._post_video(message, media_url, token)
            else:
                return await self._post_photo(message, media_url, token)

        except Exception as e:
            logger.error(f"Error posting with media to Facebook: {e}")
            return {"error": str(e), "success": False}

    async def _post_photo(self, message: str, photo_url: str, token: str) -> Dict:
        """Post photo to Facebook page"""
        try:
            data = {
                "message": message,
                "url": photo_url,
                "access_token": token
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/{self.page_id}/photos",
                    data=data
                ) as response:
                    result = await response.json()

                    if response.status == 200:
                        post_id = result.get("id")
                        return {
                            "success": True,
                            "post_id": post_id,
                            "post_url": f"https://www.facebook.com/{post_id}" if post_id else None
                        }
                    else:
                        logger.error(f"Failed to post photo to Facebook: {result}")
                        return {"error": result, "success": False}

        except Exception as e:
            logger.error(f"Error posting photo to Facebook: {e}")
            return {"error": str(e), "success": False}

    async def _post_video(self, message: str, video_url: str, token: str) -> Dict:
        """Post video to Facebook page"""
        try:
            data = {
                "description": message,
                "file_url": video_url,
                "access_token": token
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/{self.page_id}/videos",
                    data=data
                ) as response:
                    result = await response.json()

                    if response.status == 200:
                        video_id = result.get("id")
                        return {
                            "success": True,
                            "post_id": video_id,
                            "post_url": f"https://www.facebook.com/{video_id}" if video_id else None
                        }
                    else:
                        logger.error(f"Failed to post video to Facebook: {result}")
                        return {"error": result, "success": False}

        except Exception as e:
            logger.error(f"Error posting video to Facebook: {e}")
            return {"error": str(e), "success": False}

    async def get_page_posts(self, limit: int = 25, page_access_token: str = None) -> List[Dict]:
        """Get posts from Facebook page"""
        try:
            if not self.page_id:
                return []

            token = page_access_token or self.access_token

            params = {
                "fields": "id,message,created_time,permalink_url,attachments,insights.metric(post_impressions,post_engaged_users)",
                "limit": limit,
                "access_token": token
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/{self.page_id}/posts",
                    params=params
                ) as response:
                    result = await response.json()

                    if response.status == 200:
                        posts = []
                        for post in result.get("data", []):
                            post_data = {
                                "id": post.get("id"),
                                "message": post.get("message", ""),
                                "created_time": post.get("created_time"),
                                "permalink_url": post.get("permalink_url"),
                                "has_attachments": bool(post.get("attachments")),
                                "insights": post.get("insights", {}).get("data", [])
                            }
                            posts.append(post_data)

                        return posts
                    else:
                        logger.error(f"Failed to get page posts: {result}")
                        return []

        except Exception as e:
            logger.error(f"Error getting page posts: {e}")
            return []

    async def get_post_insights(self, post_id: str, page_access_token: str = None) -> Dict:
        """Get insights for a specific post"""
        try:
            token = page_access_token or self.access_token

            metrics = [
                "post_impressions",
                "post_engaged_users",
                "post_reactions_like_total",
                "post_reactions_love_total",
                "post_reactions_wow_total",
                "post_reactions_haha_total",
                "post_reactions_sorry_total",
                "post_reactions_anger_total",
                "post_clicks",
                "post_comments",
                "post_shares"
            ]

            params = {
                "metric": ",".join(metrics),
                "access_token": token
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/{post_id}/insights",
                    params=params
                ) as response:
                    result = await response.json()

                    if response.status == 200:
                        insights = {}
                        for data in result.get("data", []):
                            metric_name = data.get("name")
                            values = data.get("values", [])
                            if values:
                                insights[metric_name] = values[0].get("value", 0)

                        return insights
                    else:
                        logger.error(f"Failed to get post insights: {result}")
                        return {}

        except Exception as e:
            logger.error(f"Error getting post insights: {e}")
            return {}

    async def get_page_insights(self, page_access_token: str = None) -> Dict:
        """Get page-level insights"""
        try:
            if not self.page_id:
                return {}

            token = page_access_token or self.access_token

            metrics = [
                "page_fans",
                "page_impressions",
                "page_post_engagements",
                "page_posts_impressions",
                "page_video_views"
            ]

            params = {
                "metric": ",".join(metrics),
                "period": "day",
                "access_token": token
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/{self.page_id}/insights",
                    params=params
                ) as response:
                    result = await response.json()

                    if response.status == 200:
                        insights = {}
                        for data in result.get("data", []):
                            metric_name = data.get("name")
                            values = data.get("values", [])
                            if values:
                                insights[metric_name] = values[-1].get("value", 0)  # Get latest value

                        return insights
                    else:
                        logger.error(f"Failed to get page insights: {result}")
                        return {}

        except Exception as e:
            logger.error(f"Error getting page insights: {e}")
            return {}

    async def delete_post(self, post_id: str, page_access_token: str = None) -> Dict:
        """Delete a post from Facebook page"""
        try:
            token = page_access_token or self.access_token

            params = {
                "access_token": token
            }

            async with aiohttp.ClientSession() as session:
                async with session.delete(
                    f"{self.base_url}/{post_id}",
                    params=params
                ) as response:
                    result = await response.json()

                    if response.status == 200 and result.get("success"):
                        return {"success": True, "post_id": post_id}
                    else:
                        logger.error(f"Failed to delete post: {result}")
                        return {"error": result, "success": False}

        except Exception as e:
            logger.error(f"Error deleting post: {e}")
            return {"error": str(e), "success": False}

    async def get_page_info(self, page_access_token: str = None) -> Dict:
        """Get Facebook page information"""
        try:
            if not self.page_id:
                return {}

            token = page_access_token or self.access_token

            params = {
                "fields": "id,name,category,fan_count,talking_about_count,picture,cover,website,about",
                "access_token": token
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/{self.page_id}",
                    params=params
                ) as response:
                    result = await response.json()

                    if response.status == 200:
                        return result
                    else:
                        logger.error(f"Failed to get page info: {result}")
                        return {}

        except Exception as e:
            logger.error(f"Error getting page info: {e}")
            return {}

    async def search_posts(self, query: str, limit: int = 25) -> List[Dict]:
        """Search for public posts (requires additional permissions)"""
        try:
            # Note: This requires special permissions and may not be available
            # for all apps due to Facebook's platform policy changes

            params = {
                "q": query,
                "type": "post",
                "limit": limit,
                "access_token": self.access_token
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/search",
                    params=params
                ) as response:
                    result = await response.json()

                    if response.status == 200:
                        return result.get("data", [])
                    else:
                        logger.warning(f"Search not available or insufficient permissions: {result}")
                        return []

        except Exception as e:
            logger.error(f"Error searching posts: {e}")
            return []

    async def discover_trending_content(self, keywords: List[str], limit: int = 50) -> List[Dict]:
        """Discover trending content based on keywords"""
        # Facebook's API is very restrictive for content discovery
        # Most search APIs have been deprecated or require special permissions

        trending_content = []

        # Limited options available:
        # 1. Posts from your own page
        # 2. Posts from pages you manage
        # 3. Public posts (very limited access)

        try:
            # Get posts from your own page that might be relevant
            page_posts = await self.get_page_posts(limit=20)

            for post in page_posts:
                # Simple keyword matching
                message = post.get("message", "").lower()
                if any(keyword.lower() in message for keyword in keywords):
                    post["platform"] = "facebook"
                    post["source_keyword"] = next(
                        keyword for keyword in keywords
                        if keyword.lower() in message
                    )
                    trending_content.append(post)

            logger.info(f"Facebook content discovery limited by API restrictions for keywords: {keywords}")

        except Exception as e:
            logger.error(f"Error discovering Facebook content: {e}")

        return trending_content[:limit]

    async def schedule_post(self, message: str, publish_time: datetime,
                          media_url: str = None, page_access_token: str = None) -> Dict:
        """Schedule a post for future publication"""
        try:
            if not self.page_id:
                return {"error": "Facebook page not configured", "success": False}

            token = page_access_token or self.access_token

            # Convert datetime to Unix timestamp
            scheduled_timestamp = int(publish_time.timestamp())

            data = {
                "message": message,
                "scheduled_publish_time": scheduled_timestamp,
                "published": "false",  # This makes it scheduled
                "access_token": token
            }

            if media_url:
                # For media posts, we'd need to upload the media first
                # This is a simplified version
                data["url"] = media_url
                endpoint = f"{self.base_url}/{self.page_id}/photos"
            else:
                endpoint = f"{self.base_url}/{self.page_id}/feed"

            async with aiohttp.ClientSession() as session:
                async with session.post(endpoint, data=data) as response:
                    result = await response.json()

                    if response.status == 200:
                        post_id = result.get("id")
                        return {
                            "success": True,
                            "post_id": post_id,
                            "scheduled_time": publish_time.isoformat()
                        }
                    else:
                        logger.error(f"Failed to schedule Facebook post: {result}")
                        return {"error": result, "success": False}

        except Exception as e:
            logger.error(f"Error scheduling Facebook post: {e}")
            return {"error": str(e), "success": False}

    def is_configured(self) -> bool:
        """Check if Facebook API is properly configured"""
        return bool(self.app_id and self.app_secret and self.access_token and self.page_id)
