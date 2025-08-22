"""
AI Content Generation Module
OpenAI-powered content creation for social media platforms
"""

import openai
import logging
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from config.settings import settings

logger = logging.getLogger(__name__)

class AIContentGenerator:
    """AI-powered content generator using OpenAI"""

    def __init__(self):
        if settings.openai_api_key:
            openai.api_key = settings.openai_api_key
            if settings.openai_org_id:
                openai.organization = settings.openai_org_id
        else:
            logger.warning("OpenAI API key not configured. AI features will be disabled.")

    def _is_configured(self) -> bool:
        """Check if OpenAI is properly configured"""
        return bool(settings.openai_api_key)

    def generate_caption(
        self,
        brand_context: Dict,
        content_type: str,
        platform: str,
        topic: Optional[str] = None,
        additional_context: Optional[str] = None
    ) -> Dict:
        """Generate social media caption for specific platform"""

        if not self._is_configured():
            return {"error": "OpenAI not configured"}

        try:
            # Build context prompt
            prompt = self._build_caption_prompt(
                brand_context, content_type, platform, topic, additional_context
            )

            # Generate content
            response = openai.ChatCompletion.create(
                model=settings.ai_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional social media content creator specializing in engaging, brand-aligned posts."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=settings.ai_max_tokens,
                temperature=settings.ai_temperature,
                top_p=0.9,
                frequency_penalty=0.1,
                presence_penalty=0.1
            )

            content = response.choices[0].message.content.strip()

            # Parse and structure the response
            result = self._parse_caption_response(content, platform)

            return {
                "success": True,
                "content": result,
                "usage": response.usage._asdict(),
                "model": settings.ai_model
            }

        except Exception as e:
            logger.error(f"Error generating caption: {str(e)}")
            return {"error": f"Content generation failed: {str(e)}"}

    def generate_hashtags(
        self,
        content: str,
        platform: str,
        brand_context: Dict,
        target_count: int = 10
    ) -> List[str]:
        """Generate relevant hashtags for content"""

        if not self._is_configured():
            return []

        try:
            prompt = f"""
            Generate {target_count} relevant hashtags for this {platform} post:

            Content: "{content}"

            Brand: {brand_context.get('name', 'Unknown')}
            Industry: {brand_context.get('industry', 'General')}
            Target Audience: {brand_context.get('target_audience', 'General')}

            Platform-specific requirements:
            - {self._get_platform_hashtag_rules(platform)}

            Return only the hashtags, one per line, with # symbol.
            Focus on trending, relevant, and brand-appropriate hashtags.
            """

            response = openai.ChatCompletion.create(
                model=settings.ai_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a social media hashtag expert who creates trending, relevant hashtags."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=300,
                temperature=0.7
            )

            hashtags_text = response.choices[0].message.content.strip()
            hashtags = [
                line.strip()
                for line in hashtags_text.split('\n')
                if line.strip().startswith('#')
            ]

            return hashtags[:target_count]

        except Exception as e:
            logger.error(f"Error generating hashtags: {str(e)}")
            return []

    def generate_content_ideas(
        self,
        brand_context: Dict,
        platform: str,
        count: int = 5
    ) -> List[Dict]:
        """Generate content ideas for a brand"""

        if not self._is_configured():
            return []

        try:
            prompt = f"""
            Generate {count} creative content ideas for {platform} for this brand:

            Brand: {brand_context.get('name', 'Unknown')}
            Industry: {brand_context.get('industry', 'General')}
            Description: {brand_context.get('description', 'No description')}
            Target Audience: {brand_context.get('target_audience', 'General')}
            Content Pillars: {json.dumps(brand_context.get('content_pillars', []))}

            For each idea, provide:
            1. Content type (photo, video, carousel, story)
            2. Title/topic
            3. Brief description
            4. Key message
            5. Suggested timing

            Return as JSON array with these fields for each idea:
            {{
                "type": "photo|video|carousel|story",
                "title": "Content title",
                "description": "Brief description",
                "message": "Key message",
                "timing": "Best time to post",
                "engagement_potential": "high|medium|low"
            }}
            """

            response = openai.ChatCompletion.create(
                model=settings.ai_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a creative social media strategist who generates engaging content ideas."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1500,
                temperature=0.8
            )

            content = response.choices[0].message.content.strip()

            # Try to parse JSON response
            try:
                ideas = json.loads(content)
                return ideas if isinstance(ideas, list) else []
            except json.JSONDecodeError:
                # Fallback: parse manually
                return self._parse_ideas_fallback(content)

        except Exception as e:
            logger.error(f"Error generating content ideas: {str(e)}")
            return []

    def optimize_content_for_platform(
        self,
        content: str,
        source_platform: str,
        target_platform: str,
        brand_context: Dict
    ) -> Dict:
        """Optimize content for different platform"""

        if not self._is_configured():
            return {"error": "OpenAI not configured"}

        try:
            prompt = f"""
            Adapt this {source_platform} content for {target_platform}:

            Original Content: "{content}"

            Brand Context:
            - Name: {brand_context.get('name', 'Unknown')}
            - Tone: {brand_context.get('style_guide', {}).get('tone', 'Professional')}
            - Industry: {brand_context.get('industry', 'General')}

            Platform Requirements:
            Source ({source_platform}): {self._get_platform_requirements(source_platform)}
            Target ({target_platform}): {self._get_platform_requirements(target_platform)}

            Optimize for:
            1. Platform-specific format and style
            2. Optimal length and structure
            3. Platform-appropriate hashtags
            4. Engagement optimization

            Return the optimized content.
            """

            response = openai.ChatCompletion.create(
                model=settings.ai_model,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a social media expert who adapts content for different platforms. Focus on {target_platform} best practices."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=800,
                temperature=0.6
            )

            optimized_content = response.choices[0].message.content.strip()

            return {
                "success": True,
                "original_content": content,
                "optimized_content": optimized_content,
                "source_platform": source_platform,
                "target_platform": target_platform
            }

        except Exception as e:
            logger.error(f"Error optimizing content: {str(e)}")
            return {"error": f"Content optimization failed: {str(e)}"}

    def analyze_brand_voice(self, brand_context: Dict, sample_content: List[str]) -> Dict:
        """Analyze and define brand voice from sample content"""

        if not self._is_configured():
            return {"error": "OpenAI not configured"}

        try:
            content_sample = "\n".join(sample_content[:5])  # Limit to 5 samples

            prompt = f"""
            Analyze the brand voice and style from this content:

            Brand: {brand_context.get('name', 'Unknown')}
            Industry: {brand_context.get('industry', 'General')}

            Sample Content:
            {content_sample}

            Analyze and provide:
            1. Tone (formal, casual, friendly, professional, etc.)
            2. Voice characteristics (authoritative, conversational, inspiring, etc.)
            3. Writing style patterns
            4. Key phrases or expressions
            5. Target audience communication style
            6. Brand personality traits

            Return as JSON:
            {{
                "tone": "tone description",
                "voice_characteristics": ["trait1", "trait2", "trait3"],
                "writing_style": "style description",
                "key_phrases": ["phrase1", "phrase2"],
                "audience_style": "how they communicate with audience",
                "personality_traits": ["trait1", "trait2", "trait3"],
                "recommendations": ["recommendation1", "recommendation2"]
            }}
            """

            response = openai.ChatCompletion.create(
                model=settings.ai_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a brand strategist and communications expert who analyzes brand voice and style."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1000,
                temperature=0.5
            )

            content = response.choices[0].message.content.strip()

            try:
                analysis = json.loads(content)
                return {"success": True, "analysis": analysis}
            except json.JSONDecodeError:
                return {"success": True, "analysis": {"raw_response": content}}

        except Exception as e:
            logger.error(f"Error analyzing brand voice: {str(e)}")
            return {"error": f"Brand voice analysis failed: {str(e)}"}

    def _build_caption_prompt(
        self,
        brand_context: Dict,
        content_type: str,
        platform: str,
        topic: Optional[str],
        additional_context: Optional[str]
    ) -> str:
        """Build prompt for caption generation"""

        brand_name = brand_context.get('name', 'Unknown Brand')
        industry = brand_context.get('industry', 'General')
        description = brand_context.get('description', '')
        target_audience = brand_context.get('target_audience', 'General audience')
        style_guide = brand_context.get('style_guide', {})
        tone = style_guide.get('tone', 'Professional')

        prompt = f"""
        Create a {platform} {content_type} caption for {brand_name}.

        Brand Information:
        - Industry: {industry}
        - Description: {description}
        - Target Audience: {target_audience}
        - Brand Tone: {tone}

        Content Requirements:
        - Platform: {platform}
        - Content Type: {content_type}
        - Topic: {topic or 'General brand content'}

        Platform Guidelines:
        {self._get_platform_requirements(platform)}

        Additional Context: {additional_context or 'None'}

        Create engaging, on-brand content that:
        1. Matches the brand voice and tone
        2. Follows platform best practices
        3. Includes appropriate call-to-action
        4. Is optimized for engagement
        5. Stays within platform character limits

        Format the response with:
        - Main caption text
        - Suggested hashtags (if appropriate for platform)
        - Call-to-action
        """

        return prompt

    def _parse_caption_response(self, content: str, platform: str) -> Dict:
        """Parse AI response into structured caption data"""

        lines = content.split('\n')
        result = {
            "caption": "",
            "hashtags": [],
            "call_to_action": "",
            "full_text": content
        }

        # Try to extract structured parts
        current_section = "caption"
        caption_lines = []
        hashtags = []
        cta = ""

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Detect sections
            if "hashtag" in line.lower() and ":" in line:
                current_section = "hashtags"
                continue
            elif "call-to-action" in line.lower() or "cta" in line.lower():
                current_section = "cta"
                continue

            # Extract content based on section
            if current_section == "caption" and not line.startswith('#'):
                caption_lines.append(line)
            elif current_section == "hashtags" or line.startswith('#'):
                hashtag_text = line.replace('Hashtags:', '').replace('Tags:', '').strip()
                if hashtag_text.startswith('#'):
                    hashtags.extend([tag.strip() for tag in hashtag_text.split() if tag.startswith('#')])
            elif current_section == "cta":
                cta += " " + line

        result["caption"] = '\n'.join(caption_lines).strip()
        result["hashtags"] = hashtags[:settings.max_hashtags_per_post]
        result["call_to_action"] = cta.strip()

        # If no structured parsing worked, use full content as caption
        if not result["caption"]:
            result["caption"] = content

        return result

    def _get_platform_requirements(self, platform: str) -> str:
        """Get platform-specific requirements and best practices"""

        requirements = {
            "instagram": """
            - Character limit: 2,200 (first 125 characters visible)
            - Use emojis and line breaks for readability
            - Include call-to-action
            - Use 3-5 relevant hashtags in caption or first comment
            - Focus on visual storytelling
            """,
            "twitter": """
            - Character limit: 280 characters
            - Use 1-2 hashtags maximum
            - Include @mentions when relevant
            - Keep it concise and engaging
            - Use threads for longer content
            """,
            "linkedin": """
            - Professional tone
            - 1,300 character limit for optimal engagement
            - Include industry insights or value
            - Use professional hashtags
            - Focus on business value and networking
            """,
            "facebook": """
            - Conversational tone
            - Optimal length: 40-80 characters for highest engagement
            - Use questions to encourage interaction
            - Include relevant links
            - Use minimal hashtags (1-2)
            """
        }

        return requirements.get(platform.lower(), "General social media best practices")

    def _get_platform_hashtag_rules(self, platform: str) -> str:
        """Get platform-specific hashtag guidelines"""

        rules = {
            "instagram": "Use 3-30 hashtags, mix popular and niche tags",
            "twitter": "Use 1-2 hashtags maximum, avoid hashtag stuffing",
            "linkedin": "Use 3-5 professional hashtags",
            "facebook": "Use 1-2 hashtags, focus on branded tags"
        }

        return rules.get(platform.lower(), "Use relevant hashtags sparingly")

    def _parse_ideas_fallback(self, content: str) -> List[Dict]:
        """Fallback parser for content ideas when JSON parsing fails"""

        ideas = []
        lines = content.split('\n')
        current_idea = {}

        for line in lines:
            line = line.strip()
            if not line:
                if current_idea:
                    ideas.append(current_idea)
                    current_idea = {}
                continue

            # Try to extract structured data
            if line.startswith(('1.', '2.', '3.', '4.', '5.')):
                if current_idea:
                    ideas.append(current_idea)
                current_idea = {"title": line, "type": "photo", "description": "", "message": "", "timing": ""}
            else:
                if current_idea:
                    current_idea["description"] += " " + line

        if current_idea:
            ideas.append(current_idea)

        return ideas[:5]  # Limit to 5 ideas

# Global instance
ai_generator = AIContentGenerator()
