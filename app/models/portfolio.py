"""
Data Models using Pydantic

CONCEPT: Pydantic models are Python classes that:
1. Define the "shape" of data (schema)
2. Automatically validate incoming data
3. Provide type hints for IDEs
4. Can serialize to/from JSON

WHY PYDANTIC?
- Prevents bugs (can't accidentally pass int where str expected)
- Auto-generates OpenAPI docs in FastAPI
- Clear contracts between frontend and backend
"""

from pydantic import BaseModel, EmailStr, HttpUrl, Field
from typing import List, Optional
from datetime import date


# ============================================================================
# CONCEPT: Breaking down models into small, reusable pieces
# This is called "Composition" - building complex objects from simple ones
# ============================================================================

class PersonalInfo(BaseModel):
    """
    Personal information section
    
    VALIDATION EXPLAINED:
    - EmailStr: Ensures valid email format (name@domain.com)
    - Field(...): Provides validation rules and descriptions
    - Optional[str]: Can be None/null
    """
    name: str = Field(..., min_length=1, max_length=100, description="Full name")
    email: EmailStr = Field(..., description="Valid email address")
    phone: Optional[str] = Field(None, max_length=20, description="Contact number")
    linkedin: Optional[HttpUrl] = Field(None, description="LinkedIn profile URL")
    github: Optional[HttpUrl] = Field(None, description="GitHub profile URL")
    bio: Optional[str] = Field(None, max_length=500, description="Short professional summary")
    location: Optional[str] = Field(None, max_length=100, description="City, Country")
    photo: Optional[str] = Field(None, description="Profile photo as base64 data URL or file path")
    
    class Config:
        """
        CONCEPT: Example data for API documentation
        FastAPI will show this in the /docs page
        """
        json_schema_extra = {
            "example": {
                "name": "Jane Doe",
                "email": "jane@example.com",
                "phone": "+1-234-567-8900",
                "linkedin": "https://linkedin.com/in/janedoe",
                "github": "https://github.com/janedoe",
                "bio": "Full-stack engineer with 5 years of experience in Python and React",
                "location": "San Francisco, CA"
            }
        }


class Experience(BaseModel):
    """
    Work experience entry
    
    CONCEPT: Each job is represented by this model
    List[Experience] means an array of these objects
    """
    role: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    start_date: Optional[str] = Field(None, description="Start date (e.g., 'Jan 2020' or '2020-01')")
    end_date: Optional[str] = Field(None, description="End date or 'Present'")
    description: str = Field(default="", description="Responsibilities and achievements")
    
    class Config:
        json_schema_extra = {
            "example": {
                "role": "Senior Backend Engineer",
                "company": "Tech Corp",
                "start_date": "Jan 2020",
                "end_date": "Present",
                "description": "• Led team of 5 engineers\n• Built microservices using FastAPI\n• Reduced API latency by 40%"
            }
        }


class Education(BaseModel):
    """Education entry"""
    degree: str = Field(..., description="Degree and major")
    school: str = Field(..., description="Institution name")
    year: Optional[str] = Field(None, description="Graduation year or date range")
    gpa: Optional[str] = Field(None, description="GPA or percentage")
    description: Optional[str] = Field(None, description="Honors, coursework, or other details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "degree": "B.S. Computer Science",
                "school": "Stanford University",
                "year": "2020",
                "gpa": "3.9/4.0",
                "description": "Summa Cum Laude, Dean's List"
            }
        }


class Project(BaseModel):
    """Portfolio project entry"""
    title: str = Field(..., description="Project name")
    tech_stack: str = Field(..., description="Technologies used (comma-separated)")
    description: str = Field(..., description="What the project does")
    link: Optional[HttpUrl] = Field(None, description="Live demo or GitHub link")
    github_url: Optional[HttpUrl] = Field(None, description="GitHub repository link")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "AI Resume Parser",
                "tech_stack": "Python, FastAPI, Gemini AI",
                "description": "SaaS tool that converts resumes to structured JSON using LLMs",
                "link": "https://example.com/demo",
                "github_url": "https://github.com/user/resume-parser"
            }
        }


class Achievement(BaseModel):
    """Achievement or award entry"""
    title: str = Field(..., description="Achievement title")
    description: Optional[str] = Field(None, description="Details about the achievement")
    date: Optional[str] = Field(None, description="Date or year")
    issuer: Optional[str] = Field(None, description="Organization that issued it")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Best Paper Award",
                "description": "Recognized for outstanding research in AI",
                "date": "2023",
                "issuer": "IEEE Conference"
            }
        }


# ============================================================================
# MAIN DATA MODEL: This is what flows through the entire application
# ============================================================================

class PortfolioData(BaseModel):
    """
    Complete portfolio dataset
    
    CONCEPT: This is the "Single Source of Truth"
    - AI parser outputs this
    - Manual form outputs this
    - Site generator inputs this
    - PDF generator inputs this
    
    WHY THIS PATTERN?
    Instead of having different data shapes everywhere, we have ONE schema.
    This prevents bugs and makes code predictable.
    """
    personal_info: PersonalInfo
    skills: List[str] = Field(default_factory=list, description="List of skills")
    experience: List[Experience] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    projects: List[Project] = Field(default_factory=list)
    achievements: List[Achievement] = Field(default_factory=list, description="Awards, certifications, honors")
    design_template: str = Field(default="split_screen_hero", description="Portfolio design layout: split_screen_hero, single_page_scroll, elegant_professional, portfolio_template_new (legacy)")
    theme: str = Field(default="minimal-pro", description="Visual theme: minimal-pro, midnight-tech, creative-studio, executive-black, nature-calm, cyber-neon, classic-academia, mono-focus, product-designer, warm-personal")
    dark_mode: bool = Field(default=False, description="Enable dark mode for the portfolio theme")
    
    class Config:
        json_schema_extra = {
            "example": {
                "personal_info": {
                    "name": "Jane Doe",
                    "email": "jane@example.com",
                    "bio": "Full-stack engineer passionate about AI"
                },
                "skills": ["Python", "FastAPI", "React", "PostgreSQL"],
                "experience": [],
                "education": [],
                "projects": [],
                "design_template": "split_screen_hero",
                "theme": "minimal-pro",
                "dark_mode": False
            }
        }


# ============================================================================
# API RESPONSE MODELS
# CONCEPT: Separate input models from output models for clarity
# ============================================================================

class PublishResponse(BaseModel):
    """Response from /api/publish endpoint"""
    site_url: str = Field(..., description="Deployed portfolio URL")
    pdf_url: str = Field(..., description="Direct link to resume PDF")
    
    class Config:
        json_schema_extra = {
            "example": {
                "site_url": "https://janedoe-portfolio.netlify.app",
                "pdf_url": "https://janedoe-portfolio.netlify.app/resume.pdf"
            }
        }
