"""Predefined templates for common workflows."""

from .job import Job
from .secrets import secret
from .step import action, run
from .strategy import matrix, strategy
from .triggers import on_pull_request, on_push, on_release
from .workflow import Workflow


def python_ci_template(
    name: str = "Python CI",
    python_versions: list[str] = ["3.11", "3.12", "3.13"],
    branches: list[str] = ["main"],
) -> Workflow:
    """Template for Python CI workflow."""
    workflow = Workflow(
        name=name, on=[on_push(branches=branches), on_pull_request(branches=branches)]
    )

    # Test job with matrix
    test_job = Job(
        runs_on="ubuntu-latest",
        strategy=strategy(matrix=matrix(python_version=python_versions)),
    )

    test_job.add_step(action("actions/checkout@v4", name="Checkout code"))
    test_job.add_step(
        action(
            "actions/setup-python@v5",
            name="Set up Python ${{ matrix.python_version }}",
            with_={"python-version": "${{ matrix.python_version }}"},
        )
    )
    test_job.add_step(run("pip install -e .[dev]", name="Install dependencies"))
    test_job.add_step(run("pytest", name="Run tests"))

    workflow.add_job("test", test_job)
    return workflow


def docker_build_template(
    name: str = "Docker Build",
    image_name: str = "my-app",
    dockerfile_path: str = "Dockerfile",
) -> Workflow:
    """Template for Docker build workflow."""
    workflow = Workflow(name=name, on=[on_push(), on_pull_request()])

    build_job = Job(runs_on="ubuntu-latest")
    build_job.add_step(action("actions/checkout@v4", name="Checkout code"))
    build_job.add_step(
        action("docker/setup-buildx-action@v3", name="Set up Docker Buildx")
    )
    build_job.add_step(
        action(
            "docker/login-action@v3",
            name="Login to Docker Hub",
            with_={
                "username": "${{ secrets.DOCKER_USERNAME }}",
                "password": secret("DOCKER_PASSWORD"),
            },
        )
    )
    build_job.add_step(
        action(
            "docker/build-push-action@v5",
            name="Build and push",
            with_={
                "context": ".",
                "file": dockerfile_path,
                "push": "true",
                "tags": f"{image_name}:latest",
            },
        )
    )

    workflow.add_job("build", build_job)
    return workflow


def node_ci_template(
    name: str = "Node.js CI",
    node_versions: list[str] = ["18", "20"],
    package_manager: str = "npm",
) -> Workflow:
    """Template for Node.js CI workflow."""
    workflow = Workflow(name=name, on=[on_push(), on_pull_request()])

    test_job = Job(
        runs_on="ubuntu-latest",
        strategy=strategy(matrix=matrix(node_version=node_versions)),
    )

    test_job.add_step(action("actions/checkout@v4", name="Checkout code"))
    test_job.add_step(
        action(
            "actions/setup-node@v4",
            name="Setup Node.js ${{ matrix.node_version }}",
            with_={
                "node-version": "${{ matrix.node_version }}",
                "cache": package_manager,
            },
        )
    )

    if package_manager == "npm":
        test_job.add_step(run("npm ci", name="Install dependencies"))
        test_job.add_step(run("npm test", name="Run tests"))
    elif package_manager == "yarn":
        test_job.add_step(
            run("yarn install --frozen-lockfile", name="Install dependencies")
        )
        test_job.add_step(run("yarn test", name="Run tests"))

    workflow.add_job("test", test_job)
    return workflow


def release_template(
    name: str = "Release",
    build_command: str = "python -m build",
    test_command: str | None = "pytest",
) -> Workflow:
    """Template for release workflow with PyPI publishing."""
    workflow = Workflow(name=name, on=[on_release(types=["published"])])

    # Test job
    if test_command:
        test_job = Job(runs_on="ubuntu-latest")
        test_job.add_step(action("actions/checkout@v4", name="Checkout code"))
        test_job.add_step(action("actions/setup-python@v5", name="Setup Python"))
        test_job.add_step(run("pip install -e .[dev]", name="Install dependencies"))
        test_job.add_step(run(test_command, name="Run tests"))
        workflow.add_job("test", test_job)

    # Build job
    build_job = Job(runs_on="ubuntu-latest")
    if test_command:
        build_job.set_needs("test")

    build_job.add_step(action("actions/checkout@v4", name="Checkout code"))
    build_job.add_step(action("actions/setup-python@v5", name="Setup Python"))
    build_job.add_step(run("pip install build", name="Install build tools"))
    build_job.add_step(run(build_command, name="Build package"))
    build_job.add_step(
        action(
            "actions/upload-artifact@v4",
            name="Upload artifacts",
            with_={"name": "dist", "path": "dist/"},
        )
    )

    # Publish job
    from .environment import environment

    publish_job = Job(
        runs_on="ubuntu-latest",
        environment=environment("pypi", "https://pypi.org/p/<package-name>"),
        permissions={"id-token": "write"},
    )
    publish_job.set_needs("build")

    publish_job.add_step(
        action(
            "actions/download-artifact@v4",
            name="Download artifacts",
            with_={"name": "dist", "path": "dist/"},
        )
    )
    publish_job.add_step(
        action("pypa/gh-action-pypi-publish@release/v1", name="Publish to PyPI")
    )

    workflow.add_job("build", build_job)
    workflow.add_job("publish", publish_job)
    return workflow
