#!/usr/bin/env python3
"""
Basic GitHub Actions CI pipeline using new modular imports.
"""

from workflowforge import github_actions


def main():
    # Create workflow using snake_case
    workflow = github_actions.workflow(
        name="Basic CI Pipeline", on=github_actions.on_push(branches=["main"])
    )

    # Create job
    job = github_actions.job(runs_on="ubuntu-latest")
    job.add_step(github_actions.action("actions/checkout@v4", name="Checkout code"))
    job.add_step(
        github_actions.run("echo 'Hello from WorkflowForge!'", name="Say hello")
    )

    # Add job to workflow
    workflow.add_job("test", job)

    # Save workflow
    workflow.save("examples/github_actions/basic_ci.yml")
    print("✅ GitHub Actions workflow created: examples/github_actions/basic_ci.yml")


if __name__ == "__main__":
    main()
