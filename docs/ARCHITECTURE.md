# Architecture & Design Patterns Deep Dive

## 🏛️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         FRONTEND                             │
│  (React/Vue/HTML - Not included in this MVP)                │
│                                                              │
│  Components:                                                 │
│  - Upload Form (drag-drop PDF)                              │
│  - Manual Entry Form (text inputs)                          │
│  - Live Preview (portfolio rendering)                       │
│  - Deploy Button                                            │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   │ HTTP Requests (JSON)
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                      FASTAPI BACKEND                         │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │               API LAYER (main.py)                     │  │
│  │  Endpoints:                                           │  │
│  │  • POST /api/parse-resume  → Parse PDF               │  │
│  │  • POST /api/publish       → Deploy portfolio        │  │
│  │  • GET  /health            → Health check            │  │
│  └───────────────┬──────────────────────────────────────┘  │
│                  │                                          │
│                  │ Dependency Injection                     │
│                  ▼                                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │            SERVICES LAYER                             │  │
│  │                                                        │  │
│  │  AIParserService         ArtifactGeneratorService     │  │
│  │  ┌──────────────┐       ┌──────────────────┐         │  │
│  │  │ Chain of     │       │ Template Engine  │         │  │
│  │  │ Thought      │       │ (Jinja2)         │         │  │
│  │  │ Prompting    │       │                  │         │  │
│  │  └──────────────┘       │ • Portfolio HTML │         │  │
│  │                         │ • Resume PDF     │         │  │
│  │  NetlifyDeployerService │ • ZIP Bundle     │         │  │
│  │  ┌──────────────┐       └──────────────────┘         │  │
│  │  │ REST API     │                                     │  │
│  │  │ Client       │                                     │  │
│  │  └──────────────┘                                     │  │
│  └───────────────┬──────────────────────────────────────┘  │
│                  │                                          │
│                  │ Data Flow                                │
│                  ▼                                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │            MODELS LAYER                               │  │
│  │  (Pydantic Schemas)                                   │  │
│  │                                                        │  │
│  │  PortfolioData                                        │  │
│  │  ├─ PersonalInfo                                      │  │
│  │  ├─ Experience[]                                      │  │
│  │  ├─ Education[]                                       │  │
│  │  ├─ Projects[]                                        │  │
│  │  └─ Skills[]                                          │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   │ External API Calls
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                   EXTERNAL SERVICES                          │
│                                                              │
│  Google Gemini API              Netlify API                 │
│  ┌──────────────┐              ┌──────────────┐            │
│  │ LLM Processing│              │ CDN Hosting  │            │
│  │ (AI Parsing)  │              │ SSL/HTTPS    │            │
│  └──────────────┘              └──────────────┘            │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧩 Design Patterns Used

### **1. Service-Oriented Architecture (SOA)**

**What:** Break application into independent services.

**Why:** 
- Each service has one responsibility
- Easy to test in isolation
- Can be replaced without affecting others

**Example:**
```python
# Bad: Everything in one function
def publish_portfolio(data):
    # Generate HTML
    # Convert to PDF
    # Deploy to Netlify
    # All mixed together!

# Good: Separate services
class ArtifactGeneratorService:
    def generate_all_artifacts(data): ...

class NetlifyDeployerService:
    def deploy_site(zip_file): ...
```

---

### **2. Dependency Injection**

**What:** Pass dependencies to functions instead of creating them inside.

**Why:**
- Easier testing (inject mocks)
- Loosely coupled code
- Reuse instances (performance)

**Example:**
```python
# Bad: Hard to test
def publish_portfolio(data):
    deployer = NetlifyDeployerService()  # Created every time!
    deployer.deploy(...)

# Good: Inject dependency
def publish_portfolio(data, deployer: NetlifyDeployerService):
    deployer.deploy(...)  # Can inject mock for testing
```

---

### **3. Template Method Pattern**

**What:** Define algorithm structure, let subclasses customize steps.

**Used in:** Resume vs Portfolio HTML generation.

**Example:**
```python
class ArtifactGeneratorService:
    def _generate_html(self, data, template_name):
        # Common logic: Load template, render
        template = self.env.get_template(template_name)
        return template.render(**data)
    
    def _generate_portfolio_html(self, data):
        # Specific: Which template to use
        return self._generate_html(data, 'portfolio_template.html')
```

---

### **4. Chain of Responsibility (CoT)**

**What:** Pass request through a chain of handlers.

**Used in:** AI parsing steps.

**Flow:**
```
Resume Text
    ↓
Step 1: Section Analyzer
    ↓
Step 2: Entity Extractor
    ↓
Step 3: Validator
    ↓
Step 4: JSON Formatter
    ↓
Structured Data
```

---

## 📊 Data Flow Diagrams

### **Flow 1: AI Resume Parsing**

```
┌──────────┐
│  User    │
│ (Upload  │
│  PDF)    │
└────┬─────┘
     │
     │ 1. POST /api/parse-resume
     ▼
┌─────────────────┐
│  FastAPI        │
│  Endpoint       │
└────┬────────────┘
     │
     │ 2. Extract bytes
     ▼
┌─────────────────┐
│  PDFExtractor   │──► PyPDF2.PdfReader
│  .extract_text()│
└────┬────────────┘
     │
     │ 3. Raw text
     ▼
┌─────────────────┐
│  AIParserService│
│  .parse_resume()│
└────┬────────────┘
     │
     │ 4. Send CoT prompt
     ▼
┌─────────────────┐
│  Gemini API     │──► Chain of Thought reasoning
│  (LLM)          │
└────┬────────────┘
     │
     │ 5. JSON response
     ▼
┌─────────────────┐
│  Pydantic       │──► Validate schema
│  PortfolioData  │
└────┬────────────┘
     │
     │ 6. Return validated data
     ▼
┌──────────┐
│  User    │
│ (Auto-   │
│  filled  │
│  form)   │
└──────────┘
```

---

### **Flow 2: Portfolio Publishing**

```
┌──────────┐
│  User    │
│ (Submit  │
│  form)   │
└────┬─────┘
     │
     │ 1. POST /api/publish {PortfolioData}
     ▼
┌─────────────────────────┐
│  FastAPI Endpoint       │
└────┬────────────────────┘
     │
     │ 2. Inject dependencies
     ▼
┌─────────────────────────┐
│ ArtifactGeneratorService│
│                         │
│  ┌──────────────────┐  │
│  │ Jinja2 Rendering │  │
│  └────┬─────────────┘  │
│       │                 │
│       │ index.html      │
│       ▼                 │
│  ┌──────────────────┐  │
│  │ WeasyPrint       │  │
│  └────┬─────────────┘  │
│       │                 │
│       │ resume.pdf      │
│       ▼                 │
│  ┌──────────────────┐  │
│  │ ZIP Bundler      │  │
│  └────┬─────────────┘  │
└───────┼─────────────────┘
        │
        │ 3. ZIP file (in-memory)
        ▼
┌─────────────────────────┐
│ NetlifyDeployerService  │
│                         │
│  ┌──────────────────┐  │
│  │ HTTP POST        │  │
│  │ to Netlify API   │  │
│  └────┬─────────────┘  │
└───────┼─────────────────┘
        │
        │ 4. API request
        ▼
┌─────────────────────────┐
│  Netlify CDN            │
│  • Extract ZIP          │
│  • Deploy to edge nodes │
│  • Generate SSL cert    │
└────┬────────────────────┘
     │
     │ 5. Return URLs
     ▼
┌──────────┐
│  User    │
│ (Live    │
│  site!)  │
└──────────┘
```

---

## 🔐 Security Considerations

### **Current Implementation**

✅ **Environment Variables:** API keys not hardcoded
✅ **HTTPS:** Netlify provides SSL
✅ **Pydantic Validation:** Prevents malformed data
✅ **Jinja2 Auto-escape:** Prevents XSS

### **Production Requirements**

❌ **Authentication:** No user accounts yet
❌ **Rate Limiting:** No protection against abuse
❌ **Input Sanitization:** File uploads not deeply validated
❌ **CORS:** Currently allows all origins

**Implementation Plan:**

```python
# 1. Add JWT Authentication
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.post("/api/publish")
async def publish_portfolio(
    data: PortfolioData,
    token: str = Depends(security)  # Requires bearer token
):
    user = verify_jwt(token)  # Validate token
    # ... rest of logic

# 2. Add Rate Limiting
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/parse-resume")
@limiter.limit("5/minute")  # Max 5 requests per minute
async def parse_resume(...):
    ...

# 3. Validate File Upload
def validate_pdf(file: UploadFile):
    # Check file size
    if file.size > 10 * 1024 * 1024:  # 10MB
        raise HTTPException(400, "File too large")
    
    # Check MIME type
    if file.content_type != "application/pdf":
        raise HTTPException(400, "Only PDFs allowed")
    
    # Check magic bytes (first few bytes)
    header = file.file.read(4)
    if header != b'%PDF':
        raise HTTPException(400, "Invalid PDF file")
```

---

## 🚀 Performance Optimization

### **Current Bottlenecks**

1. **LLM API Call:** 2-5 seconds (network + processing)
2. **PDF Generation:** 1-2 seconds (WeasyPrint rendering)
3. **Netlify Deploy:** 5-10 seconds (upload + CDN propagation)

### **Optimization Strategies**

```python
# 1. Background Tasks (FastAPI)
from fastapi import BackgroundTasks

@app.post("/api/publish")
async def publish_portfolio(
    data: PortfolioData,
    background_tasks: BackgroundTasks
):
    # Return immediately, process in background
    background_tasks.add_task(generate_and_deploy, data)
    return {"status": "processing", "job_id": "123"}

# 2. Caching (Redis)
import redis
cache = redis.Redis()

def parse_resume(text: str):
    # Check cache first
    cache_key = hashlib.md5(text.encode()).hexdigest()
    cached = cache.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Parse with AI
    result = ai_parser.parse(text)
    
    # Cache for 1 hour
    cache.setex(cache_key, 3600, json.dumps(result))
    return result

# 3. Async I/O (httpx instead of requests)
import httpx

async def deploy_site(zip_file):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.netlify.com/...",
            content=zip_file
        )
    return response.json()
```

---

## 📈 Scalability Roadmap

### **Phase 1: MVP (Current)**
- Single server
- In-memory processing
- Direct API calls
- **Handles:** ~100 users/day

### **Phase 2: Production**
- Database (PostgreSQL)
- File storage (AWS S3)
- Background jobs (Celery + Redis)
- **Handles:** ~10,000 users/day

### **Phase 3: Scale**
- Kubernetes cluster
- Load balancing
- Microservices (separate PDF service, AI service)
- CDN for assets
- **Handles:** ~1M users/day

---

## 🧪 Testing Strategy

```
Unit Tests (70%)
├── test_models.py       → Pydantic validation
├── test_pdf_extractor.py → PDF parsing
├── test_ai_parser.py    → AI service (mocked)
└── test_services.py     → Business logic

Integration Tests (20%)
├── test_api_endpoints.py → Full request/response
└── test_deployment.py    → Netlify integration

E2E Tests (10%)
└── test_user_flow.py     → Selenium browser tests
```

**Run tests:**
```bash
# Unit tests only
pytest tests/test_*.py -v

# With coverage
pytest --cov=app --cov-report=html

# Specific test
pytest tests/test_parser.py::TestAIParser::test_parse_resume_success
```

---

## 💡 Extension Ideas

1. **Custom Themes:** User selects from multiple designs
2. **A/B Testing:** Try different resume formats
3. **Analytics:** Track which skills get most interviews
4. **AI Suggestions:** "Add quantifiable achievements"
5. **LinkedIn Import:** Parse LinkedIn profile
6. **Version History:** Save multiple resume versions
7. **Collaboration:** Share portfolio for review
8. **Multi-language:** Generate in different languages

---

Built with comprehensive architecture for learning and scalability!
