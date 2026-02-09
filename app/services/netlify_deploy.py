"""
Netlify Deployment Service

CONCEPT: Programmatic website deployment using Netlify's API

WHY NETLIFY?
- Free tier with SSL (HTTPS)
- Instant global CDN
- No server management
- Simple API (POST zip → get URL)

ALTERNATIVE DEPLOYMENT OPTIONS:
- Vercel (similar to Netlify, good for Next.js)
- GitHub Pages (free but no build API)
- AWS S3 + CloudFront (more complex, more control)
- Firebase Hosting (Google ecosystem)

For MVP, Netlify is perfect: simple, fast, free SSL
"""

import requests
import logging
from io import BytesIO
from typing import Dict, Any
from app.config import settings

logger = logging.getLogger(__name__)


class NetlifyDeployerService:
    """
    Deploys ZIP files to Netlify
    
    ARCHITECTURE:
    - Stateless service (each deploy is independent)
    - Uses Netlify's REST API
    - Handles authentication via token
    """
    
    API_BASE = "https://api.netlify.com/api/v1"
    
    def __init__(self):
        """
        Initialize with API credentials
        
        SECURITY NOTE:
        Access tokens should NEVER be hardcoded.
        Always use environment variables.
        """
        if not settings.netlify_access_token:
            raise ValueError("NETLIFY_ACCESS_TOKEN not found in environment")
        
        self.headers = {
            "Authorization": f"Bearer {settings.netlify_access_token}",
            "Content-Type": "application/zip"
        }
        logger.info("Netlify deployer initialized")
    
    def deploy_site(self, zip_buffer: BytesIO, site_name: str = None) -> Dict[str, str]:
        """
        Deploy a ZIP file to Netlify
        
        API WORKFLOW:
        1. POST zip to /api/v1/sites
        2. Netlify extracts files
        3. Builds and deploys to CDN
        4. Returns site URL
        
        IMPORTANT: Netlify looks for index.html in the ZIP root
        
        Args:
            zip_buffer: In-memory ZIP file
            site_name: Optional custom subdomain (e.g., "myportfolio")
            
        Returns:
            Dict with:
                - site_url: Full HTTPS URL
                - admin_url: Netlify dashboard URL
                - site_id: Unique site identifier
        
        Raises:
            ValueError: If deployment fails
        
        CONCEPT: RESTful API Call
        POST = Create a new resource
        Headers = Authentication + Content type
        Body = Binary data (ZIP file)
        Response = JSON with site details
        """
        try:
            # API endpoint for site creation
            url = f"{self.API_BASE}/sites"
            
            # CONCEPT: HTTP POST with binary data
            # We're sending the ZIP file directly in the request body
            response = requests.post(
                url,
                headers=self.headers,
                data=zip_buffer.read(),  # Read entire ZIP into memory
                timeout=60  # IMPORTANT: Deployment can take 30-60 seconds
            )
            
            # CONCEPT: HTTP status codes
            # 200-299: Success
            # 400-499: Client error (bad request, auth failed, etc.)
            # 500-599: Server error (Netlify issues)
            if response.status_code not in [200, 201]:
                try:
                    error_data = response.json()
                    error_msg = error_data.get("message", str(error_data))
                except:
                    error_msg = response.text
                logger.error(f"Netlify error (status {response.status_code}): {error_msg}")
                raise ValueError(f"Netlify deployment failed (status {response.status_code}): {error_msg}")
            
            # Parse response JSON
            site_data = response.json()
            
            # Netlify returns slightly different field names
            # For direct ZIP upload, we get 'url' instead of 'ssl_url'
            result = {
                "site_url": site_data.get("ssl_url") or site_data.get("url", "").replace("http://", "https://"),
                "admin_url": site_data.get("admin_url", ""),
                "site_id": site_data["id"],
                "site_name": site_data.get("name", site_data.get("subdomain", ""))
            }
            
            logger.info(f"Successfully deployed to {result['site_url']}")
            return result
            
        except requests.RequestException as e:
            logger.error(f"Network error during deployment: {e}")
            raise ValueError(f"Failed to connect to Netlify: {str(e)}")
        except Exception as e:
            logger.error(f"Deployment error: {e}")
            raise ValueError(f"Deployment failed: {str(e)}")
    
    def update_site(self, site_id: str, zip_buffer: BytesIO) -> Dict[str, str]:
        """
        Update an existing Netlify site
        
        USE CASE: User edits their portfolio and redeploys
        
        DIFFERENCE FROM deploy_site():
        - Uses PUT instead of POST
        - Requires site_id from previous deployment
        - Keeps the same URL
        
        Args:
            site_id: Netlify site ID (from previous deploy)
            zip_buffer: Updated ZIP file
            
        Returns:
            Updated site info
        """
        try:
            url = f"{self.API_BASE}/sites/{site_id}/deploys"
            
            response = requests.post(
                url,
                headers=self.headers,
                data=zip_buffer.read(),
                timeout=60
            )
            
            if response.status_code not in [200, 201]:
                raise ValueError(f"Update failed: {response.text}")
            
            deploy_data = response.json()
            
            logger.info(f"Successfully updated site {site_id}")
            return {
                "site_url": deploy_data["ssl_url"],
                "deploy_id": deploy_data["id"]
            }
            
        except Exception as e:
            logger.error(f"Update error: {e}")
            raise ValueError(f"Failed to update site: {str(e)}")
    
    def delete_site(self, site_id: str) -> bool:
        """
        Delete a Netlify site
        
        USE CASE: User cancels subscription or deletes portfolio
        
        IMPORTANT: This is permanent! Always confirm before calling.
        
        Args:
            site_id: Site to delete
            
        Returns:
            True if successful
        """
        try:
            url = f"{self.API_BASE}/sites/{site_id}"
            
            # Use DELETE HTTP method
            response = requests.delete(
                url,
                headers={
                    "Authorization": f"Bearer {settings.netlify_access_token}"
                },
                timeout=30
            )
            
            if response.status_code == 204:  # 204 = No Content (success for DELETE)
                logger.info(f"Successfully deleted site {site_id}")
                return True
            else:
                raise ValueError(f"Delete failed: {response.text}")
                
        except Exception as e:
            logger.error(f"Delete error: {e}")
            raise ValueError(f"Failed to delete site: {str(e)}")


# =============================================================================
# EDUCATIONAL NOTES: RESTful API Design & HTTP Methods
# =============================================================================
"""
HTTP METHOD CHEAT SHEET:

GET     → Retrieve data (read-only, no side effects)
          Example: Get list of sites

POST    → Create new resource
          Example: Deploy new site

PUT     → Update entire resource (replace)
          Example: Update site config

PATCH   → Update part of resource
          Example: Change site name only

DELETE  → Remove resource
          Example: Delete site

CONCEPT: REST (Representational State Transfer)
- Resources identified by URLs (/sites, /sites/123)
- HTTP methods define actions
- Stateless (each request independent)
- JSON for data exchange

NETLIFY API SPECIFICS:

Endpoint: POST /api/v1/sites
Body: ZIP file (binary)
Response: {
  "id": "abc123",
  "ssl_url": "https://abc123.netlify.app",
  "admin_url": "https://app.netlify.com/sites/abc123"
}

AUTHENTICATION: Bearer Token
- Create token in Netlify dashboard
- Include in Authorization header
- Never commit to Git (use .env)

ERROR HANDLING:
- 401 Unauthorized → Invalid token
- 403 Forbidden → Token lacks permissions
- 429 Too Many Requests → Rate limit (usually 100 deploys/hour)
- 500 Internal Server Error → Netlify issue (retry)

TIMEOUT CONSIDERATIONS:
- Default requests timeout: 30s
- Netlify deploys can take 60s for large sites
- Always set explicit timeout to prevent hanging
"""
