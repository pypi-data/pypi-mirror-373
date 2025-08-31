"""
WorkflowForge - A robust and flexible library for creating CI/CD pipelines.

This library allows you to create GitHub Actions workflows, Jenkins pipelines,
and AWS CodeBuild BuildSpecs programmatically with type validation and autocompletion.
"""

# Platform-specific modules
from . import azure_devops as azure_devops
from . import codebuild as aws_codebuild
from . import github_actions_module as github_actions
from . import jenkins as jenkins_platform

__version__ = "1.1.1"
__all__ = [
    "github_actions",
    "jenkins_platform",
    "aws_codebuild",
    "azure_devops",
]
