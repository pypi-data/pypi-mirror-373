"""GitHub Actions workflow trigger definitions."""

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field


class Trigger(BaseModel, ABC):
    """Abstract base class for triggers."""

    @abstractmethod
    def to_dict(self) -> str | dict[str, Any]:
        """Convert trigger to YAML format."""


class PushTrigger(Trigger):
    """Trigger for push events."""

    branches: list[str] | None = Field(None, description="Branches that trigger")
    branches_ignore: list[str] | None = Field(None, description="Branches to ignore")
    tags: list[str] | None = Field(None, description="Tags that trigger")
    tags_ignore: list[str] | None = Field(None, description="Tags to ignore")
    paths: list[str] | None = Field(None, description="Paths that trigger")
    paths_ignore: list[str] | None = Field(None, description="Paths to ignore")

    def to_dict(self) -> str | dict[str, Any]:
        """Convert to dictionary."""
        result = {}
        if self.branches:
            result["branches"] = self.branches
        if self.branches_ignore:
            result["branches-ignore"] = self.branches_ignore
        if self.tags:
            result["tags"] = self.tags
        if self.tags_ignore:
            result["tags-ignore"] = self.tags_ignore
        if self.paths:
            result["paths"] = self.paths
        if self.paths_ignore:
            result["paths-ignore"] = self.paths_ignore

        return {"push": result} if result else "push"


class PullRequestTrigger(Trigger):
    """Trigger for pull request events."""

    types: list[str] | None = Field(None, description="PR event types")
    branches: list[str] | None = Field(None, description="Target branches")
    branches_ignore: list[str] | None = Field(None, description="Branches to ignore")
    paths: list[str] | None = Field(None, description="Paths that trigger")
    paths_ignore: list[str] | None = Field(None, description="Paths to ignore")

    def to_dict(self) -> str | dict[str, Any]:
        """Convert to dictionary."""
        result = {}
        if self.types:
            result["types"] = self.types
        if self.branches:
            result["branches"] = self.branches
        if self.branches_ignore:
            result["branches-ignore"] = self.branches_ignore
        if self.paths:
            result["paths"] = self.paths
        if self.paths_ignore:
            result["paths-ignore"] = self.paths_ignore

        return {"pull_request": result} if result else "pull_request"


class ScheduleTrigger(Trigger):
    """Trigger for scheduled events (cron)."""

    cron: str = Field(..., description="Cron expression")

    def to_dict(self) -> str | dict[str, Any]:
        """Convert to dictionary."""
        return {"schedule": [{"cron": self.cron}]}


class WorkflowDispatchTrigger(Trigger):
    """Trigger for manual execution."""

    inputs: dict[str, dict[str, Any]] | None = Field(
        None, description="Workflow inputs"
    )

    def to_dict(self) -> str | dict[str, Any]:
        """Convert to dictionary."""
        result = {}
        if self.inputs:
            result["inputs"] = self.inputs
        return {"workflow_dispatch": result} if result else "workflow_dispatch"


class ReleaseTrigger(Trigger):
    """Trigger for release events."""

    types: list[str] | None = Field(None, description="Release event types")

    def to_dict(self) -> str | dict[str, Any]:
        """Convert to dictionary."""
        result = {}
        if self.types:
            result["types"] = self.types
        return {"release": result} if result else "release"


# Factory functions for convenient trigger creation
def on_push(
    branches: list[str] | None = None, paths: list[str] | None = None
) -> PushTrigger:
    """Create a PushTrigger conveniently."""
    return PushTrigger(branches=branches, paths=paths)


def on_pull_request(
    branches: list[str] | None = None, types: list[str] | None = None
) -> PullRequestTrigger:
    """Create a PullRequestTrigger conveniently."""
    return PullRequestTrigger(branches=branches, types=types)


def on_schedule(cron: str) -> ScheduleTrigger:
    """Create a ScheduleTrigger conveniently."""
    return ScheduleTrigger(cron=cron)


def on_workflow_dispatch(
    inputs: dict[str, dict[str, Any]] | None = None,
) -> WorkflowDispatchTrigger:
    """Create a WorkflowDispatchTrigger conveniently."""
    return WorkflowDispatchTrigger(inputs=inputs)


def on_release(types: list[str] | None = None) -> ReleaseTrigger:
    """Create a ReleaseTrigger conveniently."""
    return ReleaseTrigger(types=types)
