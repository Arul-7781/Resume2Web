
import pytest
from unittest.mock import Mock, patch
import builtins
from app.services.multi_llm_parser import MultiLLMParser
from app.models.portfolio import PortfolioData

@pytest.fixture
def mock_settings():
    with patch("app.services.multi_llm_parser.settings") as mock:
        mock.min_quality_score = 75.0
        mock.max_parse_attempts = 3
        # Enable all parsers
        mock.groq_api_key = "fake_key"
        mock.mistral_api_key = "fake_key"
        mock.cohere_api_key = "fake_key"
        mock.gemini_api_key = "fake_key"
        mock.openai_api_key = "fake_key"
        yield mock

@pytest.fixture
def mock_parsers():
    # Create mock parser classes
    mock_groq = Mock()
    mock_mistral = Mock()
    mock_cohere = Mock()
    mock_gemini = Mock()
    mock_openai = Mock()

    original_import = builtins.__import__

    def side_effect(name, globals=None, locals=None, fromlist=(), level=0):
        if name.startswith("app.services.parsers"):
            mock_module = Mock()
            if "groq" in name:
                mock_module.GroqParser = Mock(return_value=mock_groq)
            elif "mistral" in name:
                mock_module.MistralParser = Mock(return_value=mock_mistral)
            elif "cohere" in name:
                mock_module.CohereParser = Mock(return_value=mock_cohere)
            elif "gemini" in name:
                mock_module.GeminiParser = Mock(return_value=mock_gemini)
            elif "openai" in name:
                mock_module.OpenAIParser = Mock(return_value=mock_openai)
            return mock_module
        return original_import(name, globals, locals, fromlist, level)

    with patch("builtins.__import__", side_effect=side_effect):
        yield {
            "Groq": mock_groq,
            "Mistral": mock_mistral,
            "Cohere": mock_cohere,
            "Gemini": mock_gemini,
            "OpenAI": mock_openai
        }

def create_mock_portfolio_data(score=80):
    """Helper to create a mock PortfolioData object with a specific score"""
    data = Mock(spec=PortfolioData)

    # Low score (<50) -> Missing required fields
    if score < 50:
        data.personal_info = Mock()
        data.personal_info.name = "" # Missing name penalty
        data.personal_info.email = "invalid" # Invalid email penalty
        data.personal_info.phone = None
        data.personal_info.linkedin = None
        data.personal_info.github = None

        data.skills = []
        data.experience = []
        data.education = []
        data.projects = []
        data.achievements = []

        data.model_dump.return_value = {
            "personal_info": {"name": "", "email": "invalid", "phone": None, "linkedin": None, "github": None, "bio": None, "location": None, "photo": None},
            "skills": [],
            "experience": [],
            "education": [],
            "projects": [],
            "achievements": [],
            "design_template": "split_screen_hero",
            "theme": "minimal-pro",
            "dark_mode": False
        }
        return data

    # High score
    data.personal_info = Mock()
    data.personal_info.name = "Test User"
    data.personal_info.email = "test@example.com"
    data.personal_info.phone = "1234567890"
    data.personal_info.linkedin = None
    data.personal_info.github = None

    data.skills = ["Skill1", "Skill2"]

    exp = Mock()
    exp.start_date = "Jan 2020"
    exp.end_date = "Present"
    exp.description = "Detailed description " * 5
    exp.role = "Role"
    exp.company = "Company"
    data.experience = [exp]

    edu = Mock()
    edu.degree = "Degree"
    edu.school = "School"
    data.education = [edu]

    proj = Mock()
    proj.title = "Project"
    data.projects = [proj]

    data.achievements = []

    data.model_dump.return_value = {
        "personal_info": {"name": "Test User", "email": "test@example.com", "phone": "123", "linkedin": None, "github": None, "bio": "", "location": "", "photo": None},
        "skills": ["Skill1", "Skill2"],
        "experience": [{"description": "Detailed description "*5, "role": "Role", "company": "Company", "start_date": "2020", "end_date": "Present"}],
        "education": [],
        "projects": [],
        "achievements": [],
        "design_template": "split_screen_hero",
        "theme": "minimal-pro",
        "dark_mode": False
    }

    return data

class TestMultiLLMParser:

    def test_initialization(self, mock_settings, mock_parsers):
        parser = MultiLLMParser(mode="adaptive")
        assert len(parser.parsers) == 5
        assert parser.mode == "adaptive"

    def test_adaptive_parse_success(self, mock_settings, mock_parsers):
        parser = MultiLLMParser(mode="adaptive")

        # Groq succeeds with high score
        mock_parsers["Groq"].parse_resume.return_value = create_mock_portfolio_data(score=90)
        # Validator (Mistral) succeeds
        mock_parsers["Mistral"].parse_resume.return_value = create_mock_portfolio_data(score=90)

        result = parser.parse_resume("test resume")

        assert mock_parsers["Groq"].parse_resume.called
        assert mock_parsers["Mistral"].parse_resume.called # Validator should be called

    def test_adaptive_parse_retry_low_score(self, mock_settings, mock_parsers):
        parser = MultiLLMParser(mode="adaptive")

        # Groq returns low score
        mock_parsers["Groq"].parse_resume.return_value = create_mock_portfolio_data(score=40)

        # Mistral returns high score
        mock_parsers["Mistral"].parse_resume.return_value = create_mock_portfolio_data(score=90)

        result = parser.parse_resume("test resume")

        assert mock_parsers["Groq"].parse_resume.called
        assert mock_parsers["Mistral"].parse_resume.called
        # Groq should be used as validator for Mistral (since it's not rate limited), so called twice
        assert mock_parsers["Groq"].parse_resume.call_count == 2

    def test_rate_limit_handling(self, mock_settings, mock_parsers):
        parser = MultiLLMParser(mode="adaptive")

        # Groq raises rate limit error
        mock_parsers["Groq"].parse_resume.side_effect = Exception("Rate limit exceeded 429")

        # Mistral succeeds
        mock_parsers["Mistral"].parse_resume.return_value = create_mock_portfolio_data(score=90)
        # Validator (Cohere) succeeds
        mock_parsers["Cohere"].parse_resume.return_value = create_mock_portfolio_data(score=90)

        result = parser.parse_resume("test resume")

        assert mock_parsers["Groq"].parse_resume.called
        assert parser._is_rate_limited("Groq")
        assert mock_parsers["Mistral"].parse_resume.called
