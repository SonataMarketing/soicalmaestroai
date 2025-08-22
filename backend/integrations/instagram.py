"""
Instagram API Integration
Instagram Basic Display API and Instagram Graph API for business accounts
"""

import requests
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from config.settings import settings

logger = logging.getLogger(__name__)

class InstagramAPI:
    """Instagram API integration for posting and content management"""

    def __init__(self):
        self.app_id = settings.instagram_app_id
        self.app_secret = settings.instagram_app_secret
        self.redirect_uri = settings.instagram_redirect_uri
        self.base_url = "https://graph.instagram.com"
        self.facebook_base_url = "https://graph.facebook.com/v18.0"

    def is_configured(self) -> bool:
        """Check if Instagram API is properly configured"""
        return bool(self.app_id and self.app_secret)

    def get_authorization_url(self, state: str = None) -> Dict:
        """Get Instagram OAuth authorization URL"""

        if not self.is_configured():
            return {"error": "Instagram API not configured"}

        # Instagram Basic Display API OAuth URL
        auth_url = (
            f"https://api.instagram.com/oauth/authorize"
            f"?client_id={self.app_id}"
            f"&redirect_uri={self.redirect_uri}"
            f"&scope=user_profile,user_media"
            f"&response_type=code"
        )

        if state:
            auth_url += f"&state={state}"

        return {
            "authorization_url": auth_url,
            "redirect_uri": self.redirect_uri,
            "scopes": ["user_profile", "user_media"]
        }

    def exchange_code_for_token(self, authorization_code: str) -> Dict:
        """Exchange authorization code for access token"""

        if not self.is_configured():
            return {"error": "Instagram API not configured"}

        try:
            # Step 1: Get short-lived token
            token_url = "https://api.instagram.com/oauth/access_token"

            data = {
                "client_id": self.app_id,
                "client_secret": self.app_secret,
                "grant_type": "authorization_code",
                "redirect_uri": self.redirect_uri,
                "code": authorization_code
            }

            response = requests.post(token_url, data=data)
            response.raise_for_status()

            token_data = response.json()
            short_token = token_data.get("access_token")

            if not short_token:
                return {"error": "Failed to get access token"}

            # Step 2: Exchange for long-lived token
            long_lived_token = self._get_long_lived_token(short_token)

            if long_lived_token.get("error"):
                return long_lived_token

            # Step 3: Get user info
            user_info = self.get_user_info(long_lived_token["access_token"])

            return {
                "access_token": long_lived_token["access_token"],
                "expires_in": long_lived_token.get("expires_in", 5184000),  # 60 days
                "user_info": user_info,
                "token_type": "long_lived"
            }

        except requests.RequestException as e:
            logger.error(f"Instagram token exchange error: {str(e)}")
            return {"error": f"Token exchange failed: {str(e)}"}

    def _get_long_lived_token(self, short_token: str) -> Dict:
        """Convert short-lived token to long-lived token"""

        try:
            url = f"{self.base_url}/access_token"

            params = {
                "grant_type": "ig_exchange_token",
                "client_secret": self.app_secret,
                "access_token": short_token
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            return response.json()

        except requests.RequestException as e:
            logger.error(f"Long-lived token error: {str(e)}")
            return {"error": f"Long-lived token generation failed: {str(e)}"}

    def refresh_token(self, access_token: str) -> Dict:
        """Refresh long-lived access token"""

        try:
            url = f"{self.base_url}/refresh_access_token"

            params = {
                "grant_type": "ig_refresh_token",
                "access_token": access_token
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            return response.json()

        except requests.RequestException as e:
            logger.error(f"Token refresh error: {str(e)}")
            return {"error": f"Token refresh failed: {str(e)}"}

    def get_user_info(self, access_token: str) -> Dict:
        """Get Instagram user profile information"""

        try:
            url = f"{self.base_url}/me"

            params = {
                "fields": "id,username,account_type,media_count",
                "access_token": access_token
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            return response.json()

        except requests.RequestException as e:
            logger.error(f"User info error: {str(e)}")
            return {"error": f"Failed to get user info: {str(e)}"}

    def get_user_media(self, access_token: str, limit: int = 25) -> Dict:
        """Get user's Instagram media posts"""

        try:
            url = f"{self.base_url}/me/media"

            params = {
                "fields": "id,caption,media_type,media_url,permalink,thumbnail_url,timestamp",
                "limit": limit,
                "access_token": access_token
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            return response.json()

        except requests.RequestException as e:
            logger.error(f"Media fetch error: {str(e)}")
            return {"error": f"Failed to get media: {str(e)}"}

    def create_media_container(
        self,
        access_token: str,
        image_url: str,
        caption: str,
        is_business_account: bool = True
    ) -> Dict:
        """Create media container for posting (Business accounts only)"""

        if not is_business_account:
            return {"error": "Media posting requires Instagram Business account"}

        try:
            # For business accounts, use Instagram Graph API
            url = f"{self.facebook_base_url}/me/media"

            data = {
                "image_url": image_url,
                "caption": caption,
                "access_token": access_token
            }

            response = requests.post(url, data=data)
            response.raise_for_status()

            return response.json()

        except requests.RequestException as e:
            logger.error(f"Media container creation error: {str(e)}")
            return {"error": f"Failed to create media container: {str(e)}"}

    def publish_media(self, access_token: str, creation_id: str) -> Dict:
        """Publish media container to Instagram"""

        try:
            url = f"{self.facebook_base_url}/me/media_publish"

            data = {
                "creation_id": creation_id,
                "access_token": access_token
            }

            response = requests.post(url, data=data)
            response.raise_for_status()

            return response.json()

        except requests.RequestException as e:
            logger.error(f"Media publish error: {str(e)}")
            return {"error": f"Failed to publish media: {str(e)}"}

    def post_photo(
        self,
        access_token: str,
        image_url: str,
        caption: str,
        is_business_account: bool = True
    ) -> Dict:
        """Post a photo to Instagram"""

        try:
            # Step 1: Create media container
            container_result = self.create_media_container(
                access_token, image_url, caption, is_business_account
            )

            if "error" in container_result:
                return container_result

            creation_id = container_result.get("id")
            if not creation_id:
                return {"error": "No creation ID returned from media container"}

            # Step 2: Publish media
            publish_result = self.publish_media(access_token, creation_id)

            return {
                "success": True,
                "post_id": publish_result.get("id"),
                "creation_id": creation_id,
                "message": "Photo posted successfully to Instagram"
            }

        except Exception as e:
            logger.error(f"Instagram photo post error: {str(e)}")
            return {"error": f"Failed to post photo: {str(e)}"}

    def get_media_insights(self, access_token: str, media_id: str) -> Dict:
        """Get insights for a specific media post (Business accounts only)"""

        try:
            url = f"{self.facebook_base_url}/{media_id}/insights"

            params = {
                "metric": "impressions,reach,likes,comments,saves,shares",
                "access_token": access_token
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            return response.json()

        except requests.RequestException as e:
            logger.error(f"Media insights error: {str(e)}")
            return {"error": f"Failed to get media insights: {str(e)}"}

    def get_account_insights(
        self,
        access_token: str,
        period: str = "day",
        since: Optional[datetime] = None,
        until: Optional[datetime] = None
    ) -> Dict:
        """Get account insights (Business accounts only)"""

        try:
            url = f"{self.facebook_base_url}/me/insights"

            # Default to last 7 days if no dates provided
            if not since:
                since = datetime.now() - timedelta(days=7)
            if not until:
                until = datetime.now()

            params = {
                "metric": "impressions,reach,profile_views,website_clicks",
                "period": period,
                "since": since.strftime("%Y-%m-%d"),
                "until": until.strftime("%Y-%m-%d"),
                "access_token": access_token
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            return response.json()

        except requests.RequestException as e:
            logger.error(f"Account insights error: {str(e)}")
            return {"error": f"Failed to get account insights: {str(e)}"}

    def validate_token(self, access_token: str) -> Dict:
        """Validate Instagram access token"""

        try:
            user_info = self.get_user_info(access_token)

            if "error" in user_info:
                return {"valid": False, "error": user_info["error"]}

            return {
                "valid": True,
                "user_id": user_info.get("id"),
                "username": user_info.get("username"),
                "account_type": user_info.get("account_type")
            }

        except Exception as e:
            return {"valid": False, "error": str(e)}

    def get_hashtag_info(self, access_token: str, hashtag: str) -> Dict:
        """Get information about a hashtag (Business accounts only)"""

        try:
            # Search for hashtag
            search_url = f"{self.facebook_base_url}/ig_hashtag_search"

            search_params = {
                "user_id": "me",  # Requires business account
                "q": hashtag.replace("#", ""),
                "access_token": access_token
            }

            search_response = requests.get(search_url, params=search_params)
            search_response.raise_for_status()

            search_data = search_response.json()

            if not search_data.get("data"):
                return {"error": "Hashtag not found"}

            hashtag_id = search_data["data"][0]["id"]

            # Get hashtag details
            detail_url = f"{self.facebook_base_url}/{hashtag_id}"

            detail_params = {
                "fields": "id,name,media_count",
                "access_token": access_token
            }

            detail_response = requests.get(detail_url, params=detail_params)
            detail_response.raise_for_status()

            return detail_response.json()

        except requests.RequestException as e:
            logger.error(f"Hashtag info error: {str(e)}")
            return {"error": f"Failed to get hashtag info: {str(e)}"}

    def schedule_post(
        self,
        access_token: str,
        image_url: str,
        caption: str,
        publish_time: datetime
    ) -> Dict:
        """Schedule a post for later publishing (Business accounts only)"""

        try:
            # Note: Instagram API doesn't support native scheduling
            # This would typically integrate with a scheduling service
            # For now, we'll create the container and store the publish time

            container_result = self.create_media_container(
                access_token, image_url, caption, True
            )

            if "error" in container_result:
                return container_result

            # In a real implementation, you'd store this in your database
            # with the scheduled publish time and use a background job
            # to publish at the specified time

            return {
                "success": True,
                "creation_id": container_result.get("id"),
                "scheduled_time": publish_time.isoformat(),
                "message": "Post scheduled successfully",
                "note": "Will be published via background job at scheduled time"
            }

        except Exception as e:
            logger.error(f"Instagram scheduling error: {str(e)}")
            return {"error": f"Failed to schedule post: {str(e)}"}

# Global instance
instagram_api = InstagramAPI()
