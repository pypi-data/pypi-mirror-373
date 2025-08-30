#!/usr/bin/env python3
"""
Python matrix testing with GitHub Actions using new modular imports.
"""

from workflowforge import github_actions


def main():
    # Create workflow
    workflow = github_actions.workflow(
        name="Python Matrix Testing",
        on=[
            github_actions.on_push(branches=["main"]),
            github_actions.on_pull_request(branches=["main"]),
        ],
    )

    # Create job with matrix strategy
    job = github_actions.job(
        runs_on="ubuntu-latest",
        strategy=github_actions.strategy(
            matrix=github_actions.matrix(
                python_version=["3.11", "3.12", "3.13"],
                os=["ubuntu-latest", "windows-latest"],
            )
        ),
    )

    # Add steps
    job.add_step(github_actions.action("actions/checkout@v4"))
    job.add_step(
        github_actions.action(
            "actions/setup-python@v5",
            with_={"python-version": "${{ matrix.python_version }}"},
        )
    )
    job.add_step(github_actions.run("pip install pytest"))
    job.add_step(github_actions.run("pytest tests/"))

    workflow.add_job("test", job)

    # Save workflow
    workflow.save("examples/github_actions/python_matrix.yml")
    print(
        "✅ Python matrix workflow created: examples/github_actions/python_matrix.yml"
    )


if __name__ == "__main__":
    main()
