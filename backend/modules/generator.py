"""
Content Generation Module
Creates AI-powered social media posts using brand guidelines and trending content
Implements brand alignment scoring and content type alternation
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
import google.generativeai as genai
from sqlalchemy.orm import Session

from database.database import SessionLocal
from database.models import (
    Brand, ContentPost, ScrapedContent, PostType, Platform, PostStatus
)
from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class ContentGenerator:
    def __init__(self):
        # Configure Gemini AI
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-pro')

        # Content type alternation tracking
        self.last_content_types = {}

    async def generate_daily_content(self, brand: Brand) -> Dict:
        """Generate daily content for a brand (2 posts, alternating photo/video)"""
        logger.info(f"Generating daily content for brand: {brand.name}")

        result = {
            "brand_id": brand.id,
            "generation_timestamp": datetime.utcnow().isoformat(),
            "posts_generated": [],
            "posts_scheduled": 0,
            "errors": []
        }

        try:
            # Get brand's posting times
            posting_times = brand.posting_times or ["09:00", "17:00"]
            posts_per_day = brand.posting_frequency or 2

            # Get trending content for inspiration
            trending_content = await self.get_trending_content_for_brand(brand)

            # Generate posts for each time slot
            for i in range(min(posts_per_day, len(posting_times))):
                try:
                    # Determine content type (alternate between photo and video)
                    content_type = await self.get_next_content_type(brand.id)

                    # Select trending content for inspiration
                    inspiration = trending_content[i % len(trending_content)] if trending_content else None

                    # Generate post
                    post_data = await self.generate_post(
                        brand=brand,
                        content_type=content_type,
                        inspiration=inspiration,
                        posting_time=posting_times[i]
                    )

                    if post_data:
                        # Save to database
                        post = await self.save_generated_post(post_data, brand)

                        if post:
                            result["posts_generated"].append({
                                "post_id": post.id,
                                "content_type": post.content_type.value,
                                "platform": post.platform.value,
                                "scheduled_time": post.scheduled_time.isoformat(),
                                "brand_alignment_score": post.brand_alignment_score
                            })
                            result["posts_scheduled"] += 1

                except Exception as e:
                    error_msg = f"Error generating post {i+1}: {str(e)}"
                    logger.error(error_msg)
                    result["errors"].append(error_msg)

            logger.info(f"Generated {result['posts_scheduled']} posts for {brand.name}")

        except Exception as e:
            logger.error(f"Daily content generation failed for {brand.name}: {e}")
            result["errors"].append(str(e))

        return result

    async def get_trending_content_for_brand(self, brand: Brand) -> List[Dict]:
        """Get relevant trending content for inspiration"""
        db = SessionLocal()
        try:
            # Get recent high-relevance scraped content
            trending_content = db.query(ScrapedContent).filter(
                ScrapedContent.brand_id == brand.id,
                ScrapedContent.relevance_score >= 70,
                ScrapedContent.scraped_at >= datetime.utcnow() - timedelta(days=7)
            ).order_by(ScrapedContent.relevance_score.desc()).limit(10).all()

            return [
                {
                    "platform": content.platform.value,
                    "text": content.content_text,
                    "url": content.post_url,
                    "relevance_score": content.relevance_score,
                    "sentiment_score": content.sentiment_score,
                    "trending_keywords": content.trending_keywords
                }
                for content in trending_content
            ]

        finally:
            db.close()

    async def get_next_content_type(self, brand_id: int) -> PostType:
        """Get next content type, alternating between photo and video"""
        db = SessionLocal()
        try:
            # Get the most recent post for this brand
            last_post = db.query(ContentPost).filter(
                ContentPost.brand_id == brand_id
            ).order_by(ContentPost.created_at.desc()).first()

            if not last_post:
                return PostType.PHOTO  # Start with photo

            # Alternate content type
            if last_post.content_type == PostType.PHOTO:
                return PostType.VIDEO
            else:
                return PostType.PHOTO

        finally:
            db.close()

    async def generate_post(
        self,
        brand: Brand,
        content_type: PostType,
        inspiration: Optional[Dict] = None,
        posting_time: str = "09:00"
    ) -> Optional[Dict]:
        """Generate a single social media post"""
        logger.info(f"Generating {content_type.value} post for {brand.name}")

        try:
            # Generate post idea first
            post_idea = await self.generate_post_idea(brand, content_type, inspiration)

            if not post_idea:
                logger.warning("Failed to generate post idea")
                return None

            # Generate caption based on the idea
            caption = await self.generate_caption(brand, post_idea, content_type)

            if not caption:
                logger.warning("Failed to generate caption")
                return None

            # Generate visual brief (for image/video content)
            visual_brief = await self.generate_visual_brief(brand, post_idea, content_type)

            # Calculate brand alignment score
            brand_alignment_score = await self.calculate_brand_alignment_score(caption, brand)

            # Calculate scheduled time
            scheduled_time = await self.calculate_scheduled_time(posting_time)

            # Determine platform (for now, default to Instagram)
            platform = Platform.INSTAGRAM

            post_data = {
                "title": post_idea.get("title", ""),
                "caption": caption,
                "content_type": content_type,
                "platform": platform,
                "scheduled_time": scheduled_time,
                "brand_alignment_score": brand_alignment_score,
                "visual_brief": visual_brief,
                "inspiration_source": inspiration.get("url") if inspiration else None,
                "ai_generated": True
            }

            return post_data

        except Exception as e:
            logger.error(f"Error generating post: {e}")
            return None

    async def generate_post_idea(
        self,
        brand: Brand,
        content_type: PostType,
        inspiration: Optional[Dict] = None
    ) -> Dict:
        """Generate a post idea using AI"""
        try:
            # Prepare context
            brand_context = {
                "name": brand.name,
                "industry": brand.industry,
                "description": brand.description,
                "target_audience": brand.target_audience,
                "style_guide": brand.style_guide or {},
                "keywords": brand.keywords or []
            }

            inspiration_text = ""
            if inspiration:
                inspiration_text = f"""
                Trending Content for Inspiration:
                Platform: {inspiration['platform']}
                Content: {inspiration['text'][:500]}
                Keywords: {', '.join(inspiration.get('trending_keywords', []))}
                """

            prompt = f"""
            Generate a creative {content_type.value} post idea for this brand:

            Brand Context:
            {json.dumps(brand_context, indent=2)}

            {inspiration_text}

            Create a post idea that:
            1. Aligns with the brand's voice and style
            2. Is relevant to current trends (if inspiration provided)
            3. Engages the target audience
            4. Is suitable for {content_type.value} content
            5. Follows social media best practices

            Return the idea in JSON format:
            {{
                "title": "catchy title for the post",
                "concept": "detailed description of the post concept",
                "key_message": "main message to convey",
                "target_emotion": "emotion to evoke (inspiration, curiosity, etc.)",
                "call_to_action": "what action should users take",
                "hashtag_suggestions": ["hashtag1", "hashtag2", "hashtag3"],
                "best_platform": "most suitable platform for this content"
            }}

            Return only valid JSON.
            """

            response = self.model.generate_content(prompt)
            idea = json.loads(response.text)
            return idea

        except Exception as e:
            logger.error(f"Error generating post idea: {e}")
            return {}

    async def generate_caption(
        self,
        brand: Brand,
        post_idea: Dict,
        content_type: PostType
    ) -> str:
        """Generate engaging caption using AI"""
        try:
            # Get brand style guide
            style_guide = brand.style_guide or {}
            brand_voice = style_guide.get("brand_voice", {})

            prompt = f"""
            Write an engaging social media caption based on this post idea:

            Post Idea:
            {json.dumps(post_idea, indent=2)}

            Brand Voice Guidelines:
            {json.dumps(brand_voice, indent=2)}

            Brand Info:
            - Name: {brand.name}
            - Industry: {brand.industry}
            - Target Audience: {brand.target_audience}

            Content Type: {content_type.value}

            Caption Requirements:
            1. Match the brand's tone and voice exactly
            2. Be engaging and encourage interaction
            3. Include relevant hashtags (3-7 hashtags)
            4. Keep it concise but impactful
            5. Include a clear call-to-action
            6. Use emojis appropriately for the brand
            7. Optimize for {content_type.value} content

            Platform-specific guidelines:
            - Instagram: 150-300 characters for high engagement
            - LinkedIn: Professional tone, longer form acceptable
            - Twitter: Concise, under 280 characters

            Return only the caption text, ready to post.
            """

            response = self.model.generate_content(prompt)
            caption = response.text.strip()

            # Clean up the caption
            caption = self.clean_caption(caption)

            return caption

        except Exception as e:
            logger.error(f"Error generating caption: {e}")
            return ""

    async def generate_visual_brief(
        self,
        brand: Brand,
        post_idea: Dict,
        content_type: PostType
    ) -> str:
        """Generate visual brief for designers/content creators"""
        try:
            # Get brand visual guidelines
            style_guide = brand.style_guide or {}
            visual_identity = style_guide.get("visual_identity", {})

            prompt = f"""
            Create a detailed visual brief for this {content_type.value} content:

            Post Concept:
            {json.dumps(post_idea, indent=2)}

            Brand Visual Identity:
            {json.dumps(visual_identity, indent=2)}

            Brand Info:
            - Name: {brand.name}
            - Industry: {brand.industry}

            Generate a comprehensive visual brief that includes:
            1. Visual concept description
            2. Color palette to use
            3. Composition guidelines
            4. Typography recommendations (if text overlay needed)
            5. Props or elements to include
            6. Mood and style direction
            7. Technical specifications for {content_type.value}

            Make it detailed enough for a designer or photographer to execute.
            """

            response = self.model.generate_content(prompt)
            return response.text.strip()

        except Exception as e:
            logger.error(f"Error generating visual brief: {e}")
            return f"Visual brief for {content_type.value} content based on: {post_idea.get('concept', 'N/A')}"

    async def calculate_brand_alignment_score(self, caption: str, brand: Brand) -> float:
        """Calculate how well the caption aligns with brand guidelines"""
        try:
            style_guide = brand.style_guide or {}

            prompt = f"""
            Rate how well this social media caption aligns with the brand guidelines:

            Caption:
            {caption}

            Brand Guidelines:
            {json.dumps(style_guide, indent=2)}

            Brand Info:
            - Name: {brand.name}
            - Industry: {brand.industry}
            - Target Audience: {brand.target_audience}
            - Keywords: {', '.join(brand.keywords or [])}

            Rate the alignment on a scale of 0-100 considering:
            1. Brand voice and tone consistency (30%)
            2. Message alignment with brand values (25%)
            3. Target audience appropriateness (20%)
            4. Keyword/theme relevance (15%)
            5. Style and format consistency (10%)

            Return only the numeric score (0-100).
            """

            response = self.model.generate_content(prompt)
            score_text = response.text.strip()

            # Extract numeric score
            score = float(''.join(filter(str.isdigit, score_text)))
            return min(100, max(0, score))  # Ensure score is between 0-100

        except Exception as e:
            logger.warning(f"Error calculating brand alignment score: {e}")
            return 75.0  # Default neutral score

    async def calculate_scheduled_time(self, posting_time: str) -> datetime:
        """Calculate the next scheduled time for posting"""
        try:
            # Parse time (format: "HH:MM")
            hour, minute = map(int, posting_time.split(":"))

            # Get tomorrow's date with the specified time
            tomorrow = datetime.utcnow().replace(hour=hour, minute=minute, second=0, microsecond=0)
            tomorrow += timedelta(days=1)

            return tomorrow

        except Exception as e:
            logger.warning(f"Error calculating scheduled time: {e}")
            # Default to tomorrow at 9 AM
            return datetime.utcnow().replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1)

    def clean_caption(self, caption: str) -> str:
        """Clean and format the caption"""
        # Remove any quotes or extra formatting
        caption = caption.strip('"\'')

        # Remove any JSON formatting artifacts
        if caption.startswith('{') or caption.startswith('['):
            try:
                parsed = json.loads(caption)
                if isinstance(parsed, str):
                    caption = parsed
                elif isinstance(parsed, dict) and 'caption' in parsed:
                    caption = parsed['caption']
            except:
                pass

        return caption.strip()

    async def save_generated_post(self, post_data: Dict, brand: Brand) -> Optional[ContentPost]:
        """Save generated post to database"""
        db = SessionLocal()
        try:
            post = ContentPost(
                title=post_data.get("title", ""),
                caption=post_data["caption"],
                content_type=post_data["content_type"],
                platform=post_data["platform"],
                scheduled_time=post_data["scheduled_time"],
                status=PostStatus.PENDING_REVIEW,  # Requires human approval
                brand_alignment_score=post_data["brand_alignment_score"],
                media_description=post_data.get("visual_brief", ""),
                brand_id=brand.id,
                created_by_ai=True,
                created_at=datetime.utcnow()
            )

            # Set risk score based on brand alignment
            if post_data["brand_alignment_score"] >= 90:
                post.risk_score = "low"
            elif post_data["brand_alignment_score"] >= 75:
                post.risk_score = "medium"
            else:
                post.risk_score = "high"

            db.add(post)
            db.commit()
            db.refresh(post)

            logger.info(f"Saved generated post {post.id} for brand {brand.name}")
            return post

        except Exception as e:
            logger.error(f"Error saving generated post: {e}")
            db.rollback()
            return None
        finally:
            db.close()

    async def regenerate_post(self, post_id: int, feedback: str = "") -> Optional[ContentPost]:
        """Regenerate a post based on feedback"""
        db = SessionLocal()
        try:
            post = db.query(ContentPost).filter(ContentPost.id == post_id).first()
            if not post:
                return None

            brand = db.query(Brand).filter(Brand.id == post.brand_id).first()
            if not brand:
                return None

            logger.info(f"Regenerating post {post_id} with feedback: {feedback}")

            # Get original post idea from the existing content
            original_idea = {
                "title": post.title,
                "concept": post.media_description,
                "feedback": feedback
            }

            # Generate new caption incorporating feedback
            new_caption = await self.generate_caption_with_feedback(
                brand, original_idea, post.content_type, feedback
            )

            if new_caption:
                # Update post
                post.caption = new_caption
                post.brand_alignment_score = await self.calculate_brand_alignment_score(new_caption, brand)
                post.updated_at = datetime.utcnow()

                # Update risk score
                if post.brand_alignment_score >= 90:
                    post.risk_score = "low"
                elif post.brand_alignment_score >= 75:
                    post.risk_score = "medium"
                else:
                    post.risk_score = "high"

                db.commit()
                db.refresh(post)

                logger.info(f"Successfully regenerated post {post_id}")
                return post

        except Exception as e:
            logger.error(f"Error regenerating post {post_id}: {e}")
            db.rollback()
        finally:
            db.close()

        return None

    async def generate_caption_with_feedback(
        self,
        brand: Brand,
        original_idea: Dict,
        content_type: PostType,
        feedback: str
    ) -> str:
        """Generate new caption incorporating human feedback"""
        try:
            style_guide = brand.style_guide or {}
            brand_voice = style_guide.get("brand_voice", {})

            prompt = f"""
            Revise this social media caption based on the provided feedback:

            Original Post Idea:
            {json.dumps(original_idea, indent=2)}

            Human Feedback:
            {feedback}

            Brand Voice Guidelines:
            {json.dumps(brand_voice, indent=2)}

            Brand Info:
            - Name: {brand.name}
            - Industry: {brand.industry}
            - Target Audience: {brand.target_audience}

            Content Type: {content_type.value}

            Requirements:
            1. Address all points mentioned in the feedback
            2. Maintain brand voice and tone
            3. Keep the core message intact unless feedback suggests otherwise
            4. Improve engagement potential
            5. Include appropriate hashtags and call-to-action

            Return only the revised caption text, ready to post.
            """

            response = self.model.generate_content(prompt)
            caption = response.text.strip()

            # Clean up the caption
            caption = self.clean_caption(caption)

            return caption

        except Exception as e:
            logger.error(f"Error generating caption with feedback: {e}")
            return ""

    async def get_content_suggestions(self, brand: Brand, count: int = 5) -> List[Dict]:
        """Get content suggestions for manual creation"""
        try:
            trending_content = await self.get_trending_content_for_brand(brand)

            suggestions = []
            for i in range(count):
                content_type = PostType.PHOTO if i % 2 == 0 else PostType.VIDEO
                inspiration = trending_content[i % len(trending_content)] if trending_content else None

                idea = await self.generate_post_idea(brand, content_type, inspiration)
                if idea:
                    suggestions.append({
                        "content_type": content_type.value,
                        "idea": idea,
                        "inspiration_source": inspiration.get("url") if inspiration else None
                    })

            return suggestions

        except Exception as e:
            logger.error(f"Error getting content suggestions: {e}")
            return []
