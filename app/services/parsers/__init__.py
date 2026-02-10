"""Base parser interface for all LLM parsers"""

from abc import ABC, abstractmethod
from app.models.portfolio import PortfolioData


class BaseParser(ABC):
    """
    Abstract base class for all resume parsers
    
    All LLM parsers must implement this interface
    """
    
    @abstractmethod
    def parse_resume(self, resume_text: str) -> PortfolioData:
        """
        Parse resume text into structured PortfolioData
        
        Args:
            resume_text: Raw text from resume
            
        Returns:
            PortfolioData object
            
        Raises:
            ValueError: If parsing fails
        """
        pass
    
    def _build_prompt(self, resume_text: str) -> str:
        """
        Build Chain of Thought prompt for LLM - shared across all parsers
        
        CoT (Chain of Thought) improves accuracy by 30-80% on complex tasks
        by forcing the model to think step-by-step before outputting JSON
        """
        prompt = f"""You are an expert resume parsing AI with advanced reasoning capabilities.

Your task is to extract structured information from the following resume text using Chain of Thought reasoning.

**CHAIN OF THOUGHT PROCESS - THINK STEP BY STEP:**

Step 1: ANALYZE STRUCTURE
- Identify main sections (Personal Info, Experience, Education, Skills, Projects, Achievements)
- Note the formatting style (bullet points, paragraphs, tables)
- Determine the chronological order and section markers

Step 2: EXTRACT ENTITIES (BE THOROUGH - Extract EVERYTHING)
- Names: Look for capitalized words at the top of the resume (full name)
- Contact: Email format (contains @), phone (numbers with dashes/parentheses), location/address
- Dates: Month/Year patterns (Jan 2020, 2020-2023, Present, etc.) - DON'T miss any dates
- Companies: Usually mentioned with job titles - extract ALL work experience
- Skills: Technical terms, programming languages, frameworks, tools, certifications, soft skills
  * Look for: Programming languages (Python, Java, etc.)
  * Frameworks (React, Django, TensorFlow, etc.)
  * Tools (Git, Docker, VS Code, etc.)
  * Databases (MySQL, MongoDB, etc.)
  * Cloud platforms (AWS, GCP, Azure, etc.)
  * Soft skills mentioned anywhere
- URLs: LinkedIn (linkedin.com/in/ or linkedin.com/), GitHub (github.com/), portfolio sites, personal websites
- Projects: Look in projects section AND in experience descriptions for project work
- Achievements: Awards, certifications, honors, publications, competitions, hackathons
- Bio/Summary: Professional summary, objective statement, about me section

Step 3: VALIDATE CONSISTENCY
- Do dates make logical sense? (start_date < end_date, no future dates unless "Present")
- Are job titles consistent with descriptions?
- Do skills match project technologies?
- Are email/phone/URLs in valid formats?

Step 4: STRUCTURE DATA
- Group related information logically
- Normalize date formats to "Mon YYYY" (e.g., "Jan 2020")
- Extract achievements from job descriptions
- Map all fields to the required schema

**CRITICAL EXTRACTION RULES:**
1. Extract ONLY information that is EXPLICITLY present in the resume
2. DO NOT hallucinate or make up data
3. If a field is not found, use empty string "" or omit optional fields
4. Extract EVERY skill mentioned - look in multiple sections (skills, experience, projects, education)
5. Extract ALL projects - check experience section for project work too
6. Extract ALL achievements - look for: awards, certifications, honors, competitions, hackathons, publications
7. Be especially careful with:
   - Email addresses (must contain @)
   - Phone numbers (must have digits)
   - URLs (must start with http/https or be complete domain)
   - Dates (must be actual dates from resume, not made up)
8. For LinkedIn/GitHub without http://, add https:// prefix
9. Extract bio from any summary/objective/about section at the top

=== RESUME TEXT ===
{resume_text}

=== REASONING (Think out loud before extracting) ===
[Briefly analyze the resume structure and main sections you see]

Now, based on your step-by-step analysis, extract the data:

=== EXTRACTION REQUIREMENTS ===

**Personal Information:**
- name: Full name (usually at the top of resume)
- email: Email address (look for @ symbol)
- phone: Phone number with country code if present
- linkedin: LinkedIn profile URL (look for linkedin.com/in/)
- github: GitHub profile URL (look for github.com/)
- bio: Professional summary or objective statement
- location: City, State/Country

**Skills:**
- Extract ALL technical skills, tools, languages, frameworks
- Include soft skills if explicitly mentioned
- Return as array of strings

**Experience:**
- role: Job title/position
- company: Company/organization name  
- start_date: Start date (format: "Mon YYYY" like "Jan 2020")
- end_date: End date or "Present" for current role
- description: Key responsibilities and achievements (use \\n for bullet points)

**Education:**
- degree: Degree name (e.g., "B.S. Computer Science")
- school: School/university name (e.g., "MIT", "Stanford University")
- year: Graduation year or date range
- gpa: Grade point average if mentioned (e.g., "3.8/4.0")
- description: Honors, relevant coursework, awards

**Projects:**
- title: Project name
- tech_stack: Technologies used (comma-separated string)
- description: What the project does
- link: Website/demo URL if mentioned
- github_url: GitHub repository URL if different from link

**Achievements:**
- title: Award/certification name
- issuer: Organization that issued it
- date: When received (year or month/year)
- description: Additional details if provided

=== OUTPUT FORMAT ===
Return ONLY valid JSON in this exact structure:

{{
  "personal_info": {{
    "name": "string",
    "email": "string",
    "phone": "string",
    "linkedin": "string or null",
    "github": "string or null",
    "bio": "string",
    "location": "string"
  }},
  "skills": ["string", "string"],
  "experience": [
    {{
      "role": "string",
      "company": "string",
      "start_date": "string",
      "end_date": "string",
      "description": "string with \\n for bullets"
    }}
  ],
  "education": [
    {{
      "degree": "string",
      "institution": "string",
      "year": "string",
      "gpa": "string or null",
      "description": "string or null"
    }}
  ],
  "projects": [
    {{
      "title": "string",
      "tech_stack": "string",
      "description": "string",
      "link": "string or null",
      "github_url": "string or null"
    }}
  ],
  "achievements": [
    {{
      "title": "string",
      "issuer": "string",
      "date": "string",
      "description": "string or null"
    }}
  ]
}}

**CRITICAL:** Output ONLY the JSON object, no markdown code blocks, no explanations, no extra text.
"""
        return prompt
