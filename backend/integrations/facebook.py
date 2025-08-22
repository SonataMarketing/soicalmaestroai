"""
Facebook API Integration
Facebook Graph API integration for page posting, analytics, and content management
"""

import requests
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from config.settings import settings

logger = logging.getLogger(__name__)

class FacebookAPI:
    """Facebook Graph API integration for social media management"""

    def __init__(self):
        self.app_id = settings.facebook_app_id
        self.app_secret = settings.facebook_app_secret
        self.redirect_uri = settings.facebook_redirect_uri
        self.base_url = "https://graph.facebook.com/v18.0"

    def is_configured(self) -> bool:
        """Check if Facebook API is properly configured"""
        return bool(self.app_id and self.app_secret)

    def get_authorization_url(self, state: str = None) -> Dict:
        """Get Facebook OAuth authorization URL"""

        if not self.is_configured():
            return {"error": "Facebook API not configured"}

        # Facebook OAuth scopes for page management
        scopes = [
            "pages_show_list",
            "pages_read_engagement",
            "pages_manage_posts",
            "pages_manage_engagement",
            "public_profile"
        ]

        auth_url = (
            f"https://www.facebook.com/v18.0/dialog/oauth"
            f"?client_id={self.app_id}"
            f"&redirect_uri={self.redirect_uri}"
            f"&scope={','.join(scopes)}"
            f"&response_type=code"
        )

        if state:
            auth_url += f"&state={state}"

        return {
            "authorization_url": auth_url,
            "redirect_uri": self.redirect_uri,
            "scopes": scopes
        }

    def exchange_code_for_token(self, authorization_code: str) -> Dict:
        """Exchange authorization code for access token"""

        if not self.is_configured():
            return {"error": "Facebook API not configured"}

        try:
            # Step 1: Get short-lived user access token
            token_url = f"{self.base_url}/oauth/access_token"

            params = {
                "client_id": self.app_id,
                "client_secret": self.app_secret,
                "redirect_uri": self.redirect_uri,
                "code": authorization_code
            }

            response = requests.get(token_url, params=params)
            response.raise_for_status()

            token_data = response.json()
            short_token = token_data.get("access_token")

            if not short_token:
                return {"error": "Failed to get access token"}

            # Step 2: Exchange for long-lived token
            long_lived_token = self._get_long_lived_token(short_token)

            if "error" in long_lived_token:
                return long_lived_token

            # Step 3: Get user info and pages
            user_info = self.get_user_info(long_lived_token["access_token"])
            pages = self.get_user_pages(long_lived_token["access_token"])

            return {
                "access_token": long_lived_token["access_token"],
                "expires_in": long_lived_token.get("expires_in"),
                "user_info": user_info,
                "pages": pages,
                "token_type": "long_lived"
            }

        except requests.RequestException as e:
            logger.error(f"Facebook token exchange error: {str(e)}")
            return {"error": f"Token exchange failed: {str(e)}"}

    def _get_long_lived_token(self, short_token: str) -> Dict:
        """Convert short-lived token to long-lived token"""

        try:
            url = f"{self.base_url}/oauth/access_token"

            params = {
                "grant_type": "fb_exchange_token",
                "client_id": self.app_id,
                "client_secret": self.app_secret,
                "fb_exchange_token": short_token
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            return response.json()

        except requests.RequestException as e:
            logger.error(f"Long-lived token error: {str(e)}")
            return {"error": f"Long-lived token generation failed: {str(e)}"}

    def get_user_info(self, access_token: str) -> Dict:
        """Get Facebook user information"""

        try:
            url = f"{self.base_url}/me"

            params = {
                "fields": "id,name,email",
                "access_token": access_token
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            return response.json()

        except requests.RequestException as e:
            logger.error(f"User info error: {str(e)}")
            return {"error": f"Failed to get user info: {str(e)}"}

    def get_user_pages(self, access_token: str) -> List[Dict]:
        """Get user's Facebook pages with management permissions"""

        try:
            url = f"{self.base_url}/me/accounts"

            params = {
                "fields": "id,name,access_token,category,fan_count,picture,is_published",
                "access_token": access_token
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            return data.get("data", [])

        except requests.RequestException as e:
            logger.error(f"Get pages error: {str(e)}")
            return []

    def post_to_page(
        self,
        page_id: str,
        page_access_token: str,
        message: str,
        link: str = None,
        image_url: str = None
    ) -> Dict:
        """Post message to Facebook page"""

        try:
            url = f"{self.base_url}/{page_id}/feed"

            data = {
                "message": message,
                "access_token": page_access_token
            }

            # Add link if provided
            if link:
                data["link"] = link

            # Add image if provided
            if image_url:
                # For images, we use the photos endpoint
                return self.post_photo_to_page(page_id, page_access_token, image_url, message)

            response = requests.post(url, data=data)
            response.raise_for_status()

            result = response.json()

            return {
                "success": True,
                "post_id": result.get("id"),
                "message": "Post published successfully to Facebook"
            }

        except requests.RequestException as e:
            logger.error(f"Facebook post error: {str(e)}")
            return {"error": f"Failed to post to Facebook: {str(e)}"}

    def post_photo_to_page(
        self,
        page_id: str,
        page_access_token: str,
        image_url: str,
        caption: str = ""
    ) -> Dict:
        """Post photo to Facebook page"""

        try:
            url = f"{self.base_url}/{page_id}/photos"

            data = {
                "url": image_url,
                "caption": caption,
                "access_token": page_access_token
            }

            response = requests.post(url, data=data)
            response.raise_for_status()

            result = response.json()

            return {
                "success": True,
                "post_id": result.get("id"),
                "photo_id": result.get("post_id"),
                "message": "Photo posted successfully to Facebook"
            }

        except requests.RequestException as e:
            logger.error(f"Facebook photo post error: {str(e)}")
            return {"error": f"Failed to post photo to Facebook: {str(e)}"}

    def upload_video_to_page(
        self,
        page_id: str,
        page_access_token: str,
        video_url: str,
        title: str = "",
        description: str = ""
    ) -> Dict:
        """Upload video to Facebook page"""

        try:
            # Download video first
            video_response = requests.get(video_url)
            video_response.raise_for_status()

            url = f"{self.base_url}/{page_id}/videos"

            files = {
                "source": ("video.mp4", video_response.content, "video/mp4")
            }

            data = {
                "title": title,
                "description": description,
                "access_token": page_access_token
            }

            response = requests.post(url, files=files, data=data)
            response.raise_for_status()

            result = response.json()

            return {
                "success": True,
                "video_id": result.get("id"),
                "message": "Video uploaded successfully to Facebook"
            }

        except requests.RequestException as e:
            logger.error(f"Facebook video upload error: {str(e)}")
            return {"error": f"Failed to upload video to Facebook: {str(e)}"}

    def get_page_posts(
        self,
        page_id: str,
        page_access_token: str,
        limit: int = 25
    ) -> Dict:
        """Get posts from Facebook page"""

        try:
            url = f"{self.base_url}/{page_id}/posts"

            params = {
                "fields": "id,message,story,created_time,type,status_type,permalink_url,insights.metric(post_impressions,post_engaged_users,post_clicks)",
                "limit": limit,
                "access_token": page_access_token
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            posts = []

            for post in data.get("data", []):
                post_data = {
                    "id": post.get("id"),
                    "message": post.get("message", ""),
                    "story": post.get("story", ""),
                    "created_time": post.get("created_time"),
                    "type": post.get("type"),
                    "status_type": post.get("status_type"),
                    "permalink_url": post.get("permalink_url"),
                    "insights": {}
                }

                # Extract insights if available
                if "insights" in post and "data" in post["insights"]:
                    for insight in post["insights"]["data"]:
                        metric_name = insight.get("name")
                        metric_values = insight.get("values", [])
                        if metric_values:
                            post_data["insights"][metric_name] = metric_values[0].get("value", 0)

                posts.append(post_data)

            return {"success": True, "posts": posts}

        except requests.RequestException as e:
            logger.error(f"Get page posts error: {str(e)}")
            return {"error": f"Failed to get page posts: {str(e)}"}

    def get_post_insights(
        self,
        post_id: str,
        page_access_token: str
    ) -> Dict:
        """Get insights for a specific Facebook post"""

        try:
            url = f"{self.base_url}/{post_id}/insights"

            params = {
                "metric": "post_impressions,post_engaged_users,post_clicks,post_reactions_by_type_total",
                "access_token": page_access_token
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            insights = {}

            for insight in data.get("data", []):
                metric_name = insight.get("name")
                metric_values = insight.get("values", [])
                if metric_values:
                    insights[metric_name] = metric_values[0].get("value", 0)

            return {"success": True, "insights": insights}

        except requests.RequestException as e:
            logger.error(f"Post insights error: {str(e)}")
            return {"error": f"Failed to get post insights: {str(e)}"}

    def get_page_insights(
        self,
        page_id: str,
        page_access_token: str,
        period: str = "day",
        since: Optional[datetime] = None,
        until: Optional[datetime] = None
    ) -> Dict:
        """Get page insights and analytics"""

        try:
            url = f"{self.base_url}/{page_id}/insights"

            # Default to last 7 days if no dates provided
            if not since:
                since = datetime.now() - timedelta(days=7)
            if not until:
                until = datetime.now()

            params = {
                "metric": "page_impressions,page_engaged_users,page_fan_adds,page_fan_removes,page_views_total",
                "period": period,
                "since": since.strftime("%Y-%m-%d"),
                "until": until.strftime("%Y-%m-%d"),
                "access_token": page_access_token
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            insights = {}

            for insight in data.get("data", []):
                metric_name = insight.get("name")
                metric_values = insight.get("values", [])
                if metric_values:
                    # Get the latest value
                    insights[metric_name] = metric_values[-1].get("value", 0)

            return {"success": True, "insights": insights, "period": period}

        except requests.RequestException as e:
            logger.error(f"Page insights error: {str(e)}")
            return {"error": f"Failed to get page insights: {str(e)}"}

    def schedule_post(
        self,
        page_id: str,
        page_access_token: str,
        message: str,
        scheduled_time: datetime,
        link: str = None,
        image_url: str = None
    ) -> Dict:
        """Schedule a post for later publishing"""

        try:
            # Facebook requires Unix timestamp for scheduled publishing
            scheduled_timestamp = int(scheduled_time.timestamp())

            url = f"{self.base_url}/{page_id}/feed"

            data = {
                "message": message,
                "scheduled_publish_time": scheduled_timestamp,
                "published": "false",  # This makes it scheduled
                "access_token": page_access_token
            }

            # Add link if provided
            if link:
                data["link"] = link

            # For images with scheduled posts, we need to upload first
            if image_url:
                # Upload image first to get attachment
                upload_result = self._upload_image_for_scheduling(
                    page_id, page_access_token, image_url
                )
                if "error" not in upload_result:
                    data["object_attachment"] = upload_result["id"]

            response = requests.post(url, data=data)
            response.raise_for_status()

            result = response.json()

            return {
                "success": True,
                "post_id": result.get("id"),
                "scheduled_time": scheduled_time.isoformat(),
                "message": "Post scheduled successfully for Facebook"
            }

        except requests.RequestException as e:
            logger.error(f"Facebook scheduling error: {str(e)}")
            return {"error": f"Failed to schedule Facebook post: {str(e)}"}

    def _upload_image_for_scheduling(
        self,
        page_id: str,
        page_access_token: str,
        image_url: str
    ) -> Dict:
        """Upload image for scheduled posts"""

        try:
            # Download image
            image_response = requests.get(image_url)
            image_response.raise_for_status()

            url = f"{self.base_url}/{page_id}/photos"

            files = {
                "source": ("image.jpg", image_response.content, "image/jpeg")
            }

            data = {
                "published": "false",  # Don't publish, just upload
                "access_token": page_access_token
            }

            response = requests.post(url, files=files, data=data)
            response.raise_for_status()

            return response.json()

        except requests.RequestException as e:
            logger.error(f"Image upload error: {str(e)}")
            return {"error": f"Failed to upload image: {str(e)}"}

    def delete_post(self, post_id: str, page_access_token: str) -> Dict:
        """Delete a Facebook post"""

        try:
            url = f"{self.base_url}/{post_id}"

            params = {
                "access_token": page_access_token
            }

            response = requests.delete(url, params=params)
            response.raise_for_status()

            result = response.json()

            if result.get("success"):
                return {
                    "success": True,
                    "post_id": post_id,
                    "message": "Post deleted successfully"
                }
            else:
                return {"error": "Failed to delete post"}

        except requests.RequestException as e:
            logger.error(f"Facebook delete error: {str(e)}")
            return {"error": f"Failed to delete post: {str(e)}"}

    def get_page_info(self, page_id: str, page_access_token: str) -> Dict:
        """Get detailed information about a Facebook page"""

        try:
            url = f"{self.base_url}/{page_id}"

            params = {
                "fields": "id,name,category,description,fan_count,engagement,picture,cover,website,phone,location",
                "access_token": page_access_token
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            return {"success": True, "page_info": response.json()}

        except requests.RequestException as e:
            logger.error(f"Get page info error: {str(e)}")
            return {"error": f"Failed to get page info: {str(e)}"}

    def validate_token(self, access_token: str) -> Dict:
        """Validate Facebook access token"""

        try:
            user_info = self.get_user_info(access_token)

            if "error" in user_info:
                return {"valid": False, "error": user_info["error"]}

            pages = self.get_user_pages(access_token)

            return {
                "valid": True,
                "user_id": user_info.get("id"),
                "user_name": user_info.get("name"),
                "pages_count": len(pages)
            }

        except Exception as e:
            return {"valid": False, "error": str(e)}

    def create_lead_ad(
        self,
        page_id: str,
        page_access_token: str,
        name: str,
        objective: str = "LEAD_GENERATION"
    ) -> Dict:
        """Create a lead generation ad campaign (basic setup)"""

        try:
            # This is a simplified version - full implementation would require
            # campaign creation, ad set creation, and ad creative setup

            url = f"{self.base_url}/{page_id}/campaigns"

            data = {
                "name": name,
                "objective": objective,
                "status": "PAUSED",  # Start paused for review
                "access_token": page_access_token
            }

            response = requests.post(url, data=data)
            response.raise_for_status()

            result = response.json()

            return {
                "success": True,
                "campaign_id": result.get("id"),
                "message": "Lead ad campaign created successfully"
            }

        except requests.RequestException as e:
            logger.error(f"Lead ad creation error: {str(e)}")
            return {"error": f"Failed to create lead ad: {str(e)}"}

    def get_comments(self, post_id: str, page_access_token: str) -> Dict:
        """Get comments for a Facebook post"""

        try:
            url = f"{self.base_url}/{post_id}/comments"

            params = {
                "fields": "id,message,created_time,from,like_count,comment_count",
                "access_token": page_access_token
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json()

            return {"success": True, "comments": data.get("data", [])}

        except requests.RequestException as e:
            logger.error(f"Get comments error: {str(e)}")
            return {"error": f"Failed to get comments: {str(e)}"}

    def reply_to_comment(
        self,
        comment_id: str,
        page_access_token: str,
        message: str
    ) -> Dict:
        """Reply to a comment on Facebook"""

        try:
            url = f"{self.base_url}/{comment_id}/comments"

            data = {
                "message": message,
                "access_token": page_access_token
            }

            response = requests.post(url, data=data)
            response.raise_for_status()

            result = response.json()

            return {
                "success": True,
                "reply_id": result.get("id"),
                "message": "Reply posted successfully"
            }

        except requests.RequestException as e:
            logger.error(f"Reply to comment error: {str(e)}")
            return {"error": f"Failed to reply to comment: {str(e)}"}

# Global instance
facebook_api = FacebookAPI()
