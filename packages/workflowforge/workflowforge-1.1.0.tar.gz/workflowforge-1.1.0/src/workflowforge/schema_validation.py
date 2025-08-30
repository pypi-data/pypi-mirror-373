"""GitHub Actions schema validation."""

from typing import Any

from ruamel.yaml import YAML

# Simplified GitHub Actions schema validation
GITHUB_ACTIONS_SCHEMA = {
    "required_fields": ["name", "on", "jobs"],
    "valid_triggers": [
        "push",
        "pull_request",
        "release",
        "schedule",
        "workflow_dispatch",
        "workflow_call",
        "issues",
        "issue_comment",
        "create",
        "delete",
    ],
    "valid_job_fields": [
        "runs-on",
        "steps",
        "needs",
        "if",
        "strategy",
        "environment",
        "permissions",
        "outputs",
        "env",
        "defaults",
        "timeout-minutes",
    ],
    "valid_step_fields": [
        "name",
        "uses",
        "run",
        "with",
        "env",
        "if",
        "id",
        "continue-on-error",
    ],
}


def validate_github_actions_schema(workflow_dict: dict[str, Any]) -> list[str]:
    """Validate workflow against GitHub Actions schema."""
    errors = []

    # Check required fields
    for field in GITHUB_ACTIONS_SCHEMA["required_fields"]:
        if field not in workflow_dict:
            errors.append(f"Missing required field: {field}")

    # Validate triggers
    if "on" in workflow_dict:
        on_value = workflow_dict["on"]
        if isinstance(on_value, str):
            if on_value not in GITHUB_ACTIONS_SCHEMA["valid_triggers"]:
                errors.append(f"Invalid trigger: {on_value}")
        elif isinstance(on_value, dict):
            for trigger in on_value.keys():
                if trigger not in GITHUB_ACTIONS_SCHEMA["valid_triggers"]:
                    errors.append(f"Invalid trigger: {trigger}")

    # Validate jobs
    if "jobs" in workflow_dict:
        for job_name, job_config in workflow_dict["jobs"].items():
            if not isinstance(job_config, dict):
                errors.append(f"Job '{job_name}' must be an object")
                continue

            # Check required job fields
            if "runs-on" not in job_config:
                errors.append(f"Job '{job_name}' missing required 'runs-on' field")

            # Validate job fields
            for field in job_config.keys():
                if field not in GITHUB_ACTIONS_SCHEMA["valid_job_fields"]:
                    errors.append(f"Invalid job field in '{job_name}': {field}")

            # Validate steps
            if "steps" in job_config:
                for i, step in enumerate(job_config["steps"]):
                    if not isinstance(step, dict):
                        errors.append(f"Step {i} in job '{job_name}' must be an object")
                        continue

                    # Must have either 'uses' or 'run'
                    if "uses" not in step and "run" not in step:
                        errors.append(
                            f"Step {i} in job '{job_name}' must have "
                            "either 'uses' or 'run'"
                        )

                    # Validate step fields
                    for field in step.keys():
                        if field not in GITHUB_ACTIONS_SCHEMA["valid_step_fields"]:
                            errors.append(
                                f"Invalid step field in job '{job_name}', "
                                f"step {i}: {field}"
                            )

    return errors


def validate_yaml_syntax(yaml_content: str) -> list[str]:
    """Validate YAML syntax."""
    errors = []
    try:
        yaml = YAML(typ="safe")
        yaml.load(yaml_content)
    except Exception as e:
        errors.append(f"YAML syntax error: {str(e)}")
    return errors


def validate_workflow_yaml(yaml_content: str) -> list[str]:
    """Complete workflow validation."""
    errors = []

    # First validate YAML syntax
    yaml_errors = validate_yaml_syntax(yaml_content)
    if yaml_errors:
        return yaml_errors

    # Parse and validate structure
    try:
        yaml = YAML(typ="safe")
        workflow_dict = yaml.load(yaml_content)
        schema_errors = validate_github_actions_schema(workflow_dict)
        errors.extend(schema_errors)
    except Exception as e:
        errors.append(f"Validation error: {str(e)}")

    return errors
