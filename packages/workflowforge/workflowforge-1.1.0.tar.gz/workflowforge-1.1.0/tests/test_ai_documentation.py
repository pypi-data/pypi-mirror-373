"""Tests for AI documentation generation."""

from unittest.mock import Mock, patch

from workflowforge.ai_documentation import (
    OllamaClient,
    _template_generate_readme,
    generate_workflow_readme,
)


class TestOllamaClient:
    """Test OllamaClient functionality."""

    def test_ollama_client_creation(self):
        """Test OllamaClient creation with defaults."""
        client = OllamaClient()
        assert client.base_url == "http://localhost:11434"
        assert client.model == "llama3.2"
        assert client.timeout == 30

    def test_ollama_client_custom_config(self):
        """Test OllamaClient with custom configuration."""
        client = OllamaClient(
            base_url="http://custom:8080", model="codellama", timeout=60
        )
        assert client.base_url == "http://custom:8080"
        assert client.model == "codellama"
        assert client.timeout == 60

    @patch("requests.get")
    def test_is_available_success(self, mock_get):
        """Test is_available when Ollama is running."""
        mock_get.return_value.status_code = 200

        client = OllamaClient()
        assert client.is_available() is True
        mock_get.assert_called_once_with("http://localhost:11434/api/tags", timeout=5)

    @patch("requests.get")
    def test_is_available_failure(self, mock_get):
        """Test is_available when Ollama is not running."""
        mock_get.side_effect = Exception("Connection failed")

        client = OllamaClient()
        assert client.is_available() is False

    @patch("workflowforge.ai_documentation.requests.post")
    @patch("workflowforge.ai_documentation.requests.get")
    def test_generate_success(self, mock_get, mock_post):
        """Test successful text generation."""
        # Mock is_available to return True
        mock_get.return_value.status_code = 200

        # Mock generate request
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "Generated text"}
        mock_post.return_value = mock_response

        client = OllamaClient()
        result = client.generate("Test prompt")

        assert result == "Generated text"
        mock_post.assert_called_once()

    @patch("workflowforge.ai_documentation.requests.post")
    @patch("workflowforge.ai_documentation.requests.get")
    def test_generate_failure(self, mock_get, mock_post):
        """Test failed text generation."""
        # Mock is_available to return True
        mock_get.return_value.status_code = 200

        # Mock generate request to fail
        mock_post.side_effect = Exception("Request failed")

        client = OllamaClient()
        result = client.generate("Test prompt")

        assert result is None


class TestDocumentationGeneration:
    """Test documentation generation functions."""

    def test_template_generate_readme_github(self):
        """Test template-based README generation for GitHub."""
        workflow_content = "name: Test\\non: push"
        result = _template_generate_readme(workflow_content, "github")

        assert "# GitHub Actions Workflow" in result
        assert "Generated with WorkflowForge" in result
        assert workflow_content in result

    def test_template_generate_readme_jenkins(self):
        """Test template-based README generation for Jenkins."""
        pipeline_content = "pipeline { agent any }"
        result = _template_generate_readme(pipeline_content, "jenkins")

        assert "# Jenkins Pipeline Workflow" in result
        assert "Generated with WorkflowForge" in result
        assert pipeline_content in result

    def test_template_generate_readme_codebuild(self):
        """Test template-based README generation for CodeBuild."""
        buildspec_content = "version: 0.2"
        result = _template_generate_readme(buildspec_content, "codebuild")

        assert "# AWS CodeBuild Workflow" in result
        assert "Generated with WorkflowForge" in result
        assert buildspec_content in result

    @patch("workflowforge.ai_documentation.OllamaClient")
    def test_generate_workflow_readme_with_ai(self, mock_client_class):
        """Test AI-powered README generation."""
        mock_client = Mock()
        mock_client.is_available.return_value = True
        mock_client.generate.return_value = "AI generated documentation"
        mock_client_class.return_value = mock_client

        result = generate_workflow_readme("test content", "github", use_ai=True)

        assert "AI generated documentation" in result
        assert "Documentation generated with WorkflowForge AI" in result

    @patch("workflowforge.ai_documentation.OllamaClient")
    def test_generate_workflow_readme_fallback(self, mock_client_class):
        """Test fallback to template when AI is not available."""
        mock_client = Mock()
        mock_client.is_available.return_value = False
        mock_client_class.return_value = mock_client

        result = generate_workflow_readme("test content", "github", use_ai=True)

        assert "# GitHub Actions Workflow" in result
        assert "Generated with WorkflowForge" in result

    def test_generate_workflow_readme_template_mode(self):
        """Test template mode (AI disabled)."""
        result = generate_workflow_readme("test content", "jenkins", use_ai=False)

        assert "# Jenkins Pipeline Workflow" in result
        assert "Generated with WorkflowForge" in result
