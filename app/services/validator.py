"""
AI-Powered Resume Validation Service
Validates that parsed data matches the original resume content
"""
import google.generativeai as genai
from typing import Dict, Any, List
import json
import os
from dotenv import load_dotenv
from app.models.portfolio import PortfolioData

# Load environment variables
load_dotenv()


class ResumeValidator:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY", "")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")
    
    def validate(self, resume_text: str, parsed_data: PortfolioData) -> Dict[str, Any]:
        """
        Validate that parsed data contains all information from resume.
        
        Args:
            resume_text: Original resume text extracted from PDF
            parsed_data: Structured data parsed by AI
            
        Returns:
            {
                "completeness_score": 85,  # 0-100
                "is_complete": False,
                "missing_items": ["Skills: Python missing", "Project: XYZ not included"],
                "suggestions": ["Add Python to skills list", "Include XYZ project"],
                "validation_details": {...}
            }
        """
        # Convert parsed data to JSON for comparison
        parsed_json = parsed_data.model_dump_json(indent=2, exclude_none=True)
        
        # Create validation prompt
        prompt = f"""You are a resume validation expert. Your job is to compare a resume's original text with its parsed structured data to ensure NO INFORMATION IS LOST.

ORIGINAL RESUME TEXT:
{resume_text}

PARSED STRUCTURED DATA:
{parsed_json}

VALIDATION TASK:
1. Carefully read the original resume
2. Compare it with the parsed data
3. Identify ANY missing information (work experience, projects, skills, education, achievements, dates, descriptions, etc.)
4. Calculate a completeness score (0-100%)
5. Provide specific actionable suggestions

CRITICAL RULES:
- Score 100% ONLY if ALL information is captured accurately
- Be strict: partial information (e.g., job title without full description) counts as incomplete
- Check dates, descriptions, technologies, achievements - EVERYTHING
- Missing a single skill, project detail, or achievement should reduce the score
- Empty descriptions or "Not specified" dates indicate missing data

OUTPUT FORMAT (valid JSON only):
{{
    "completeness_score": <number 0-100>,
    "is_complete": <true if score >= 95, else false>,
    "missing_items": [
        "Skills section missing: Python, Docker, AWS",
        "Project 'E-commerce Platform' description is incomplete - missing tech stack details",
        "Work experience at Company X missing end date",
        "Education GPA not captured"
    ],
    "suggestions": [
        "Add the following skills that appear in resume: Python, Docker, AWS",
        "Expand project description to include: React, Node.js, MongoDB mentioned in original",
        "Update work experience with end date: December 2023",
        "Include GPA: 3.8/4.0"
    ],
    "validation_details": {{
        "personal_info": "complete/incomplete - explain",
        "skills": "complete/incomplete - list missing",
        "experience": "complete/incomplete - list missing",
        "projects": "complete/incomplete - list missing",
        "education": "complete/incomplete - list missing"
    }}
}}

Respond with ONLY the JSON object, no other text."""

        try:
            # Call Gemini for validation
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Extract JSON from response
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            # Parse JSON response
            validation_result = json.loads(result_text)
            
            # Ensure required fields exist
            validation_result.setdefault("completeness_score", 0)
            validation_result.setdefault("is_complete", False)
            validation_result.setdefault("missing_items", [])
            validation_result.setdefault("suggestions", [])
            validation_result.setdefault("validation_details", {})
            
            return validation_result
            
        except json.JSONDecodeError as e:
            # Fallback: Return basic validation failure
            return {
                "completeness_score": 0,
                "is_complete": False,
                "missing_items": ["Validation failed - unable to parse AI response"],
                "suggestions": ["Try parsing again or check resume format"],
                "validation_details": {"error": str(e)},
                "raw_response": result_text if 'result_text' in locals() else ""
            }
        except Exception as e:
            return {
                "completeness_score": 0,
                "is_complete": False,
                "missing_items": [f"Validation error: {str(e)}"],
                "suggestions": ["Try parsing again"],
                "validation_details": {"error": str(e)}
            }
    
    def quick_validate(self, parsed_data: PortfolioData) -> Dict[str, Any]:
        """
        Quick rule-based validation without AI (faster, for basic checks).
        """
        issues = []
        score = 100
        
        # Check personal info
        if not parsed_data.personal_info.name or len(parsed_data.personal_info.name) < 2:
            issues.append("Name is missing or too short")
            score -= 20
        
        if not parsed_data.personal_info.email:
            issues.append("Email is missing")
            score -= 10
        
        # Check skills
        if not parsed_data.skills or len(parsed_data.skills) < 3:
            issues.append("Skills section seems incomplete (less than 3 skills)")
            score -= 15
        
        # Check experience
        if not parsed_data.experience:
            issues.append("No work experience found")
            score -= 20
        else:
            for i, exp in enumerate(parsed_data.experience):
                if not exp.description or exp.description == "":
                    issues.append(f"Experience #{i+1} ({exp.role}) missing description")
                    score -= 10
        
        # Check projects
        if not parsed_data.projects:
            issues.append("No projects found")
            score -= 15
        
        # Check education
        if not parsed_data.education:
            issues.append("No education found")
            score -= 10
        
        score = max(0, score)
        
        return {
            "completeness_score": score,
            "is_complete": score >= 90,
            "missing_items": issues,
            "suggestions": [f"Review and fix: {item}" for item in issues],
            "validation_type": "quick"
        }
