#!/usr/bin/env python3
"""
Maven build pipeline with Jenkins using new modular imports.
"""

from workflowforge import jenkins_platform


def main():
    # Create Jenkins pipeline using snake_case
    pipeline = jenkins_platform.pipeline()
    pipeline.set_agent(jenkins_platform.agent_docker("maven:3.9.3-eclipse-temurin-17"))

    # Build stage
    build_stage = jenkins_platform.stage("Build")
    build_stage.add_step("sh 'mvn clean compile'")
    pipeline.add_stage(build_stage)

    # Test stage
    test_stage = jenkins_platform.stage("Test")
    test_stage.add_step("sh 'mvn test'")
    pipeline.add_stage(test_stage)

    # Package stage
    package_stage = jenkins_platform.stage("Package")
    package_stage.add_step("sh 'mvn package'")
    pipeline.add_stage(package_stage)

    # Save pipeline
    pipeline.save("examples/jenkins/Jenkinsfile")
    print("✅ Jenkins pipeline created: examples/jenkins/Jenkinsfile")


if __name__ == "__main__":
    main()
