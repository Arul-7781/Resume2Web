# 📁 Project Structure Overview

```
Portfolio_Website/
│
├── 📄 README.md                    # Project overview
├── 📄 SETUP_GUIDE.md               # Step-by-step setup instructions
├── 📄 ARCHITECTURE.md              # System design and patterns
├── 📄 CHAIN_OF_THOUGHT.md          # AI prompting deep dive
├── 📄 LEARNING_SUMMARY.md          # Concepts and skills learned
├── 📄 PROJECT_STRUCTURE.md         # This file
│
├── 🔧 Configuration Files
│   ├── requirements.txt            # Python dependencies
│   ├── .env.example                # Environment template
│   ├── .gitignore                  # Git ignore rules
│   └── setup.sh                    # Quick setup script
│
├── 📦 app/                         # Main application package
│   │
│   ├── __init__.py                 # Package marker
│   ├── main.py                     # FastAPI app + endpoints
│   ├── config.py                   # Settings management
│   │
│   ├── 📊 models/                  # Data schemas
│   │   ├── __init__.py
│   │   └── portfolio.py            # Pydantic models
│   │
│   ├── 🔧 services/                # Business logic
│   │   ├── __init__.py
│   │   ├── ai_parser.py            # AI resume parser (CoT)
│   │   ├── artifact_gen.py         # HTML/PDF generator
│   │   └── netlify_deploy.py       # Deployment service
│   │
│   ├── 🎨 templates/               # Jinja2 templates
│   │   ├── resume_template.html    # ATS-friendly resume
│   │   └── portfolio_template.html # Modern portfolio site
│   │
│   └── 🛠️ utils/                   # Helper functions
│       ├── __init__.py
│       └── pdf_extractor.py        # PDF text extraction
│
└── 🧪 tests/                       # Test suite
    ├── __init__.py
    └── test_parser.py              # AI parser tests

```

---

## 📂 Detailed File Descriptions

### **Root Level Files**

#### `README.md`
- **Purpose:** Project overview and quick start
- **Contains:** Features, tech stack, API workflow
- **Audience:** First-time viewers, GitHub visitors

#### `SETUP_GUIDE.md`
- **Purpose:** Comprehensive setup instructions
- **Contains:** Step-by-step setup, troubleshooting, testing
- **Audience:** Developers setting up the project

#### `ARCHITECTURE.md`
- **Purpose:** Deep dive into system design
- **Contains:** Architecture diagrams, design patterns, scalability
- **Audience:** Developers wanting to understand the "why"

#### `CHAIN_OF_THOUGHT.md`
- **Purpose:** Explains AI prompting technique
- **Contains:** Research, examples, best practices
- **Audience:** Learners interested in AI/LLM integration

#### `LEARNING_SUMMARY.md`
- **Purpose:** Educational recap and next steps
- **Contains:** Concepts mastered, real-world applications, learning path
- **Audience:** You (the learner) and others learning from this project

---

### **Configuration Files**

#### `requirements.txt`
- **Purpose:** Python package dependencies
- **Usage:** `pip install -r requirements.txt`
- **Contains:** FastAPI, Pydantic, Gemini, WeasyPrint, etc.

#### `.env.example`
- **Purpose:** Template for environment variables
- **Usage:** `cp .env.example .env` then fill in API keys
- **Security:** Never commit actual `.env` to Git

#### `.gitignore`
- **Purpose:** Exclude files from Git tracking
- **Contains:** venv/, .env, __pycache__, generated files

#### `setup.sh`
- **Purpose:** Automated setup script
- **Usage:** `bash setup.sh`
- **Contains:** Creates venv, installs deps, checks config

---

### **app/ - Main Application**

#### `main.py` (Heart of the Application)
- **Purpose:** FastAPI app definition and endpoints
- **Endpoints:**
  - `GET /health` - Health check
  - `POST /api/parse-resume` - Upload PDF, get JSON
  - `POST /api/publish` - Deploy portfolio
- **Concepts:** Dependency injection, middleware, error handling

#### `config.py`
- **Purpose:** Centralized configuration management
- **Pattern:** Pydantic Settings (type-safe env vars)
- **Contains:** API keys, debug settings, server config

---

### **app/models/ - Data Schemas**

#### `portfolio.py`
- **Purpose:** Define data structure (Pydantic models)
- **Models:**
  - `PersonalInfo` - Name, email, contact
  - `Experience` - Job history
  - `Education` - Degrees
  - `Project` - Portfolio projects
  - `PortfolioData` - Complete dataset
  - `PublishResponse` - API response
- **Concepts:** Data validation, type hints, JSON schema

---

### **app/services/ - Business Logic**

#### `ai_parser.py`
- **Purpose:** AI-powered resume parsing
- **Method:** Chain of Thought prompting
- **Flow:** PDF text → CoT prompt → Gemini → JSON → Validation
- **Concepts:** Prompt engineering, LLM integration, retry logic

#### `artifact_gen.py`
- **Purpose:** Generate HTML portfolio + PDF resume
- **Templates:** Jinja2 rendering
- **Output:** In-memory ZIP file (index.html + resume.pdf)
- **Concepts:** Template engines, PDF generation, in-memory processing

#### `netlify_deploy.py`
- **Purpose:** Deploy to Netlify via REST API
- **Method:** POST ZIP to Netlify API
- **Output:** Live HTTPS URL
- **Concepts:** RESTful API consumption, HTTP methods

---

### **app/templates/ - HTML Templates**

#### `resume_template.html`
- **Purpose:** ATS-friendly resume PDF
- **Design:** Single column, standard fonts, semantic HTML
- **Optimization:** Black/white, no images, machine-readable
- **Output:** Converted to PDF via WeasyPrint

#### `portfolio_template.html`
- **Purpose:** Modern portfolio website
- **Design:** Responsive (Tailwind CSS), dark mode, card layout
- **Features:** Download resume button, social links
- **Output:** Served as index.html on Netlify

---

### **app/utils/ - Helper Functions**

#### `pdf_extractor.py`
- **Purpose:** Extract text from PDF files
- **Library:** PyPDF2
- **Methods:**
  - `extract_text_from_pdf()` - Get all text
  - `clean_text()` - Remove extra whitespace
- **Concepts:** Binary file handling, text preprocessing

---

### **tests/ - Test Suite**

#### `test_parser.py`
- **Purpose:** Unit tests for AI parser
- **Framework:** pytest
- **Techniques:** Mocking (fake LLM responses), fixtures
- **Coverage:** Parsing success, JSON extraction, error handling

---

## 🔄 Data Flow Visualization

```
┌──────────────┐
│   Upload PDF │
└──────┬───────┘
       │
       ▼
┌──────────────────────┐
│ PDFExtractor         │ (utils/pdf_extractor.py)
│ .extract_text()      │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ AIParserService      │ (services/ai_parser.py)
│ .parse_resume()      │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ PortfolioData        │ (models/portfolio.py)
│ (Validated JSON)     │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ ArtifactGenerator    │ (services/artifact_gen.py)
│ .generate_artifacts()│
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ NetlifyDeployer      │ (services/netlify_deploy.py)
│ .deploy_site()       │
└──────┬───────────────┘
       │
       ▼
┌──────────────┐
│  Live URL    │
└──────────────┘
```

---

## 🎯 Which File to Edit for What?

### **Add a New Field (e.g., certifications)**

1. Edit `app/models/portfolio.py`
   - Add `certifications: List[str]` to `PortfolioData`

2. Edit `app/templates/resume_template.html`
   - Add section to display certifications

3. Edit `app/templates/portfolio_template.html`
   - Add certifications to portfolio

4. Edit `app/services/ai_parser.py`
   - Update CoT prompt to extract certifications

### **Add a New Endpoint**

1. Edit `app/main.py`
   - Add new `@app.post()` or `@app.get()` function

### **Add a New Theme**

1. Create `app/templates/modern_template.html`
2. Edit `app/services/artifact_gen.py`
   - Add logic to select template based on `data.theme`

### **Add Database Support**

1. Create `app/database.py` (SQLAlchemy setup)
2. Create `app/models/db_models.py` (SQLAlchemy models)
3. Edit `app/main.py` (add database endpoints)

---

## 🚀 Quick Navigation

- **Want to understand the code?** → Start with `app/main.py`
- **Want to modify AI parsing?** → Edit `app/services/ai_parser.py`
- **Want to change resume design?** → Edit `app/templates/resume_template.html`
- **Want to change portfolio design?** → Edit `app/templates/portfolio_template.html`
- **Want to add new features?** → Read `ARCHITECTURE.md` for patterns

---

Structure follows **separation of concerns** - each file has ONE clear purpose!
