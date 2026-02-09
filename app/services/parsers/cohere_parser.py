"""
Cohere Parser - Specialized in structured extraction and RAG
Using command-r for cost-effective parsing
"""

import json
import logging
import re
from typing import Dict, Any
from app.config import settings
from app.models.portfolio import PortfolioData
from app.services.parsers import BaseParser

logger = logging.getLogger(__name__)


class CohereParser(BaseParser):
    """Resume parser using Cohere models"""
    
    def __init__(self):
        try:
            import cohere
            self.cohere_module = cohere
        except ImportError:
            raise ValueError("cohere package not installed. Run: pip install cohere")
        
        if not hasattr(settings, 'cohere_api_key') or not settings.cohere_api_key:
            raise ValueError("COHERE_API_KEY not configured")
        
        self.client = cohere.ClientV2(api_key=settings.cohere_api_key)
        self.model = getattr(settings, 'cohere_model', 'command-r')
        logger.info(f"Cohere parser initialized with {self.model}")
    
    def parse_resume(self, resume_text: str) -> PortfolioData:
        """Parse resume using Cohere"""
        try:
            prompt = self._build_prompt(resume_text)
            
            logger.info(f"Sending to Cohere {self.model}...")
            response = self.client.chat(
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
            
            response_text = response.message.content[0].text
            parsed_data = self._extract_json(response_text)
            parsed_data = self._clean_data(parsed_data)
            
            portfolio_data = PortfolioData(**parsed_data)
            
            logger.info(f"✓ Cohere parsed: {portfolio_data.personal_info.name}")
            return portfolio_data
            
        except Exception as e:
            logger.error(f"Cohere parsing failed: {e}")
            raise ValueError(f"Cohere parse error: {str(e)}")
    
    def _extract_json(self, response_text: str) -> Dict[str, Any]:
        """Extract JSON from Cohere response"""
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            response_text = re.sub(r'```json\s*', '', response_text)
            response_text = re.sub(r'```\s*', '', response_text)
            
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            else:
                raise ValueError("No valid JSON in Cohere response")
    
    def _clean_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and normalize data"""
        # Map institution → school for backwards compatibility
        if "education" in data:
            for edu in data["education"]:
                if "institution" in edu and "school" not in edu:
                    edu["school"] = edu.pop("institution")
                elif "institution" in edu:
                    edu.pop("institution")
        
        if "personal_info" in data:
            for url_field in ["linkedin", "github"]:
                if url_field in data["personal_info"]:
                    value = data["personal_info"][url_field]
                    if value and not value.startswith("http"):
                        data["personal_info"][url_field] = None
                    elif not value or value.strip() == "":
                        data["personal_info"][url_field] = None
        
        if "experience" in data:
            for exp in data["experience"]:
                if not exp.get("description"):
                    exp["description"] = ""
                if not exp.get("start_date"):
                    exp["start_date"] = "Not specified"
        
        if "achievements" not in data:
            data["achievements"] = []
        
        return data
