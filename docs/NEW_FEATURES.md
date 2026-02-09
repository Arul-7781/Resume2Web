# New Features - v1.1

This document describes the new features added to the Portfolio Builder in version 1.1.

## 1. Link Enrichment

**Feature**: After AI parsing, users can add LinkedIn and GitHub profile links that may not have been included in the resume.

**How it works**:
- After uploading a resume and getting the AI-parsed data, a new "Link Enrichment" section appears
- Users can fill in their LinkedIn and GitHub URLs
- Clicking "Apply Links" updates the portfolio data without re-parsing
- Links are automatically included in the generated portfolio

**Location**: 
- UI: Between validation results and data preview sections
- Backend: Personal info model in `app/models/portfolio.py`

## 2. Achievements & Certifications Section

**Feature**: New section to showcase awards, certifications, and notable achievements.

**Fields**:
- Title (e.g., "AWS Certified Solutions Architect")
- Issuer (e.g., "Amazon Web Services")
- Date (e.g., "2023")
- Description (optional details)

**How it works**:
- AI parsing automatically extracts achievements from resumes
- Manual entry form includes "Add Achievement" button
- Achievements appear as a dedicated section in generated portfolios

**Location**:
- Backend model: `Achievement` class in `app/models/portfolio.py`
- Frontend form: Between Projects and Theme Selection
- Template: New section in `portfolio_template_new.html`

## 3. Enhanced Project Information

**Feature**: Projects now have separate fields for live demo links and GitHub repositories.

**New Fields**:
- `link`: Live demo/website URL
- `github_url`: GitHub repository URL (new)

**How it works**:
- Manual entry form has separate inputs for demo link and GitHub repo
- Generated portfolios show both buttons side-by-side
- GitHub button styled as outlined, Live Demo as filled

**Location**:
- Backend: `Project` model updated with `github_url` field
- Frontend: `addProject()` function creates 3-column grid
- Template: Both links rendered with distinct styling

## 4. Enhanced Education Details

**Feature**: Education entries now support GPA and detailed descriptions.

**New Fields**:
- `gpa`: Grade point average or percentage (e.g., "3.8/4.0" or "85%")
- `description`: Honors, relevant coursework, or additional details

**How it works**:
- Initially collapsed to show degree, school, and year
- Clicking expands to reveal GPA and description
- Smooth transition animation

**Location**:
- Backend: `Education` model updated with optional `gpa` and `description` fields
- Frontend: `addEducation()` function includes new fields
- Template: Collapsible section with toggle icon

## 5. Collapsible Sections

**Feature**: Projects and Education sections are now collapsible in generated portfolios.

**How it works**:
- **Projects**: Click to expand and see full description, tech stack details, and both links
- **Education**: Click to expand and see GPA and additional details
- Toggle icon changes from `+` to `−` when expanded
- Smooth CSS transitions for better UX

**Implementation**:
- CSS classes: `.project-details`, `.education-details`, `.toggle-icon`
- JavaScript: `toggleSection()` function handles expand/collapse
- Hidden by default, expands on click

## Data Model Summary

```python
# New Achievement model
class Achievement(BaseModel):
    title: str
    description: Optional[str] = None
    date: Optional[str] = None
    issuer: Optional[str] = None

# Updated Education model
class Education(BaseModel):
    degree: str
    institution: str
    year: str
    gpa: Optional[str] = None        # New
    description: Optional[str] = None # New

# Updated Project model
class Project(BaseModel):
    title: str
    description: str
    tech_stack: str
    link: Optional[str] = None
    github_url: Optional[str] = None  # New

# Updated PortfolioData
class PortfolioData(BaseModel):
    personal_info: PersonalInfo
    skills: List[str]
    experience: List[Experience]
    education: List[Education]
    projects: List[Project]
    achievements: List[Achievement]  # New
```

## Future Enhancements (Roadmap)

These features are planned but not yet implemented:

1. **Multi-LLM Support**: Rotate between Gemini, GPT, and Claude to handle rate limits
2. **UI Polish**: More professional, modern design improvements
3. **Export Options**: PDF generation with multiple layout options
4. **Social Integration**: Auto-fetch GitHub stats, LinkedIn endorsements
5. **Template Builder**: Visual theme customization tool

## Migration Notes

Existing portfolios will continue to work. New fields are optional and backward-compatible.

To use new features:
1. Re-upload resume to get achievements auto-parsed
2. Use "Edit Data" to manually add GPA, descriptions, GitHub links
3. Apply link enrichment for social profiles
