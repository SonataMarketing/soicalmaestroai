"""
LinkedIn API Integration
LinkedIn API integration for professional content posting and company page management
"""

import requests
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from config.settings import settings

logger = logging.getLogger(__name__)

class LinkedInAPI:
    """LinkedIn API integration for professional social media management"""

    def __init__(self):
        self.client_id = settings.linkedin_client_id
        self.client_secret = settings.linkedin_client_secret
        self.redirect_uri = settings.linkedin_redirect_uri
        self.base_url = "https://api.linkedin.com/v2"

    def is_configured(self) -> bool:
        """Check if LinkedIn API is properly configured"""
        return bool(self.client_id and self.client_secret)

    def get_authorization_url(self, state: str = None) -> Dict:
        """Get LinkedIn OAuth authorization URL"""

        if not self.is_configured():
            return {"error": "LinkedIn API not configured"}

        # LinkedIn OAuth scopes
        scopes = [
            "r_liteprofile",
            "r_emailaddress",
            "w_member_social",
            "r_organization_social",
            "w_organization_social"
        ]

        auth_url = (
            f"https://www.linkedin.com/oauth/v2/authorization"
            f"?response_type=code"
            f"&client_id={self.client_id}"
            f"&redirect_uri={self.redirect_uri}"
            f"&scope={' '.join(scopes)}"
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
            return {"error": "LinkedIn API not configured"}

        try:
            token_url = "https://www.linkedin.com/oauth/v2/accessToken"

            data = {
                "grant_type": "authorization_code",
                "code": authorization_code,
                "redirect_uri": self.redirect_uri,
                "client_id": self.client_id,
                "client_secret": self.client_secret
            }

            headers = {
                "Content-Type": "application/x-www-form-urlencoded"
            }

            response = requests.post(token_url, data=data, headers=headers)
            response.raise_for_status()

            token_data = response.json()
            access_token = token_data.get("access_token")

            if not access_token:
                return {"error": "Failed to get access token"}

            # Get user profile information
            user_info = self.get_user_profile(access_token)

            return {
                "access_token": access_token,
                "expires_in": token_data.get("expires_in", 5184000),  # Default 60 days
                "user_info": user_info,
                "token_type": "Bearer"
            }

        except requests.RequestException as e:
            logger.error(f"LinkedIn token exchange error: {str(e)}")
            return {"error": f"Token exchange failed: {str(e)}"}

    def get_user_profile(self, access_token: str) -> Dict:
        """Get LinkedIn user profile information"""

        try:
            url = f"{self.base_url}/people/~"

            params = {
                "projection": "(id,firstName,lastName,profilePicture(displayImage~:playableStreams))"
            }

            headers = {
                "Authorization": f"Bearer {access_token}"
            }

            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()

            data = response.json()

            # Also get email address
            email_url = f"{self.base_url}/emailAddress"
            email_params = {"q": "members", "projection": "(elements*(handle~))"}
            email_response = requests.get(email_url, params=email_params, headers=headers)

            email_data = {}
            if email_response.status_code == 200:
                email_data = email_response.json()

            # Extract email if available
            email = None
            if "elements" in email_data and email_data["elements"]:
                email = email_data["elements"][0].get("handle~", {}).get("emailAddress")

            return {
                "id": data.get("id"),
                "first_name": data.get("firstName", {}).get("localized", {}).get("en_US", ""),
                "last_name": data.get("lastName", {}).get("localized", {}).get("en_US", ""),
                "email": email,
                "profile_picture": self._extract_profile_picture(data)
            }

        except requests.RequestException as e:
            logger.error(f"LinkedIn profile error: {str(e)}")
            return {"error": f"Failed to get profile: {str(e)}"}

    def _extract_profile_picture(self, profile_data: Dict) -> Optional[str]:
        """Extract profile picture URL from LinkedIn API response"""

        try:
            profile_picture = profile_data.get("profilePicture", {})
            display_image = profile_picture.get("displayImage~", {})
            elements = display_image.get("elements", [])

            if elements:
                # Get the largest image
                largest_image = max(elements, key=lambda x: x.get("data", {}).get("com.linkedin.digitalmedia.mediaartifact.StillImage", {}).get("storageSize", {}).get("width", 0))
                identifiers = largest_image.get("identifiers", [])
                if identifiers:
                    return identifiers[0].get("identifier")

            return None

        except Exception:
            return None

    def post_to_profile(
        self,
        access_token: str,
        text: str,
        image_url: str = None,
        article_url: str = None
    ) -> Dict:
        """Post text content to LinkedIn profile"""

        try:
            url = f"{self.base_url}/ugcPosts"

            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0"
            }

            # Get person URN
            person_urn = self._get_person_urn(access_token)
            if not person_urn:
                return {"error": "Failed to get person URN"}

            # Build post data
            post_data = {
                "author": person_urn,
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

            # Add media if provided
            if image_url:
                media_urn = self._upload_image(access_token, image_url, person_urn)
                if media_urn:
                    post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "IMAGE"
                    post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [
                        {
                            "status": "READY",
                            "description": {
                                "text": "Image"
                            },
                            "media": media_urn
                        }
                    ]

            # Add article link if provided
            if article_url:
                post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "ARTICLE"
                post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [
                    {
                        "status": "READY",
                        "originalUrl": article_url
                    }
                ]

            response = requests.post(url, json=post_data, headers=headers)
            response.raise_for_status()

            result = response.json()

            return {
                "success": True,
                "post_id": result.get("id"),
                "message": "Post published successfully to LinkedIn"
            }

        except requests.RequestException as e:
            logger.error(f"LinkedIn post error: {str(e)}")
            return {"error": f"Failed to post to LinkedIn: {str(e)}"}

    def _get_person_urn(self, access_token: str) -> Optional[str]:
        """Get person URN for posting"""

        try:
            url = f"{self.base_url}/people/~"

            headers = {
                "Authorization": f"Bearer {access_token}"
            }

            response = requests.get(url, headers=headers)
            response.raise_for_status()

            data = response.json()
            person_id = data.get("id")

            if person_id:
                return f"urn:li:person:{person_id}"

            return None

        except Exception as e:
            logger.error(f"Error getting person URN: {str(e)}")
            return None

    def _upload_image(self, access_token: str, image_url: str, person_urn: str) -> Optional[str]:
        """Upload image to LinkedIn for use in posts"""

        try:
            # Step 1: Register upload
            register_url = f"{self.base_url}/assets"

            register_data = {
                "registerUploadRequest": {
                    "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                    "owner": person_urn,
                    "serviceRelationships": [
                        {
                            "relationshipType": "OWNER",
                            "identifier": "urn:li:userGeneratedContent"
                        }
                    ]
                }
            }

            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }

            register_response = requests.post(register_url, json=register_data, headers=headers)
            register_response.raise_for_status()

            register_result = register_response.json()
            upload_mechanism = register_result.get("value", {}).get("uploadMechanism", {})
            upload_url = upload_mechanism.get("com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest", {}).get("uploadUrl")
            asset_urn = register_result.get("value", {}).get("asset")

            if not upload_url or not asset_urn:
                return None

            # Step 2: Download image
            image_response = requests.get(image_url)
            image_response.raise_for_status()

            # Step 3: Upload image
            upload_headers = {
                "Authorization": f"Bearer {access_token}"
            }

            upload_response = requests.post(
                upload_url,
                data=image_response.content,
                headers=upload_headers
            )
            upload_response.raise_for_status()

            return asset_urn

        except Exception as e:
            logger.error(f"LinkedIn image upload error: {str(e)}")
            return None

    def get_profile_posts(self, access_token: str, count: int = 20) -> Dict:
        """Get user's LinkedIn posts"""

        try:
            person_urn = self._get_person_urn(access_token)
            if not person_urn:
                return {"error": "Failed to get person URN"}

            url = f"{self.base_url}/ugcPosts"

            params = {
                "q": "authors",
                "authors": person_urn,
                "count": count,
                "projection": "(id,author,created,specificContent,ugcPostAnalytics)"
            }

            headers = {
                "Authorization": f"Bearer {access_token}"
            }

            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()

            data = response.json()
            posts = []

            for post in data.get("elements", []):
                post_data = {
                    "id": post.get("id"),
                    "created": post.get("created", {}).get("time"),
                    "text": self._extract_post_text(post),
                    "analytics": post.get("ugcPostAnalytics", {})
                }
                posts.append(post_data)

            return {"success": True, "posts": posts}

        except requests.RequestException as e:
            logger.error(f"LinkedIn posts error: {str(e)}")
            return {"error": f"Failed to get posts: {str(e)}"}

    def _extract_post_text(self, post_data: Dict) -> str:
        """Extract text content from LinkedIn post"""

        try:
            specific_content = post_data.get("specificContent", {})
            share_content = specific_content.get("com.linkedin.ugc.ShareContent", {})
            share_commentary = share_content.get("shareCommentary", {})
            return share_commentary.get("text", "")
        except Exception:
            return ""

    def get_company_pages(self, access_token: str) -> List[Dict]:
        """Get company pages that user can manage"""

        try:
            url = f"{self.base_url}/organizationAcls"

            params = {
                "q": "roleAssignee",
                "projection": "(elements*(organization~(id,name,logoV2),roleAssignee,role))"
            }

            headers = {
                "Authorization": f"Bearer {access_token}"
            }

            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()

            data = response.json()
            companies = []

            for element in data.get("elements", []):
                organization = element.get("organization~", {})
                role = element.get("role")

                if role in ["ADMINISTRATOR", "DIRECT_SPONSORED_CONTENT_POSTER"]:
                    companies.append({
                        "id": organization.get("id"),
                        "name": organization.get("name", {}).get("localized", {}).get("en_US", ""),
                        "role": role,
                        "logo": self._extract_company_logo(organization)
                    })

            return companies

        except requests.RequestException as e:
            logger.error(f"LinkedIn company pages error: {str(e)}")
            return []

    def _extract_company_logo(self, organization_data: Dict) -> Optional[str]:
        """Extract company logo URL from organization data"""

        try:
            logo_v2 = organization_data.get("logoV2", {})
            cropped_image = logo_v2.get("cropped~", {})
            elements = cropped_image.get("elements", [])

            if elements:
                # Get the largest image
                largest_image = max(elements, key=lambda x: x.get("data", {}).get("com.linkedin.digitalmedia.mediaartifact.StillImage", {}).get("storageSize", {}).get("width", 0))
                identifiers = largest_image.get("identifiers", [])
                if identifiers:
                    return identifiers[0].get("identifier")

            return None

        except Exception:
            return None

    def post_to_company_page(
        self,
        access_token: str,
        company_id: str,
        text: str,
        image_url: str = None
    ) -> Dict:
        """Post content to LinkedIn company page"""

        try:
            url = f"{self.base_url}/ugcPosts"

            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0"
            }

            company_urn = f"urn:li:organization:{company_id}"

            # Build post data
            post_data = {
                "author": company_urn,
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

            # Add image if provided
            if image_url:
                media_urn = self._upload_image_for_company(access_token, image_url, company_urn)
                if media_urn:
                    post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "IMAGE"
                    post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [
                        {
                            "status": "READY",
                            "description": {
                                "text": "Image"
                            },
                            "media": media_urn
                        }
                    ]

            response = requests.post(url, json=post_data, headers=headers)
            response.raise_for_status()

            result = response.json()

            return {
                "success": True,
                "post_id": result.get("id"),
                "message": "Post published successfully to LinkedIn company page"
            }

        except requests.RequestException as e:
            logger.error(f"LinkedIn company post error: {str(e)}")
            return {"error": f"Failed to post to LinkedIn company page: {str(e)}"}

    def _upload_image_for_company(self, access_token: str, image_url: str, company_urn: str) -> Optional[str]:
        """Upload image for company page posts"""

        try:
            # Step 1: Register upload for company
            register_url = f"{self.base_url}/assets"

            register_data = {
                "registerUploadRequest": {
                    "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                    "owner": company_urn,
                    "serviceRelationships": [
                        {
                            "relationshipType": "OWNER",
                            "identifier": "urn:li:userGeneratedContent"
                        }
                    ]
                }
            }

            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }

            register_response = requests.post(register_url, json=register_data, headers=headers)
            register_response.raise_for_status()

            register_result = register_response.json()
            upload_mechanism = register_result.get("value", {}).get("uploadMechanism", {})
            upload_url = upload_mechanism.get("com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest", {}).get("uploadUrl")
            asset_urn = register_result.get("value", {}).get("asset")

            if not upload_url or not asset_urn:
                return None

            # Step 2: Download and upload image
            image_response = requests.get(image_url)
            image_response.raise_for_status()

            upload_headers = {
                "Authorization": f"Bearer {access_token}"
            }

            upload_response = requests.post(
                upload_url,
                data=image_response.content,
                headers=upload_headers
            )
            upload_response.raise_for_status()

            return asset_urn

        except Exception as e:
            logger.error(f"LinkedIn company image upload error: {str(e)}")
            return None

    def get_post_analytics(self, access_token: str, post_id: str) -> Dict:
        """Get analytics for a specific LinkedIn post"""

        try:
            url = f"{self.base_url}/ugcPostAnalytics/{post_id}"

            headers = {
                "Authorization": f"Bearer {access_token}"
            }

            response = requests.get(url, headers=headers)
            response.raise_for_status()

            return {"success": True, "analytics": response.json()}

        except requests.RequestException as e:
            logger.error(f"LinkedIn post analytics error: {str(e)}")
            return {"error": f"Failed to get post analytics: {str(e)}"}

    def delete_post(self, access_token: str, post_id: str) -> Dict:
        """Delete a LinkedIn post"""

        try:
            url = f"{self.base_url}/ugcPosts/{post_id}"

            headers = {
                "Authorization": f"Bearer {access_token}"
            }

            response = requests.delete(url, headers=headers)
            response.raise_for_status()

            return {
                "success": True,
                "post_id": post_id,
                "message": "Post deleted successfully"
            }

        except requests.RequestException as e:
            logger.error(f"LinkedIn delete error: {str(e)}")
            return {"error": f"Failed to delete post: {str(e)}"}

    def validate_token(self, access_token: str) -> Dict:
        """Validate LinkedIn access token"""

        try:
            profile_info = self.get_user_profile(access_token)

            if "error" in profile_info:
                return {"valid": False, "error": profile_info["error"]}

            companies = self.get_company_pages(access_token)

            return {
                "valid": True,
                "user_id": profile_info.get("id"),
                "user_name": f"{profile_info.get('first_name', '')} {profile_info.get('last_name', '')}".strip(),
                "company_pages_count": len(companies)
            }

        except Exception as e:
            return {"valid": False, "error": str(e)}

    def search_companies(self, access_token: str, query: str) -> Dict:
        """Search for companies on LinkedIn"""

        try:
            url = f"{self.base_url}/companySearch"

            params = {
                "keywords": query,
                "facet": "network",
                "facetNetwork": ["F"],
                "count": 10
            }

            headers = {
                "Authorization": f"Bearer {access_token}"
            }

            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()

            data = response.json()
            companies = []

            for company in data.get("companies", {}).get("values", []):
                companies.append({
                    "id": company.get("id"),
                    "name": company.get("name"),
                    "description": company.get("description"),
                    "industry": company.get("industries", {}).get("values", [{}])[0].get("name") if company.get("industries") else None,
                    "size": company.get("size"),
                    "website": company.get("websiteUrl")
                })

            return {"success": True, "companies": companies}

        except requests.RequestException as e:
            logger.error(f"LinkedIn company search error: {str(e)}")
            return {"error": f"Failed to search companies: {str(e)}"}

# Global instance
linkedin_api = LinkedInAPI()
