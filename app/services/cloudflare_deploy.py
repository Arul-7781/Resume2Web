"""
Cloudflare Pages Deployment Service
Deploys portfolio websites to Cloudflare Pages with UNLIMITED bandwidth
"""
import os
import requests
import logging
from io import BytesIO
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class CloudflareDeployerService:
    """
    Deploys static sites to Cloudflare Pages
    
    ADVANTAGES OVER NETLIFY:
    - Unlimited bandwidth (no caps!)
    - Global CDN with 300+ locations
    - Free SSL certificates
    - Better performance in most regions
    
    API DOCS: https://developers.cloudflare.com/pages/
    """
    
    def __init__(self):
        self.api_token = os.getenv("CLOUDFLARE_API_TOKEN", "")
        self.account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID", "")
        
        if not self.api_token or not self.account_id:
            logger.warning("Cloudflare credentials not configured")
        
        self.base_url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/pages/projects"
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
    
    def deploy_site(self, zip_buffer: BytesIO, project_name: str = None) -> Dict[str, Any]:
        """
        Deploy ZIP file to Cloudflare Pages
        
        WORKFLOW:
        1. Create or get project
        2. Upload files via Direct Upload API
        3. Return deployment URL
        
        Args:
            zip_buffer: ZIP file containing index.html and resume.pdf
            project_name: Optional project name (auto-generated if None)
            
        Returns:
            {
                "site_url": "https://portfolio-abc123.pages.dev",
                "deployment_id": "...",
                "platform": "cloudflare"
            }
        """
        try:
            # Generate unique project name if not provided
            if not project_name:
                import uuid
                project_name = f"portfolio-{uuid.uuid4().hex[:12]}"
            
            # Cloudflare Pages project names must be lowercase and alphanumeric
            project_name = project_name.lower().replace('_', '-')
            
            logger.info(f"Deploying to Cloudflare Pages: {project_name}")
            
            # Step 1: Create project (or get existing)
            project = self._create_or_get_project(project_name)
            
            # Step 2: Deploy via Direct Upload
            deployment = self._upload_deployment(project_name, zip_buffer)
            
            # Step 3: Construct production URL
            # Cloudflare returns deployment-specific URLs, but we want the main project URL
            # Format: https://project-name.pages.dev
            site_url = f"https://{project_name}.pages.dev"
            
            # Also get the deployment-specific URL for reference
            deployment_url = deployment.get("url", "")
            
            logger.info(f"✅ Cloudflare deployment successful: {site_url}")
            logger.info(f"Deployment URL: {deployment_url}")
            
            return {
                "site_url": site_url,
                "deployment_id": deployment.get("id"),
                "deployment_url": deployment_url,
                "platform": "cloudflare",
                "environment": deployment.get("environment", "production")
            }
            
        except Exception as e:
            logger.error(f"Cloudflare deployment failed: {e}")
            raise Exception(f"Cloudflare deployment error: {str(e)}")
    
    def _create_or_get_project(self, project_name: str) -> Dict[str, Any]:
        """Create a new Cloudflare Pages project or get existing one"""
        
        # Check if project exists
        try:
            response = requests.get(
                f"{self.base_url}/{project_name}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                logger.info(f"Using existing project: {project_name}")
                return response.json()["result"]
        except Exception as e:
            logger.debug(f"Project doesn't exist, will create: {e}")
        
        # Create new project
        payload = {
            "name": project_name,
            "production_branch": "main",
            "build_config": {
                "build_command": "",
                "destination_dir": "",
                "root_dir": ""
            }
        }
        
        response = requests.post(
            self.base_url,
            headers=self.headers,
            json=payload
        )
        
        if response.status_code in [200, 201]:
            logger.info(f"Created new project: {project_name}")
            return response.json()["result"]
        else:
            raise Exception(f"Failed to create project: {response.text}")
    
    def _upload_deployment(self, project_name: str, zip_buffer: BytesIO) -> Dict[str, Any]:
        """
        Upload deployment using Direct Upload API with manifest
        
        Cloudflare requires:
        1. Extract files from ZIP
        2. Create manifest mapping file paths to hashes
        3. Upload files in multipart form
        """
        import zipfile
        import hashlib
        import json
        
        # Reset buffer position
        zip_buffer.seek(0)
        
        # Extract files and build manifest
        manifest = {}
        files_to_upload = {}
        
        with zipfile.ZipFile(zip_buffer, 'r') as zip_ref:
            for file_name in zip_ref.namelist():
                # Skip directories
                if file_name.endswith('/'):
                    continue
                    
                # Read file content
                file_content = zip_ref.read(file_name)
                
                # Cloudflare expects paths without leading slash for manifest
                # But uses the filename as the form field name
                clean_name = file_name.lstrip('/')
                
                # Calculate hash for manifest
                file_hash = hashlib.sha256(file_content).hexdigest()
                
                # Add to manifest (path -> empty object, Cloudflare infers from upload)
                manifest[f"/{clean_name}"] = {}
                
                # Store for upload
                files_to_upload[clean_name] = file_content
        
        # Build multipart form data
        # Manifest goes first
        files_form = [
            ('manifest', (None, json.dumps(manifest), 'application/json'))
        ]
        
        # Add each file
        for file_name, content in files_to_upload.items():
            files_form.append((file_name, (file_name, content)))
        
        # Upload headers
        upload_headers = {
            "Authorization": f"Bearer {self.api_token}"
        }
        
        # Deploy via Direct Upload API
        deploy_url = f"{self.base_url}/{project_name}/deployments"
        
        logger.info(f"Uploading {len(files_to_upload)} files to Cloudflare...")
        
        response = requests.post(
            deploy_url,
            headers=upload_headers,
            files=files_form,
            timeout=120  # Increased timeout for upload
        )
        
        if response.status_code in [200, 201]:
            result = response.json()["result"]
            logger.info(f"✅ Deployment uploaded successfully")
            return result
        else:
            logger.error(f"Upload failed: {response.status_code} - {response.text}")
            raise Exception(f"Failed to upload deployment: {response.text}")
    
    def list_projects(self) -> list:
        """List all Cloudflare Pages projects"""
        response = requests.get(self.base_url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()["result"]
        else:
            raise Exception(f"Failed to list projects: {response.text}")
    
    def delete_project(self, project_name: str) -> bool:
        """Delete a Cloudflare Pages project"""
        response = requests.delete(
            f"{self.base_url}/{project_name}",
            headers=self.headers
        )
        
        return response.status_code in [200, 204]
