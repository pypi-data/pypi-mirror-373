"""Validation utilities for WorkflowForge."""

import re
from typing import Any


def validate_job_name(name: str) -> bool:
    """Validate GitHub Actions job name."""
    return bool(re.match(r"^[a-zA-Z_][a-zA-Z0-9_-]*$", name))


def validate_step_name(name: str) -> bool:
    """Validate GitHub Actions step name."""
    return len(name) > 0 and len(name) <= 255


def validate_environment_name(name: str) -> bool:
    """Validate GitHub Actions environment name."""
    return bool(re.match(r"^[a-zA-Z0-9_-]+$", name))


def validate_secret_name(name: str) -> bool:
    """Validate GitHub Actions secret name."""
    return bool(re.match(r"^[A-Z][A-Z0-9_]*$", name))


def validate_cron_expression(cron: str) -> bool:
    """Basic validation for cron expressions."""
    parts = cron.split()
    if len(parts) != 5:
        return False

    # Basic pattern check (not comprehensive)
    cron_pattern = r"^[0-9*,-/]+\s+[0-9*,-/]+\s+[0-9*,-/]+\s+[0-9*,-/]+\s+[0-9*,-/]+$"
    return bool(re.match(cron_pattern, cron))


def validate_docker_image(image: str) -> bool:
    """Validate Docker image name format."""
    # Basic validation for Docker image names
    pattern = (
        r"^[a-z0-9]+(?:[._-][a-z0-9]+)*"
        r"(?:/[a-z0-9]+(?:[._-][a-z0-9]+)*)*"
        r"(?::[a-zA-Z0-9._-]+)?$"
    )
    return bool(re.match(pattern, image))


class ValidationError(Exception):
    """Raised when validation fails."""


def validate_workflow_structure(workflow_dict: dict[str, Any]) -> list[str]:
    """Validate workflow structure and return list of errors."""
    errors = []

    # Required fields
    if "name" not in workflow_dict:
        errors.append("Workflow must have a 'name' field")

    if "on" not in workflow_dict:
        errors.append("Workflow must have an 'on' field")

    if "jobs" not in workflow_dict:
        errors.append("Workflow must have a 'jobs' field")
    elif not workflow_dict["jobs"]:
        errors.append("Workflow must have at least one job")

    # Validate job names
    if "jobs" in workflow_dict:
        for job_name in workflow_dict["jobs"]:
            if not validate_job_name(job_name):
                errors.append(f"Invalid job name: '{job_name}'")

    return errors
