# WorkflowForge Examples

This directory contains examples demonstrating the modular import structure of WorkflowForge.

## New Import Style

Use the modular imports for a clear, type-safe API:

```python
from workflowforge import github_actions

workflow = github_actions.workflow(name="CI")
job = github_actions.job(runs_on="ubuntu-latest")
job.add_step(github_actions.action("actions/checkout@v4"))
```

## Examples

### GitHub Actions

- **basic_ci.py** - Simple CI pipeline with checkout and hello world
- **python_matrix.py** - Matrix testing across Python versions and OS

### Jenkins

- **maven_build.py** - Maven build pipeline with multiple stages

### AWS CodeBuild

- **node_app.py** - Node.js application build with testing and artifacts

## Running Examples

Run individual examples:

```bash
python examples/github_actions/basic_ci.py
python examples/jenkins/maven_build.py
python examples/codebuild/node_app.py
```

Run Azure DevOps examples:

```bash
python examples/azure_devops/hello_world.py
python examples/azure_devops/python_ci.py
python examples/azure_devops/python_ci_scan.py
```

## Benefits of Modular Structure

✅ **Platform separation** - Clear namespace for each platform
✅ **Snake case naming** - Follows Python conventions

### Azure DevOps

- **hello_world.py** - Minimal ADO pipeline that echoes a message
- **python_ci.py** - Python matrix CI across Ubuntu/Windows/macOS with pip cache
- **python_ci_scan.py** - Same as above, plus optional Checkov scan of emitted YAML
    ✅ **IDE autocompletion** - Better IntelliSense support
    ✅ **Shorter aliases** - `gh = github_actions` for convenience
