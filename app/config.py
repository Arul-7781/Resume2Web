"""
Configuration Management using Pydantic Settings

CONCEPT: Pydantic Settings provides type-safe configuration from environment variables.
- Automatically reads from .env file
- Validates types (str, int, bool)
- Provides defaults
- Raises errors if required vars are missing

WHY USE THIS?
- Prevents typos in env var names
- Centralizes all configuration
- Makes testing easier (can override settings)
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application configuration schema
    
    Inherits from BaseSettings which:
    1. Reads from environment variables
    2. Reads from .env file
    3. Validates types automatically
    """
    
    # AI Configuration
    gemini_api_key: Optional[str] = None
    gemini_model: str = "gemini-2.5-flash"  # Latest fast model
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"  # Cost-effective model
    groq_api_key: Optional[str] = None
    groq_model: str = "llama-3.3-70b-versatile"  # Fast, high quality
    mistral_api_key: Optional[str] = None
    mistral_model: str = "mistral-small-latest"  # Balanced model
    cohere_api_key: Optional[str] = None
    cohere_model: str = "command-r"  # Cost-effective, good accuracy
    
    # Multi-LLM Configuration
    parser_mode: str = "adaptive"  # Options: fallback, ensemble, validation, adaptive
    min_quality_score: float = 75.0  # Minimum acceptable quality score
    max_parse_attempts: int = 3  # Maximum re-parsing attempts
    
    # Netlify Configuration
    netlify_access_token: Optional[str] = None  # Optional for development
    
    # Cloudflare Pages Configuration
    cloudflare_api_token: Optional[str] = None
    cloudflare_account_id: Optional[str] = None
    
    # Application Settings
    debug: bool = False
    log_level: str = "INFO"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    class Config:
        """
        CONCEPT: Nested Config class tells Pydantic where to find values
        """
        env_file = ".env"
        case_sensitive = False  # GEMINI_API_KEY and gemini_api_key both work


# Create a singleton instance
# PATTERN: This ensures we only load .env once, not on every import
settings = Settings()
