"""Pipeline visualization for WorkflowForge using Graphviz."""

import os
import tempfile
from typing import Any

from pydantic import BaseModel, Field


class PipelineVisualizer(BaseModel):
    """Generates visual diagrams of CI/CD pipelines."""

    output_format: str = Field(
        default="png", description="Output format (png, svg, pdf)"
    )
    theme: str = Field(default="default", description="Visual theme")

    def generate_github_diagram(self, workflow: Any) -> str:
        """Generate diagram for GitHub Actions workflow."""
        dot_content = self._create_github_dot(workflow)
        return self._render_diagram(dot_content, f"{workflow.name}_workflow")

    def generate_jenkins_diagram(self, pipeline: Any) -> str:
        """Generate diagram for Jenkins pipeline."""
        dot_content = self._create_jenkins_dot(pipeline)
        return self._render_diagram(dot_content, "jenkins_pipeline")

    def generate_codebuild_diagram(self, buildspec: Any) -> str:
        """Generate diagram for CodeBuild spec."""
        dot_content = self._create_codebuild_dot(buildspec)
        return self._render_diagram(dot_content, "codebuild_spec")

    def _create_github_dot(self, workflow: Any) -> str:
        """Create Graphviz DOT content for GitHub workflow."""
        dot = ["digraph GitHubWorkflow {"]
        dot.append("    rankdir=TB;")
        dot.append("    node [shape=box, style=rounded];")
        dot.append("    edge [color=blue];")

        # Triggers
        triggers = self._format_triggers(workflow.on)
        dot.append(
            f'    trigger [label="Triggers\\n{triggers}", '
            "shape=ellipse, color=green];"
        )

        # Jobs
        for job_name, job in workflow.jobs.items():
            steps_count = len(job.steps) if hasattr(job, "steps") else 0
            runs_on = getattr(job, "runs_on", "ubuntu-latest")

            label = f"{job_name}\\nRuns on: {runs_on}\\nSteps: {steps_count}"
            dot.append(f'    {job_name} [label="{label}"];')

            # Connect trigger to job
            dot.append(f"    trigger -> {job_name};")

            # Job dependencies
            if hasattr(job, "needs") and job.needs:
                needs = job.needs if isinstance(job.needs, list) else [job.needs]
                for need in needs:
                    dot.append(f"    {need} -> {job_name};")

        dot.append("}")
        return "\n".join(dot)

    def _create_jenkins_dot(self, pipeline: Any) -> str:
        """Create Graphviz DOT content for Jenkins pipeline."""
        dot = ["digraph JenkinsPipeline {"]
        dot.append("    rankdir=TB;")
        dot.append("    node [shape=box, style=rounded];")
        dot.append("    edge [color=orange];")

        # Agent
        agent_info = self._format_jenkins_agent(pipeline.agent)
        dot.append(
            f'    agent [label="Agent\\n{agent_info}", ' "shape=ellipse, color=blue];"
        )

        # Stages
        prev_stage = "agent"
        for i, stage in enumerate(pipeline.stages):
            stage_name = stage.name.replace(" ", "_").replace("-", "_")
            steps_count = len(stage.steps)

            label = f"{stage.name}\\nSteps: {steps_count}"
            dot.append(f'    {stage_name} [label="{label}"];')
            dot.append(f"    {prev_stage} -> {stage_name};")
            prev_stage = stage_name

        dot.append("}")
        return "\n".join(dot)

    def _create_codebuild_dot(self, buildspec: Any) -> str:
        """Create Graphviz DOT content for CodeBuild spec."""
        dot = ["digraph CodeBuildSpec {"]
        dot.append("    rankdir=TB;")
        dot.append("    node [shape=box, style=rounded];")
        dot.append("    edge [color=purple];")

        # Environment
        if buildspec.env:
            vars_count = len(buildspec.env.variables) if buildspec.env.variables else 0
            dot.append(
                f'    env [label="Environment\\nVariables: {vars_count}", '
                "shape=ellipse, color=green];"
            )
            prev_node = "env"
        else:
            prev_node = None

        # Phases
        phases = [
            ("install", buildspec.install),
            ("pre_build", buildspec.pre_build),
            ("build", buildspec.build),
            ("post_build", buildspec.post_build),
        ]

        for phase_name, phase in phases:
            if phase:
                commands_count = len(phase.commands) if phase.commands else 0
                phase_display = phase_name.replace("_", " ").title()
                label = f"{phase_display}\\nCommands: {commands_count}"
                dot.append(f'    {phase_name} [label="{label}"];')

                if prev_node:
                    dot.append(f"    {prev_node} -> {phase_name};")
                prev_node = phase_name

        # Artifacts
        if buildspec.artifacts:
            files_count = len(buildspec.artifacts.files)
            dot.append(
                f'    artifacts [label="Artifacts\\nFiles: {files_count}", '
                "shape=ellipse, color=red];"
            )
            if prev_node:
                dot.append(f"    {prev_node} -> artifacts;")

        dot.append("}")
        return "\n".join(dot)

    def _format_triggers(self, triggers: Any) -> str:
        """Format workflow triggers for display."""
        if isinstance(triggers, list):
            return "\\n".join([str(t) for t in triggers])
        return str(triggers)

    def _format_jenkins_agent(self, agent: Any) -> str:
        """Format Jenkins agent for display."""
        if hasattr(agent, "docker") and agent.docker:
            return f"Docker: {agent.docker}"
        elif hasattr(agent, "label") and agent.label:
            return f"Label: {agent.label}"
        return "Any"

    def _render_diagram(self, dot_content: str, filename: str) -> str:
        """Render DOT content to image file."""
        try:
            # Try using graphviz command
            import subprocess  # nosec B404

            # Create temp file for DOT content
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".dot", delete=False
            ) as f:
                f.write(dot_content)
                dot_file = f.name

            # Output file
            output_file = f"{filename}.{self.output_format}"

            # Render with graphviz
            result = subprocess.run(  # nosec B603 B607
                ["dot", f"-T{self.output_format}", dot_file, "-o", output_file],
                capture_output=True,
                text=True,
            )

            # Cleanup
            os.unlink(dot_file)

            if result.returncode == 0:
                return output_file
            else:
                # Fallback: save DOT file
                fallback_file = f"{filename}.dot"
                with open(fallback_file, "w") as f:
                    f.write(dot_content)
                return fallback_file

        except (ImportError, FileNotFoundError):
            # Fallback: save DOT file
            fallback_file = f"{filename}.dot"
            with open(fallback_file, "w") as f:
                f.write(dot_content)
            return fallback_file


# Factory function
def visualizer(output_format: str = "png") -> PipelineVisualizer:
    """Create a pipeline visualizer."""
    return PipelineVisualizer(output_format=output_format)
