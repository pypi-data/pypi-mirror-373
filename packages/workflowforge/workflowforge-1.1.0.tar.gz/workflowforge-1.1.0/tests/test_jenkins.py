"""Tests for Jenkins pipeline generation."""

from workflowforge.jenkins import agent_docker, pipeline, stage


def test_jenkins_pipeline_creation():
    """Test basic Jenkins pipeline creation."""
    jp = pipeline()
    assert len(jp.stages) == 0


def test_jenkins_pipeline_with_stages():
    """Test Jenkins pipeline with stages."""
    jp = pipeline()
    build_stage = stage("Build")
    build_stage.add_step("echo 'Building'")
    jp.add_stage(build_stage)

    jenkinsfile = jp.to_jenkinsfile()
    assert "// Do not modify - Generated with WorkflowForge" in jenkinsfile
    assert "stage('Build')" in jenkinsfile
    assert "echo 'Building'" in jenkinsfile


def test_jenkins_docker_agent():
    """Test Jenkins Docker agent."""
    jp = pipeline()
    jp.set_agent(agent_docker("maven:3.9.3"))

    jenkinsfile = jp.to_jenkinsfile()
    assert "docker 'maven:3.9.3'" in jenkinsfile


def test_jenkins_environment_variables():
    """Test Jenkins environment variables."""
    jp = pipeline()
    jp.set_env("JAVA_HOME", "/usr/lib/jvm/java-11")

    jenkinsfile = jp.to_jenkinsfile()
    assert "environment {" in jenkinsfile
    assert "JAVA_HOME = '/usr/lib/jvm/java-11'" in jenkinsfile


def test_jenkins_description():
    """Test Jenkins pipeline description."""
    jp = pipeline()
    jp.set_description("My Pipeline")

    jenkinsfile = jp.to_jenkinsfile()
    assert "description 'My Pipeline - Generated with WorkflowForge'" in jenkinsfile
