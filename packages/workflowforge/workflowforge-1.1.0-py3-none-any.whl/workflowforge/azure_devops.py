"""Azure DevOps Pipelines support for WorkflowForge.

Minimal, type-safe models to generate Azure Pipelines YAML for
Python CI matrices and common steps.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field
from ruamel.yaml import YAML

# ------------------------- Steps -------------------------


class ADOStep(BaseModel):
    """Abstract base for Azure Pipelines steps."""

    def to_dict(self) -> dict[str, Any]:  # pragma: no cover - implemented by subclasses
        raise NotImplementedError


class ADOTaskStep(ADOStep):
    """Represents a `- task:` step.

    Example:
    - task: UsePythonVersion@0
      inputs:
        versionSpec: '3.11'
      displayName: Use Python 3.11
    """

    task: str = Field(..., description="Task spec, e.g., UsePythonVersion@0")
    inputs: dict[str, Any] | None = Field(
        default=None, description="Task inputs under 'inputs' key"
    )
    displayName: str | None = Field(default=None, description="Friendly step name")

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"task": self.task}
        if self.inputs:
            result["inputs"] = self.inputs
        if self.displayName:
            result["displayName"] = self.displayName
        return result


class ADOScriptStep(ADOStep):
    """Represents a `- script:` step."""

    script: str = Field(..., description="Inline script to execute")
    displayName: str | None = Field(default=None, description="Friendly step name")

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"script": self.script}
        if self.displayName:
            result["displayName"] = self.displayName
        return result


def task(
    task_spec: str, inputs: dict[str, Any] | None = None, name: str | None = None
) -> ADOTaskStep:
    """Factory to create a task step."""
    return ADOTaskStep(task=task_spec, inputs=inputs, displayName=name)


def script(cmd: str, name: str | None = None) -> ADOScriptStep:
    """Factory to create a script step."""
    return ADOScriptStep(script=cmd, displayName=name)


# ------------------------- Job & Strategy -------------------------


class ADOStrategy(BaseModel):
    """Strategy with matrix support."""

    matrix: dict[str, dict[str, Any]] | None = Field(
        default=None, description="Matrix entries (name -> variables map)"
    )

    def to_dict(self) -> dict[str, Any]:
        return {"matrix": self.matrix} if self.matrix else {}


def strategy(matrix: dict[str, dict[str, Any]] | None = None) -> ADOStrategy:
    return ADOStrategy(matrix=matrix)


class ADOJob(BaseModel):
    """Represents a job entry with steps and optional matrix strategy."""

    name: str = Field(..., description="Job name identifier")
    vm_image: str = Field("ubuntu-latest", description="Microsoft-hosted image")
    strategy: ADOStrategy | None = Field(None, description="Job strategy")
    variables: dict[str, Any] | None = Field(
        default=None, description="Job-level variables"
    )
    steps: list[ADOStep] = Field(default_factory=list, description="Job steps")

    def add_step(self, step: ADOStep) -> ADOJob:
        self.steps.append(step)
        return self

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "job": self.name,
            "pool": {"vmImage": self.vm_image},
            "steps": [s.to_dict() for s in self.steps],
        }
        if self.variables:
            data["variables"] = self.variables
        if self.strategy:
            strat = self.strategy.to_dict()
            if strat:
                data["strategy"] = strat
        return data


def job(
    name: str,
    vm_image: str = "ubuntu-latest",
    strategy: ADOStrategy | None = None,
    variables: dict[str, Any] | None = None,
) -> ADOJob:
    return ADOJob(name=name, vm_image=vm_image, strategy=strategy, variables=variables)


# ------------------------- Pipeline -------------------------


class ADOPipeline(BaseModel):
    """Top-level Azure Pipelines YAML structure (minimal)."""

    name: str | None = Field(None, description="Pipeline name")
    trigger: list[str] | None = Field(
        default=None, description="CI trigger branches (shorthand list)"
    )
    pr: list[str] | None = Field(
        default=None, description="PR trigger branches (shorthand list)"
    )
    variables: dict[str, Any] | None = Field(
        default=None, description="Root variables map"
    )
    jobs: list[ADOJob] = Field(default_factory=list, description="Pipeline jobs")

    def add_job(self, j: ADOJob) -> ADOPipeline:
        self.jobs.append(j)
        return self

    def to_yaml(self) -> str:
        data: dict[str, Any] = {}
        if self.name:
            data["name"] = self.name
        if self.trigger is not None:
            data["trigger"] = self.trigger
        if self.pr is not None:
            data["pr"] = self.pr
        if self.variables:
            data["variables"] = self.variables
        data["jobs"] = [j.to_dict() for j in self.jobs]

        yaml = YAML()
        yaml.default_flow_style = False
        yaml.indent(mapping=2, sequence=4, offset=2)
        yaml.width = 120
        yaml.preserve_quotes = True

        from io import StringIO

        stream = StringIO()
        yaml.dump(data, stream)
        content = stream.getvalue()
        return f"# Do not modify - Generated with WorkflowForge\n{content}"

    def save(self, filepath: str = "azure-pipelines.yml") -> None:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(self.to_yaml())


def pipeline(
    name: str | None = None,
    trigger: list[str] | None = None,
    pr: list[str] | None = None,
    variables: dict[str, Any] | None = None,
) -> ADOPipeline:
    return ADOPipeline(name=name, trigger=trigger, pr=pr, variables=variables)


# ------------------------- Templates -------------------------


def python_ci_template_azure(
    python_versions: list[str] | None = None,
    branches: list[str] | None = None,
    os_list: list[str] | None = None,
    use_cache: bool = True,
) -> ADOPipeline:
    """Create a Python CI matrix pipeline for Azure Pipelines.

    - Uses UsePythonVersion@0 for each matrix entry
    - Installs dev dependencies and runs lint/type/tests similar to GitHub Actions
    """

    if python_versions is None:
        python_versions = ["3.11", "3.12", "3.13"]
    if branches is None:
        branches = ["main"]
    if os_list is None:
        os_list = ["ubuntu-latest", "windows-latest", "macOS-latest"]

    # Build matrix mapping: combine python + OS
    matrix_map: dict[str, dict[str, str]] = {}
    for v in python_versions:
        for os_name in os_list:
            key = f"Py{v.replace('.', '')}_{os_name.replace('-', '').replace('.', '')}"
            matrix_map[key] = {"python.version": v, "vmImage": os_name}

    pl = pipeline(name="Python CI", trigger=branches, pr=branches)

    test_job = job(
        name="Test",
        vm_image="$(vmImage)",
        strategy=strategy(matrix=matrix_map),
        variables=(
            {"PIP_CACHE_DIR": "$(Pipeline.Workspace)/.pip"} if use_cache else None
        ),
    )
    test_job.add_step(
        task(
            "UsePythonVersion@0",
            inputs={"versionSpec": "$(python.version)"},
            name="Use Python",
        )
    )
    if use_cache:
        test_job.add_step(
            task(
                "Cache@2",
                inputs={
                    "key": "pip | $(Agent.OS) | $(python.version) | pyproject.toml",
                    "restoreKeys": "pip | $(Agent.OS) | $(python.version)",
                    "path": "$(PIP_CACHE_DIR)",
                },
                name="Cache pip",
            )
        )
    test_job.add_step(script("python -m pip install --upgrade pip", name="Upgrade pip"))
    test_job.add_step(script("pip install -e .[dev]", name="Install deps"))
    test_job.add_step(script("black --check src/ tests/", name="Black"))
    test_job.add_step(script("isort --check-only src/ tests/", name="Isort"))
    test_job.add_step(script("flake8 src/ tests/ examples/", name="Flake8"))
    test_job.add_step(
        script("mypy --install-types --non-interactive src/", name="Mypy")
    )
    test_job.add_step(script("pytest -q", name="Pytest"))

    pl.add_job(test_job)
    return pl


# Public aliases to match library style
azure_pipeline = pipeline


def hello_world_template_azure(
    name: str = "Hello ADO",
    message: str = "Hello from WorkflowForge!",
    vm_image: str = "ubuntu-latest",
    branches: list[str] | None = None,
) -> ADOPipeline:
    """Create a minimal Azure Pipelines pipeline that prints a message.

    Args:
        name: Pipeline display name.
        message: Text to echo during the job.
        vm_image: Hosted image for the job.
        branches: CI trigger branches (default: ['main']).
    """
    if branches is None:
        branches = ["main"]

    pl = pipeline(name=name, trigger=branches, pr=branches)
    j = job(name="hello", vm_image=vm_image)
    j.add_step(script(f"echo {message}", name="Say hello"))
    pl.add_job(j)
    return pl
