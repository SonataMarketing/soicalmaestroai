"""
Content Scraping Module
Scrapes Instagram and Reddit for trending content
Implements relevance scoring and caching
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import requests
import praw
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import google.generativeai as genai
from sqlalchemy.orm import Session

from database.database import SessionLocal
from database.models import Brand, ScrapedContent, CachedContent, Platform
from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class ContentScraper:
    def __init__(self):
        # Configure Gemini AI
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-pro')

        # Configure Reddit API
        self.reddit = praw.Reddit(
            client_id=settings.reddit_client_id,
            client_secret=settings.reddit_client_secret,
            user_agent="SocialMaestro v1.0"
        )

        # Configure Selenium for Instagram
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--disable-gpu")

    async def scrape_for_brand(self, brand: Brand) -> Dict:
        """Main scraping function for a brand"""
        logger.info(f"Starting content scraping for brand: {brand.name}")

        results = {
            "brand_id": brand.id,
            "scraping_timestamp": datetime.utcnow().isoformat(),
            "instagram_results": [],
            "reddit_results": [],
            "total_scraped": 0,
            "high_relevance_count": 0
        }

        try:
            # Scrape Instagram
            instagram_content = await self.scrape_instagram(brand.keywords or [], brand.industry)
            results["instagram_results"] = instagram_content

            # Scrape Reddit
            reddit_content = await self.scrape_reddit(brand.keywords or [], brand.industry)
            results["reddit_results"] = reddit_content

            # Process and score all content
            all_content = instagram_content + reddit_content
            processed_content = await self.process_and_score_content(all_content, brand)

            # Save to database
            await self.save_scraped_content(processed_content, brand.id)

            results["total_scraped"] = len(processed_content)
            results["high_relevance_count"] = len([c for c in processed_content if c["relevance_score"] >= 70])

            logger.info(f"Scraping completed for {brand.name}: {results['total_scraped']} items, {results['high_relevance_count']} high relevance")

        except Exception as e:
            logger.error(f"Scraping failed for brand {brand.name}: {e}")
            # Fallback to cached content
            results = await self.get_cached_content(brand.id)
            results["error"] = str(e)
            results["used_cache"] = True

        return results

    async def scrape_instagram(self, keywords: List[str], industry: str) -> List[Dict]:
        """Scrape Instagram for trending content"""
        logger.info("Scraping Instagram content")
        content = []

        try:
            driver = webdriver.Chrome(options=self.chrome_options)

            for keyword in keywords[:3]:  # Limit to avoid rate limits
                try:
                    # Search for hashtag
                    search_url = f"https://www.instagram.com/explore/tags/{keyword.replace('#', '')}/"
                    driver.get(search_url)

                    # Wait for content to load
                    WebDriverWait(driver, 10).wait(
                        EC.presence_of_element_located((By.CLASS_NAME, "_aagu"))
                    )

                    # Get post elements
                    posts = driver.find_elements(By.CSS_SELECTOR, "article a")[:9]  # Top 9 posts

                    for post in posts:
                        try:
                            post_url = post.get_attribute("href")

                            # Get post details
                            post_data = await self.get_instagram_post_details(driver, post_url)
                            if post_data:
                                post_data["source_keyword"] = keyword
                                post_data["platform"] = "instagram"
                                content.append(post_data)

                        except Exception as e:
                            logger.warning(f"Error processing Instagram post: {e}")
                            continue

                    # Rate limiting
                    await asyncio.sleep(2)

                except Exception as e:
                    logger.error(f"Error scraping Instagram keyword {keyword}: {e}")
                    continue

            driver.quit()

        except Exception as e:
            logger.error(f"Instagram scraping failed: {e}")
            # Return sample data for development
            content = await self.get_sample_instagram_data(keywords)

        return content

    async def get_instagram_post_details(self, driver, post_url: str) -> Optional[Dict]:
        """Get detailed information about an Instagram post"""
        try:
            driver.get(post_url)
            await asyncio.sleep(2)

            # Extract post details
            caption_element = driver.find_element(By.CSS_SELECTOR, "meta[property='og:description']")
            caption = caption_element.get_attribute("content") if caption_element else ""

            # Extract engagement (this is simplified - real implementation would need API access)
            likes_count = 0  # Placeholder
            comments_count = 0  # Placeholder

            return {
                "url": post_url,
                "caption": caption,
                "likes_count": likes_count,
                "comments_count": comments_count,
                "scraped_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.warning(f"Error getting Instagram post details: {e}")
            return None

    async def scrape_reddit(self, keywords: List[str], industry: str) -> List[Dict]:
        """Scrape Reddit for trending content"""
        logger.info("Scraping Reddit content")
        content = []

        try:
            # Define relevant subreddits based on industry
            subreddits = self.get_relevant_subreddits(industry)

            for subreddit_name in subreddits[:5]:  # Limit subreddits
                try:
                    subreddit = self.reddit.subreddit(subreddit_name)

                    # Get hot posts
                    for post in subreddit.hot(limit=10):
                        # Check if post contains relevant keywords
                        if self.contains_keywords(post.title + " " + post.selftext, keywords):
                            post_data = {
                                "url": f"https://reddit.com{post.permalink}",
                                "title": post.title,
                                "content": post.selftext,
                                "subreddit": subreddit_name,
                                "score": post.score,
                                "comments_count": post.num_comments,
                                "created_at": datetime.fromtimestamp(post.created_utc).isoformat(),
                                "platform": "reddit",
                                "scraped_at": datetime.utcnow().isoformat()
                            }
                            content.append(post_data)

                    # Rate limiting
                    await asyncio.sleep(1)

                except Exception as e:
                    logger.warning(f"Error scraping Reddit subreddit {subreddit_name}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Reddit scraping failed: {e}")
            # Return sample data for development
            content = await self.get_sample_reddit_data(keywords)

        return content

    def get_relevant_subreddits(self, industry: str) -> List[str]:
        """Get relevant subreddits based on industry"""
        industry_subreddits = {
            "technology": ["technology", "programming", "MachineLearning", "artificial", "gadgets"],
            "marketing": ["marketing", "socialmedia", "digital_marketing", "advertising", "entrepreneur"],
            "fashion": ["fashion", "streetwear", "malefashionadvice", "femalefashionadvice", "fashiontrends"],
            "fitness": ["fitness", "bodybuilding", "loseit", "nutrition", "running"],
            "food": ["food", "recipes", "cooking", "FoodPorn", "meal_prep"],
            "travel": ["travel", "solotravel", "backpacking", "digitalnomad", "earthporn"]
        }

        return industry_subreddits.get(industry.lower(), ["popular", "all", "news"])

    def contains_keywords(self, text: str, keywords: List[str]) -> bool:
        """Check if text contains any of the brand keywords"""
        text_lower = text.lower()
        return any(keyword.lower().replace("#", "") in text_lower for keyword in keywords)

    async def process_and_score_content(self, content: List[Dict], brand: Brand) -> List[Dict]:
        """Process scraped content and calculate relevance scores using AI"""
        logger.info(f"Processing and scoring {len(content)} pieces of content")

        processed_content = []

        for item in content:
            try:
                # Calculate relevance score using Gemini AI
                relevance_score = await self.calculate_relevance_score(item, brand)

                # Only keep content with score >= 70%
                if relevance_score >= 70:
                    item["relevance_score"] = relevance_score
                    item["sentiment_score"] = await self.calculate_sentiment_score(item)
                    item["trending_keywords"] = await self.extract_trending_keywords(item)
                    processed_content.append(item)

            except Exception as e:
                logger.warning(f"Error processing content item: {e}")
                continue

        return processed_content

    async def calculate_relevance_score(self, content: Dict, brand: Brand) -> float:
        """Calculate relevance score using Gemini AI"""
        try:
            # Prepare content text
            content_text = ""
            if "caption" in content:
                content_text = content["caption"]
            elif "title" in content and "content" in content:
                content_text = f"{content['title']} {content['content']}"

            # Prepare brand context
            brand_context = {
                "name": brand.name,
                "industry": brand.industry,
                "keywords": brand.keywords or [],
                "description": brand.description or ""
            }

            # Create prompt for AI
            prompt = f"""
            Analyze the relevance of this social media content to the given brand:

            Brand Context:
            - Name: {brand_context['name']}
            - Industry: {brand_context['industry']}
            - Keywords: {', '.join(brand_context['keywords'])}
            - Description: {brand_context['description']}

            Content to Analyze:
            {content_text}

            Rate the relevance of this content to the brand on a scale of 0-100, considering:
            1. Industry alignment
            2. Keyword relevance
            3. Brand message compatibility
            4. Potential audience interest

            Return only the numeric score (0-100).
            """

            response = self.model.generate_content(prompt)
            score_text = response.text.strip()

            # Extract numeric score
            score = float(''.join(filter(str.isdigit, score_text)))
            return min(100, max(0, score))  # Ensure score is between 0-100

        except Exception as e:
            logger.warning(f"Error calculating relevance score: {e}")
            return 50.0  # Default neutral score

    async def calculate_sentiment_score(self, content: Dict) -> float:
        """Calculate sentiment score using AI"""
        try:
            content_text = content.get("caption") or content.get("title", "") + " " + content.get("content", "")

            prompt = f"""
            Analyze the sentiment of this social media content and return a score between -1 and 1:
            -1 = Very Negative
            0 = Neutral
            1 = Very Positive

            Content: {content_text}

            Return only the numeric score (-1 to 1).
            """

            response = self.model.generate_content(prompt)
            score = float(response.text.strip())
            return max(-1, min(1, score))

        except Exception as e:
            logger.warning(f"Error calculating sentiment score: {e}")
            return 0.0

    async def extract_trending_keywords(self, content: Dict) -> List[str]:
        """Extract trending keywords from content using AI"""
        try:
            content_text = content.get("caption") or content.get("title", "") + " " + content.get("content", "")

            prompt = f"""
            Extract the top 5 most important keywords/hashtags from this social media content:

            Content: {content_text}

            Return keywords as a comma-separated list.
            """

            response = self.model.generate_content(prompt)
            keywords = [k.strip() for k in response.text.split(",")]
            return keywords[:5]

        except Exception as e:
            logger.warning(f"Error extracting keywords: {e}")
            return []

    async def save_scraped_content(self, content: List[Dict], brand_id: int):
        """Save scraped content to database"""
        db = SessionLocal()
        try:
            for item in content:
                scraped_content = ScrapedContent(
                    platform=Platform.INSTAGRAM if item["platform"] == "instagram" else Platform.REDDIT,
                    post_url=item["url"],
                    content_text=item.get("caption") or item.get("title", "") + " " + item.get("content", ""),
                    hashtags=item.get("trending_keywords", []),
                    likes_count=item.get("likes_count", 0),
                    comments_count=item.get("comments_count", 0),
                    shares_count=item.get("score", 0),  # Use Reddit score as shares
                    relevance_score=item["relevance_score"],
                    sentiment_score=item["sentiment_score"],
                    trending_keywords=item["trending_keywords"],
                    brand_id=brand_id,
                    scraped_at=datetime.utcnow()
                )
                db.add(scraped_content)

            db.commit()
            logger.info(f"Saved {len(content)} scraped content items to database")

        except Exception as e:
            logger.error(f"Error saving scraped content: {e}")
            db.rollback()
        finally:
            db.close()

    async def get_cached_content(self, brand_id: int) -> Dict:
        """Get cached content as fallback"""
        db = SessionLocal()
        try:
            # Get recent scraped content from database
            recent_content = db.query(ScrapedContent).filter(
                ScrapedContent.brand_id == brand_id,
                ScrapedContent.scraped_at >= datetime.utcnow() - timedelta(days=7)
            ).limit(20).all()

            return {
                "brand_id": brand_id,
                "scraping_timestamp": datetime.utcnow().isoformat(),
                "cached_results": [
                    {
                        "url": content.post_url,
                        "text": content.content_text,
                        "platform": content.platform.value,
                        "relevance_score": content.relevance_score,
                        "sentiment_score": content.sentiment_score
                    }
                    for content in recent_content
                ],
                "total_scraped": len(recent_content),
                "high_relevance_count": len([c for c in recent_content if c.relevance_score >= 70]),
                "from_cache": True
            }

        finally:
            db.close()

    async def get_sample_instagram_data(self, keywords: List[str]) -> List[Dict]:
        """Return sample Instagram data for development"""
        return [
            {
                "url": "https://instagram.com/p/sample1",
                "caption": f"Amazing {keywords[0] if keywords else 'content'} trends that are taking over social media! 🚀 #trending #viral",
                "likes_count": 2847,
                "comments_count": 156,
                "platform": "instagram",
                "scraped_at": datetime.utcnow().isoformat()
            },
            {
                "url": "https://instagram.com/p/sample2",
                "caption": f"The future of {keywords[1] if len(keywords) > 1 else 'innovation'} is here! Check out these game-changing insights. 💡",
                "likes_count": 1234,
                "comments_count": 87,
                "platform": "instagram",
                "scraped_at": datetime.utcnow().isoformat()
            }
        ]

    async def get_sample_reddit_data(self, keywords: List[str]) -> List[Dict]:
        """Return sample Reddit data for development"""
        return [
            {
                "url": "https://reddit.com/r/sample/post1",
                "title": f"Discussion: How {keywords[0] if keywords else 'AI'} is transforming industries",
                "content": "This is a detailed discussion about the impact of new technologies...",
                "subreddit": "technology",
                "score": 1500,
                "comments_count": 234,
                "platform": "reddit",
                "scraped_at": datetime.utcnow().isoformat()
            }
        ]
