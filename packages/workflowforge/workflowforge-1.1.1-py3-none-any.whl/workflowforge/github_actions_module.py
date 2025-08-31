"""
GitHub Actions module for WorkflowForge.

Provides all GitHub Actions specific functionality in a single namespace.
"""

from .job import Job
from .secrets import GitHubContext, Secret, Variable, github_context, secret, variable
from .step import ActionStep, RunStep, Step, action, run
from .strategy import Matrix, Strategy, matrix, strategy
from .triggers import (
    PullRequestTrigger,
    PushTrigger,
    ReleaseTrigger,
    ScheduleTrigger,
    WorkflowDispatchTrigger,
    on_pull_request,
    on_push,
    on_release,
    on_schedule,
    on_workflow_dispatch,
)
from .workflow import Workflow

# Aliases with snake_case naming
workflow = Workflow
job = Job
push_trigger = PushTrigger
pull_request_trigger = PullRequestTrigger
schedule_trigger = ScheduleTrigger
workflow_dispatch_trigger = WorkflowDispatchTrigger
release_trigger = ReleaseTrigger

__all__ = [
    "Workflow",
    "Job",
    "Step",
    "ActionStep",
    "RunStep",
    "PushTrigger",
    "PullRequestTrigger",
    "ScheduleTrigger",
    "WorkflowDispatchTrigger",
    "ReleaseTrigger",
    "Strategy",
    "Matrix",
    "Secret",
    "Variable",
    "GitHubContext",
    # Functions (snake_case)
    "workflow",
    "job",
    "action",
    "run",
    "on_push",
    "on_pull_request",
    "on_schedule",
    "on_workflow_dispatch",
    "on_release",
    "matrix",
    "strategy",
    "secret",
    "variable",
    "github_context",
    # Aliases (snake_case)
    "push_trigger",
    "pull_request_trigger",
    "schedule_trigger",
    "workflow_dispatch_trigger",
    "release_trigger",
]
