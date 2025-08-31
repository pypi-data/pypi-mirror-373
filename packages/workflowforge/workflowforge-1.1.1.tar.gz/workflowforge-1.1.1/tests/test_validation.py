"""Tests for validation utilities."""

from workflowforge.validation import validate_job_name, validate_secret_name


def test_validate_job_name():
    """Test job name validation."""
    assert validate_job_name("test")
    assert validate_job_name("test_job")
    assert validate_job_name("test-job")
    assert not validate_job_name("123test")
    assert not validate_job_name("test job")


def test_validate_secret_name():
    """Test secret name validation."""
    assert validate_secret_name("MY_SECRET")
    assert validate_secret_name("API_TOKEN")
    assert not validate_secret_name("my_secret")
    assert not validate_secret_name("123SECRET")


def test_validate_workflow_structure():
    """Test workflow structure validation."""
    from workflowforge.validation import validate_workflow_structure

    invalid_workflow = {"name": "test"}
    errors = validate_workflow_structure(invalid_workflow)
    assert len(errors) > 0
    assert any("must have an 'on' field" in error for error in errors)
