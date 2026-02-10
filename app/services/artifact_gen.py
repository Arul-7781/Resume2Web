"""
Artifact Generation Service

CONCEPT: Generate multiple artifacts from structured data
- HTML portfolio website
- ATS-friendly PDF resume
- Bundled zip file for deployment

WHY JINJA2?
- Separation of logic (Python) and presentation (HTML)
- Reusable templates
- Safe escaping (prevents XSS attacks)

WHY WEASYPRINT?
- Converts HTML+CSS to PDF using web standards
- Better than LaTeX for modern layouts
- Full CSS support (flexbox, grid, etc.)
"""

import os
import zipfile
from io import BytesIO
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS
from app.models.portfolio import PortfolioData
import logging

logger = logging.getLogger(__name__)


class ArtifactGeneratorService:
    """
    Generates portfolio website and resume artifacts
    
    ARCHITECTURE:
    - Template-based generation (Jinja2)
    - Multi-format output (HTML, PDF, ZIP)
    - In-memory processing (no disk I/O for scalability)
    """
    
    def __init__(self):
        """
        Initialize Jinja2 template environment
        
        CONCEPT: Template engine setup
        - Loads templates from app/templates/
        - Configures autoescape for security
        """
        template_dir = Path(__file__).parent.parent / "templates"
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=True  # SECURITY: Prevents XSS by escaping HTML
        )
        logger.info(f"Artifact generator initialized with templates from {template_dir}")
    
    def generate_all_artifacts(self, data: PortfolioData) -> BytesIO:
        """
        Generate complete deployment package
        
        WORKFLOW:
        1. Render portfolio HTML
        2. Render + convert resume HTML to PDF
        3. Bundle into ZIP file
        
        Args:
            data: Validated portfolio data
            
        Returns:
            BytesIO: In-memory ZIP file containing:
                - index.html (portfolio site)
                - resume.pdf (ATS-friendly resume)
                - style.css (optional, for custom themes)
        
        CONCEPT: In-Memory Processing
        We never write to disk → faster, scalable, stateless
        Perfect for serverless/containerized deployments
        """
        try:
            # Generate portfolio HTML
            portfolio_html = self._generate_portfolio_html(data)
            
            # Generate resume PDF
            resume_pdf_bytes = self._generate_resume_pdf(data)
            
            # Create ZIP bundle
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # Add portfolio HTML
                zip_file.writestr('index.html', portfolio_html)
                
                # Add resume PDF
                zip_file.writestr('resume.pdf', resume_pdf_bytes)
                
                # Add basic CSS (inline in HTML for simplicity)
                # In production, you'd add separate CSS file here
            
            # IMPORTANT: Seek to start so it can be read
            zip_buffer.seek(0)
            
            logger.info(f"Generated artifacts for {data.personal_info.name}")
            return zip_buffer
            
        except Exception as e:
            logger.error(f"Artifact generation failed: {e}")
            raise ValueError(f"Failed to generate artifacts: {str(e)}")
    
    def _generate_portfolio_html(self, data: PortfolioData) -> str:
        """
        Render portfolio website HTML
        
        CONCEPT: Template Rendering
        Jinja2 replaces {{ variable }} with actual values
        
        Example:
        Template: <h1>{{ name }}</h1>
        Data: {"name": "Jane"}
        Output: <h1>Jane</h1>
        
        Args:
            data: Portfolio data
            
        Returns:
            Complete HTML string
        """
        # Map design template selection to actual template files
        template_map = {
            'split_screen_hero': 'split_screen_hero.html',
            'single_page_scroll': 'single_page_scroll.html',
            'elegant_professional': 'elegant_professional.html',
            'developer_dark': 'developer_dark.html',
            'minimal_monochrome': 'minimal_monochrome.html',
            'modern_personal': 'modern_personal.html',
            'dark_anonymous': 'dark_anonymous.html',
            'orange_professional': 'orange_professional.html',
            'portfolio_template_new': 'portfolio_template_new.html',  # Legacy support
        }
        
        # Get template name, default to split_screen_hero if not found
        template_name = template_map.get(
            data.design_template,
            'split_screen_hero.html'
        )
        
        logger.info(f"Using portfolio template: {template_name}")
        template = self.env.get_template(template_name)
        
        # CONCEPT: Template context
        # This dict is available in the template as variables
        html = template.render(
            personal_info=data.personal_info,
            skills=data.skills,
            experience=data.experience,
            education=data.education,
            projects=data.projects,
            achievements=data.achievements,
            theme=data.theme
        )
        
        return html
    
    def _generate_resume_pdf(self, data: PortfolioData) -> bytes:
        """
        Generate ATS-friendly PDF resume
        
        PROCESS:
        1. Render resume_template.html with data
        2. Convert HTML to PDF using WeasyPrint
        3. Return PDF bytes
        
        ATS OPTIMIZATION EXPLAINED:
        - Single column layout (ATS parsers read top-to-bottom)
        - Standard fonts (Arial, Calibri) → machine-readable
        - Semantic HTML (h1, h2, p) → clear structure
        - No images in text areas → prevents OCR errors
        - Black text on white background → high contrast
        
        Args:
            data: Portfolio data
            
        Returns:
            PDF file as bytes
        """
        # Render HTML template
        template = self.env.get_template('resume_template.html')
        resume_html = template.render(
            personal_info=data.personal_info,
            skills=data.skills,
            experience=data.experience,
            education=data.education,
            projects=data.projects
        )
        
        # CONCEPT: HTML to PDF conversion
        # WeasyPrint uses Cairo graphics library (same as Firefox)
        # Supports modern CSS (flexbox, grid, media queries)
        pdf_bytes = HTML(string=resume_html).write_pdf()
        
        logger.info(f"Generated {len(pdf_bytes)} byte PDF resume")
        return pdf_bytes
    
    def generate_preview(self, data: PortfolioData) -> str:
        """
        Generate HTML preview without full artifact generation
        
        USE CASE: Frontend live preview as user types
        
        Args:
            data: Portfolio data
            
        Returns:
            HTML string for preview
        """
        return self._generate_portfolio_html(data)


# =============================================================================
# EDUCATIONAL NOTES: Template Engines vs String Concatenation
# =============================================================================
"""
WHY NOT JUST USE f-strings?

BAD APPROACH:
html = f"<h1>{name}</h1><p>{bio}</p>"
Problems:
- XSS vulnerability (what if name = "<script>alert('hack')</script>")
- Hard to maintain (HTML mixed with Python)
- No reusability

GOOD APPROACH (Jinja2):
template = "<h1>{{ name }}</h1><p>{{ bio }}</p>"
html = template.render(name=name, bio=bio)
Benefits:
- Auto-escapes HTML (converts < to &lt;)
- Separates logic from presentation
- Designers can edit templates without touching Python
- Template inheritance (base templates + child templates)

JINJA2 FEATURES USED HERE:
1. Variables: {{ variable }}
2. Loops: {% for item in items %}
3. Conditionals: {% if condition %}
4. Filters: {{ text|upper }}
5. Auto-escaping: Prevents XSS

WHY WEASYPRINT FOR PDF?

ALTERNATIVES:
- ReportLab: Low-level (like drawing with coordinates)
- pdfkit/wkhtmltopdf: Deprecated, maintenance issues
- LaTeX: Overkill, hard to customize
- Puppeteer (headless Chrome): Requires Node.js

WEASYPRINT BENEFITS:
- Pure Python (no external dependencies)
- Uses web standards (HTML + CSS)
- Excellent CSS support
- Active maintenance
- ATS-friendly output (selectable text, proper fonts)
"""
