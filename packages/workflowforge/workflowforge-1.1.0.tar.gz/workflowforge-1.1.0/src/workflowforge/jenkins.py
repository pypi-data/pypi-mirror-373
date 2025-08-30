"""Jenkins pipeline generation for WorkflowForge."""

from typing import Any

from pydantic import BaseModel, Field


class JenkinsStage(BaseModel):
    """Represents a Jenkins pipeline stage."""

    name: str = Field(..., description="Stage name")
    steps: list[str] = Field(default_factory=list, description="Stage steps")
    when: str | None = Field(None, description="When condition")
    parallel: dict[str, "JenkinsStage"] | None = Field(
        None, description="Parallel stages"
    )

    def add_step(self, step: str) -> "JenkinsStage":
        """Add a step to the stage."""
        self.steps.append(step)
        return self

    def set_when(self, condition: str) -> "JenkinsStage":
        """Set when condition."""
        self.when = condition
        return self


class JenkinsAgent(BaseModel):
    """Represents Jenkins agent configuration."""

    label: str | None = Field(None, description="Agent label")
    docker: str | None = Field(None, description="Docker image")
    any: bool | None = Field(None, description="Any available agent")

    def to_dict(self) -> str | dict[str, Any]:
        """Convert to Jenkinsfile format."""
        if self.any:
            return "any"
        if self.docker:
            return {"docker": self.docker}
        if self.label:
            return {"label": self.label}
        return "any"


class JenkinsPipeline(BaseModel):
    """Represents a complete Jenkins pipeline."""

    agent: JenkinsAgent = Field(
        default_factory=lambda: JenkinsAgent(any=True), description="Pipeline agent"
    )
    stages: list[JenkinsStage] = Field(
        default_factory=list, description="Pipeline stages"
    )
    environment: dict[str, str] | None = Field(
        None, description="Environment variables"
    )
    tools: dict[str, str] | None = Field(None, description="Tools configuration")
    options: list[str] | None = Field(None, description="Pipeline options")
    triggers: list[str] | None = Field(None, description="Pipeline triggers")
    post: dict[str, list[str]] | None = Field(None, description="Post actions")
    libraries: list[str] | None = Field(None, description="Shared libraries")
    parameters: list[dict[str, Any]] | None = Field(
        None, description="Pipeline parameters"
    )
    description: str | None = Field(None, description="Pipeline description")

    def add_stage(self, stage: JenkinsStage) -> "JenkinsPipeline":
        """Add a stage to the pipeline."""
        self.stages.append(stage)
        return self

    def set_agent(self, agent: JenkinsAgent) -> "JenkinsPipeline":
        """Set pipeline agent."""
        self.agent = agent
        return self

    def set_env(self, key: str, value: str) -> "JenkinsPipeline":
        """Set environment variable."""
        if self.environment is None:
            self.environment = {}
        self.environment[key] = value
        return self

    def add_tool(self, name: str, version: str) -> "JenkinsPipeline":
        """Add tool configuration."""
        if self.tools is None:
            self.tools = {}
        self.tools[name] = version
        return self

    def add_library(self, library: str) -> "JenkinsPipeline":
        """Add shared library."""
        if self.libraries is None:
            self.libraries = []
        self.libraries.append(library)
        return self

    def add_parameter(
        self, param_type: str, name: str, **kwargs: Any
    ) -> "JenkinsPipeline":
        """Add pipeline parameter."""
        if self.parameters is None:
            self.parameters = []
        param = {"type": param_type, "name": name, **kwargs}
        self.parameters.append(param)
        return self

    def add_credential(self, id: str, description: str = "") -> "JenkinsPipeline":
        """Add credential parameter."""
        return self.add_parameter("credentials", id, description=description)

    def set_description(self, description: str) -> "JenkinsPipeline":
        """Set pipeline description."""
        forge_note = "Generated with WorkflowForge"
        if description:
            self.description = f"{description} - {forge_note}"
        else:
            self.description = forge_note
        return self

    def to_jenkinsfile(self) -> str:
        """Convert to Jenkinsfile format."""
        lines = []

        # WorkflowForge comment
        lines.append("// Do not modify - Generated with WorkflowForge")
        lines.append("")

        # Libraries (before pipeline block)
        if self.libraries:
            for library in self.libraries:
                lines.append(f"@Library('{library}') _")
            lines.append("")

        lines.append("pipeline {")

        # Description (if set)
        if self.description:
            lines.append(f"    description '{self.description}'")

        # Agent
        agent_config = self.agent.to_dict()
        if isinstance(agent_config, str):
            lines.append(f"    agent {agent_config}")
        else:
            lines.append("    agent {")
            for key, value in agent_config.items():
                lines.append(f"        {key} '{value}'")
            lines.append("    }")

        # Parameters
        if self.parameters:
            lines.append("    parameters {")
            for param in self.parameters:
                param_line = f"        {param['type']}("
                param_line += f"name: '{param['name']}'"
                for key, value in param.items():
                    if key not in ["type", "name"]:
                        if isinstance(value, str):
                            param_line += f", {key}: '{value}'"
                        else:
                            param_line += f", {key}: {value}"
                param_line += ")"
                lines.append(param_line)
            lines.append("    }")

        # Environment
        if self.environment:
            lines.append("    environment {")
            for key, value in self.environment.items():
                lines.append(f"        {key} = '{value}'")
            lines.append("    }")

        # Tools
        if self.tools:
            lines.append("    tools {")
            for name, version in self.tools.items():
                lines.append(f"        {name} '{version}'")
            lines.append("    }")

        # Options
        if self.options:
            lines.append("    options {")
            for option in self.options:
                lines.append(f"        {option}")
            lines.append("    }")

        # Triggers
        if self.triggers:
            lines.append("    triggers {")
            for trigger in self.triggers:
                lines.append(f"        {trigger}")
            lines.append("    }")

        # Stages
        lines.append("    stages {")
        for stage in self.stages:
            lines.extend(self._format_stage(stage, 2))
        lines.append("    }")

        # Post
        if self.post:
            lines.append("    post {")
            for condition, actions in self.post.items():
                lines.append(f"        {condition} {{")
                for action in actions:
                    lines.append(f"            {action}")
                lines.append("        }")
            lines.append("    }")

        lines.append("}")
        return "\n".join(lines) + "\n"

    def _format_stage(self, stage: JenkinsStage, indent: int) -> list[str]:
        """Format a stage for Jenkinsfile."""
        prefix = "    " * indent
        lines = [f"{prefix}stage('{stage.name}') {{"]

        if stage.when:
            lines.append(f"{prefix}    when {{ {stage.when} }}")

        if stage.parallel:
            lines.append(f"{prefix}    parallel {{")
            for name, parallel_stage in stage.parallel.items():
                lines.append(f"{prefix}        '{name}': {{")
                lines.append(f"{prefix}            steps {{")
                for step in parallel_stage.steps:
                    lines.append(f"{prefix}                {step}")
                lines.append(f"{prefix}            }}")
                lines.append(f"{prefix}        }}")
            lines.append(f"{prefix}    }}")
        else:
            lines.append(f"{prefix}    steps {{")
            for step in stage.steps:
                lines.append(f"{prefix}        {step}")
            lines.append(f"{prefix}    }}")

        lines.append(f"{prefix}}}")
        return lines

    def generate_readme(self, use_ai: bool = True, ai_model: str = "llama3.2") -> str:
        """Generate README documentation for this pipeline.

        Args:
            use_ai: Whether to use AI generation (requires Ollama)
            ai_model: AI model to use for generation

        Returns:
            Generated README content
        """
        from .ai_documentation import generate_workflow_readme

        return generate_workflow_readme(self.to_jenkinsfile(), "jenkins", use_ai)

    def generate_diagram(self, output_format: str = "png") -> str:
        """Generate visual diagram of this pipeline.

        Args:
            output_format: Output format (png, svg, pdf, dot)

        Returns:
            Path to generated diagram file
        """
        from .visualization import visualizer

        viz = visualizer(output_format=output_format)
        return viz.generate_jenkins_diagram(self)

    def save(
        self,
        filepath: str = "Jenkinsfile",
        generate_readme: bool = False,
        use_ai: bool = True,
        generate_diagram: bool = True,
    ) -> None:
        """Save pipeline to Jenkinsfile.

        Args:
            filepath: Path to save the Jenkinsfile (default: Jenkinsfile)
                     Note: Jenkins typically expects 'Jenkinsfile' (no extension)
            generate_readme: Whether to also generate a README file
            use_ai: Whether to use AI for README generation
            generate_diagram: Whether to generate visual diagram
        """
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(self.to_jenkinsfile())

        if generate_readme:
            readme_path = filepath.replace("Jenkinsfile", "Jenkinsfile_README.md")
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(self.generate_readme(use_ai=use_ai))

        if generate_diagram:
            diagram_path = self.generate_diagram()
            print(f"📊 Pipeline diagram saved: {diagram_path}")


# Factory functions
def agent_any() -> JenkinsAgent:
    """Create any agent."""
    return JenkinsAgent(any=True)


def agent_docker(image: str) -> JenkinsAgent:
    """Create docker agent."""
    return JenkinsAgent(docker=image)


def agent_label(label: str) -> JenkinsAgent:
    """Create label agent."""
    return JenkinsAgent(label=label)


def stage(name: str) -> JenkinsStage:
    """Create a stage."""
    return JenkinsStage(name=name)


def pipeline() -> JenkinsPipeline:
    """Create a pipeline."""
    return JenkinsPipeline()
