"""Step definitions for GitHub Actions jobs."""

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field


class Step(BaseModel, ABC):
    """Abstract base class for steps."""

    name: str | None = Field(None, description="Step name")
    id: str | None = Field(None, description="Unique step ID")
    if_condition: str | None = Field(
        None, alias="if", description="Condition to execute step"
    )
    continue_on_error: bool | None = Field(None, description="Continue on error")
    timeout_minutes: int | None = Field(None, description="Timeout in minutes")
    env: dict[str, Any] | None = Field(None, description="Step environment variables")

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """Convert step to dictionary for YAML."""


class ActionStep(Step):
    """Step that executes an action."""

    uses: str = Field(..., description="Action to use")
    with_params: dict[str, Any] | None = Field(None, description="Action parameters")

    def to_dict(self) -> dict[str, Any]:
        """Convert ActionStep to dictionary."""
        result: dict[str, Any] = {"uses": self.uses}

        if self.name:
            result["name"] = self.name
        if self.id:
            result["id"] = self.id
        if self.if_condition:
            result["if"] = self.if_condition
        if self.continue_on_error is not None:
            result["continue-on-error"] = self.continue_on_error
        if self.timeout_minutes:
            result["timeout-minutes"] = self.timeout_minutes
        if self.env:
            result["env"] = self.env
        if self.with_params:
            result["with"] = self.with_params

        return result


class RunStep(Step):
    """Step that executes shell commands."""

    run: str = Field(..., description="Command to execute")
    shell: str | None = Field(None, description="Shell to use")
    working_directory: str | None = Field(
        None, alias="working-directory", description="Working directory"
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert RunStep to dictionary."""
        result: dict[str, Any] = {"run": self.run}

        if self.name:
            result["name"] = self.name
        if self.id:
            result["id"] = self.id
        if self.if_condition:
            result["if"] = self.if_condition
        if self.continue_on_error is not None:
            result["continue-on-error"] = self.continue_on_error
        if self.timeout_minutes:
            result["timeout-minutes"] = self.timeout_minutes
        if self.env:
            result["env"] = self.env
        if self.shell:
            result["shell"] = self.shell
        if self.working_directory:
            result["working-directory"] = self.working_directory

        return result


# Factory functions for convenient step creation
def action(
    uses: str,
    name: str | None = None,
    with_: dict[str, Any] | None = None,
    **kwargs: Any,
) -> ActionStep:
    """Create an ActionStep conveniently."""
    with_params = with_ if with_ is not None else (kwargs if kwargs else None)
    return ActionStep(uses=uses, name=name, with_params=with_params)


def run(command: str, name: str | None = None, shell: str | None = None) -> RunStep:
    """Create a RunStep conveniently."""
    return RunStep(run=command, name=name, shell=shell)  # nosec B604
