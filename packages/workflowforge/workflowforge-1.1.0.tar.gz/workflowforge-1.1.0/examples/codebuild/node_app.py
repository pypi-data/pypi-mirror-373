#!/usr/bin/env python3
"""
Node.js application build with AWS CodeBuild using new modular imports.
"""

from workflowforge import aws_codebuild


def main():
    # Create BuildSpec using snake_case
    spec = aws_codebuild.buildspec()

    # Set environment
    env = aws_codebuild.environment()
    env.add_variable("NODE_ENV", "production")
    spec.set_env(env)

    # Install phase
    install_phase = aws_codebuild.phase()
    install_phase.add_command("npm install")
    spec.set_install_phase(install_phase)

    # Pre-build phase
    pre_build_phase = aws_codebuild.phase()
    pre_build_phase.add_command("npm run lint")
    pre_build_phase.add_command("npm test")
    spec.set_pre_build_phase(pre_build_phase)

    # Build phase
    build_phase = aws_codebuild.phase()
    build_phase.add_command("npm run build")
    spec.set_build_phase(build_phase)

    # Set artifacts
    artifacts_obj = aws_codebuild.artifacts(["dist/**/*"])
    spec.set_artifacts(artifacts_obj)

    # Save buildspec
    spec.save("examples/codebuild/buildspec.yml")
    print("✅ CodeBuild spec created: examples/codebuild/buildspec.yml")


if __name__ == "__main__":
    main()
