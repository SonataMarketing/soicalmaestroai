"""
Brand Analysis Module
Analyzes brand voice, style, and visual identity from websites and social media
Creates comprehensive brand style guides using AI
"""

import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from PIL import Image
import io
import json
from urllib.parse import urljoin, urlparse
from sqlalchemy.orm import Session

from database.database import SessionLocal
from database.models import Brand, ContentPost, ScrapedContent
from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class BrandAnalyzer:
    def __init__(self):
        # Configure Gemini AI
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.vision_model = genai.GenerativeModel('gemini-pro-vision')

    async def analyze_brand_weekly(self, brand: Brand) -> Dict:
        """Run comprehensive weekly brand analysis"""
        logger.info(f"Starting weekly brand analysis for: {brand.name}")

        analysis_result = {
            "brand_id": brand.id,
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "website_analysis": {},
            "social_content_analysis": {},
            "visual_analysis": {},
            "updated_style_guide": {},
            "recommendations": []
        }

        try:
            # Analyze website if URL provided
            if brand.website_url:
                analysis_result["website_analysis"] = await self.analyze_website(brand.website_url)

            # Analyze recent social media content
            analysis_result["social_content_analysis"] = await self.analyze_social_content(brand)

            # Analyze visual elements
            analysis_result["visual_analysis"] = await self.analyze_visual_elements(brand)

            # Generate updated style guide
            analysis_result["updated_style_guide"] = await self.create_style_guide(brand, analysis_result)

            # Generate recommendations
            analysis_result["recommendations"] = await self.generate_recommendations(brand, analysis_result)

            # Update brand record
            await self.update_brand_style_guide(brand, analysis_result["updated_style_guide"])

            logger.info(f"Brand analysis completed for {brand.name}")

        except Exception as e:
            logger.error(f"Brand analysis failed for {brand.name}: {e}")
            analysis_result["error"] = str(e)

        return analysis_result

    async def analyze_website(self, url: str) -> Dict:
        """Analyze brand website for voice, tone, and messaging"""
        logger.info(f"Analyzing website: {url}")

        analysis = {
            "url": url,
            "text_content": "",
            "navigation_structure": [],
            "meta_information": {},
            "tone_analysis": {},
            "messaging_themes": [],
            "color_analysis": {}
        }

        try:
            # Fetch website content
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract text content
            analysis["text_content"] = await self.extract_text_content(soup)

            # Extract meta information
            analysis["meta_information"] = await self.extract_meta_info(soup)

            # Extract navigation structure
            analysis["navigation_structure"] = await self.extract_navigation(soup)

            # Analyze tone and voice using AI
            analysis["tone_analysis"] = await self.analyze_tone_and_voice(analysis["text_content"])

            # Extract messaging themes
            analysis["messaging_themes"] = await self.extract_messaging_themes(analysis["text_content"])

            # Extract colors from CSS (simplified)
            analysis["color_analysis"] = await self.extract_colors_from_website(soup, url)

        except Exception as e:
            logger.error(f"Website analysis failed for {url}: {e}")
            analysis["error"] = str(e)

        return analysis

    async def extract_text_content(self, soup: BeautifulSoup) -> str:
        """Extract meaningful text content from website"""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Extract text from key sections
        key_sections = []

        # Homepage hero/banner content
        hero_selectors = [".hero", ".banner", ".jumbotron", "header", ".intro"]
        for selector in hero_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                if len(text) > 50:  # Only meaningful content
                    key_sections.append(text)

        # About section
        about_selectors = ["#about", ".about", "[id*='about']", "[class*='about']"]
        for selector in about_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                if len(text) > 100:
                    key_sections.append(text)

        # Main content
        main_content = soup.find("main") or soup.find("article") or soup.find(".content")
        if main_content:
            text = main_content.get_text(strip=True)
            if len(text) > 200:
                key_sections.append(text[:1000])  # Limit length

        return " ".join(key_sections)

    async def extract_meta_info(self, soup: BeautifulSoup) -> Dict:
        """Extract meta information from website"""
        meta_info = {}

        # Title
        title = soup.find("title")
        if title:
            meta_info["title"] = title.get_text(strip=True)

        # Meta description
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc:
            meta_info["description"] = meta_desc.get("content", "")

        # Meta keywords
        meta_keywords = soup.find("meta", attrs={"name": "keywords"})
        if meta_keywords:
            meta_info["keywords"] = meta_keywords.get("content", "").split(",")

        # Open Graph data
        og_tags = soup.find_all("meta", property=lambda x: x and x.startswith("og:"))
        for tag in og_tags:
            prop = tag.get("property", "").replace("og:", "")
            content = tag.get("content", "")
            if prop and content:
                meta_info[f"og_{prop}"] = content

        return meta_info

    async def extract_navigation(self, soup: BeautifulSoup) -> List[str]:
        """Extract navigation structure"""
        nav_items = []

        # Find navigation elements
        nav_elements = soup.find_all(["nav", "ul", "ol"], class_=lambda x: x and any(
            nav_term in x.lower() for nav_term in ["nav", "menu", "header"]
        ))

        for nav in nav_elements:
            links = nav.find_all("a")
            for link in links:
                text = link.get_text(strip=True)
                if text and len(text) < 50:  # Reasonable nav item length
                    nav_items.append(text)

        return list(set(nav_items))  # Remove duplicates

    async def analyze_tone_and_voice(self, text_content: str) -> Dict:
        """Analyze brand tone and voice using AI"""
        if not text_content:
            return {}

        try:
            prompt = f"""
            Analyze the tone and voice of this brand's website content:

            Content:
            {text_content[:2000]}  # Limit to avoid token limits

            Provide analysis in JSON format with these elements:
            {{
                "tone": "describe the overall tone (e.g., professional, casual, friendly, authoritative)",
                "voice_characteristics": ["list", "of", "voice", "traits"],
                "personality_traits": ["list", "of", "brand", "personality", "traits"],
                "communication_style": "describe how the brand communicates",
                "target_audience_inference": "inferred target audience based on language",
                "formality_level": "scale from 1-10 where 1 is very casual, 10 is very formal",
                "emotional_tone": "positive/neutral/negative and specific emotions conveyed"
            }}

            Return only valid JSON.
            """

            response = self.model.generate_content(prompt)
            result = json.loads(response.text)
            return result

        except Exception as e:
            logger.warning(f"Error analyzing tone and voice: {e}")
            return {}

    async def extract_messaging_themes(self, text_content: str) -> List[str]:
        """Extract key messaging themes using AI"""
        if not text_content:
            return []

        try:
            prompt = f"""
            Extract the top 5 key messaging themes from this brand content:

            Content:
            {text_content[:2000]}

            Return themes as a simple JSON array of strings:
            ["theme1", "theme2", "theme3", "theme4", "theme5"]

            Focus on the main value propositions, benefits, and core messages.
            """

            response = self.model.generate_content(prompt)
            themes = json.loads(response.text)
            return themes[:5]  # Ensure max 5 themes

        except Exception as e:
            logger.warning(f"Error extracting messaging themes: {e}")
            return []

    async def extract_colors_from_website(self, soup: BeautifulSoup, base_url: str) -> Dict:
        """Extract color palette from website (simplified version)"""
        colors = {
            "primary_colors": [],
            "secondary_colors": [],
            "accent_colors": []
        }

        try:
            # Look for CSS files
            css_links = soup.find_all("link", rel="stylesheet")

            # Extract inline styles
            inline_styles = soup.find_all(style=True)

            # This is a simplified implementation
            # In production, you'd want to parse CSS files and extract color values
            # For now, return sample data
            colors["primary_colors"] = ["#2563eb", "#1e40af"]  # Sample blues
            colors["secondary_colors"] = ["#6b7280", "#374151"]  # Sample grays
            colors["accent_colors"] = ["#f97316", "#ea580c"]  # Sample oranges

        except Exception as e:
            logger.warning(f"Error extracting colors: {e}")

        return colors

    async def analyze_social_content(self, brand: Brand) -> Dict:
        """Analyze recent social media content for brand consistency"""
        logger.info(f"Analyzing social content for brand: {brand.name}")

        db = SessionLocal()
        try:
            # Get recent published posts
            recent_posts = db.query(ContentPost).filter(
                ContentPost.brand_id == brand.id,
                ContentPost.status.in_(["published", "scheduled"])
            ).order_by(ContentPost.created_at.desc()).limit(20).all()

            if not recent_posts:
                return {"error": "No recent social content found"}

            # Analyze content consistency
            all_captions = [post.caption for post in recent_posts if post.caption]

            analysis = {
                "total_posts_analyzed": len(recent_posts),
                "content_themes": await self.analyze_content_themes(all_captions),
                "voice_consistency": await self.analyze_voice_consistency(all_captions),
                "hashtag_analysis": await self.analyze_hashtag_usage(recent_posts),
                "posting_patterns": await self.analyze_posting_patterns(recent_posts),
                "engagement_insights": await self.analyze_engagement_patterns(recent_posts)
            }

            return analysis

        finally:
            db.close()

    async def analyze_content_themes(self, captions: List[str]) -> Dict:
        """Analyze themes in social media content"""
        if not captions:
            return {}

        try:
            combined_content = " ".join(captions)

            prompt = f"""
            Analyze the content themes in these social media captions:

            Captions:
            {combined_content[:3000]}

            Return analysis in JSON format:
            {{
                "main_themes": ["theme1", "theme2", "theme3"],
                "content_categories": {{
                    "educational": percentage,
                    "promotional": percentage,
                    "entertainment": percentage,
                    "inspirational": percentage,
                    "behind_the_scenes": percentage
                }},
                "topic_frequency": {{"topic": count}}
            }}
            """

            response = self.model.generate_content(prompt)
            return json.loads(response.text)

        except Exception as e:
            logger.warning(f"Error analyzing content themes: {e}")
            return {}

    async def analyze_voice_consistency(self, captions: List[str]) -> Dict:
        """Analyze voice consistency across content"""
        if not captions:
            return {}

        try:
            sample_captions = captions[:10]  # Analyze sample

            prompt = f"""
            Analyze voice consistency across these social media captions:

            Captions:
            {json.dumps(sample_captions)}

            Return analysis in JSON format:
            {{
                "consistency_score": 0-100,
                "voice_variations": ["variation1", "variation2"],
                "tone_consistency": 0-100,
                "style_consistency": 0-100,
                "recommendations": ["recommendation1", "recommendation2"]
            }}
            """

            response = self.model.generate_content(prompt)
            return json.loads(response.text)

        except Exception as e:
            logger.warning(f"Error analyzing voice consistency: {e}")
            return {}

    async def analyze_hashtag_usage(self, posts: List[ContentPost]) -> Dict:
        """Analyze hashtag usage patterns"""
        hashtag_data = {
            "total_unique_hashtags": 0,
            "most_used_hashtags": [],
            "hashtag_frequency": {},
            "average_hashtags_per_post": 0
        }

        try:
            all_hashtags = []
            for post in posts:
                if hasattr(post, 'hashtags') and post.hashtags:
                    all_hashtags.extend(post.hashtags)

            if all_hashtags:
                from collections import Counter
                hashtag_counts = Counter(all_hashtags)

                hashtag_data["total_unique_hashtags"] = len(hashtag_counts)
                hashtag_data["most_used_hashtags"] = [tag for tag, count in hashtag_counts.most_common(10)]
                hashtag_data["hashtag_frequency"] = dict(hashtag_counts.most_common(20))
                hashtag_data["average_hashtags_per_post"] = len(all_hashtags) / len(posts)

        except Exception as e:
            logger.warning(f"Error analyzing hashtags: {e}")

        return hashtag_data

    async def analyze_posting_patterns(self, posts: List[ContentPost]) -> Dict:
        """Analyze posting time and frequency patterns"""
        patterns = {
            "posting_frequency": {},
            "best_performing_times": [],
            "content_type_distribution": {}
        }

        try:
            # Analyze posting times
            posting_hours = []
            content_types = []

            for post in posts:
                if post.published_time:
                    posting_hours.append(post.published_time.hour)
                content_types.append(post.content_type.value)

            if posting_hours:
                from collections import Counter
                hour_counts = Counter(posting_hours)
                patterns["best_performing_times"] = [f"{hour}:00" for hour, count in hour_counts.most_common(5)]

            if content_types:
                from collections import Counter
                type_counts = Counter(content_types)
                total = len(content_types)
                patterns["content_type_distribution"] = {
                    content_type: (count / total) * 100
                    for content_type, count in type_counts.items()
                }

        except Exception as e:
            logger.warning(f"Error analyzing posting patterns: {e}")

        return patterns

    async def analyze_engagement_patterns(self, posts: List[ContentPost]) -> Dict:
        """Analyze engagement patterns across content"""
        engagement = {
            "average_engagement_rate": 0,
            "best_performing_content_types": [],
            "engagement_trends": {}
        }

        try:
            engagement_rates = []
            type_engagement = {}

            for post in posts:
                if post.actual_engagement_rate:
                    engagement_rates.append(post.actual_engagement_rate)

                    content_type = post.content_type.value
                    if content_type not in type_engagement:
                        type_engagement[content_type] = []
                    type_engagement[content_type].append(post.actual_engagement_rate)

            if engagement_rates:
                engagement["average_engagement_rate"] = sum(engagement_rates) / len(engagement_rates)

                # Best performing content types
                avg_by_type = {}
                for content_type, rates in type_engagement.items():
                    avg_by_type[content_type] = sum(rates) / len(rates)

                engagement["best_performing_content_types"] = sorted(
                    avg_by_type.keys(),
                    key=lambda x: avg_by_type[x],
                    reverse=True
                )

        except Exception as e:
            logger.warning(f"Error analyzing engagement patterns: {e}")

        return engagement

    async def analyze_visual_elements(self, brand: Brand) -> Dict:
        """Analyze visual brand elements"""
        visual_analysis = {
            "logo_analysis": {},
            "color_consistency": {},
            "image_style_analysis": {},
            "typography_analysis": {}
        }

        # This would typically analyze uploaded brand assets
        # For now, return placeholder data
        visual_analysis["color_consistency"] = {
            "primary_color_usage": 85,
            "secondary_color_usage": 70,
            "brand_color_adherence": 78
        }

        return visual_analysis

    async def create_style_guide(self, brand: Brand, analysis_data: Dict) -> Dict:
        """Create comprehensive brand style guide using AI"""
        try:
            # Combine all analysis data
            combined_analysis = json.dumps({
                "website_analysis": analysis_data.get("website_analysis", {}),
                "social_analysis": analysis_data.get("social_content_analysis", {}),
                "visual_analysis": analysis_data.get("visual_analysis", {}),
                "brand_info": {
                    "name": brand.name,
                    "industry": brand.industry,
                    "description": brand.description,
                    "target_audience": brand.target_audience
                }
            })

            prompt = f"""
            Create a comprehensive brand style guide based on this analysis:

            Analysis Data:
            {combined_analysis[:4000]}  # Limit to avoid token limits

            Generate a detailed brand style guide in JSON format:
            {{
                "brand_voice": {{
                    "tone": "overall brand tone",
                    "personality_traits": ["trait1", "trait2", "trait3"],
                    "communication_style": "how the brand communicates",
                    "voice_guidelines": ["guideline1", "guideline2"]
                }},
                "messaging": {{
                    "key_messages": ["message1", "message2"],
                    "value_propositions": ["prop1", "prop2"],
                    "taglines": ["tagline1", "tagline2"],
                    "content_pillars": ["pillar1", "pillar2", "pillar3"]
                }},
                "visual_identity": {{
                    "color_palette": {{
                        "primary": ["#color1", "#color2"],
                        "secondary": ["#color3", "#color4"],
                        "accent": ["#color5"]
                    }},
                    "typography": {{
                        "primary_font": "font name",
                        "secondary_font": "font name",
                        "font_guidelines": "usage guidelines"
                    }},
                    "image_style": {{
                        "style_description": "description of image style",
                        "color_treatment": "how colors should be used",
                        "composition_guidelines": "layout and composition rules"
                    }}
                }},
                "content_guidelines": {{
                    "dos": ["do1", "do2"],
                    "donts": ["dont1", "dont2"],
                    "hashtag_strategy": ["strategy1", "strategy2"],
                    "posting_best_practices": ["practice1", "practice2"]
                }},
                "target_audience": {{
                    "primary_audience": "description",
                    "demographics": "age, location, interests",
                    "psychographics": "values, attitudes, lifestyle",
                    "communication_preferences": "how they prefer to be communicated with"
                }}
            }}

            Return only valid JSON.
            """

            response = self.model.generate_content(prompt)
            style_guide = json.loads(response.text)

            # Add timestamp and version
            style_guide["created_at"] = datetime.utcnow().isoformat()
            style_guide["version"] = "1.0"

            return style_guide

        except Exception as e:
            logger.error(f"Error creating style guide: {e}")
            return {}

    async def generate_recommendations(self, brand: Brand, analysis_data: Dict) -> List[Dict]:
        """Generate actionable recommendations based on analysis"""
        try:
            prompt = f"""
            Based on this brand analysis, generate 5 actionable recommendations:

            Analysis Summary:
            {json.dumps(analysis_data, indent=2)[:3000]}

            Return recommendations in JSON format:
            [
                {{
                    "category": "voice/visual/content/strategy",
                    "title": "recommendation title",
                    "description": "detailed description",
                    "priority": "high/medium/low",
                    "impact": "description of expected impact",
                    "action_items": ["action1", "action2"]
                }}
            ]

            Focus on practical, implementable recommendations.
            """

            response = self.model.generate_content(prompt)
            recommendations = json.loads(response.text)
            return recommendations

        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return []

    async def update_brand_style_guide(self, brand: Brand, style_guide: Dict):
        """Update brand record with new style guide"""
        db = SessionLocal()
        try:
            brand.style_guide = style_guide

            # Extract and update other fields
            if "visual_identity" in style_guide and "color_palette" in style_guide["visual_identity"]:
                brand.color_palette = style_guide["visual_identity"]["color_palette"]

            if "visual_identity" in style_guide and "typography" in style_guide["visual_identity"]:
                brand.typography = style_guide["visual_identity"]["typography"]

            if "messaging" in style_guide and "content_pillars" in style_guide["messaging"]:
                brand.content_pillars = style_guide["messaging"]["content_pillars"]

            brand.updated_at = datetime.utcnow()
            db.commit()

            logger.info(f"Updated style guide for brand {brand.name}")

        except Exception as e:
            logger.error(f"Error updating brand style guide: {e}")
            db.rollback()
        finally:
            db.close()
