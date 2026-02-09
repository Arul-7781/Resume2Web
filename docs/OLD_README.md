# Portfolio & Resume Builder SaaS MVP

## 🎯 Project Overview
A FastAPI-based SaaS that enables users to:
1. **Upload Resume PDF** → AI extracts data → Auto-fill form
2. **Manual Entry** → Fill form directly
3. **One-Click Deploy** → Get live portfolio + ATS-friendly PDF

---

## 🧠 Core Concepts Explained

### 1. **Chain of Thought (CoT) Reasoning**
The AI parser uses CoT to improve accuracy:
```
Step 1: Identify sections (Education, Experience, Skills)
Step 2: Extract entities (dates, companies, degrees)
Step 3: Validate logical consistency
Step 4: Structure into JSON
```

### 2. **Service-Oriented Architecture**
```
API Layer (main.py) → Orchestrates services
Services Layer → Business logic (parsing, generation, deployment)
Models Layer → Data contracts (Pydantic schemas)
Templates Layer → HTML blueprints
```

### 3. **ATS Optimization**
ATS (Applicant Tracking Systems) parse PDFs. We ensure compatibility by:
- Single-column layout (no tables/columns)
- Standard fonts (Arial, Calibri)
- Semantic HTML (h1, h2, p tags)
- No images/graphics in text areas

---

## 📁 Folder Structure

```
portfolio_builder/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app + endpoints
│   ├── config.py            # Environment variables
│   ├── models/
│   │   ├── __init__.py
│   │   └── portfolio.py     # Pydantic schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai_parser.py     # LLM resume parser (CoT)
│   │   ├── artifact_gen.py  # Site + PDF generator
│   │   └── netlify_deploy.py# Deployment service
│   ├── templates/
│   │   ├── resume_template.html      # ATS-friendly
│   │   └── portfolio_template.html   # Modern portfolio
│   └── utils/
│       ├── __init__.py
│       ├── pdf_extractor.py # PDF text extraction
│       └── validators.py    # Custom validation logic
├── tests/
│   ├── __init__.py
│   ├── test_parser.py
│   └── test_api.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites
```bash
Python 3.10+
pip install -r requirements.txt
```

### Environment Setup
```bash
cp .env.example .env
# Add your API keys:
# GEMINI_API_KEY=your_key
# NETLIFY_ACCESS_TOKEN=your_token
```

### Run Locally
```bash
uvicorn app.main:app --reload
```

Visit: `http://localhost:8000/docs` for interactive API docs

---

## 🔄 API Workflow

### Endpoint 1: `/api/parse-resume` (POST)
**Purpose:** Upload PDF to autofill form  
**Input:** Multipart file (PDF)  
**Output:** 
```json
{
  "personal_info": { "name": "John Doe", ... },
  "skills": ["Python", "FastAPI"],
  "experience": [...],
  ...
}
```

### Endpoint 2: `/api/publish` (POST)
**Purpose:** Deploy portfolio + generate PDF  
**Input:** PortfolioData JSON  
**Output:**
```json
{
  "site_url": "https://your-site.netlify.app",
  "pdf_url": "https://your-site.netlify.app/resume.pdf"
}
```

---

## 📚 Learning Resources

### FastAPI Concepts
- **Dependency Injection:** Used for sharing services (e.g., AI parser instance)
- **Background Tasks:** For async PDF generation
- **CORS:** Allows frontend to call API from different domain

### LLM Integration
- **Prompt Engineering:** Structured prompts for consistent JSON output
- **Token Management:** Limiting context window for cost efficiency
- **Error Handling:** Fallback when LLM fails to parse

### PDF Generation
- **WeasyPrint:** Converts HTML+CSS to PDF using Cairo graphics library
- **ATS Compatibility:** Why we avoid complex layouts

---

## 🔐 Security Considerations (Future)
- Input sanitization (prevent XSS in user data)
- Rate limiting (prevent API abuse)
- Authentication (JWT tokens)
- File type validation (ensure uploads are PDFs)

---

## 📈 Roadmap
- [ ] Phase 1: Core MVP (parsing + deployment)
- [ ] Phase 2: User accounts + saved portfolios
- [ ] Phase 3: Multiple themes
- [ ] Phase 4: Custom domain support
