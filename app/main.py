"""
FastAPI Main Application

CONCEPT: FastAPI is an ASGI framework (Asynchronous Server Gateway Interface)
- Built on Starlette (async web framework) + Pydantic (data validation)
- Auto-generates OpenAPI docs at /docs
- Type hints enable auto-validation and serialization

WHY FASTAPI?
- Fast: Comparable to Node.js and Go
- Easy: Intuitive API, great developer experience
- Robust: Production-ready with built-in validation
- Modern: Async/await, type hints, dependency injection
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import logging
from typing import Dict, Any

from app.config import settings
from app.models.portfolio import PortfolioData, PublishResponse
from app.services import ArtifactGeneratorService, NetlifyDeployerService, CloudflareDeployerService
from app.services.multi_llm_parser import MultiLLMParser
from app.services.validator import ResumeValidator
from app.utils import PDFExtractor

# =============================================================================
# LOGGING SETUP
# CONCEPT: Structured logging for debugging and monitoring
# =============================================================================
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# =============================================================================
# FASTAPI APP INITIALIZATION
# =============================================================================
app = FastAPI(
    title="Portfolio & Resume Builder API",
    description="AI-powered portfolio generator with resume parsing",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc"  # ReDoc (alternative docs)
)

# Mount static files directory for frontend
app.mount("/static", StaticFiles(directory="app/static"), name="static")


# =============================================================================
# MIDDLEWARE CONFIGURATION
# CONCEPT: Middleware intercepts every request/response for cross-cutting concerns
# =============================================================================

# CORS (Cross-Origin Resource Sharing)
# EXPLANATION: Allows frontend (e.g., React app on localhost:3000) to call this API
# Without CORS, browsers block cross-origin requests for security
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins: ["https://yourapp.com"]
    allow_credentials=True,
    allow_methods=["*"],  # Allow GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],  # Allow all headers
)


# =============================================================================
# DEPENDENCY INJECTION
# CONCEPT: FastAPI's way of sharing instances across endpoints
# Instead of creating new service instances in every function, we inject them
# =============================================================================

# These will be created once and reused (singleton pattern)
ai_parser = None
artifact_generator = None
netlify_deployer = None
cloudflare_deployer = None
resume_validator = None


def get_ai_parser() -> MultiLLMParser:
    """
    Dependency: Multi-LLM Parser Service
    
    CONCEPT: Lazy initialization
    Only create the service when first needed (not at startup)
    Uses multi-LLM approach for better accuracy
    """
    global ai_parser
    if ai_parser is None:
        parser_mode = settings.parser_mode
        logger.info(f"Initializing Multi-LLM Parser in {parser_mode} mode")
        ai_parser = MultiLLMParser(mode=parser_mode)
    return ai_parser


def get_artifact_generator() -> ArtifactGeneratorService:
    """Dependency: Artifact Generator Service"""
    global artifact_generator
    if artifact_generator is None:
        artifact_generator = ArtifactGeneratorService()
    return artifact_generator


def get_netlify_deployer() -> NetlifyDeployerService:
    """Dependency: Netlify Deployer Service"""
    global netlify_deployer
    if netlify_deployer is None:
        netlify_deployer = NetlifyDeployerService()
    return netlify_deployer


def get_cloudflare_deployer() -> CloudflareDeployerService:
    """Dependency: Cloudflare Pages Deployer Service"""
    global cloudflare_deployer
    if cloudflare_deployer is None:
        cloudflare_deployer = CloudflareDeployerService()
    return cloudflare_deployer


def get_resume_validator() -> ResumeValidator:
    """Dependency: Resume Validator Service"""
    global resume_validator
    if resume_validator is None:
        resume_validator = ResumeValidator()
    return resume_validator


# =============================================================================
# ROOT & HEALTH CHECK ENDPOINTS
# =============================================================================

@app.get("/", response_class=HTMLResponse)
async def root():
    """
    Serve the frontend UI
    """
    with open("app/static/index.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.get("/api")
async def api_info():
    """
    API information endpoint
    
    Returns:
        Welcome message with links
    """
    return {
        "message": "Portfolio & Resume Builder API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "endpoints": {
            "parse_resume": "POST /api/parse-resume",
            "publish": "POST /api/publish"
        }
    }


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint
    
    Returns:
        Status message
    
    USAGE:
    - Load balancer: Pings this to check if server is alive
    - Monitoring: Alerts if this returns 500 error
    - CI/CD: Waits for this before declaring deployment successful
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": "development" if settings.debug else "production"
    }


# =============================================================================
# ENDPOINT 1: PARSE RESUME (AI Upload Flow)
# =============================================================================

@app.post("/api/parse-resume", response_model=PortfolioData)
async def parse_resume(
    file: UploadFile = File(...)
) -> PortfolioData:
    """
    Parse uploaded resume PDF and extract structured data
    
    WORKFLOW:
    1. Validate file is PDF
    2. Extract text from PDF
    3. Send to AI for parsing (Chain of Thought)
    4. Return structured JSON
    
    Args:
        file: Uploaded PDF file (multipart/form-data)
        
    Returns:
        PortfolioData: Structured resume data
        
    Raises:
        HTTPException: If file is invalid or parsing fails
    
    FRONTEND INTEGRATION:
    ```javascript
    const formData = new FormData();
    formData.append('file', pdfFile);
    
    const response = await fetch('/api/parse-resume', {
      method: 'POST',
      body: formData
    });
    
    const data = await response.json();
    // data now contains structured portfolio data
    // Use it to populate the manual entry form
    ```
    """
    try:
        # VALIDATION: Ensure file is PDF
        if not file.filename.endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are supported"
            )
        
        logger.info(f"Parsing resume: {file.filename}")
        
        # Extract text from PDF
        pdf_text = PDFExtractor.extract_text_from_pdf(file.file)
        
        if not pdf_text or len(pdf_text) < 50:
            raise HTTPException(
                status_code=400,
                detail="Could not extract sufficient text from PDF. Please ensure the PDF contains readable text."
            )
        
        # Clean text for better AI parsing
        cleaned_text = PDFExtractor.clean_text(pdf_text)
        
        # Parse with AI (lazy initialization - uses adaptive multi-LLM)
        parser = get_ai_parser()
        portfolio_data = parser.parse_resume(cleaned_text)
        
        # Validate parsed data against original resume
        validator = get_resume_validator()
        try:
            validation_result = validator.validate(cleaned_text, portfolio_data)
            logger.info(f"Successfully parsed resume for {portfolio_data.personal_info.name}")
            logger.info(f"AI Validation score: {validation_result['completeness_score']}%")
        except Exception as val_error:
            # Fallback to quick validation if Gemini validator fails (e.g., rate limit)
            logger.warning(f"AI validation failed ({val_error}), using quick validation")
            validation_result = validator.quick_validate(portfolio_data)
            logger.info(f"Quick Validation score: {validation_result['completeness_score']}%")
        
        # Return both parsed data and validation results
        return JSONResponse(content={
            "portfolio_data": portfolio_data.model_dump(mode='json'),
            "validation": validation_result
        })
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        logger.error(f"Resume parsing error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse resume: {str(e)}"
        )


# =============================================================================
# ENDPOINT 2: PREVIEW PORTFOLIO (Before Publishing)
# =============================================================================

@app.post("/api/preview")
async def preview_portfolio(data: Dict[str, Any]) -> JSONResponse:
    """
    Generate portfolio HTML preview without deploying
    
    WORKFLOW:
    1. Receive raw JSON (not validated yet for flexibility)
    2. Clean and validate data
    3. Generate HTML portfolio (no deployment)
    4. Return HTML as string for iframe preview
    
    Args:
        data: Portfolio data as raw dict
        
    Returns:
        JSONResponse with HTML content
    
    FRONTEND INTEGRATION:
    ```javascript
    const response = await fetch('/api/preview', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(portfolioData)
    });
    
    const { html } = await response.json();
    // Show in iframe or new window
    document.getElementById('previewFrame').srcdoc = html;
    ```
    """
    try:
        # Validate and convert to PortfolioData
        portfolio_data = PortfolioData(**data)
        
        logger.info(f"Generating preview for {portfolio_data.personal_info.name}")
        
        # Generate HTML only (no ZIP, no PDF, no deployment)
        generator = get_artifact_generator()
        html_content = generator._generate_portfolio_html(portfolio_data)
        
        return JSONResponse(content={
            "html": html_content,
            "name": portfolio_data.personal_info.name
        })
        
    except Exception as e:
        logger.error(f"Preview generation error: {e}")
        raise HTTPException(
            status_code=422,
            detail=f"Invalid portfolio data: {str(e)}"
        )


# =============================================================================
# ENDPOINT 3: PUBLISH PORTFOLIO (Final Deployment)
# =============================================================================

@app.post("/api/publish", response_model=PublishResponse)
async def publish_portfolio(
    data: PortfolioData,
    platform: str = "netlify",
    background_tasks: BackgroundTasks = None
) -> PublishResponse:
    """
    Generate and deploy portfolio website + resume PDF
    
    WORKFLOW:
    1. Validate input data (automatic via Pydantic)
    2. Generate HTML portfolio + PDF resume
    3. Bundle into ZIP file
    4. Deploy to chosen platform (Netlify or Cloudflare)
    5. Return live URLs
    
    Args:
        data: Complete portfolio data (from manual form OR AI parsing)
        platform: Deployment platform - "netlify" or "cloudflare" (default: "netlify")
        background_tasks: FastAPI background task manager
        
    Returns:
        PublishResponse: Deployed site URLs
        
    PLATFORM OPTIONS:
    - netlify: 100 GB/month bandwidth, mature API
    - cloudflare: UNLIMITED bandwidth, global CDN, faster
    
    FRONTEND INTEGRATION:
    ```javascript
    const response = await fetch('/api/publish?platform=cloudflare', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(portfolioData)
    });
    
    const result = await response.json();
    console.log('Live site:', result.site_url);
    console.log('Resume PDF:', result.pdf_url);
    ```
    """
    try:
        logger.info(f"Publishing portfolio for {data.personal_info.name} to {platform}")
        
        # Validate platform
        if platform not in ["netlify", "cloudflare"]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid platform: {platform}. Must be 'netlify' or 'cloudflare'"
            )
        
        # Lazy initialization of services
        generator = get_artifact_generator()
        
        # STEP 1: Generate artifacts (ZIP with HTML + PDF)
        logger.info("Generating artifacts...")
        zip_buffer = generator.generate_all_artifacts(data)
        
        # STEP 2: Deploy to chosen platform
        if platform == "cloudflare":
            logger.info("Deploying to Cloudflare Pages...")
            deployer = get_cloudflare_deployer()
            deploy_result = deployer.deploy_site(zip_buffer)
        else:  # netlify
            logger.info("Deploying to Netlify...")
            deployer = get_netlify_deployer()
            deploy_result = deployer.deploy_site(zip_buffer)
        
        # STEP 3: Construct PDF URL
        # Both platforms serve all files in the ZIP at the root
        # So resume.pdf is accessible at {site_url}/resume.pdf
        site_url = deploy_result["site_url"]
        pdf_url = f"{site_url}/resume.pdf"
        
        logger.info(f"✅ Successfully deployed to {platform}: {site_url}")
        
        return PublishResponse(
            site_url=site_url,
            pdf_url=pdf_url
        )
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        logger.error(f"Publish error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to publish portfolio: {str(e)}"
        )


# =============================================================================
# ERROR HANDLERS
# CONCEPT: Global exception handling for consistent error responses
# =============================================================================

@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle validation errors"""
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Catch-all for unexpected errors"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# =============================================================================
# STARTUP EVENT
# CONCEPT: Run code when server starts (before accepting requests)
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """
    Run on server startup
    
    COMMON USES:
    - Initialize database connections
    - Load ML models into memory
    - Warm up caches
    - Verify API credentials
    """
    logger.info("="*50)
    logger.info("Portfolio Builder API Starting...")
    logger.info(f"Debug Mode: {settings.debug}")
    logger.info(f"Gemini API: {'Configured' if settings.gemini_api_key else 'Missing'}")
    logger.info(f"Netlify Token: {'Configured' if settings.netlify_access_token else 'Missing'}")
    logger.info("="*50)


# =============================================================================
# SHUTDOWN EVENT
# =============================================================================

@app.on_event("shutdown")
async def shutdown_event():
    """
    Run on server shutdown
    
    COMMON USES:
    - Close database connections
    - Flush logs
    - Save state
    """
    logger.info("Portfolio Builder API Shutting Down...")


# =============================================================================
# EDUCATIONAL NOTES: FastAPI Architecture Patterns
# =============================================================================
"""
1. **DEPENDENCY INJECTION**
   Instead of:
   ```
   @app.post("/api/publish")
   def publish():
       generator = ArtifactGeneratorService()  # Created every request!
   ```
   
   We use:
   ```
   def get_generator():
       global generator
       if generator is None:
           generator = ArtifactGeneratorService()  # Created once
       return generator
   
   @app.post("/api/publish")
   def publish(generator: ArtifactGeneratorService = Depends(get_generator)):
       # Injected instance
   ```
   
   Benefits:
   - Singleton pattern (one instance)
   - Easy testing (can inject mocks)
   - Clean separation of concerns

2. **TYPE HINTS + PYDANTIC**
   When you write:
   ```
   @app.post("/api/publish", response_model=PublishResponse)
   async def publish(data: PortfolioData) -> PublishResponse:
   ```
   
   FastAPI automatically:
   - Validates request body matches PortfolioData schema
   - Returns 422 error if validation fails
   - Validates return value matches PublishResponse
   - Generates OpenAPI schema for /docs

3. **ASYNC/AWAIT**
   - `async def` = Coroutine (can pause and resume)
   - `await` = Pause here until operation completes
   - Allows handling 1000s of concurrent requests
   
   When to use async:
   ✅ I/O-bound tasks (API calls, database queries)
   ❌ CPU-bound tasks (image processing, ML inference)

4. **MIDDLEWARE**
   Wraps every request:
   Request → Middleware → Endpoint → Middleware → Response
   
   Common middleware:
   - CORS (cross-origin requests)
   - Authentication (check JWT tokens)
   - Rate limiting (prevent abuse)
   - Logging (track all requests)

5. **EXCEPTION HANDLING**
   - HTTPException: Return specific HTTP status codes
   - Global handlers: Catch all exceptions of a type
   - Custom responses: Return JSON instead of HTML errors

PRODUCTION CONSIDERATIONS:
- Add authentication (JWT tokens, OAuth)
- Implement rate limiting (slowapi library)
- Use PostgreSQL for user data (SQLAlchemy ORM)
- Add caching (Redis)
- Deploy with Docker + Kubernetes or AWS Lambda
"""
