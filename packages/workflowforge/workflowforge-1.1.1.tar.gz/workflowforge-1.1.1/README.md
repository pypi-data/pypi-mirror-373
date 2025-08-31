# WorkflowForge 🔨

## 📊 Project Status

[![License: MIT][license-badge]][license-url]
[![PyPI version][pypi-badge]][pypi-url]
[![Test PyPI][testpypi-badge]][testpypi-url]
[![Python Versions][python-versions-badge]][python-versions-url]
[![Tests][tests-badge]][tests-url]
[![pre-commit.ci status][precommit-badge]][precommit-url]
[![Ruff][ruff-badge]][ruff-url]
[![Security][security-badge]][security-url]
[![Maintained by Brainy Nimbus][maintained-badge]][maintained-url]

A robust and flexible library for creating GitHub Actions workflows, Azure DevOps pipelines, Jenkins pipelines, and AWS CodeBuild BuildSpecs programmatically in Python.

## ✨ Features

- **Intuitive API**: Fluent and easy-to-use syntax
- **Type Validation**: Built on Pydantic for automatic validation
- **IDE Support**: Full autocompletion with type hints
- **Type Safety**: Complete mypy compliance with strict type checking
- **Multi-Platform**: GitHub Actions, Azure DevOps, Jenkins, AWS CodeBuild
- **Pipeline Visualization**: Automatic diagram generation with Graphviz
- **Secrets Support**: Secure credential handling across all platforms
- **Templates**: Pre-built workflows for common use cases
- **Validation**: Schema validation and best practices checking
- **Optional Security Scan**: On-demand Checkov scan for generated workflows (GitHub Actions and Azure)
- **Optional AI Documentation**: AI-powered README generation with OllamaPipelines)

## 🚀 Installation

```bash
pip install workflowforge
```

## 📚 Examples

Check out the `examples/` directory for complete working examples:

```bash

# Run individual examples
python examples/github_actions/basic_ci.py
python examples/jenkins/maven_build.py
python examples/codebuild/node_app.py
python examples/azure_devops/hello_world.py
python examples/azure_devops/python_ci.py
```

This will generate actual pipeline files and diagrams using the new import structure.

## 🤖 AI Documentation (Optional)

WorkflowForge can automatically generate comprehensive README documentation for your workflows using **Ollama** (free local AI):

```bash
# Install Ollama (one-time setup)
curl -fsSL https://ollama.com/install.sh | sh
ollama serve
ollama pull llama3.2
```

```python
# Generate workflow with AI documentation and diagram
workflow.save(".github/workflows/ci.yml", generate_readme=True, use_ai=True, generate_diagram=True)
# Creates: ci.yml + ci_README.md + CI_Pipeline_workflow.png

# Or generate README separately
readme = workflow.generate_readme(use_ai=True, ai_model="llama3.2")
print(readme)
```

**Features:**

- ✅ **Completely free** - no API keys or cloud services
- ✅ **Works offline** - local AI processing
- ✅ **Optional** - gracefully falls back to templates if Ollama not available
- ✅ **Comprehensive** - explains purpose, triggers, jobs, secrets, setup instructions
- ✅ **All platforms** - GitHub Actions, Azure DevOps, Jenkins, AWS CodeBuild

## 📊 Pipeline Visualization (Automatic)

WorkflowForge automatically generates visual diagrams of your pipelines using **Graphviz**:

```bash
# Install Graphviz (one-time setup)
brew install graphviz          # macOS
sudo apt-get install graphviz  # Ubuntu
choco install graphviz         # Windows
```

```python
# Generate workflow with automatic diagram
workflow.save(".github/workflows/ci.yml", generate_diagram=True)
# Creates: ci.yml + CI_Pipeline_workflow.png

# Generate diagram separately
diagram_path = workflow.generate_diagram("png")
print(f"📊 Diagram saved: {diagram_path}")

# Multiple formats supported
workflow.generate_diagram("svg")  # Vector graphics
workflow.generate_diagram("pdf")  # PDF document
```

**Features:**

- ✅ **Automatic generation** - every pipeline gets a visual diagram
- ✅ **Multiple formats** - PNG, SVG, PDF, DOT
- ✅ **Smart fallback** - DOT files if Graphviz not installed
- ✅ **Platform-specific styling** - Azure DevOps (blue), GitHub (purple), Jenkins (orange), CodeBuild (toasted AWS yellow)
- ✅ **Comprehensive view** - shows triggers, jobs, dependencies, step counts

## 📖 Basic Usage

### GitHub Actions Usage

```python
from workflowforge import github_actions

# Create workflow using snake_case functions
workflow = github_actions.workflow(
    name="My Workflow",
    on=github_actions.on_push(branches=["main"])
)

# Create job
job = github_actions.job(runs_on="ubuntu-latest")
job.add_step(github_actions.action("actions/checkout@v4", name="Checkout"))
job.add_step(github_actions.run("echo 'Hello World!'", name="Say Hello"))

# Add job to workflow
workflow.add_job("hello", job)

# Generate YAML
print(workflow.to_yaml())

# Save with documentation and diagram
workflow.save(".github/workflows/hello.yml", generate_readme=True, generate_diagram=True)
# Creates: hello.yml + hello_README.md + My_Workflow.png
```

### Jenkins Pipeline Usage

```python
from workflowforge import jenkins_platform

# Create Jenkins pipeline using snake_case
pipeline = jenkins_platform.pipeline()
pipeline.set_agent(jenkins_platform.agent_docker("maven:3.9.3-eclipse-temurin-17"))

# Add stages
build_stage = jenkins_platform.stage("Build")
build_stage.add_step("mvn clean compile")
pipeline.add_stage(build_stage)

# Generate Jenkinsfile with diagram
pipeline.save("Jenkinsfile", generate_diagram=True)
# Creates: Jenkinsfile + jenkins_pipeline.png
```

### AWS CodeBuild BuildSpec Usage

```python
from workflowforge import aws_codebuild

# Create BuildSpec using snake_case
spec = aws_codebuild.buildspec()

# Add environment
env = aws_codebuild.environment()
env.add_variable("JAVA_HOME", "/usr/lib/jvm/java-17-openjdk")
spec.set_env(env)

# Add build phase
build_phase = aws_codebuild.phase()
build_phase.add_command("mvn clean package")
spec.set_build_phase(build_phase)

# Set artifacts
artifacts_obj = aws_codebuild.artifacts(["target/*.jar"])
spec.set_artifacts(artifacts_obj)

# Generate buildspec.yml with AI documentation and diagram
spec.save("buildspec.yml", generate_readme=True, use_ai=True, generate_diagram=True)
# Creates: buildspec.yml + buildspec_README.md + codebuild_spec.png
```

### Azure DevOps Usage

Generate a simple “hello” pipeline:

```python
from workflowforge import azure_devops as ado

pipeline = ado.hello_world_template_azure(
    name="Hello ADO",
    message="Hello Azure DevOps from WorkflowForge!",
)
pipeline.save("azure-pipelines.yml")
```

Or generate a Python matrix CI with caching across Ubuntu/Windows/macOS:

```python
from workflowforge import azure_devops as ado

pipeline = ado.python_ci_template_azure(
    python_versions=["3.11", "3.12", "3.13"],
    os_list=["ubuntu-latest", "windows-latest", "macOS-latest"],
    use_cache=True,
)
pipeline.save("azure-pipelines.yml")
```

Optionally, scan the emitted YAML with Checkov (if installed):

```python
from workflowforge import azure_devops as ado

pipeline = ado.python_ci_template_azure()
pipeline.save("azure-pipelines.yml", scan_with_checkov=True)
```

See also: `examples/azure_devops/python_ci_scan.py`.

### AI Documentation Examples

```python
# GitHub Actions with AI README
workflow = Workflow(name="CI Pipeline", on=on_push())
job = Job(runs_on="ubuntu-latest")
job.add_step(action("actions/checkout@v4"))
workflow.add_job("test", job)

# Save with AI documentation and diagram
workflow.save("ci.yml", generate_readme=True, use_ai=True, generate_diagram=True)
# Creates: ci.yml + ci_README.md + Test_Workflow.png

# Jenkins with AI README and diagram
pipeline = pipeline()
stage_build = stage("Build")
stage_build.add_step("mvn clean package")
pipeline.add_stage(stage_build)

# Save with AI documentation and diagram
pipeline.save("Jenkinsfile", generate_readme=True, use_ai=True, generate_diagram=True)
# Creates: Jenkinsfile + Jenkinsfile_README.md + jenkins_pipeline.png

# Check AI availability
from workflowforge import OllamaClient
client = OllamaClient()
if client.is_available():
    print("AI documentation available!")
else:
    print("Using template documentation (Ollama not running)")
```

## Modular Import Structure

WorkflowForge supports **platform-specific imports** with **snake_case naming** following Python conventions:

### Platform Modules

```python
# Import specific platforms
from workflowforge import github_actions, jenkins_platform, aws_codebuild, azure_devops

# Or use short aliases
from workflowforge import github_actions as gh
from workflowforge import jenkins_platform as jenkins
from workflowforge import aws_codebuild as cb
from workflowforge import azure_devops as ado
```

### Benefits

✅ **Platform separation** - Clear namespace for each platform
✅ **Snake case naming** - Follows Python PEP 8 conventions
✅ **IDE autocompletion** - Better IntelliSense support
✅ **Shorter code** - `gh.action()` vs `github_actions.action()`

## 🔧 Advanced Examples

### Build Matrix Workflow

```python
from workflowforge import github_actions as gh

job = gh.job(
    runs_on="ubuntu-latest",
    strategy=gh.strategy(
        matrix=gh.matrix(
            python_version=["3.11", "3.12", "3.13"],
            os=["ubuntu-latest", "windows-latest"]
        )
    )
)
```

### Multiple Triggers

```python
from workflowforge import github_actions as gh

workflow = gh.workflow(
    name="CI/CD",
    on=[
        gh.on_push(branches=["main"]),
        gh.on_pull_request(branches=["main"]),
        gh.on_schedule("0 2 * * *")  # Daily at 2 AM
    ]
)
```

### Jobs with Dependencies

```python
from workflowforge import github_actions as gh

test_job = gh.job(runs_on="ubuntu-latest")
deploy_job = gh.job(runs_on="ubuntu-latest")
deploy_job.needs = "test"

workflow = gh.workflow(name="CI/CD")
workflow.add_job("test", test_job)
workflow.add_job("deploy", deploy_job)
```

## 📚 Complete Documentation

### Platform Support

**GitHub Actions:**

- `on_push()`, `on_pull_request()`, `on_schedule()`, `on_workflow_dispatch()`
- `action()`, `run()` steps
- `secret()`, `variable()`, `github_context()` for credentials
- Build matrices, strategies, environments
- Optional Checkov scan: `workflow.save(path, scan_with_checkov=True)`

**Jenkins:**

- `pipeline()`, `stage()`, `agent_docker()`, `agent_any()`
- `jenkins_credential()`, `jenkins_env()`, `jenkins_param()`
- Shared libraries, parameters, post actions

**AWS CodeBuild:**

- `buildspec()`, `phase()`, `environment()`, `artifacts()`
- `codebuild_secret()`, `codebuild_parameter()`, `codebuild_env()`
- Runtime versions, caching, reports

**Azure DevOps:**

- `pipeline()`, `job()`, `strategy(matrix=...)`, `task()`, `script()`
- Build matrices, multi-OS matrix, and pip caching
- Hello world template
- Optional Checkov scan: `pipeline.save(path, scan_with_checkov=True)`

### AI Documentation

- **Ollama Integration**: Local AI models (llama3.2, codellama, qwen2.5-coder)
- **Automatic README**: Explains workflow purpose, triggers, jobs, setup
- **Fallback Support**: Template-based documentation if AI unavailable
- **All Platforms**: Works with GitHub Actions, Azure DevOps, Jenkins, CodeBuild

### Pipeline Visualization

- **Graphviz Integration**: Native diagram generation using DOT language
- **Multiple Formats**: PNG, SVG, PDF, DOT files
- **Platform Styling**: Color-coded diagrams (Azure DevOps: blue, GitHub: purple, Jenkins: orange, CodeBuild: toasted AWS yellow)
- **Smart Fallback**: DOT files if Graphviz not installed, images if available
- **Comprehensive View**: Shows triggers, jobs, dependencies, step counts, execution flow

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
1. Create a feature branch
1. Add tests
1. Submit a pull request

## 👨‍💻 Author & Maintainer

**Brainy Nimbus, LLC** - We love opensource! 💖

Website: [brainynimbus.io](https://brainynimbus.io)
Email: <info@brainynimbus.io>
GitHub: [@brainynimbus](https://github.com/brainynimbus)

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🔗 Links

**GitHub Actions:**

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Actions Marketplace](https://github.com/marketplace?type=actions)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)

**Jenkins:**

- [Jenkins Documentation](https://www.jenkins.io/doc/)
- [Pipeline Syntax](https://www.jenkins.io/doc/book/pipeline/syntax/)
- [Jenkins Plugins](https://plugins.jenkins.io/)

**AWS CodeBuild:**

- [CodeBuild Documentation](https://docs.aws.amazon.com/codebuild/)
- [BuildSpec Reference](https://docs.aws.amazon.com/codebuild/latest/userguide/build-spec-ref.html)
- [CodeBuild Samples](https://docs.aws.amazon.com/codebuild/latest/userguide/samples.html)

**Azure DevOps Pipelines:**

- [YAML schema reference](https://learn.microsoft.com/en-us/azure/devops/pipelines/yaml-schema)
- [Customize Python pipelines](https://learn.microsoft.com/en-us/azure/devops/pipelines/ecosystems/customize-python)

[license-badge]: https://img.shields.io/badge/License-MIT-yellow.svg
[license-url]: https://opensource.org/licenses/MIT
[maintained-badge]: https://img.shields.io/badge/maintained%20by-Brainy%20Nimbus-8A2BE2?style=flat
[maintained-url]: https://brainynimbus.io/
[precommit-badge]: https://results.pre-commit.ci/badge/github/brainynimbus/workflowforge/main.svg
[precommit-url]: https://results.pre-commit.ci/latest/github/brainynimbus/workflowforge/main
[pypi-badge]: https://badge.fury.io/py/workflowforge.svg
[pypi-url]: https://badge.fury.io/py/workflowforge
[python-versions-badge]: https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue
[python-versions-url]: https://www.python.org/
[ruff-badge]: https://img.shields.io/badge/linting-ruff-46A3FF?logo=ruff&logoColor=white
[ruff-url]: https://github.com/astral-sh/ruff
[security-badge]: https://img.shields.io/badge/security-bandit-brightgreen?style=flat
[security-url]: https://bandit.readthedocs.io/
[testpypi-badge]: https://img.shields.io/badge/Test%20PyPI-published-green
[testpypi-url]: https://test.pypi.org/project/workflowforge/
[tests-badge]: https://github.com/brainynimbus/workflowforge/workflows/Publish%20WorkflowForge%20to%20PyPI/badge.svg
[tests-url]: https://github.com/brainynimbus/workflowforge/actions
