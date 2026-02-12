
import pytest
from unittest.mock import Mock, patch
from app.services.artifact_gen import ArtifactGeneratorService
from app.models.portfolio import PortfolioData

@pytest.fixture
def mock_portfolio_data():
    data = Mock(spec=PortfolioData)
    data.personal_info = Mock()
    data.personal_info.name = "Test User"
    data.personal_info.email = "test@example.com"
    data.skills = ["Skill1"]
    data.experience = []
    data.education = []
    data.projects = []
    data.achievements = []
    data.theme = "minimal-pro"
    data.design_template = "portfolio_template_new"
    data.dark_mode = True
    return data

class TestArtifactGenerator:

    @patch("app.services.artifact_gen.Environment")
    def test_generate_portfolio_html_passes_dark_mode(self, mock_env_cls, mock_portfolio_data):
        # Setup mock environment and template
        mock_env = Mock()
        mock_env_cls.return_value = mock_env
        mock_template = Mock()
        mock_env.get_template.return_value = mock_template

        service = ArtifactGeneratorService()
        service._generate_portfolio_html(mock_portfolio_data)

        # Verify render called with dark_mode
        args, kwargs = mock_template.render.call_args
        assert "dark_mode" in kwargs
        assert kwargs["dark_mode"] is True
