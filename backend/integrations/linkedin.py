"""
LinkedIn API Integration
Real API integration using LinkedIn Marketing API for posting and analytics
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

class LinkedInAPI:
    """LinkedIn API client"""

    def __init__(self):
        self.client_id = settings.linkedin_client_id
        self.client_secret = settings.linkedin_client_secret
        self.access_token = settings.linkedin_access_token
        self.base_url = "https://api.linkedin.com/v2"

        # User profile info (will be populated after initialization)
        self.user_id = None
        self.user_info = {}

    async def get_auth_url(self, redirect_uri: str, state: str = None) -> str:
        """Generate LinkedIn authorization URL"""
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "state": state or "linkedin_auth",
            "scope": "r_liteprofile r_emailaddress w_member_social"
        }

        auth_url = f"https://www.linkedin.com/oauth/v2/authorization?{urlencode(params)}"
        return auth_url

    async def exchange_code_for_token(self, code: str, redirect_uri: str) -> Dict:
        """Exchange authorization code for access token"""
        try:
            data = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
                "client_id": self.client_id,
                "client_secret": self.client_secret
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://www.linkedin.com/oauth/v2/accessToken",
                    data=data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                ) as response:
                    result = await response.json()

                    if response.status == 200:
                        return {
                            "access_token": result["access_token"],
                            "token_type": result["token_type"],
                            "expires_in": result["expires_in"],
                            "scope": result.get("scope", "")
                        }
                    else:
                        logger.error(f"Failed to exchange code for token: {result}")
                        return {"error": result}

        except Exception as e:
            logger.error(f"Error exchanging code for token: {e}")
            return {"error": str(e)}

    async def get_user_profile(self, access_token: str = None) -> Dict:
        """Get user profile information"""
        token = access_token or self.access_token

        if not token:
            return {"error": "No access token available"}

        try:
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/people/~",
                    headers=headers
                ) as response:
                    result = await response.json()

                    if response.status == 200:
                        self.user_id = result.get("id")
                        self.user_info = result
                        return result
                    else:
                        logger.error(f"Failed to get user profile: {result}")
                        return {"error": result}

        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            return {"error": str(e)}

    async def post_text(self, text: str) -> Dict:
        """Post text-only update to LinkedIn"""
        try:
            if not self.access_token:
                return {"error": "LinkedIn not configured", "success": False}

            if not self.user_id:
                profile = await self.get_user_profile()
                if "error" in profile:
                    return {"error": "Failed to get user profile", "success": False}

            post_data = {
                "author": f"urn:li:person:{self.user_id}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": text
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }

            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0"
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/ugcPosts",
                    json=post_data,
                    headers=headers
                ) as response:
                    result = await response.json()

                    if response.status == 201:
                        post_id = result.get("id")
                        return {
                            "success": True,
                            "post_id": post_id,
                            "post_url": f"https://www.linkedin.com/feed/update/{post_id}/" if post_id else None
                        }
                    else:
                        logger.error(f"Failed to post to LinkedIn: {result}")
                        return {"error": result, "success": False}

        except Exception as e:
            logger.error(f"Error posting to LinkedIn: {e}")
            return {"error": str(e), "success": False}

    async def post_with_media(self, text: str, media_url: str) -> Dict:
        """Post update with media to LinkedIn"""
        try:
            if not self.access_token:
                return {"error": "LinkedIn not configured", "success": False}

            if not self.user_id:
                profile = await self.get_user_profile()
                if "error" in profile:
                    return {"error": "Failed to get user profile", "success": False}

            # First, upload the media
            media_urn = await self._upload_media(media_url)

            if not media_urn:
                return {"error": "Failed to upload media", "success": False}

            post_data = {
                "author": f"urn:li:person:{self.user_id}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": text
                        },
                        "shareMediaCategory": "IMAGE",  # or VIDEO based on media type
                        "media": [
                            {
                                "status": "READY",
                                "description": {
                                    "text": "Media shared via AI Social Manager"
                                },
                                "media": media_urn,
                                "title": {
                                    "text": "AI Generated Content"
                                }
                            }
                        ]
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }

            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0"
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/ugcPosts",
                    json=post_data,
                    headers=headers
                ) as response:
                    result = await response.json()

                    if response.status == 201:
                        post_id = result.get("id")
                        return {
                            "success": True,
                            "post_id": post_id,
                            "post_url": f"https://www.linkedin.com/feed/update/{post_id}/" if post_id else None,
                            "media_urn": media_urn
                        }
                    else:
                        logger.error(f"Failed to post with media to LinkedIn: {result}")
                        return {"error": result, "success": False}

        except Exception as e:
            logger.error(f"Error posting with media to LinkedIn: {e}")
            return {"error": str(e), "success": False}

    async def _upload_media(self, media_url: str) -> Optional[str]:
        """Upload media to LinkedIn and return media URN"""
        try:
            # Download media from URL
            async with aiohttp.ClientSession() as session:
                async with session.get(media_url) as response:
                    if response.status != 200:
                        logger.error(f"Failed to download media from {media_url}")
                        return None

                    media_data = await response.read()
                    content_type = response.headers.get('content-type', '')

            # Register upload
            upload_request = {
                "registerUploadRequest": {
                    "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                    "owner": f"urn:li:person:{self.user_id}",
                    "serviceRelationships": [
                        {
                            "relationshipType": "OWNER",
                            "identifier": "urn:li:userGeneratedContent"
                        }
                    ]
                }
            }

            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }

            async with aiohttp.ClientSession() as session:
                # Register upload
                async with session.post(
                    f"{self.base_url}/assets?action=registerUpload",
                    json=upload_request,
                    headers=headers
                ) as response:
                    register_result = await response.json()

                    if response.status != 200:
                        logger.error(f"Failed to register upload: {register_result}")
                        return None

                    upload_url = register_result["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
                    asset_id = register_result["value"]["asset"]

                # Upload media
                upload_headers = {
                    "Authorization": f"Bearer {self.access_token}"
                }

                async with session.put(
                    upload_url,
                    data=media_data,
                    headers=upload_headers
                ) as upload_response:
                    if upload_response.status not in [200, 201]:
                        logger.error(f"Failed to upload media: {upload_response.status}")
                        return None

                    return asset_id

        except Exception as e:
            logger.error(f"Error uploading media to LinkedIn: {e}")
            return None

    async def get_user_posts(self, limit: int = 10) -> List[Dict]:
        """Get user's recent posts"""
        try:
            if not self.access_token or not self.user_id:
                return []

            params = {
                "q": "authors",
                "authors": f"urn:li:person:{self.user_id}",
                "count": limit,
                "sortBy": "LAST_MODIFIED"
            }

            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/ugcPosts",
                    params=params,
                    headers=headers
                ) as response:
                    result = await response.json()

                    if response.status == 200:
                        posts = []
                        for post in result.get("elements", []):
                            post_data = {
                                "id": post.get("id"),
                                "text": post.get("specificContent", {}).get("com.linkedin.ugc.ShareContent", {}).get("shareCommentary", {}).get("text", ""),
                                "created_time": post.get("created", {}).get("time"),
                                "last_modified": post.get("lastModified", {}).get("time"),
                                "lifecycle_state": post.get("lifecycleState"),
                                "url": f"https://www.linkedin.com/feed/update/{post.get('id')}/" if post.get('id') else None
                            }
                            posts.append(post_data)

                        return posts
                    else:
                        logger.error(f"Failed to get user posts: {result}")
                        return []

        except Exception as e:
            logger.error(f"Error getting user posts: {e}")
            return []

    async def get_post_analytics(self, post_id: str) -> Dict:
        """Get analytics for a specific post"""
        try:
            if not self.access_token:
                return {}

            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }

            # Note: LinkedIn analytics API requires special permissions
            # This is a simplified version
            params = {
                "q": "ugcPost",
                "ugcPost": post_id
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/socialActions",
                    params=params,
                    headers=headers
                ) as response:
                    result = await response.json()

                    if response.status == 200:
                        # Process analytics data
                        analytics = {
                            "post_id": post_id,
                            "likes": 0,
                            "comments": 0,
                            "shares": 0,
                            "impressions": 0
                        }

                        # Parse LinkedIn analytics response
                        # This would need to be implemented based on actual API response structure

                        return analytics
                    else:
                        logger.error(f"Failed to get post analytics: {result}")
                        return {}

        except Exception as e:
            logger.error(f"Error getting post analytics: {e}")
            return {}

    async def search_content(self, keywords: List[str], limit: int = 20) -> List[Dict]:
        """Search for content on LinkedIn (limited by API access)"""
        try:
            # Note: LinkedIn's search API is very limited for third-party apps
            # This is a placeholder implementation

            content = []

            # In a real implementation, you might:
            # 1. Use LinkedIn's Company Pages API to get content from specific companies
            # 2. Use the Professional Community API if available
            # 3. Implement web scraping (with caution regarding terms of service)

            logger.info(f"LinkedIn content search not fully implemented for keywords: {keywords}")

            return content

        except Exception as e:
            logger.error(f"Error searching LinkedIn content: {e}")
            return []

    async def get_user_connections(self, limit: int = 100) -> List[Dict]:
        """Get user connections (requires additional permissions)"""
        try:
            if not self.access_token:
                return []

            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }

            params = {
                "count": limit,
                "start": 0
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/people/~/connections",
                    params=params,
                    headers=headers
                ) as response:
                    result = await response.json()

                    if response.status == 200:
                        connections = []
                        for connection in result.get("values", []):
                            connection_data = {
                                "id": connection.get("id"),
                                "first_name": connection.get("firstName"),
                                "last_name": connection.get("lastName"),
                                "headline": connection.get("headline"),
                                "industry": connection.get("industry"),
                                "location": connection.get("location", {}).get("name"),
                                "profile_url": connection.get("publicProfileUrl")
                            }
                            connections.append(connection_data)

                        return connections
                    else:
                        logger.error(f"Failed to get connections: {result}")
                        return []

        except Exception as e:
            logger.error(f"Error getting connections: {e}")
            return []

    async def discover_trending_content(self, keywords: List[str], limit: int = 50) -> List[Dict]:
        """Discover trending content based on keywords"""
        # LinkedIn's API is quite restrictive for content discovery
        # This would typically require:
        # 1. Company pages API access
        # 2. Professional community API access
        # 3. Or web scraping (with proper rate limiting and ToS compliance)

        trending_content = []

        logger.info(f"LinkedIn trending content discovery limited by API access for keywords: {keywords}")

        # Placeholder implementation - in production you might integrate with:
        # - LinkedIn Sales Navigator API (if available)
        # - Company pages you have access to
        # - Public posts from your network

        return trending_content[:limit]

    def is_configured(self) -> bool:
        """Check if LinkedIn API is properly configured"""
        return bool(self.client_id and self.client_secret and self.access_token)
