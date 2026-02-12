"""
Gemini Parser - Google Gemini API integration
Enhanced with better error handling and validation
"""

from google import genai
from google.genai import types
import json
import logging
import re
from typing import Dict, Any
from app.config import settings
from app.models.portfolio import PortfolioData
from app.services.parsers import BaseParser

logger = logging.getLogger(__name__)


class GeminiParser(BaseParser):
    """Resume parser using Google Gemini"""
    
    def __init__(self):
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY not configured")
        
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model_name = settings.gemini_model
        logger.info(f"Gemini parser initialized with {settings.gemini_model}")
    
    def parse_resume(self, resume_text: str) -> PortfolioData:
        """Parse resume using Gemini"""
        try:
            prompt = self._build_prompt(resume_text)
            
            logger.info("Sending to Gemini...")
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1,  # Lower temperature for more consistent output
                    top_p=0.95,
                    top_k=40,
                    max_output_tokens=4096,
                )
            )
            
            parsed_data = self._extract_json(response.text)
            parsed_data = self._clean_data(parsed_data)
            
            # Validate with Pydantic
            portfolio_data = PortfolioData(**parsed_data)
            
            logger.info(f"✓ Gemini parsed: {portfolio_data.personal_info.name}")
            return portfolio_data
            
        except Exception as e:
            logger.error(f"Gemini parsing failed: {e}")
            raise ValueError(f"Gemini parse error: {str(e)}")
    
    def _extract_json(self, response_text: str) -> Dict[str, Any]:
        """Extract JSON from Gemini response"""
        # Remove markdown code blocks
        response_text = re.sub(r'```json\s*', '', response_text)
        response_text = re.sub(r'```\s*', '', response_text)
        
        # Try to find JSON object
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
        else:
            json_str = response_text
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}\nResponse: {response_text[:500]}")
            raise ValueError("Invalid JSON from Gemini")
    
    def _clean_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and normalize data"""
        # Map institution → school for backwards compatibility
        if "education" in data:
            for edu in data["education"]:
                if "institution" in edu and "school" not in edu:
                    edu["school"] = edu.pop("institution")
                elif "institution" in edu:
                    edu.pop("institution")  # Remove duplicate
        
        # Clean personal info URLs
        if "personal_info" in data:
            for url_field in ["linkedin", "github"]:
                if url_field in data["personal_info"]:
                    value = data["personal_info"][url_field]
                    if value and not value.startswith("http"):
                        # Invalid URL, set to None
                        data["personal_info"][url_field] = None
                    elif not value or value.strip() == "":
                        data["personal_info"][url_field] = None
        
        # Ensure required fields have defaults
        if "experience" in data:
            for exp in data["experience"]:
                if not exp.get("description"):
                    exp["description"] = ""
                if not exp.get("start_date"):
                    exp["start_date"] = "Not specified"
        
        # Ensure achievements array exists
        if "achievements" not in data:
            data["achievements"] = []
        
        return data
