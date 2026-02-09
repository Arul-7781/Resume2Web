"""
Test Suite for AI Parser Service

CONCEPT: Unit Testing
- Test individual components in isolation
- Mock external dependencies (LLM API calls)
- Verify expected behavior

WHY TEST?
- Catch bugs early (before production)
- Enable refactoring (ensure nothing breaks)
- Document expected behavior
- Build confidence in code quality
"""

import pytest
from unittest.mock import Mock, patch
from app.services.ai_parser import AIParserService
from app.models.portfolio import PortfolioData


class TestAIParser:
    """Test cases for AI parser service"""
    
    @pytest.fixture
    def sample_resume_text(self):
        """
        CONCEPT: Pytest Fixture
        Reusable test data that's set up before each test
        """
        return """
        John Doe
        john@example.com | +1-234-567-8900
        
        EXPERIENCE
        Senior Engineer at Tech Corp
        Jan 2020 - Present
        - Built microservices using Python
        - Led team of 5 engineers
        
        EDUCATION
        B.S. Computer Science, MIT, 2019
        
        SKILLS
        Python, FastAPI, React, PostgreSQL
        """
    
    @patch('app.services.ai_parser.genai.GenerativeModel')
    def test_parse_resume_success(self, mock_model, sample_resume_text):
        """
        Test successful resume parsing
        
        CONCEPT: Mocking
        Replace real LLM API with fake response
        Avoids:
        - Actual API calls (cost money, slow, flaky)
        - Network dependency (tests should work offline)
        """
        # Setup mock response
        mock_response = Mock()
        mock_response.text = '''
        {
          "personal_info": {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "+1-234-567-8900"
          },
          "skills": ["Python", "FastAPI", "React"],
          "experience": [{
            "role": "Senior Engineer",
            "company": "Tech Corp",
            "start_date": "Jan 2020",
            "end_date": "Present",
            "description": "Built microservices"
          }],
          "education": [{
            "degree": "B.S. Computer Science",
            "school": "MIT",
            "year": "2019"
          }],
          "projects": [],
          "theme": "minimalist"
        }
        '''
        
        mock_model.return_value.generate_content.return_value = mock_response
        
        # Create parser (will use mocked model)
        parser = AIParserService()
        
        # Test parsing
        result = parser.parse_resume(sample_resume_text)
        
        # Assertions (verify expected behavior)
        assert isinstance(result, PortfolioData)
        assert result.personal_info.name == "John Doe"
        assert result.personal_info.email == "john@example.com"
        assert "Python" in result.skills
        assert len(result.experience) == 1
        assert result.experience[0].company == "Tech Corp"
    
    def test_extract_json_from_markdown(self):
        """Test JSON extraction from markdown code blocks"""
        parser = AIParserService()
        
        # LLM often wraps JSON in markdown
        response_text = '''
        Here's the extracted data:
        
        ```json
        {"name": "Test User", "email": "test@example.com"}
        ```
        '''
        
        result = parser._extract_json_from_response(response_text)
        
        assert result["name"] == "Test User"
        assert result["email"] == "test@example.com"


# =============================================================================
# EDUCATIONAL NOTES: Testing Best Practices
# =============================================================================
"""
TESTING PYRAMID:

1. **Unit Tests** (70% of tests)
   - Test individual functions
   - Fast (milliseconds)
   - No external dependencies
   
2. **Integration Tests** (20%)
   - Test multiple components together
   - Use real database (test DB)
   - Slower (seconds)
   
3. **End-to-End Tests** (10%)
   - Test entire user flow
   - Use real browser (Selenium)
   - Slowest (minutes)

MOCKING EXPLAINED:
When testing AIParserService, we don't want to:
- Call real Gemini API (costs money)
- Depend on network (tests fail if API is down)
- Wait for API response (slow tests)

Solution: Replace genai.GenerativeModel with a fake (mock)
The mock returns our predefined response immediately.

ASSERTIONS:
- assert x == y: Equality check
- assert x in y: Membership check
- assert isinstance(x, Type): Type check
- pytest.raises(Exception): Expect an exception

FIXTURES:
Reusable setup code that runs before each test:
```
@pytest.fixture
def sample_data():
    return {"key": "value"}

def test_something(sample_data):
    # sample_data is automatically injected
    assert sample_data["key"] == "value"
```

RUNNING TESTS:
```bash
pytest                    # Run all tests
pytest -v                 # Verbose output
pytest tests/test_parser.py  # Run specific file
pytest -k "test_parse"    # Run tests matching name
pytest --cov=app          # Show code coverage
```
"""
