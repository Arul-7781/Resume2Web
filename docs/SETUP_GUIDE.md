# Portfolio & Resume Builder - Setup Guide

## 🎯 What You'll Learn

This project teaches you:

### **1. Backend Architecture**
- **FastAPI** - Modern async web framework
- **Pydantic** - Data validation with type hints
- **Service-oriented design** - Separation of concerns
- **RESTful APIs** - Industry-standard endpoint design

### **2. AI/LLM Integration**
- **Chain of Thought prompting** - Advanced prompt engineering
- **Structured data extraction** - PDF → JSON conversion
- **Error handling** - Dealing with non-deterministic AI

### **3. Document Processing**
- **PDF text extraction** - PyPDF2 library
- **HTML to PDF conversion** - WeasyPrint
- **Template rendering** - Jinja2 templating

### **4. Deployment**
- **Netlify API** - Programmatic hosting
- **ZIP bundling** - Package distribution
- **CDN deployment** - Global content delivery

---

## 📚 Step-by-Step Setup

### **Step 1: Environment Setup**

```bash
# Clone or navigate to project
cd /Users/arul/ws/projects/Portfolio_Website

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

**CONCEPT: Virtual Environments**
- Isolates project dependencies
- Prevents version conflicts
- Each project has its own packages

---

### **Step 2: Get API Keys**

#### **Google Gemini API Key**
1. Go to https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key

#### **Netlify Access Token**
1. Sign up at https://netlify.com
2. Go to User Settings → Applications → Personal Access Tokens
3. Generate new token
4. Copy the token

---

### **Step 3: Configure Environment**

```bash
# Copy example env file
cp .env.example .env

# Edit .env file
nano .env  # or use VS Code
```

Add your keys:
```env
GEMINI_API_KEY=your_actual_gemini_key_here
NETLIFY_ACCESS_TOKEN=your_actual_netlify_token_here
DEBUG=True
LOG_LEVEL=INFO
```

**SECURITY WARNING:** Never commit `.env` to Git!

---

### **Step 4: Run the Server**

```bash
# Start FastAPI server
uvicorn app.main:app --reload

# Server runs at: http://localhost:8000
```

**Understanding the Command:**
- `uvicorn` - ASGI server (like Node.js for Python)
- `app.main:app` - Import path to FastAPI instance
- `--reload` - Auto-restart on code changes (dev only)

---

### **Step 5: Test the API**

#### **Option 1: Interactive Docs**
Open browser: http://localhost:8000/docs

You'll see Swagger UI with:
- All endpoints listed
- "Try it out" buttons
- Example requests/responses

#### **Option 2: cURL**

```bash
# Test health check
curl http://localhost:8000/health

# Test parse-resume (replace with your PDF)
curl -X POST \
  http://localhost:8000/api/parse-resume \
  -F "file=@sample_resume.pdf"

# Test publish (with JSON data)
curl -X POST \
  http://localhost:8000/api/publish \
  -H "Content-Type: application/json" \
  -d '{
    "personal_info": {
      "name": "John Doe",
      "email": "john@example.com",
      "bio": "Software Engineer"
    },
    "skills": ["Python", "FastAPI"],
    "experience": [],
    "education": [],
    "projects": [],
    "theme": "minimalist"
  }'
```

---

## 🧪 Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=html

# View coverage
open htmlcov/index.html  # macOS
```

---

## 🐛 Troubleshooting

### **"ModuleNotFoundError: No module named 'app'"**
- Ensure you're in the project root directory
- Virtual environment is activated

### **"GEMINI_API_KEY not found"**
- Check `.env` file exists
- Verify key is correct (no quotes, no spaces)

### **"Failed to extract text from PDF"**
- Ensure PDF contains selectable text (not scanned image)
- Try different PDF

### **"Netlify deployment failed: 401 Unauthorized"**
- Verify Netlify token is correct
- Check token has deployment permissions

---

## 📖 Understanding the Code Flow

### **Workflow 1: AI Resume Parsing**

```
User uploads PDF
       ↓
FastAPI receives file (/api/parse-resume)
       ↓
PDFExtractor extracts text
       ↓
AIParserService sends to Gemini with CoT prompt
       ↓
Gemini thinks step-by-step, outputs JSON
       ↓
Pydantic validates JSON → PortfolioData
       ↓
Return to frontend (auto-fill form)
```

### **Workflow 2: Portfolio Publishing**

```
User submits form data
       ↓
FastAPI receives JSON (/api/publish)
       ↓
ArtifactGeneratorService:
  - Renders portfolio_template.html with data
  - Renders resume_template.html
  - Converts resume HTML to PDF (WeasyPrint)
  - Bundles into ZIP (index.html + resume.pdf)
       ↓
NetlifyDeployerService:
  - POSTs ZIP to Netlify API
  - Netlify extracts files
  - Deploys to CDN
       ↓
Return URLs (site_url + pdf_url)
```

---

## 🎓 Key Concepts Explained

### **1. Chain of Thought (CoT) Prompting**

Traditional prompt:
```
"Extract JSON from this resume: [text]"
```

CoT prompt:
```
"Step 1: Analyze sections
 Step 2: Extract entities
 Step 3: Validate consistency
 Step 4: Output JSON"
```

**Why it works:** Forces the AI to break down complex tasks.

---

### **2. Pydantic Data Validation**

Instead of manually checking:
```python
if "email" not in data or "@" not in data["email"]:
    raise Error("Invalid email")
```

Pydantic does it automatically:
```python
class PersonalInfo(BaseModel):
    email: EmailStr  # Auto-validates email format
```

---

### **3. Template Rendering**

Instead of string concatenation:
```python
html = f"<h1>{name}</h1>"  # XSS vulnerability!
```

Use Jinja2:
```python
template = "<h1>{{ name }}</h1>"
html = template.render(name=name)  # Auto-escapes HTML
```

---

### **4. ATS Optimization**

ATS (Applicant Tracking Systems) parse resumes. Our PDF is optimized:
- ✅ Single-column layout
- ✅ Standard fonts (Arial)
- ✅ Semantic HTML (h1, h2, p)
- ✅ No images in text
- ✅ Selectable text (not scanned image)

---

## 🚀 Next Steps

1. **Build a Frontend**
   - React/Vue/Svelte app
   - Form for manual entry
   - File upload for AI parsing
   - Display live preview

2. **Add User Accounts**
   - JWT authentication
   - SQLAlchemy + PostgreSQL
   - Save/load portfolios

3. **Multiple Themes**
   - Create theme variants (dark, modern, minimal)
   - User selects theme

4. **Custom Domains**
   - Netlify API supports custom domains
   - Add UI for domain configuration

5. **Payment Integration**
   - Stripe for subscriptions
   - Free tier + premium features

---

## 📚 Further Reading

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Jinja2 Documentation](https://jinja.palletsprojects.com/)
- [WeasyPrint Documentation](https://doc.courtbouillon.org/weasyprint/)
- [Chain of Thought Paper](https://arxiv.org/abs/2201.11903)

---

## 💡 Practice Exercises

1. Add a new field to PortfolioData (e.g., certifications)
2. Create a new theme template
3. Add rate limiting to prevent API abuse
4. Write integration tests for /api/publish
5. Add logging to track user activity

---

Built with ❤️ for learning. Questions? Check the inline comments in the code!
