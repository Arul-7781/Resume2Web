# Contributing to Portfolio Builder

Thank you for your interest in contributing! This document provides guidelines for developers.

## 📋 Development Setup

1. Fork and clone the repository
2. Create a virtual environment: `python3 -m venv .venv`
3. Activate it: `source .venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and add your API keys
6. Run the app: `uvicorn app.main:app --reload`

## 🏗️ Architecture

### Service-Oriented Design
Each service has a single responsibility:
- **AIParserService** - Extract data from PDF using Gemini
- **ArtifactGeneratorService** - Generate HTML/PDF from data
- **NetlifyDeployerService** - Deploy to Netlify
- **CloudflareDeployerService** - Deploy to Cloudflare Pages
- **ResumeValidator** - Validate parsing quality

### Data Flow
```
PDF Upload → PDFExtractor → AIParserService → PortfolioData
                                                    ↓
                                            ResumeValidator
                                                    ↓
                                         ArtifactGenerator
                                                    ↓
                                           NetlifyDeployer
                                                    ↓
                                              Live URL
```

## 🎨 Adding a New Theme

1. **Update Template** (`app/templates/portfolio_template_new.html`)
```css
/* Add theme variables */
[data-theme="your-theme"][data-mode="light"] {
    --bg-primary: #FFFFFF;
    --text-primary: #000000;
    --accent-primary: #FF0000;
}

[data-theme="your-theme"][data-mode="dark"] {
    --bg-primary: #000000;
    --text-primary: #FFFFFF;
    --accent-primary: #FF6666;
}
```

2. **Update Frontend** (`app/static/index.html`)

Add theme option in TWO places (AI upload section and manual entry section):
```html
<label class="theme-option-card">
    <input type="radio" name="aiTheme" value="your-theme" class="hidden">
    <div>
        <h4 class="font-semibold mb-1">Your Theme Name</h4>
        <p class="text-xs mb-2">Theme description</p>
        <p class="text-xs font-medium">🎯 Best for: Your target audience</p>
    </div>
</label>
```

3. **Update Model** (`app/models/portfolio.py`)

Add theme name to the description:
```python
theme: str = Field(
    default="minimal-pro", 
    description="Visual theme: minimal-pro, midnight-tech, ..., your-theme"
)
```

## 🧪 Testing

### Run All Tests
```bash
pytest tests/
```

### Run Specific Test
```bash
pytest tests/test_parser.py -v
```

### Test Coverage
```bash
pytest --cov=app tests/
```

## 📝 Code Style

- Follow PEP 8
- Use type hints
- Add docstrings to all functions
- Keep functions under 50 lines
- Use descriptive variable names

### Example
```python
def parse_resume(pdf_file: UploadFile) -> PortfolioData:
    """
    Extract structured data from resume PDF
    
    Args:
        pdf_file: Uploaded PDF file
        
    Returns:
        PortfolioData with extracted information
        
    Raises:
        ValueError: If PDF is invalid or unreadable
    """
    # Implementation
```

## 🐛 Reporting Bugs

1. Check if issue already exists
2. Create detailed bug report with:
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment (Python version, OS)
   - Error logs/screenshots

## 💡 Feature Requests

1. Open an issue with `[Feature Request]` prefix
2. Describe the problem it solves
3. Provide use cases
4. Suggest implementation (optional)

## 🔀 Pull Request Process

1. Create a feature branch from `main`
2. Make your changes
3. Add tests for new functionality
4. Ensure all tests pass
5. Update documentation if needed
6. Submit PR with clear description
7. Wait for review

### PR Checklist
- [ ] Code follows style guidelines
- [ ] Tests added and passing
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)
- [ ] Commit messages are clear

## 📚 Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Gemini API Docs](https://ai.google.dev/docs)
- [Netlify API Docs](https://docs.netlify.com/api/get-started/)

## 🙏 Thank You!

Every contribution helps make this project better for everyone.
