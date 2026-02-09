"""
Groq Parser - Fast Llama models with generous free tier
Using llama-3.3-70b-versatile for best balance of speed and quality
"""

import json
import logging
import re
from typing import Dict, Any
from app.config import settings
from app.models.portfolio import PortfolioData
from app.services.parsers import BaseParser

logger = logging.getLogger(__name__)


class GroqParser(BaseParser):
    """Resume parser using Groq's Llama models"""
    
    def __init__(self):
        try:
            from groq import Groq
            self.groq_module = Groq
        except ImportError:
            raise ValueError("groq package not installed. Run: pip install groq")
        
        if not hasattr(settings, 'groq_api_key') or not settings.groq_api_key:
            raise ValueError("GROQ_API_KEY not configured")
        
        self.client = self.groq_module(api_key=settings.groq_api_key)
        self.model = getattr(settings, 'groq_model', 'llama-3.3-70b-versatile')
        logger.info(f"Groq parser initialized with {self.model}")
    
    def parse_resume(self, resume_text: str) -> PortfolioData:
        """Parse resume using Groq"""
        try:
            prompt = self._build_prompt(resume_text)
            
            logger.info(f"Sending to Groq {self.model}...")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert resume parser. Extract information accurately and return only valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=4096,
                response_format={"type": "json_object"}
            )
            
            response_text = response.choices[0].message.content
            parsed_data = self._extract_json(response_text)
            parsed_data = self._clean_data(parsed_data)
            
            portfolio_data = PortfolioData(**parsed_data)
            
            logger.info(f"✓ Groq parsed: {portfolio_data.personal_info.name}")
            return portfolio_data
            
        except Exception as e:
            logger.error(f"Groq parsing failed: {e}")
            raise ValueError(f"Groq parse error: {str(e)}")
    
    def _extract_json(self, response_text: str) -> Dict[str, Any]:
        """Extract JSON from Groq response"""
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Fallback: try to extract JSON from text
            response_text = re.sub(r'```json\s*', '', response_text)
            response_text = re.sub(r'```\s*', '', response_text)
            
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            else:
                raise ValueError("No valid JSON in Groq response")
    
    def _clean_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and normalize data"""
        # Map institution → school for backwards compatibility
        if "education" in data:
            for edu in data["education"]:
                if "institution" in edu and "school" not in edu:
                    edu["school"] = edu.pop("institution")
                elif "institution" in edu:
                    edu.pop("institution")
        
        # Clean URLs
        if "personal_info" in data:
            for url_field in ["linkedin", "github"]:
                if url_field in data["personal_info"]:
                    value = data["personal_info"][url_field]
                    if value and not value.startswith("http"):
                        data["personal_info"][url_field] = None
                    elif not value or value.strip() == "":
                        data["personal_info"][url_field] = None
        
        # Ensure defaults
        if "experience" in data:
            for exp in data["experience"]:
                if not exp.get("description"):
                    exp["description"] = ""
                if not exp.get("start_date"):
                    exp["start_date"] = "Not specified"
        
        if "achievements" not in data:
            data["achievements"] = []
        
        return data
