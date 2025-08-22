"""
Reddit API Integration
Real API integration using PRAW for content discovery and trend analysis
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import praw
import prawcore
from praw.models import Submission, Comment

from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class RedditAPI:
    """Reddit API client using PRAW"""

    def __init__(self):
        self.client_id = settings.reddit_client_id
        self.client_secret = settings.reddit_client_secret
        self.user_agent = settings.reddit_user_agent

        # Initialize Reddit instance
        try:
            self.reddit = praw.Reddit(
                client_id=self.client_id,
                client_secret=self.client_secret,
                user_agent=self.user_agent,
                check_for_async=False  # We'll handle async manually
            )
            # Test the connection
            self.reddit.user.me()
            self.is_authenticated = True
        except Exception as e:
            logger.error(f"Failed to initialize Reddit API: {e}")
            self.reddit = None
            self.is_authenticated = False

    async def get_subreddit_info(self, subreddit_name: str) -> Optional[Dict]:
        """Get information about a subreddit"""
        if not self.reddit:
            return None

        try:
            subreddit = self.reddit.subreddit(subreddit_name)

            return {
                "name": subreddit.display_name,
                "title": subreddit.title,
                "description": subreddit.description,
                "subscribers": subreddit.subscribers,
                "active_users": subreddit.active_user_count,
                "created_utc": datetime.fromtimestamp(subreddit.created_utc).isoformat(),
                "over18": subreddit.over18,
                "public_description": subreddit.public_description
            }

        except prawcore.exceptions.NotFound:
            logger.error(f"Subreddit {subreddit_name} not found")
            return None
        except Exception as e:
            logger.error(f"Error getting subreddit info for {subreddit_name}: {e}")
            return None

    async def get_hot_posts(self, subreddit_name: str, limit: int = 25) -> List[Dict]:
        """Get hot posts from a subreddit"""
        if not self.reddit:
            return []

        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            posts = []

            for submission in subreddit.hot(limit=limit):
                post_data = await self._submission_to_dict(submission)
                post_data["source_subreddit"] = subreddit_name
                post_data["sort_type"] = "hot"
                posts.append(post_data)

            return posts

        except prawcore.exceptions.NotFound:
            logger.error(f"Subreddit {subreddit_name} not found")
            return []
        except Exception as e:
            logger.error(f"Error getting hot posts from {subreddit_name}: {e}")
            return []

    async def get_top_posts(self, subreddit_name: str, time_filter: str = "day", limit: int = 25) -> List[Dict]:
        """Get top posts from a subreddit"""
        if not self.reddit:
            return []

        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            posts = []

            for submission in subreddit.top(time_filter=time_filter, limit=limit):
                post_data = await self._submission_to_dict(submission)
                post_data["source_subreddit"] = subreddit_name
                post_data["sort_type"] = f"top_{time_filter}"
                posts.append(post_data)

            return posts

        except prawcore.exceptions.NotFound:
            logger.error(f"Subreddit {subreddit_name} not found")
            return []
        except Exception as e:
            logger.error(f"Error getting top posts from {subreddit_name}: {e}")
            return []

    async def get_new_posts(self, subreddit_name: str, limit: int = 25) -> List[Dict]:
        """Get new posts from a subreddit"""
        if not self.reddit:
            return []

        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            posts = []

            for submission in subreddit.new(limit=limit):
                post_data = await self._submission_to_dict(submission)
                post_data["source_subreddit"] = subreddit_name
                post_data["sort_type"] = "new"
                posts.append(post_data)

            return posts

        except prawcore.exceptions.NotFound:
            logger.error(f"Subreddit {subreddit_name} not found")
            return []
        except Exception as e:
            logger.error(f"Error getting new posts from {subreddit_name}: {e}")
            return []

    async def search_posts(self, query: str, subreddit_name: str = None, sort: str = "relevance",
                          time_filter: str = "week", limit: int = 25) -> List[Dict]:
        """Search for posts across Reddit or within a specific subreddit"""
        if not self.reddit:
            return []

        try:
            if subreddit_name:
                subreddit = self.reddit.subreddit(subreddit_name)
                search_results = subreddit.search(query, sort=sort, time_filter=time_filter, limit=limit)
            else:
                search_results = self.reddit.subreddit("all").search(query, sort=sort, time_filter=time_filter, limit=limit)

            posts = []
            for submission in search_results:
                post_data = await self._submission_to_dict(submission)
                post_data["search_query"] = query
                post_data["search_sort"] = sort
                posts.append(post_data)

            return posts

        except Exception as e:
            logger.error(f"Error searching posts for query '{query}': {e}")
            return []

    async def get_trending_subreddits(self, limit: int = 50) -> List[Dict]:
        """Get trending/popular subreddits"""
        if not self.reddit:
            return []

        try:
            subreddits = []

            # Get popular subreddits
            for subreddit in self.reddit.subreddits.popular(limit=limit):
                subreddit_data = {
                    "name": subreddit.display_name,
                    "title": subreddit.title,
                    "subscribers": subreddit.subscribers,
                    "active_users": subreddit.active_user_count,
                    "description": subreddit.public_description[:200] if subreddit.public_description else "",
                    "over18": subreddit.over18,
                    "created_utc": datetime.fromtimestamp(subreddit.created_utc).isoformat()
                }
                subreddits.append(subreddit_data)

            return subreddits

        except Exception as e:
            logger.error(f"Error getting trending subreddits: {e}")
            return []

    async def get_post_comments(self, post_id: str, limit: int = 10) -> List[Dict]:
        """Get comments for a specific post"""
        if not self.reddit:
            return []

        try:
            submission = self.reddit.submission(id=post_id)
            submission.comments.replace_more(limit=0)  # Remove "more comments"

            comments = []
            for comment in submission.comments[:limit]:
                if isinstance(comment, Comment):
                    comment_data = {
                        "id": comment.id,
                        "author": str(comment.author) if comment.author else "[deleted]",
                        "body": comment.body,
                        "score": comment.score,
                        "created_utc": datetime.fromtimestamp(comment.created_utc).isoformat(),
                        "is_submitter": comment.is_submitter,
                        "distinguished": comment.distinguished,
                        "permalink": f"https://reddit.com{comment.permalink}"
                    }
                    comments.append(comment_data)

            return comments

        except Exception as e:
            logger.error(f"Error getting comments for post {post_id}: {e}")
            return []

    async def discover_trending_content(self, keywords: List[str], subreddits: List[str] = None,
                                     limit: int = 50) -> List[Dict]:
        """Discover trending content based on keywords and subreddits"""
        if not self.reddit:
            return []

        trending_content = []

        # Default subreddits if none provided
        if not subreddits:
            subreddits = self.get_default_subreddits()

        try:
            # Search within specific subreddits
            for subreddit_name in subreddits[:10]:  # Limit to avoid rate limits
                try:
                    # Get hot posts
                    hot_posts = await self.get_hot_posts(subreddit_name, limit=10)
                    trending_content.extend(hot_posts)

                    # Search for keyword-related content
                    for keyword in keywords[:3]:  # Limit keywords per subreddit
                        keyword_posts = await self.search_posts(
                            query=keyword,
                            subreddit_name=subreddit_name,
                            sort="hot",
                            time_filter="week",
                            limit=5
                        )
                        trending_content.extend(keyword_posts)

                    # Rate limiting
                    await asyncio.sleep(0.5)

                except Exception as e:
                    logger.warning(f"Error processing subreddit {subreddit_name}: {e}")
                    continue

            # Also search globally for keywords
            for keyword in keywords[:5]:
                try:
                    global_posts = await self.search_posts(
                        query=keyword,
                        sort="hot",
                        time_filter="week",
                        limit=10
                    )
                    trending_content.extend(global_posts)

                    await asyncio.sleep(0.5)

                except Exception as e:
                    logger.warning(f"Error searching globally for keyword {keyword}: {e}")
                    continue

            # Remove duplicates and sort by score
            seen_ids = set()
            unique_content = []

            for post in trending_content:
                if post["id"] not in seen_ids:
                    seen_ids.add(post["id"])
                    unique_content.append(post)

            # Sort by score (upvotes) and engagement
            unique_content.sort(
                key=lambda x: (x["score"] + x["num_comments"]),
                reverse=True
            )

            return unique_content[:limit]

        except Exception as e:
            logger.error(f"Error discovering trending content: {e}")
            return []

    async def get_user_posts(self, username: str, limit: int = 25) -> List[Dict]:
        """Get posts from a specific user"""
        if not self.reddit:
            return []

        try:
            user = self.reddit.redditor(username)
            posts = []

            for submission in user.submissions.new(limit=limit):
                post_data = await self._submission_to_dict(submission)
                posts.append(post_data)

            return posts

        except prawcore.exceptions.NotFound:
            logger.error(f"User {username} not found")
            return []
        except Exception as e:
            logger.error(f"Error getting posts for user {username}: {e}")
            return []

    async def analyze_subreddit_trends(self, subreddit_name: str, days: int = 7) -> Dict:
        """Analyze trends in a subreddit over time"""
        if not self.reddit:
            return {}

        try:
            subreddit = self.reddit.subreddit(subreddit_name)

            # Get posts from different time periods
            daily_posts = list(subreddit.top("day", limit=100))
            weekly_posts = list(subreddit.top("week", limit=100))

            # Analyze posting patterns
            analysis = {
                "subreddit": subreddit_name,
                "total_daily_posts": len(daily_posts),
                "total_weekly_posts": len(weekly_posts),
                "avg_daily_score": sum(post.score for post in daily_posts) / len(daily_posts) if daily_posts else 0,
                "avg_weekly_score": sum(post.score for post in weekly_posts) / len(weekly_posts) if weekly_posts else 0,
                "top_keywords": await self._extract_trending_keywords(daily_posts + weekly_posts),
                "posting_times": await self._analyze_posting_times(daily_posts + weekly_posts),
                "content_types": await self._analyze_content_types(daily_posts + weekly_posts)
            }

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing subreddit trends for {subreddit_name}: {e}")
            return {}

    async def _submission_to_dict(self, submission: Submission) -> Dict:
        """Convert Reddit submission to dictionary"""
        return {
            "id": submission.id,
            "title": submission.title,
            "selftext": submission.selftext,
            "author": str(submission.author) if submission.author else "[deleted]",
            "score": submission.score,
            "upvote_ratio": submission.upvote_ratio,
            "num_comments": submission.num_comments,
            "created_utc": datetime.fromtimestamp(submission.created_utc).isoformat(),
            "url": submission.url,
            "permalink": f"https://reddit.com{submission.permalink}",
            "subreddit": submission.subreddit.display_name,
            "domain": submission.domain,
            "is_self": submission.is_self,
            "is_video": submission.is_video,
            "over_18": submission.over_18,
            "spoiler": submission.spoiler,
            "stickied": submission.stickied,
            "link_flair_text": submission.link_flair_text,
            "content_text": f"{submission.title} {submission.selftext}".strip(),
            "platform": "reddit"
        }

    async def _extract_trending_keywords(self, posts: List[Submission]) -> List[Dict]:
        """Extract trending keywords from posts"""
        import re
        from collections import Counter

        # Combine all text
        all_text = []
        for post in posts:
            text = f"{post.title} {post.selftext}".lower()
            # Remove URLs, special characters
            text = re.sub(r'http\S+|www\S+|https\S+', '', text)
            text = re.sub(r'[^a-zA-Z\s]', '', text)
            all_text.extend(text.split())

        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'cannot', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}

        filtered_words = [word for word in all_text if len(word) > 3 and word not in stop_words]

        # Count frequency
        word_counts = Counter(filtered_words)

        return [
            {"keyword": word, "frequency": count}
            for word, count in word_counts.most_common(20)
        ]

    async def _analyze_posting_times(self, posts: List[Submission]) -> Dict:
        """Analyze when posts are typically made"""
        from collections import defaultdict

        hour_counts = defaultdict(int)
        day_counts = defaultdict(int)

        for post in posts:
            dt = datetime.fromtimestamp(post.created_utc)
            hour_counts[dt.hour] += 1
            day_counts[dt.strftime("%A")] += 1

        return {
            "best_hours": sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:5],
            "best_days": sorted(day_counts.items(), key=lambda x: x[1], reverse=True)
        }

    async def _analyze_content_types(self, posts: List[Submission]) -> Dict:
        """Analyze types of content posted"""
        types = {"text": 0, "link": 0, "image": 0, "video": 0}

        for post in posts:
            if post.is_self:
                types["text"] += 1
            elif post.is_video:
                types["video"] += 1
            elif any(ext in post.url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif']):
                types["image"] += 1
            else:
                types["link"] += 1

        total = sum(types.values())
        if total > 0:
            for content_type in types:
                types[content_type] = round((types[content_type] / total) * 100, 1)

        return types

    def get_default_subreddits(self) -> List[str]:
        """Get default subreddits for content discovery"""
        return [
            "technology", "business", "marketing", "socialmedia",
            "entrepreneur", "startups", "digitalmarketing",
            "webdev", "design", "artificial", "MachineLearning",
            "productivity", "getmotivated", "todayilearned",
            "LifeProTips", "explainlikeimfive", "futurology"
        ]

    def get_industry_subreddits(self, industry: str) -> List[str]:
        """Get relevant subreddits for specific industries"""
        industry_mapping = {
            "technology": ["technology", "programming", "webdev", "artificial", "MachineLearning", "gadgets"],
            "marketing": ["marketing", "digital_marketing", "socialmedia", "advertising", "entrepreneur"],
            "fashion": ["fashion", "streetwear", "malefashionadvice", "femalefashionadvice"],
            "fitness": ["fitness", "bodybuilding", "nutrition", "running", "loseit"],
            "food": ["food", "recipes", "cooking", "FoodPorn", "MealPrepSunday"],
            "travel": ["travel", "solotravel", "backpacking", "digitalnomad"],
            "finance": ["personalfinance", "investing", "financialindependence", "stocks"],
            "gaming": ["gaming", "Games", "pcgaming", "nintendo", "PS4", "xbox"],
            "photography": ["photography", "photocritique", "analog", "streetphotography"],
            "music": ["Music", "WeAreTheMusicMakers", "edmproduction", "hiphopheads"]
        }

        return industry_mapping.get(industry.lower(), self.get_default_subreddits())

    def is_configured(self) -> bool:
        """Check if Reddit API is properly configured"""
        return bool(self.reddit and self.is_authenticated)
