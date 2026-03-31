"""
Test Resume Validator Service
"""
import pytest
from unittest.mock import Mock, patch
from app.services.validator import ResumeValidator
from app.models.portfolio import PortfolioData

@pytest.fixture
def mock_genai_client():
    with patch("app.services.validator.genai.Client") as mock_client:
        yield mock_client

def test_resume_validator_init(mock_genai_client):
    validator = ResumeValidator()
    assert validator.client is not None

def test_resume_validator_validate(mock_genai_client):
    # Setup mock response
    mock_response = Mock()
    mock_response.text = '{"completeness_score": 90, "is_complete": false}'
    mock_genai_client.return_value.models.generate_content.return_value = mock_response

    validator = ResumeValidator()

    # Mock data
    data = Mock(spec=PortfolioData)
    data.model_dump_json.return_value = "{}"

    result = validator.validate("resume text", data)

    assert result["completeness_score"] == 90
