"""AI-powered documentation generation for WorkflowForge."""

import requests
from pydantic import BaseModel, Field


class OllamaClient(BaseModel):
    """Client for interacting with Ollama local LLM."""

    base_url: str = Field(
        default="http://localhost:11434", description="Ollama server URL"
    )
    model: str = Field(default="llama3.2", description="Model to use")
    timeout: int = Field(default=30, description="Request timeout in seconds")

    def is_available(self) -> bool:
        """Check if Ollama is running and accessible."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return bool(response.status_code == 200)
        except Exception:
            return False

    def generate(self, prompt: str) -> str | None:
        """Generate text using Ollama."""
        if not self.is_available():
            return None

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=self.timeout,
            )

            if response.status_code == 200:
                result = response.json().get("response", "")
                return result.strip() if isinstance(result, str) else None
            return None
        except Exception:
            return None


def generate_workflow_readme(
    workflow_content: str, platform: str = "github", use_ai: bool = True
) -> str:
    """Generate README documentation for a workflow.

    Args:
        workflow_content: The YAML/Jenkinsfile content
        platform: Platform type (github, jenkins, codebuild)
        use_ai: Whether to use AI generation (requires Ollama)

    Returns:
        Generated README content
    """
    if use_ai:
        return _ai_generate_readme(workflow_content, platform)
    else:
        return _template_generate_readme(workflow_content, platform)


def _ai_generate_readme(workflow_content: str, platform: str) -> str:
    """Generate README using Ollama AI."""
    client = OllamaClient()

    if not client.is_available():
        return _template_generate_readme(workflow_content, platform)

    prompt = f"""
Analyze this {platform.upper()} CI/CD workflow and generate a comprehensive README.md.

Workflow content:
```
{workflow_content}
```

Please provide:
1. Brief description of what this workflow does
2. Triggers (when it runs)
3. Jobs/stages breakdown with explanations
4. Required secrets/variables/credentials
5. Prerequisites and setup instructions
6. Expected outputs/artifacts

Format as proper markdown with clear sections and code blocks where appropriate.
Keep it concise but informative for developers.
"""

    ai_response = client.generate(prompt)

    if ai_response:
        return (
            f"# Workflow Documentation\n\n{ai_response}\n\n---\n"
            "*Documentation generated with WorkflowForge AI*"
        )
    else:
        return _template_generate_readme(workflow_content, platform)


def _template_generate_readme(workflow_content: str, platform: str) -> str:
    """Generate basic README using templates."""
    platform_name = {
        "github": "GitHub Actions",
        "jenkins": "Jenkins Pipeline",
        "codebuild": "AWS CodeBuild",
    }.get(platform, platform.title())

    return f"""# {platform_name} Workflow

## Overview
This {platform_name} workflow was generated using WorkflowForge.

## Workflow Content
```yaml
{workflow_content}
```

## Setup Instructions
1. Review the workflow configuration above
2. Configure required secrets/variables in your {platform_name} settings
3. Ensure all dependencies and permissions are properly set
4. Test the workflow in a development environment first

## Maintenance
- Review and update dependencies regularly
- Monitor workflow execution and performance
- Update documentation when making changes

---
*Generated with WorkflowForge*
"""


# Factory function
def ai_documentation_client(model: str = "llama3.2") -> OllamaClient:
    """Create an Ollama client for AI documentation generation."""
    return OllamaClient(model=model)
