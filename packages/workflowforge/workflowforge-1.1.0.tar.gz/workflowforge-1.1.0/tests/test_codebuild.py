"""Tests for AWS CodeBuild BuildSpec generation."""

import yaml

from workflowforge.codebuild import BuildEnvironment, artifacts, buildspec, phase


def environment():
    """Helper function to create BuildEnvironment."""
    return BuildEnvironment()


def test_buildspec_creation():
    """Test basic BuildSpec creation."""
    spec = buildspec()
    assert spec.version == "0.2"


def test_buildspec_with_phases():
    """Test BuildSpec with phases."""
    spec = buildspec()
    build_phase = phase()
    build_phase.add_command("echo 'Building'")
    spec.set_build_phase(build_phase)

    yaml_output = spec.to_yaml()
    assert "# Do not modify - Generated with WorkflowForge" in yaml_output

    parsed = yaml.safe_load(yaml_output.split("\n", 1)[1])  # Skip comment
    assert "phases" in parsed
    assert "build" in parsed["phases"]
    assert "echo 'Building'" in parsed["phases"]["build"]["commands"]


def test_buildspec_environment():
    """Test BuildSpec environment variables."""
    spec = buildspec()
    env = environment()
    env.add_variable("NODE_ENV", "production")
    spec.set_env(env)

    yaml_output = spec.to_yaml()
    parsed = yaml.safe_load(yaml_output.split("\n", 1)[1])

    assert "env" in parsed
    assert "variables" in parsed["env"]
    assert parsed["env"]["variables"]["NODE_ENV"] == "production"


def test_buildspec_artifacts():
    """Test BuildSpec artifacts configuration."""
    spec = buildspec()
    arts = artifacts(["**/*"])
    arts.name = "my-artifacts"
    spec.set_artifacts(arts)

    yaml_output = spec.to_yaml()
    parsed = yaml.safe_load(yaml_output.split("\n", 1)[1])

    assert "artifacts" in parsed
    assert parsed["artifacts"]["files"] == ["**/*"]
    assert parsed["artifacts"]["name"] == "my-artifacts"
