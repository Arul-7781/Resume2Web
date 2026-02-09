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
            
        except Exception as e:
            error_msg = str(e).lower()
            # Check if it's a rate limit error
            if any(keyword in error_msg for keyword in ['rate limit', 'quota', '429', 'resource_exhausted', 'exceeded']):
                # Return quick validation instead of error
                print(f"⚠️ Gemini validator rate limited, using quick validation")
                return self.quick_validate(parsed_data)
            
            # For other errors, still try quick validation as fallback
            return self.quick_validate(parsed_data)
    
    def quick_validate(self, parsed_data: PortfolioData) -> Dict[str, Any]:
        """
        Quick rule-based validation without AI (faster, for basic checks).
        Returns high scores for well-parsed data.
        """
        issues = []
        score = 100
        
        # Check personal info (critical)
        if not parsed_data.personal_info.name or len(parsed_data.personal_info.name) < 2:
            issues.append("Name is missing or too short")
            score -= 25
        
        if not parsed_data.personal_info.email or '@' not in parsed_data.personal_info.email:
            issues.append("Email is missing or invalid")
            score -= 25
        
        # Check skills (important)
        if not parsed_data.skills:
            issues.append("Skills section is empty")
            score -= 15
        elif len(parsed_data.skills) < 3:
            issues.append("Skills section seems incomplete (less than 3 skills)")
            score -= 5
        
        # Check experience (important)
        if not parsed_data.experience:
            issues.append("No work experience found")
            score -= 15
        else:
            missing_desc_count = 0
            for exp in parsed_data.experience:
                if not exp.description or len(exp.description.strip()) < 20:
                    missing_desc_count += 1
            if missing_desc_count > 0:
                issues.append(f"{missing_desc_count} experience(s) have incomplete descriptions")
                score -= min(missing_desc_count * 3, 10)
        
        # Check education (important)
        if not parsed_data.education:
            issues.append("No education found")
            score -= 10
        
        # Optional fields - minor deductions
        if not parsed_data.projects:
            score -= 5  # Projects optional, minor deduction
        
        if not parsed_data.personal_info.phone:
            score -= 2
        
        if not parsed_data.personal_info.location:
            score -= 2
        
        score = max(0, score)
        
        suggestions = []
        if score < 100:
            suggestions = [f"Consider reviewing: {item}" for item in issues]
        else:
            suggestions = ["All required fields are present!"]
        
        return {
            "completeness_score": score,
            "is_complete": score >= 85,
            "missing_items": issues,
            "suggestions": suggestions,
            "validation_type": "quick (AI validator unavailable - using rule-based validation)"
        }
