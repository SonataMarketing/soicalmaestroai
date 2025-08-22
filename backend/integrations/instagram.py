"""
Instagram Graph API Integration
Real API integration for content discovery, posting, and analytics
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import requests
import aiohttp
from urllib.parse import urlencode

from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class InstagramAPI:
    """Instagram Graph API client"""

    def __init__(self):
        self.app_id = settings.instagram_app_id
        self.app_secret = settings.instagram_app_secret
        self.access_token = settings.instagram_access_token
        self.business_account_id = settings.instagram_business_account_id
        self.base_url = "https://graph.facebook.com/v18.0"

    async def get_auth_url(self, redirect_uri: str, state: str = None) -> str:
        """Generate Instagram authorization URL"""
        params = {
            "client_id": self.app_id,
            "redirect_uri": redirect_uri,
            "scope": "instagram_basic,instagram_content_publish,pages_show_list,pages_read_engagement",
            "response_type": "code",
            "state": state or "instagram_auth"
        }

        auth_url = f"https://api.instagram.com/oauth/authorize?{urlencode(params)}"
        return auth_url

    async def exchange_code_for_token(self, code: str, redirect_uri: str) -> Dict:
        """Exchange authorization code for access token"""
        try:
            async with aiohttp.ClientSession() as session:
                data = {
                    "client_id": self.app_id,
                    "client_secret": self.app_secret,
                    "grant_type": "authorization_code",
                    "redirect_uri": redirect_uri,
                    "code": code
                }

                async with session.post(
                    "https://api.instagram.com/oauth/access_token",
                    data=data
                ) as response:
                    result = await response.json()

                    if response.status == 200:
                        # Exchange short-lived token for long-lived token
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
                "grant_type": "ig_exchange_token",
                "client_secret": self.app_secret,
                "access_token": short_token
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
                            "token_type": result["token_type"],
                            "expires_in": result.get("expires_in", 5183944)  # ~60 days
                        }
                    else:
                        logger.error(f"Failed to get long-lived token: {result}")
                        return {"error": result}

        except Exception as e:
            logger.error(f"Error getting long-lived token: {e}")
            return {"error": str(e)}

    async def refresh_access_token(self, current_token: str) -> Dict:
        """Refresh long-lived access token"""
        try:
            params = {
                "grant_type": "ig_refresh_token",
                "access_token": current_token
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/refresh_access_token",
                    params=params
                ) as response:
                    result = await response.json()

                    if response.status == 200:
                        return {
                            "access_token": result["access_token"],
                            "token_type": result["token_type"],
                            "expires_in": result.get("expires_in", 5183944)
                        }
                    else:
                        logger.error(f"Failed to refresh token: {result}")
                        return {"error": result}

        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            return {"error": str(e)}

    async def get_user_info(self, access_token: str = None) -> Dict:
        """Get Instagram user information"""
        token = access_token or self.access_token

        try:
            params = {
                "fields": "id,username,account_type,media_count",
                "access_token": token
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/me",
                    params=params
                ) as response:
                    result = await response.json()

                    if response.status == 200:
                        return result
                    else:
                        logger.error(f"Failed to get user info: {result}")
                        return {"error": result}

        except Exception as e:
            logger.error(f"Error getting user info: {e}")
            return {"error": str(e)}

    async def get_business_accounts(self, access_token: str = None) -> List[Dict]:
        """Get connected Instagram business accounts"""
        token = access_token or self.access_token

        try:
            params = {
                "fields": "instagram_business_account{id,username,name,profile_picture_url,followers_count,media_count}",
                "access_token": token
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/me/accounts",
                    params=params
                ) as response:
                    result = await response.json()

                    if response.status == 200:
                        accounts = []
                        for page in result.get("data", []):
                            if "instagram_business_account" in page:
                                accounts.append(page["instagram_business_account"])
                        return accounts
                    else:
                        logger.error(f"Failed to get business accounts: {result}")
                        return []

        except Exception as e:
            logger.error(f"Error getting business accounts: {e}")
            return []

    async def get_hashtag_search(self, hashtag: str, count: int = 25) -> List[Dict]:
        """Search for recent posts by hashtag"""
        if not self.business_account_id or not self.access_token:
            logger.warning("Instagram business account not configured")
            return []

        try:
            # First, get hashtag ID
            hashtag_id = await self.get_hashtag_id(hashtag)
            if not hashtag_id:
                return []

            # Get recent media for hashtag
            params = {
                "fields": "id,media_type,media_url,permalink,caption,timestamp,like_count,comments_count",
                "limit": count,
                "access_token": self.access_token
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/{hashtag_id}/recent_media",
                    params=params
                ) as response:
                    result = await response.json()

                    if response.status == 200:
                        return result.get("data", [])
                    else:
                        logger.error(f"Failed to search hashtag {hashtag}: {result}")
                        return []

        except Exception as e:
            logger.error(f"Error searching hashtag {hashtag}: {e}")
            return []

    async def get_hashtag_id(self, hashtag: str) -> Optional[str]:
        """Get hashtag ID for searches"""
        try:
            params = {
                "q": hashtag.replace("#", ""),
                "access_token": self.access_token
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/ig_hashtag_search",
                    params=params
                ) as response:
                    result = await response.json()

                    if response.status == 200 and result.get("data"):
                        return result["data"][0]["id"]
                    else:
                        logger.error(f"Failed to get hashtag ID for {hashtag}: {result}")
                        return None

        except Exception as e:
            logger.error(f"Error getting hashtag ID for {hashtag}: {e}")
            return None

    async def get_user_media(self, limit: int = 25, fields: str = None) -> List[Dict]:
        """Get user's media posts"""
        if not self.business_account_id or not self.access_token:
            logger.warning("Instagram business account not configured")
            return []

        default_fields = "id,media_type,media_url,permalink,caption,timestamp,like_count,comments_count"
        fields = fields or default_fields

        try:
            params = {
                "fields": fields,
                "limit": limit,
                "access_token": self.access_token
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/{self.business_account_id}/media",
                    params=params
                ) as response:
                    result = await response.json()

                    if response.status == 200:
                        return result.get("data", [])
                    else:
                        logger.error(f"Failed to get user media: {result}")
                        return []

        except Exception as e:
            logger.error(f"Error getting user media: {e}")
            return []

    async def create_media_object(self, image_url: str, caption: str, is_video: bool = False) -> Optional[str]:
        """Create media object for publishing"""
        if not self.business_account_id or not self.access_token:
            logger.error("Instagram business account not configured")
            return None

        try:
            data = {
                "caption": caption,
                "access_token": self.access_token
            }

            if is_video:
                data["media_type"] = "VIDEO"
                data["video_url"] = image_url
            else:
                data["image_url"] = image_url

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/{self.business_account_id}/media",
                    data=data
                ) as response:
                    result = await response.json()

                    if response.status == 200:
                        return result["id"]
                    else:
                        logger.error(f"Failed to create media object: {result}")
                        return None

        except Exception as e:
            logger.error(f"Error creating media object: {e}")
            return None

    async def publish_media(self, creation_id: str) -> Dict:
        """Publish media object"""
        if not self.business_account_id or not self.access_token:
            logger.error("Instagram business account not configured")
            return {"error": "Account not configured"}

        try:
            data = {
                "creation_id": creation_id,
                "access_token": self.access_token
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/{self.business_account_id}/media_publish",
                    data=data
                ) as response:
                    result = await response.json()

                    if response.status == 200:
                        return {"id": result["id"], "success": True}
                    else:
                        logger.error(f"Failed to publish media: {result}")
                        return {"error": result, "success": False}

        except Exception as e:
            logger.error(f"Error publishing media: {e}")
            return {"error": str(e), "success": False}

    async def post_photo(self, image_url: str, caption: str) -> Dict:
        """Post a photo to Instagram"""
        try:
            # Create media object
            creation_id = await self.create_media_object(image_url, caption, is_video=False)

            if not creation_id:
                return {"error": "Failed to create media object", "success": False}

            # Wait a moment for processing
            await asyncio.sleep(2)

            # Publish the media
            result = await self.publish_media(creation_id)

            if result.get("success"):
                logger.info(f"Successfully posted photo to Instagram: {result['id']}")
                return {
                    "success": True,
                    "post_id": result["id"],
                    "creation_id": creation_id
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error posting photo: {e}")
            return {"error": str(e), "success": False}

    async def post_video(self, video_url: str, caption: str) -> Dict:
        """Post a video to Instagram"""
        try:
            # Create media object for video
            creation_id = await self.create_media_object(video_url, caption, is_video=True)

            if not creation_id:
                return {"error": "Failed to create video media object", "success": False}

            # Videos take longer to process
            await asyncio.sleep(10)

            # Check if video is ready for publishing
            ready = await self.check_media_status(creation_id)
            if not ready:
                return {"error": "Video not ready for publishing", "success": False}

            # Publish the video
            result = await self.publish_media(creation_id)

            if result.get("success"):
                logger.info(f"Successfully posted video to Instagram: {result['id']}")
                return {
                    "success": True,
                    "post_id": result["id"],
                    "creation_id": creation_id
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error posting video: {e}")
            return {"error": str(e), "success": False}

    async def check_media_status(self, creation_id: str) -> bool:
        """Check if media is ready for publishing"""
        try:
            params = {
                "fields": "status_code",
                "access_token": self.access_token
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/{creation_id}",
                    params=params
                ) as response:
                    result = await response.json()

                    if response.status == 200:
                        status = result.get("status_code")
                        return status == "FINISHED"
                    else:
                        logger.error(f"Failed to check media status: {result}")
                        return False

        except Exception as e:
            logger.error(f"Error checking media status: {e}")
            return False

    async def get_media_insights(self, media_id: str) -> Dict:
        """Get insights for a specific media post"""
        try:
            params = {
                "metric": "engagement,impressions,reach,saved",
                "access_token": self.access_token
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/{media_id}/insights",
                    params=params
                ) as response:
                    result = await response.json()

                    if response.status == 200:
                        insights = {}
                        for data in result.get("data", []):
                            insights[data["name"]] = data["values"][0]["value"]
                        return insights
                    else:
                        logger.error(f"Failed to get media insights: {result}")
                        return {}

        except Exception as e:
            logger.error(f"Error getting media insights: {e}")
            return {}

    async def get_account_insights(self, period: str = "day") -> Dict:
        """Get account-level insights"""
        if not self.business_account_id or not self.access_token:
            logger.warning("Instagram business account not configured")
            return {}

        try:
            params = {
                "metric": "follower_count,impressions,reach,profile_views",
                "period": period,
                "access_token": self.access_token
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/{self.business_account_id}/insights",
                    params=params
                ) as response:
                    result = await response.json()

                    if response.status == 200:
                        insights = {}
                        for data in result.get("data", []):
                            values = data.get("values", [])
                            if values:
                                insights[data["name"]] = values[-1]["value"]  # Get latest value
                        return insights
                    else:
                        logger.error(f"Failed to get account insights: {result}")
                        return {}

        except Exception as e:
            logger.error(f"Error getting account insights: {e}")
            return {}

    async def discover_trending_content(self, keywords: List[str], limit: int = 50) -> List[Dict]:
        """Discover trending content based on keywords"""
        trending_content = []

        for keyword in keywords[:5]:  # Limit API calls
            try:
                # Search hashtag
                if keyword.startswith("#"):
                    hashtag_content = await self.get_hashtag_search(keyword, limit//len(keywords))
                    for content in hashtag_content:
                        content["source_keyword"] = keyword
                        content["platform"] = "instagram"
                        trending_content.append(content)

                await asyncio.sleep(1)  # Rate limiting

            except Exception as e:
                logger.error(f"Error discovering content for keyword {keyword}: {e}")
                continue

        # Sort by engagement (likes + comments)
        trending_content.sort(
            key=lambda x: (x.get("like_count", 0) + x.get("comments_count", 0)),
            reverse=True
        )

        return trending_content[:limit]

    def is_configured(self) -> bool:
        """Check if Instagram API is properly configured"""
        return bool(self.app_id and self.app_secret and self.access_token and self.business_account_id)
