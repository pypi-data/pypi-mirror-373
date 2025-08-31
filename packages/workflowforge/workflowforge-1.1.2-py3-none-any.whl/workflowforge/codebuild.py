"""AWS CodeBuild BuildSpec generation for WorkflowForge."""

from typing import Any

from pydantic import BaseModel, Field
from ruamel.yaml import YAML


class BuildPhase(BaseModel):
    """Represents a CodeBuild phase."""

    run_as: str | None = Field(None, description="Linux user to run commands")
    on_failure: str | None = Field(None, description="Action on failure")
    runtime_versions: dict[str, str] | None = Field(
        None, description="Runtime versions"
    )
    commands: list[str] = Field(default_factory=list, description="Commands to execute")
    finally_commands: list[str] | None = Field(None, description="Finally commands")

    def add_command(self, command: str) -> "BuildPhase":
        """Add a command to the phase."""
        self.commands.append(command)
        return self

    def add_runtime(self, runtime: str, version: str) -> "BuildPhase":
        """Add runtime version."""
        if self.runtime_versions is None:
            self.runtime_versions = {}
        self.runtime_versions[runtime] = version
        return self

    def set_on_failure(self, action: str) -> "BuildPhase":
        """Set on-failure action."""
        self.on_failure = action
        return self


class BuildEnvironment(BaseModel):
    """Represents CodeBuild environment configuration."""

    shell: str | None = Field(None, description="Shell to use")
    variables: dict[str, str] | None = Field(None, description="Environment variables")
    parameter_store: dict[str, str] | None = Field(
        None, description="Parameter Store variables"
    )
    secrets_manager: dict[str, str] | None = Field(
        None, description="Secrets Manager variables"
    )
    exported_variables: list[str] | None = Field(None, description="Exported variables")
    git_credential_helper: bool | None = Field(
        None, description="Git credential helper"
    )

    def add_variable(self, key: str, value: str) -> "BuildEnvironment":
        """Add environment variable."""
        if self.variables is None:
            self.variables = {}
        self.variables[key] = value
        return self

    def add_parameter_store(self, key: str, parameter: str) -> "BuildEnvironment":
        """Add Parameter Store variable."""
        if self.parameter_store is None:
            self.parameter_store = {}
        self.parameter_store[key] = parameter
        return self

    def add_secret(self, key: str, secret: str) -> "BuildEnvironment":
        """Add Secrets Manager variable."""
        if self.secrets_manager is None:
            self.secrets_manager = {}
        self.secrets_manager[key] = secret
        return self


class BuildArtifacts(BaseModel):
    """Represents CodeBuild artifacts configuration."""

    files: list[str] = Field(..., description="Files to include")
    name: str | None = Field(None, description="Artifact name")
    discard_paths: bool | None = Field(None, description="Discard paths")
    base_directory: str | None = Field(None, description="Base directory")
    exclude_paths: list[str] | None = Field(None, description="Paths to exclude")
    enable_symlinks: bool | None = Field(None, description="Enable symlinks")
    s3_prefix: str | None = Field(None, description="S3 prefix")

    def add_file(self, file_pattern: str) -> "BuildArtifacts":
        """Add file pattern."""
        self.files.append(file_pattern)
        return self


class BuildCache(BaseModel):
    """Represents CodeBuild cache configuration."""

    key: str | None = Field(None, description="Cache key")
    fallback_keys: list[str] | None = Field(None, description="Fallback keys")
    action: str | None = Field(None, description="Cache action")
    paths: list[str] = Field(default_factory=list, description="Paths to cache")

    def add_path(self, path: str) -> "BuildCache":
        """Add cache path."""
        self.paths.append(path)
        return self


class BuildSpec(BaseModel):
    """Represents a complete AWS CodeBuild BuildSpec."""

    version: str = Field(default="0.2", description="BuildSpec version")
    run_as: str | None = Field(None, description="Global run-as user")
    env: BuildEnvironment | None = Field(None, description="Environment configuration")
    install: BuildPhase | None = Field(None, description="Install phase")
    pre_build: BuildPhase | None = Field(None, description="Pre-build phase")
    build: BuildPhase | None = Field(None, description="Build phase")
    post_build: BuildPhase | None = Field(None, description="Post-build phase")
    artifacts: BuildArtifacts | None = Field(
        None, description="Artifacts configuration"
    )
    cache: BuildCache | None = Field(None, description="Cache configuration")
    reports: dict[str, dict[str, Any]] | None = Field(
        None, description="Reports configuration"
    )

    def set_env(self, env: BuildEnvironment) -> "BuildSpec":
        """Set environment configuration."""
        self.env = env
        return self

    def set_install_phase(self, phase: BuildPhase) -> "BuildSpec":
        """Set install phase."""
        self.install = phase
        return self

    def set_pre_build_phase(self, phase: BuildPhase) -> "BuildSpec":
        """Set pre-build phase."""
        self.pre_build = phase
        return self

    def set_build_phase(self, phase: BuildPhase) -> "BuildSpec":
        """Set build phase."""
        self.build = phase
        return self

    def set_post_build_phase(self, phase: BuildPhase) -> "BuildSpec":
        """Set post-build phase."""
        self.post_build = phase
        return self

    def set_artifacts(self, artifacts: BuildArtifacts) -> "BuildSpec":
        """Set artifacts configuration."""
        self.artifacts = artifacts
        return self

    def set_cache(self, cache: BuildCache) -> "BuildSpec":
        """Set cache configuration."""
        self.cache = cache
        return self

    def to_yaml(self) -> str:
        """Convert to BuildSpec YAML format."""
        data: dict[str, Any] = {"version": self.version}

        if self.run_as:
            data["run-as"] = self.run_as

        # Environment
        if self.env:
            env_data: dict[str, Any] = {}
            if self.env.shell:
                env_data["shell"] = self.env.shell
            if self.env.variables:
                env_data["variables"] = self.env.variables
            if self.env.parameter_store:
                env_data["parameter-store"] = self.env.parameter_store
            if self.env.secrets_manager:
                env_data["secrets-manager"] = self.env.secrets_manager
            if self.env.exported_variables:
                env_data["exported-variables"] = self.env.exported_variables
            if self.env.git_credential_helper is not None:
                env_data["git-credential-helper"] = (
                    "yes" if self.env.git_credential_helper else "no"
                )
            if env_data:
                data["env"] = env_data

        # Phases
        phases: dict[str, Any] = {}
        for phase_name, phase in [
            ("install", self.install),
            ("pre_build", self.pre_build),
            ("build", self.build),
            ("post_build", self.post_build),
        ]:
            if phase:
                phase_data: dict[str, Any] = {}
                if phase.run_as:
                    phase_data["run-as"] = phase.run_as
                if phase.on_failure:
                    phase_data["on-failure"] = phase.on_failure
                if phase.runtime_versions:
                    phase_data["runtime-versions"] = phase.runtime_versions
                if phase.commands:
                    phase_data["commands"] = phase.commands
                if phase.finally_commands:
                    phase_data["finally"] = phase.finally_commands
                if phase_data:
                    phases[phase_name] = phase_data

        if phases:
            data["phases"] = phases

        # Artifacts
        if self.artifacts:
            artifacts_data: dict[str, Any] = {"files": self.artifacts.files}
            if self.artifacts.name:
                artifacts_data["name"] = self.artifacts.name
            if self.artifacts.discard_paths is not None:
                artifacts_data["discard-paths"] = (
                    "yes" if self.artifacts.discard_paths else "no"
                )
            if self.artifacts.base_directory:
                artifacts_data["base-directory"] = self.artifacts.base_directory
            if self.artifacts.exclude_paths:
                artifacts_data["exclude-paths"] = self.artifacts.exclude_paths
            if self.artifacts.enable_symlinks is not None:
                artifacts_data["enable-symlinks"] = (
                    "yes" if self.artifacts.enable_symlinks else "no"
                )
            if self.artifacts.s3_prefix:
                artifacts_data["s3-prefix"] = self.artifacts.s3_prefix
            data["artifacts"] = artifacts_data

        # Cache
        if self.cache:
            cache_data: dict[str, Any] = {}
            if self.cache.key:
                cache_data["key"] = self.cache.key
            if self.cache.fallback_keys:
                cache_data["fallback-keys"] = self.cache.fallback_keys
            if self.cache.action:
                cache_data["action"] = self.cache.action
            if self.cache.paths:
                cache_data["paths"] = self.cache.paths
            if cache_data:
                data["cache"] = cache_data

        # Reports
        if self.reports:
            data["reports"] = self.reports

        yaml = YAML()
        yaml.default_flow_style = False
        yaml.indent(mapping=2, sequence=4, offset=2)
        yaml.width = 120
        yaml.preserve_quotes = True

        from io import StringIO

        stream = StringIO()
        yaml.dump(data, stream)
        yaml_content = stream.getvalue()

        return f"# Do not modify - Generated with WorkflowForge\n{yaml_content}"

    def generate_readme(self, use_ai: bool = True, ai_model: str = "llama3.2") -> str:
        """Generate README documentation for this BuildSpec.

        Args:
            use_ai: Whether to use AI generation (requires Ollama)
            ai_model: AI model to use for generation

        Returns:
            Generated README content
        """
        from .ai_documentation import generate_workflow_readme

        return generate_workflow_readme(self.to_yaml(), "codebuild", use_ai)

    def generate_diagram(self, output_format: str = "png") -> str:
        """Generate visual diagram of this BuildSpec.

        Args:
            output_format: Output format (png, svg, pdf, dot)

        Returns:
            Path to generated diagram file
        """
        from .visualization import visualizer

        viz = visualizer(output_format=output_format)
        return viz.generate_codebuild_diagram(self)

    def save(
        self,
        filepath: str = "buildspec.yml",
        generate_readme: bool = False,
        use_ai: bool = True,
        generate_diagram: bool = True,
    ) -> None:
        """Save BuildSpec to file.

        Args:
            filepath: Path to save the buildspec YAML (default: buildspec.yml)
                     Can be customized (e.g., buildspec_debug.yml, config/buildspec.yml)
            generate_readme: Whether to also generate a README file
            use_ai: Whether to use AI for README generation
            generate_diagram: Whether to generate visual diagram
        """
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(self.to_yaml())

        if generate_readme:
            readme_path = filepath.replace(".yml", "_README.md").replace(
                ".yaml", "_README.md"
            )
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(self.generate_readme(use_ai=use_ai))

        if generate_diagram:
            diagram_path = self.generate_diagram()
            print(f"📊 BuildSpec diagram saved: {diagram_path}")


# Factory functions
def buildspec() -> BuildSpec:
    """Create a new BuildSpec."""
    return BuildSpec()


def phase() -> BuildPhase:
    """Create a new BuildPhase."""
    return BuildPhase()


def environment() -> BuildEnvironment:
    """Create a new BuildEnvironment."""
    return BuildEnvironment()


def artifacts(files: list[str]) -> BuildArtifacts:
    """Create BuildArtifacts."""
    return BuildArtifacts(files=files)


def cache(paths: list[str]) -> BuildCache:
    """Create BuildCache."""
    return BuildCache(paths=paths)
