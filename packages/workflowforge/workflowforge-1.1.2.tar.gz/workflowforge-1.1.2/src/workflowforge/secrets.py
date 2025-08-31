"""Secrets and variables support for all platforms."""

from pydantic import BaseModel, Field


# GitHub Actions
class Secret(BaseModel):
    """Represents a GitHub Actions secret reference."""

    name: str = Field(..., description="Secret name")

    def __str__(self) -> str:
        return f"${{{{ secrets.{self.name} }}}}"


class Variable(BaseModel):
    """Represents a GitHub Actions variable reference."""

    name: str = Field(..., description="Variable name")

    def __str__(self) -> str:
        return f"${{{{ vars.{self.name} }}}}"


class GitHubContext(BaseModel):
    """Represents GitHub context variables."""

    @staticmethod
    def event_name() -> str:
        return "${{ github.event_name }}"

    @staticmethod
    def ref() -> str:
        return "${{ github.ref }}"

    @staticmethod
    def sha() -> str:
        return "${{ github.sha }}"

    @staticmethod
    def actor() -> str:
        return "${{ github.actor }}"

    @staticmethod
    def repository() -> str:
        return "${{ github.repository }}"


# Jenkins
class JenkinsCredential(BaseModel):
    """Represents a Jenkins credential reference."""

    id: str = Field(..., description="Credential ID")

    def __str__(self) -> str:
        return f"credentials('{self.id}')"


class JenkinsEnvVar(BaseModel):
    """Represents a Jenkins environment variable."""

    name: str = Field(..., description="Environment variable name")

    def __str__(self) -> str:
        return f"env.{self.name}"


class JenkinsParam(BaseModel):
    """Represents a Jenkins parameter."""

    name: str = Field(..., description="Parameter name")

    def __str__(self) -> str:
        return f"params.{self.name}"


# AWS CodeBuild
class CodeBuildSecret(BaseModel):
    """Represents an AWS CodeBuild secret from Secrets Manager."""

    name: str = Field(..., description="Secret name")

    def __str__(self) -> str:
        return f"${self.name}"


class CodeBuildParameter(BaseModel):
    """Represents an AWS CodeBuild parameter from Parameter Store."""

    name: str = Field(..., description="Parameter name")

    def __str__(self) -> str:
        return f"${self.name}"


class CodeBuildEnvVar(BaseModel):
    """Represents an AWS CodeBuild environment variable."""

    name: str = Field(..., description="Environment variable name")

    def __str__(self) -> str:
        return f"${self.name}"


# Factory functions
# GitHub Actions
def secret(name: str) -> str:
    """Create a GitHub Actions secret reference."""
    return str(Secret(name=name))


def variable(name: str) -> str:
    """Create a GitHub Actions variable reference."""
    return str(Variable(name=name))


def github_context() -> GitHubContext:
    """Get GitHub context helper."""
    return GitHubContext()


# Jenkins
def jenkins_credential(id: str) -> str:
    """Create a Jenkins credential reference."""
    return str(JenkinsCredential(id=id))


def jenkins_env(name: str) -> str:
    """Create a Jenkins environment variable reference."""
    return str(JenkinsEnvVar(name=name))


def jenkins_param(name: str) -> str:
    """Create a Jenkins parameter reference."""
    return str(JenkinsParam(name=name))


# AWS CodeBuild
def codebuild_secret(name: str) -> str:
    """Create a CodeBuild Secrets Manager reference."""
    return str(CodeBuildSecret(name=name))


def codebuild_parameter(name: str) -> str:
    """Create a CodeBuild Parameter Store reference."""
    return str(CodeBuildParameter(name=name))


def codebuild_env(name: str) -> str:
    """Create a CodeBuild environment variable reference."""
    return str(CodeBuildEnvVar(name=name))
