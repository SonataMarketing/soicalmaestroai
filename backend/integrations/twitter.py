"""
Twitter API Integration
Real API integration using Twitter API v2 for posting and analytics
"""

import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
import aiohttp
import tweepy
from urllib.parse import urlencode

from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class TwitterAPI:
    """Twitter API v2 client"""

    def __init__(self):
        self.api_key = settings.twitter_api_key
        self.api_secret = settings.twitter_api_secret
        self.access_token = settings.twitter_access_token
        self.access_token_secret = settings.twitter_access_token_secret
        self.bearer_token = settings.twitter_bearer_token

        # Initialize Tweepy client
        try:
            if all([self.api_key, self.api_secret, self.access_token, self.access_token_secret]):
                self.client = tweepy.Client(
                    bearer_token=self.bearer_token,
                    consumer_key=self.api_key,
                    consumer_secret=self.api_secret,
                    access_token=self.access_token,
                    access_token_secret=self.access_token_secret,
                    wait_on_rate_limit=True
                )

                # Test the connection
                me = self.client.get_me()
                self.user_id = me.data.id if me.data else None
                logger.info(f"Twitter API initialized successfully for user: {me.data.username if me.data else 'Unknown'}")
            else:
                self.client = None
                self.user_id = None
                logger.warning("Twitter API credentials not configured")

        except Exception as e:
            logger.error(f"Failed to initialize Twitter API: {e}")
            self.client = None
            self.user_id = None

    async def post_tweet(self, text: str) -> Dict:
        """Post a text-only tweet"""
        try:
            if not self.client:
                return {"error": "Twitter API not configured", "success": False}

            # Ensure text is within Twitter's character limit
            if len(text) > 280:
                text = text[:277] + "..."

            response = self.client.create_tweet(text=text)

            if response.data:
                tweet_id = response.data['id']
                return {
                    "success": True,
                    "tweet_id": tweet_id,
                    "tweet_url": f"https://twitter.com/user/status/{tweet_id}"
                }
            else:
                return {"error": "Failed to create tweet", "success": False}

        except Exception as e:
            logger.error(f"Error posting tweet: {e}")
            return {"error": str(e), "success": False}

    async def post_with_media(self, text: str, media_url: str) -> Dict:
        """Post tweet with media attachment"""
        try:
            if not self.client:
                return {"error": "Twitter API not configured", "success": False}

            # First, upload the media
            media_id = await self._upload_media(media_url)

            if not media_id:
                return {"error": "Failed to upload media", "success": False}

            # Ensure text is within character limit
            if len(text) > 280:
                text = text[:277] + "..."

            # Create tweet with media
            response = self.client.create_tweet(text=text, media_ids=[media_id])

            if response.data:
                tweet_id = response.data['id']
                return {
                    "success": True,
                    "tweet_id": tweet_id,
                    "tweet_url": f"https://twitter.com/user/status/{tweet_id}",
                    "media_id": media_id
                }
            else:
                return {"error": "Failed to create tweet with media", "success": False}

        except Exception as e:
            logger.error(f"Error posting tweet with media: {e}")
            return {"error": str(e), "success": False}

    async def _upload_media(self, media_url: str) -> Optional[str]:
        """Upload media to Twitter and return media ID"""
        try:
            # Download media from URL
            async with aiohttp.ClientSession() as session:
                async with session.get(media_url) as response:
                    if response.status != 200:
                        logger.error(f"Failed to download media from {media_url}")
                        return None

                    media_data = await response.read()
                    content_type = response.headers.get('content-type', '')

            # Use Tweepy's media upload
            # Note: This is simplified - in production you'd handle different media types
            api = tweepy.API(tweepy.OAuth1UserHandler(
                self.api_key, self.api_secret,
                self.access_token, self.access_token_secret
            ))

            # Save media temporarily and upload
            import tempfile
            import os

            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(media_data)
                temp_file_path = temp_file.name

            try:
                media = api.media_upload(temp_file_path)
                return media.media_id_string
            finally:
                os.unlink(temp_file_path)

        except Exception as e:
            logger.error(f"Error uploading media to Twitter: {e}")
            return None

    async def get_tweet_metrics(self, tweet_id: str) -> Dict:
        """Get metrics for a specific tweet"""
        try:
            if not self.client:
                return {}

            tweet = self.client.get_tweet(
                tweet_id,
                tweet_fields=['public_metrics', 'created_at', 'context_annotations']
            )

            if tweet.data:
                metrics = tweet.data.public_metrics
                return {
                    "tweet_id": tweet_id,
                    "retweet_count": metrics.get('retweet_count', 0),
                    "like_count": metrics.get('like_count', 0),
                    "reply_count": metrics.get('reply_count', 0),
                    "quote_count": metrics.get('quote_count', 0),
                    "impression_count": metrics.get('impression_count', 0),
                    "created_at": tweet.data.created_at.isoformat() if tweet.data.created_at else None
                }
            else:
                return {}

        except Exception as e:
            logger.error(f"Error getting tweet metrics: {e}")
            return {}

    async def get_user_tweets(self, limit: int = 10) -> List[Dict]:
        """Get user's recent tweets"""
        try:
            if not self.client or not self.user_id:
                return []

            tweets = self.client.get_users_tweets(
                self.user_id,
                max_results=limit,
                tweet_fields=['public_metrics', 'created_at', 'context_annotations']
            )

            tweet_list = []
            if tweets.data:
                for tweet in tweets.data:
                    tweet_data = {
                        "id": tweet.id,
                        "text": tweet.text,
                        "created_at": tweet.created_at.isoformat() if tweet.created_at else None,
                        "metrics": tweet.public_metrics if hasattr(tweet, 'public_metrics') else {},
                        "url": f"https://twitter.com/user/status/{tweet.id}"
                    }
                    tweet_list.append(tweet_data)

            return tweet_list

        except Exception as e:
            logger.error(f"Error getting user tweets: {e}")
            return []

    async def search_tweets(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for tweets"""
        try:
            if not self.client:
                return []

            tweets = self.client.search_recent_tweets(
                query=query,
                max_results=limit,
                tweet_fields=['public_metrics', 'created_at', 'author_id']
            )

            tweet_list = []
            if tweets.data:
                for tweet in tweets.data:
                    tweet_data = {
                        "id": tweet.id,
                        "text": tweet.text,
                        "author_id": tweet.author_id,
                        "created_at": tweet.created_at.isoformat() if tweet.created_at else None,
                        "metrics": tweet.public_metrics if hasattr(tweet, 'public_metrics') else {},
                        "url": f"https://twitter.com/user/status/{tweet.id}"
                    }
                    tweet_list.append(tweet_data)

            return tweet_list

        except Exception as e:
            logger.error(f"Error searching tweets: {e}")
            return []

    async def get_trending_topics(self, woeid: int = 1) -> List[Dict]:
        """Get trending topics (requires API v1.1)"""
        try:
            # This requires the old API v1.1
            api = tweepy.API(tweepy.OAuth1UserHandler(
                self.api_key, self.api_secret,
                self.access_token, self.access_token_secret
            ))

            trends = api.get_place_trends(woeid)

            trending_list = []
            if trends:
                for trend in trends[0]['trends'][:10]:  # Top 10 trends
                    trending_list.append({
                        "name": trend['name'],
                        "url": trend['url'],
                        "tweet_volume": trend.get('tweet_volume'),
                        "promoted_content": trend.get('promoted_content')
                    })

            return trending_list

        except Exception as e:
            logger.error(f"Error getting trending topics: {e}")
            return []

    async def delete_tweet(self, tweet_id: str) -> Dict:
        """Delete a tweet"""
        try:
            if not self.client:
                return {"error": "Twitter API not configured", "success": False}

            response = self.client.delete_tweet(tweet_id)

            if response.data and response.data.get('deleted'):
                return {"success": True, "tweet_id": tweet_id}
            else:
                return {"error": "Failed to delete tweet", "success": False}

        except Exception as e:
            logger.error(f"Error deleting tweet: {e}")
            return {"error": str(e), "success": False}

    async def get_user_info(self) -> Dict:
        """Get authenticated user information"""
        try:
            if not self.client:
                return {}

            user = self.client.get_me(
                user_fields=['public_metrics', 'created_at', 'description', 'location', 'verified']
            )

            if user.data:
                return {
                    "id": user.data.id,
                    "username": user.data.username,
                    "name": user.data.name,
                    "description": user.data.description,
                    "location": user.data.location,
                    "verified": user.data.verified,
                    "created_at": user.data.created_at.isoformat() if user.data.created_at else None,
                    "followers_count": user.data.public_metrics.get('followers_count', 0) if user.data.public_metrics else 0,
                    "following_count": user.data.public_metrics.get('following_count', 0) if user.data.public_metrics else 0,
                    "tweet_count": user.data.public_metrics.get('tweet_count', 0) if user.data.public_metrics else 0
                }
            else:
                return {}

        except Exception as e:
            logger.error(f"Error getting user info: {e}")
            return {}

    async def discover_trending_content(self, keywords: List[str], limit: int = 50) -> List[Dict]:
        """Discover trending content based on keywords"""
        trending_content = []

        for keyword in keywords[:5]:  # Limit API calls
            try:
                # Search for keyword
                tweets = await self.search_tweets(f"{keyword} -is:retweet", limit=10)

                for tweet in tweets:
                    tweet["source_keyword"] = keyword
                    tweet["platform"] = "twitter"
                    trending_content.append(tweet)

                await asyncio.sleep(1)  # Rate limiting

            except Exception as e:
                logger.error(f"Error discovering content for keyword {keyword}: {e}")
                continue

        # Sort by engagement (likes + retweets + replies)
        trending_content.sort(
            key=lambda x: (
                x.get("metrics", {}).get("like_count", 0) +
                x.get("metrics", {}).get("retweet_count", 0) +
                x.get("metrics", {}).get("reply_count", 0)
            ),
            reverse=True
        )

        return trending_content[:limit]

    def is_configured(self) -> bool:
        """Check if Twitter API is properly configured"""
        return bool(self.client and self.user_id)
