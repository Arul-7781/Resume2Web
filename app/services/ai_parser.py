"""
AI-Powered Resume Parser with Chain of Thought Reasoning

CONCEPT: Chain of Thought (CoT) Prompting
Instead of asking the AI to directly output JSON, we ask it to:
1. THINK step-by-step
2. SHOW its reasoning
3. THEN produce structured output

WHY CoT IMPROVES ACCURACY?
- Forces the model to break down complex tasks
- Reduces hallucination (making up data)
- Makes debugging easier (you can see the reasoning)
- Improves consistency across different resume formats

RESEARCH: "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models"
(Wei et al., 2022) - showed 3x improvement on complex tasks
"""

import google.generativeai as genai
import json
import logging
from typing import Dict, Any
from app.config import settings
from app.models.portfolio import PortfolioData

logger = logging.getLogger(__name__)


class AIParserService:
    """
    Resume parsing service using Google Gemini with Chain of Thought
    
    ARCHITECTURE:
    - Stateful service (maintains API client)
    - Configurable prompts for different parsing strategies
    - Structured output validation
    """
    
    def __init__(self):
        """
        Initialize the AI client
        
        CONCEPT: Lazy initialization
        Only create the client when this service is actually used
        """
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(settings.gemini_model)
        logger.info(f"AI Parser initialized with {settings.gemini_model}")
    
    def parse_resume(self, resume_text: str) -> PortfolioData:
        """
        Parse resume text into structured PortfolioData
        
        ALGORITHM (Chain of Thought):
        1. Send resume + CoT prompt to LLM
        2. LLM thinks step-by-step (reasoning phase)
        3. LLM outputs JSON (extraction phase)
        4. Validate JSON against Pydantic schema
        5. Return structured data
        
        Args:
            resume_text: Raw text extracted from PDF
            
        Returns:
            PortfolioData object (validated)
            
        Raises:
            ValueError: If parsing fails or JSON is invalid
        """
        try:
            # Build the Chain of Thought prompt
            prompt = self._build_cot_prompt(resume_text)
            
            # Call the LLM
            logger.info("Sending resume to AI for parsing...")
            response = self.model.generate_content(prompt)
            
            # Extract the JSON from the response
            # CONCEPT: LLM responses often include explanatory text + JSON
            # We need to extract just the JSON part
            parsed_data = self._extract_json_from_response(response.text)
            
            # Clean the data before validation
            parsed_data = self._clean_parsed_data(parsed_data)
            
            # CONCEPT: Pydantic validation
            # This automatically checks all types, required fields, email format, etc.
            portfolio_data = PortfolioData(**parsed_data)
            
            logger.info(f"Successfully parsed resume for {portfolio_data.personal_info.name}")
            return portfolio_data
            
        except Exception as e:
            logger.error(f"Resume parsing failed: {e}")
            raise ValueError(f"Failed to parse resume: {str(e)}")
    
    def _build_cot_prompt(self, resume_text: str) -> str:
        """
        Build Chain of Thought prompt for resume parsing
        
        PROMPT ENGINEERING EXPLAINED:
        
        1. **Role Assignment**: Tell AI what it is ("expert resume analyst")
           → Improves response quality through persona framing
        
        2. **Step-by-Step Instructions**: Break task into phases
           → Each step builds on previous (chain of thought)
        
        3. **Few-Shot Examples**: Show expected reasoning format
           → Teaches AI the pattern to follow
        
        4. **Output Schema**: Define exact JSON structure
           → Ensures parseable output
        
        5. **Constraints**: "ONLY output valid JSON"
           → Prevents unwanted text before/after JSON
        """
        
        prompt = f"""You are an expert resume parsing AI with advanced reasoning capabilities.

Your task is to extract structured information from the following resume text.

**IMPORTANT**: Use Chain of Thought reasoning. Think step-by-step before extracting data.

=== CHAIN OF THOUGHT PROCESS ===

Step 1: ANALYZE STRUCTURE
- Identify main sections (Personal Info, Experience, Education, Skills, Projects)
- Note the formatting style (bullet points, paragraphs, etc.)
- Determine the chronological order

Step 2: EXTRACT ENTITIES
- Names: Look for capitalized words at the top
- Contact: Email format (contains @), phone (numbers with dashes/parentheses)
- Dates: Month/Year patterns (Jan 2020, 2020-2023, etc.)
- Companies: Usually after job titles
- Skills: Technical terms, programming languages, tools

Step 3: VALIDATE CONSISTENCY
- Do dates make logical sense? (start < end)
- Are job titles consistent with descriptions?
- Do skills match project descriptions?

Step 4: STRUCTURE DATA
- Group related information
- Normalize date formats
- Extract achievements from job descriptions

=== RESUME TEXT ===
{resume_text}

=== REASONING (Think out loud) ===
[Write your step-by-step analysis here]

Now, based on your analysis, extract the data into this EXACT JSON format:

**CRITICAL REQUIREMENTS:**
- All fields must be strings (not arrays)
- Use "Not specified" for missing dates
- Join bullet points with newline characters (\\n)
- DO NOT use null, use empty string "" instead
- descriptions must be a SINGLE STRING, not an array

{{
  "personal_info": {{
    "name": "Full Name",
    "email": "email@example.com",
    "phone": "+1-234-567-8900",
    "linkedin": "https://linkedin.com/in/username",
    "github": "https://github.com/username",
    "bio": "Professional summary",
    "location": "City, State"
  }},
  "skills": ["Skill1", "Skill2", "Skill3"],
  "experience": [
    {{
      "role": "Job Title",
      "company": "Company Name",
      "start_date": "Jan 2020",
      "end_date": "Dec 2023",
      "description": "• Achievement 1\\n• Achievement 2\\n• Achievement 3"
    }}
  ],
  "education": [
    {{
      "degree": "B.S. Computer Science",
      "school": "University Name",
      "year": "2020"
    }}
  ],
  "projects": [
    {{
      "title": "Project Name",
      "tech_stack": "Python, FastAPI, React",
      "description": "Brief description of the project",
      "link": "https://github.com/user/project"
    }}
  ],
  "theme": "minimalist"
}}

=== FINAL JSON OUTPUT ===
[Output ONLY valid JSON, no markdown code blocks, no extra text]
"""
        return prompt
    
    def _extract_json_from_response(self, response_text: str) -> Dict[str, Any]:
        """
        Extract JSON from LLM response
        
        PROBLEM: LLMs often wrap JSON in markdown or add explanatory text
        Example:
        ```
        Here's the extracted data:
        ```json
        {"name": "John"}
        ```
        ```
        
        SOLUTION: Use regex or string manipulation to find JSON block
        
        Args:
            response_text: Raw LLM response
            
        Returns:
            Parsed JSON dict
        """
        import re
        
        # Try to find JSON in markdown code blocks
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find raw JSON (look for outermost braces)
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                # Last resort: assume entire response is JSON
                json_str = response_text
        
        try:
            # CONCEPT: json.loads() converts JSON string to Python dict
            parsed = json.loads(json_str)
            return parsed
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}\nResponse: {response_text[:500]}")
            raise ValueError("LLM did not return valid JSON")
    
    def _clean_parsed_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean AI-generated data to fix common issues
        
        FIXES:
        - Convert list descriptions to strings (join with newlines)
        - Replace None with empty strings for required fields
        - Convert empty strings to None for URL fields
        - Normalize date formats
        """
        # Clean personal info URLs
        if "personal_info" in data:
            for url_field in ["linkedin", "github"]:
                if url_field in data["personal_info"] and not data["personal_info"][url_field]:
                    data["personal_info"][url_field] = None
        
        # Clean experience data
        if "experience" in data:
            for exp in data["experience"]:
                # Convert list to string
                if isinstance(exp.get("description"), list):
                    exp["description"] = "\n".join(f"• {item}" for item in exp["description"])
                # Ensure start_date is string or None (not undefined)
                if "start_date" not in exp or exp["start_date"] is None:
                    exp["start_date"] = "Not specified"
                # Ensure description exists
                if not exp.get("description"):
                    exp["description"] = "No description provided"
        
        # Clean education data
        if "education" in data:
            for edu in data["education"]:
                # Ensure year is string or None
                if "year" not in edu or edu["year"] is None:
                    edu["year"] = "Not specified"
        
        # Clean projects data
        if "projects" in data:
            for proj in data["projects"]:
                # Convert list descriptions to string
                if isinstance(proj.get("description"), list):
                    proj["description"] = " ".join(proj["description"])
                # Convert empty string to None for URL
                if "link" in proj and not proj["link"]:
                    proj["link"] = None
        
        return data
    
    def parse_with_retry(self, resume_text: str, max_retries: int = 3) -> PortfolioData:
        """
        Parse with retry logic
        
        CONCEPT: Resilience pattern
        LLMs can be non-deterministic (different output each time)
        If parsing fails, retry with slightly modified prompt
        
        Args:
            resume_text: Resume text
            max_retries: Maximum retry attempts
            
        Returns:
            PortfolioData
        """
        for attempt in range(max_retries):
            try:
                return self.parse_resume(resume_text)
            except Exception as e:
                logger.warning(f"Parse attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise
        
        raise ValueError("All retry attempts exhausted")


# =============================================================================
# EDUCATIONAL NOTES: Why Chain of Thought Works
# =============================================================================
"""
TRADITIONAL APPROACH (Single-Shot):
Prompt: "Extract JSON from this resume: [text]"
Problem: LLM tries to do everything at once → makes mistakes

CHAIN OF THOUGHT APPROACH:
Prompt: "First analyze the sections, then extract entities, then validate, then output JSON"
Benefit: LLM builds intermediate reasoning → more accurate final output

REAL-WORLD ANALOGY:
Bad: "Build me a house" (vague, likely to have issues)
Good: "First design the foundation, then frame the walls, then add the roof" (clear steps)

RESEARCH FINDINGS:
- 30-80% accuracy improvement on complex tasks
- Especially effective for structured data extraction
- Works better with larger models (Gemini Pro, GPT-4)

WHEN TO USE CoT:
✅ Complex extraction (resumes, invoices, legal docs)
✅ Multi-step reasoning (math, logic, planning)
✅ High accuracy requirements

❌ Simple classification ("Is this spam?")
❌ Low-latency requirements (CoT adds tokens = slower)
"""
