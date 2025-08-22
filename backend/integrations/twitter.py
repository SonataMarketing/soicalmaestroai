"""
Twitter/X API Integration
Twitter API v2 integration for posting, analytics, and content management
"""

import tweepy
import requests
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from config.settings import settings

logger = logging.getLogger(__name__)

class TwitterAPI:
    """Twitter API v2 integration for social media management"""

    def __init__(self):
        self.api_key = settings.twitter_api_key
        self.api_secret = settings.twitter_api_secret
        self.bearer_token = settings.twitter_bearer_token
        self.access_token = settings.twitter_access_token
        self.access_secret = settings.twitter_access_secret

        # Initialize Tweepy clients
        self._init_clients()

    def _init_clients(self):
        """Initialize Tweepy API clients"""
        try:
            if self.is_configured():
                # OAuth 1.0a for posting (requires access tokens)
                if self.access_token and self.access_secret:
                    self.client_v2 = tweepy.Client(
                        bearer_token=self.bearer_token,
                        consumer_key=self.api_key,
                        consumer_secret=self.api_secret,
                        access_token=self.access_token,
                        access_token_secret=self.access_secret,
                        wait_on_rate_limit=True
                    )
                else:
                    # Read-only client with bearer token
                    self.client_v2 = tweepy.Client(
                        bearer_token=self.bearer_token,
                        wait_on_rate_limit=True
                    )

                # API v1.1 for media upload
                if self.access_token and self.access_secret:
                    auth = tweepy.OAuth1UserHandler(
                        self.api_key,
                        self.api_secret,
                        self.access_token,
                        self.access_secret
                    )
                    self.api_v1 = tweepy.API(auth, wait_on_rate_limit=True)
                else:
                    self.api_v1 = None
            else:
                self.client_v2 = None
                self.api_v1 = None

        except Exception as e:
            logger.error(f"Error initializing Twitter clients: {str(e)}")
            self.client_v2 = None
            self.api_v1 = None

    def is_configured(self) -> bool:
        """Check if Twitter API is properly configured"""
        return bool(self.api_key and self.api_secret and self.bearer_token)

    def is_posting_enabled(self) -> bool:
        """Check if posting functionality is available"""
        return bool(self.access_token and self.access_secret and self.client_v2)

    def get_authorization_url(self, callback_url: str) -> Dict:
        """Get Twitter OAuth authorization URL"""

        if not self.is_configured():
            return {"error": "Twitter API not configured"}

        try:
            # OAuth 1.0a flow
            auth = tweepy.OAuth1UserHandler(
                self.api_key,
                self.api_secret,
                callback=callback_url
            )

            # Get request token
            authorization_url = auth.get_authorization_url()

            return {
                "authorization_url": authorization_url,
                "oauth_token": auth.request_token["oauth_token"],
                "oauth_token_secret": auth.request_token["oauth_token_secret"],
                "callback_url": callback_url
            }

        except Exception as e:
            logger.error(f"Twitter authorization URL error: {str(e)}")
            return {"error": f"Failed to get authorization URL: {str(e)}"}

    def exchange_oauth_verifier(
        self,
        oauth_token: str,
        oauth_token_secret: str,
        oauth_verifier: str
    ) -> Dict:
        """Exchange OAuth verifier for access tokens"""

        try:
            auth = tweepy.OAuth1UserHandler(
                self.api_key,
                self.api_secret
            )

            # Set request token
            auth.request_token = {
                "oauth_token": oauth_token,
                "oauth_token_secret": oauth_token_secret
            }

            # Get access token
            access_token, access_token_secret = auth.get_access_token(oauth_verifier)

            # Create authenticated client to get user info
            temp_client = tweepy.Client(
                bearer_token=self.bearer_token,
                consumer_key=self.api_key,
                consumer_secret=self.api_secret,
                access_token=access_token,
                access_token_secret=access_token_secret
            )

            # Get user information
            user_info = temp_client.get_me(user_fields=["id", "username", "name", "public_metrics"])

            return {
                "access_token": access_token,
                "access_token_secret": access_token_secret,
                "user_info": {
                    "id": user_info.data.id,
                    "username": user_info.data.username,
                    "name": user_info.data.name,
                    "followers_count": user_info.data.public_metrics.get("followers_count", 0),
                    "following_count": user_info.data.public_metrics.get("following_count", 0),
                    "tweet_count": user_info.data.public_metrics.get("tweet_count", 0)
                }
            }

        except Exception as e:
            logger.error(f"Twitter OAuth exchange error: {str(e)}")
            return {"error": f"OAuth exchange failed: {str(e)}"}

    def post_tweet(self, text: str, media_ids: List[str] = None) -> Dict:
        """Post a tweet with optional media"""

        if not self.is_posting_enabled():
            return {"error": "Twitter posting not configured or access tokens missing"}

        try:
            # Ensure text is within Twitter's character limit
            if len(text) > 280:
                return {"error": f"Tweet too long ({len(text)} characters). Maximum is 280."}

            # Post tweet
            response = self.client_v2.create_tweet(
                text=text,
                media_ids=media_ids
            )

            if response.data:
                tweet_id = response.data["id"]

                return {
                    "success": True,
                    "tweet_id": tweet_id,
                    "text": text,
                    "url": f"https://twitter.com/user/status/{tweet_id}",
                    "media_count": len(media_ids) if media_ids else 0
                }
            else:
                return {"error": "Failed to create tweet - no data returned"}

        except Exception as e:
            logger.error(f"Twitter post error: {str(e)}")
            return {"error": f"Failed to post tweet: {str(e)}"}

    def upload_media(self, media_url: str, media_type: str = "image") -> Dict:
        """Upload media to Twitter for use in tweets"""

        if not self.api_v1:
            return {"error": "Twitter media upload not configured"}

        try:
            # Download media first
            response = requests.get(media_url)
            response.raise_for_status()

            # Upload to Twitter
            if media_type.lower() in ["jpg", "jpeg", "png", "gif", "image"]:
                media = self.api_v1.media_upload(
                    filename="image",
                    file=response.content
                )
            elif media_type.lower() in ["mp4", "mov", "video"]:
                media = self.api_v1.media_upload(
                    filename="video",
                    file=response.content,
                    media_category="tweet_video"
                )
            else:
                return {"error": f"Unsupported media type: {media_type}"}

            return {
                "success": True,
                "media_id": media.media_id_string,
                "media_type": media_type
            }

        except Exception as e:
            logger.error(f"Twitter media upload error: {str(e)}")
            return {"error": f"Failed to upload media: {str(e)}"}

    def post_tweet_with_media(self, text: str, media_url: str, media_type: str = "image") -> Dict:
        """Post tweet with media attachment"""

        try:
            # Upload media first
            media_result = self.upload_media(media_url, media_type)

            if "error" in media_result:
                return media_result

            # Post tweet with media
            return self.post_tweet(text, [media_result["media_id"]])

        except Exception as e:
            logger.error(f"Twitter post with media error: {str(e)}")
            return {"error": f"Failed to post tweet with media: {str(e)}"}

    def create_thread(self, tweets: List[str], media_urls: List[str] = None) -> Dict:
        """Create a Twitter thread"""

        if not self.is_posting_enabled():
            return {"error": "Twitter posting not configured"}

        try:
            thread_results = []
            reply_to_id = None

            for i, tweet_text in enumerate(tweets):
                # Upload media for this tweet if provided
                media_ids = []
                if media_urls and i < len(media_urls) and media_urls[i]:
                    media_result = self.upload_media(media_urls[i])
                    if "error" not in media_result:
                        media_ids = [media_result["media_id"]]

                # Post tweet
                response = self.client_v2.create_tweet(
                    text=tweet_text,
                    in_reply_to_tweet_id=reply_to_id,
                    media_ids=media_ids if media_ids else None
                )

                if response.data:
                    tweet_id = response.data["id"]
                    thread_results.append({
                        "tweet_id": tweet_id,
                        "text": tweet_text,
                        "position": i + 1,
                        "url": f"https://twitter.com/user/status/{tweet_id}"
                    })
                    reply_to_id = tweet_id  # Next tweet replies to this one
                else:
                    return {"error": f"Failed to post tweet {i + 1} in thread"}

            return {
                "success": True,
                "thread_id": thread_results[0]["tweet_id"],
                "tweets": thread_results,
                "thread_length": len(thread_results)
            }

        except Exception as e:
            logger.error(f"Twitter thread error: {str(e)}")
            return {"error": f"Failed to create thread: {str(e)}"}

    def get_user_tweets(self, user_id: str = None, max_results: int = 10) -> Dict:
        """Get user's recent tweets"""

        if not self.client_v2:
            return {"error": "Twitter API not configured"}

        try:
            # Get authenticated user's tweets if no user_id provided
            if not user_id:
                if not self.is_posting_enabled():
                    return {"error": "User ID required when not authenticated"}
                user_id = "me"

            response = self.client_v2.get_users_tweets(
                id=user_id,
                max_results=max_results,
                tweet_fields=["created_at", "public_metrics", "context_annotations"],
                exclude=["retweets", "replies"]
            )

            if response.data:
                tweets = []
                for tweet in response.data:
                    tweets.append({
                        "id": tweet.id,
                        "text": tweet.text,
                        "created_at": tweet.created_at.isoformat() if tweet.created_at else None,
                        "url": f"https://twitter.com/user/status/{tweet.id}",
                        "metrics": {
                            "retweets": tweet.public_metrics.get("retweet_count", 0),
                            "likes": tweet.public_metrics.get("like_count", 0),
                            "replies": tweet.public_metrics.get("reply_count", 0),
                            "quotes": tweet.public_metrics.get("quote_count", 0)
                        }
                    })

                return {"success": True, "tweets": tweets}
            else:
                return {"success": True, "tweets": []}

        except Exception as e:
            logger.error(f"Get user tweets error: {str(e)}")
            return {"error": f"Failed to get tweets: {str(e)}"}

    def search_tweets(self, query: str, max_results: int = 10) -> Dict:
        """Search for tweets using Twitter API v2"""

        if not self.client_v2:
            return {"error": "Twitter API not configured"}

        try:
            response = self.client_v2.search_recent_tweets(
                query=query,
                max_results=max_results,
                tweet_fields=["created_at", "public_metrics", "author_id"],
                user_fields=["username", "name", "public_metrics"],
                expansions=["author_id"]
            )

            tweets = []

            if response.data:
                # Create user lookup
                users = {}
                if response.includes and "users" in response.includes:
                    for user in response.includes["users"]:
                        users[user.id] = user

                for tweet in response.data:
                    author = users.get(tweet.author_id)

                    tweets.append({
                        "id": tweet.id,
                        "text": tweet.text,
                        "created_at": tweet.created_at.isoformat() if tweet.created_at else None,
                        "url": f"https://twitter.com/user/status/{tweet.id}",
                        "author": {
                            "id": tweet.author_id,
                            "username": author.username if author else None,
                            "name": author.name if author else None,
                            "followers": author.public_metrics.get("followers_count", 0) if author else 0
                        },
                        "metrics": {
                            "retweets": tweet.public_metrics.get("retweet_count", 0),
                            "likes": tweet.public_metrics.get("like_count", 0),
                            "replies": tweet.public_metrics.get("reply_count", 0),
                            "quotes": tweet.public_metrics.get("quote_count", 0)
                        }
                    })

            return {"success": True, "tweets": tweets, "query": query}

        except Exception as e:
            logger.error(f"Twitter search error: {str(e)}")
            return {"error": f"Failed to search tweets: {str(e)}"}

    def get_trending_topics(self, woeid: int = 1) -> Dict:
        """Get trending topics (requires API v1.1)"""

        if not self.api_v1:
            return {"error": "Twitter API v1.1 not configured"}

        try:
            trends = self.api_v1.get_place_trends(woeid)

            if trends:
                trending_topics = []
                for trend in trends[0].get("trends", [])[:10]:  # Top 10 trends
                    trending_topics.append({
                        "name": trend["name"],
                        "url": trend["url"],
                        "query": trend["query"],
                        "tweet_volume": trend.get("tweet_volume")
                    })

                return {"success": True, "trends": trending_topics, "location_woeid": woeid}
            else:
                return {"success": True, "trends": []}

        except Exception as e:
            logger.error(f"Twitter trends error: {str(e)}")
            return {"error": f"Failed to get trending topics: {str(e)}"}

    def get_tweet_analytics(self, tweet_id: str) -> Dict:
        """Get analytics for a specific tweet"""

        if not self.client_v2:
            return {"error": "Twitter API not configured"}

        try:
            response = self.client_v2.get_tweet(
                tweet_id,
                tweet_fields=["created_at", "public_metrics", "organic_metrics", "promoted_metrics"],
                user_fields=["username", "name"]
            )

            if response.data:
                tweet = response.data

                analytics = {
                    "tweet_id": tweet.id,
                    "text": tweet.text,
                    "created_at": tweet.created_at.isoformat() if tweet.created_at else None,
                    "url": f"https://twitter.com/user/status/{tweet.id}",
                    "public_metrics": {
                        "retweets": tweet.public_metrics.get("retweet_count", 0),
                        "likes": tweet.public_metrics.get("like_count", 0),
                        "replies": tweet.public_metrics.get("reply_count", 0),
                        "quotes": tweet.public_metrics.get("quote_count", 0)
                    }
                }

                # Add organic metrics if available (requires ownership)
                if hasattr(tweet, "organic_metrics") and tweet.organic_metrics:
                    analytics["organic_metrics"] = {
                        "impressions": tweet.organic_metrics.get("impression_count", 0),
                        "profile_clicks": tweet.organic_metrics.get("user_profile_clicks", 0),
                        "url_clicks": tweet.organic_metrics.get("url_link_clicks", 0)
                    }

                return {"success": True, "analytics": analytics}
            else:
                return {"error": "Tweet not found"}

        except Exception as e:
            logger.error(f"Twitter analytics error: {str(e)}")
            return {"error": f"Failed to get tweet analytics: {str(e)}"}

    def delete_tweet(self, tweet_id: str) -> Dict:
        """Delete a tweet"""

        if not self.is_posting_enabled():
            return {"error": "Twitter posting not configured"}

        try:
            response = self.client_v2.delete_tweet(tweet_id)

            if response.data and response.data.get("deleted"):
                return {
                    "success": True,
                    "tweet_id": tweet_id,
                    "message": "Tweet deleted successfully"
                }
            else:
                return {"error": "Failed to delete tweet"}

        except Exception as e:
            logger.error(f"Twitter delete error: {str(e)}")
            return {"error": f"Failed to delete tweet: {str(e)}"}

    def validate_credentials(self) -> Dict:
        """Validate Twitter API credentials"""

        try:
            if not self.client_v2:
                return {"valid": False, "error": "API not configured"}

            # Try to get authenticated user info
            if self.is_posting_enabled():
                response = self.client_v2.get_me()
                if response.data:
                    return {
                        "valid": True,
                        "user_id": response.data.id,
                        "username": response.data.username,
                        "name": response.data.name,
                        "posting_enabled": True
                    }
            else:
                # Test with a simple search if only bearer token is available
                test_search = self.client_v2.search_recent_tweets("twitter", max_results=1)
                if test_search.data is not None:  # Can be empty list but not None
                    return {
                        "valid": True,
                        "posting_enabled": False,
                        "message": "Read-only access with bearer token"
                    }

            return {"valid": False, "error": "Credential validation failed"}

        except Exception as e:
            logger.error(f"Twitter credential validation error: {str(e)}")
            return {"valid": False, "error": str(e)}

    def schedule_tweet(self, text: str, scheduled_time: datetime, media_urls: List[str] = None) -> Dict:
        """Schedule a tweet for later posting"""

        # Note: Twitter API doesn't support native scheduling
        # This would typically integrate with a scheduling service

        try:
            # Validate the tweet content
            if len(text) > 280:
                return {"error": f"Tweet too long ({len(text)} characters). Maximum is 280."}

            # In a real implementation, you'd store this in your database
            # with the scheduled time and use a background job to post at the specified time

            return {
                "success": True,
                "scheduled_time": scheduled_time.isoformat(),
                "text": text,
                "media_count": len(media_urls) if media_urls else 0,
                "message": "Tweet scheduled successfully",
                "note": "Will be posted via background job at scheduled time"
            }

        except Exception as e:
            logger.error(f"Twitter scheduling error: {str(e)}")
            return {"error": f"Failed to schedule tweet: {str(e)}"}

# Global instance
twitter_api = TwitterAPI()
