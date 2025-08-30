# v1.1.0 — Azure DevOps CI Support

## Summary
Adds first-class Azure DevOps Pipelines support for CI while keeping releases on GitHub Actions. Includes a Python matrix CI template with multi‑OS and caching, plus a minimal hello‑world pipeline.

## What's New
- New module: `workflowforge.azure_devops`
  - `pipeline`, `job`, `strategy(matrix)`, `task`, `script`
  - YAML emitter with readable indentation
- Templates:
  - `python_ci_template_azure(...)` — matrix over Python (3.11/3.12/3.13) and OS (Ubuntu/Windows/macOS) with pip caching via Cache@2
  - `hello_world_template_azure(...)` — single job printing a message
- Examples:
  - `examples/azure_devops/python_ci.yml` and generator `python_ci.py`
  - `examples/azure_devops/hello_world.yml` and generator `hello_world.py`

## CI/CD Strategy
- CI on Azure DevOps (build/lint/type/test)
- Release remains on GitHub Actions with:
  - Tag/version guard (tag `vX.Y.Z` must match `pyproject.toml`)
  - Idempotent publishing to PyPI/TestPyPI (`skip-existing: true`)

## Upgrade Notes
- Import as: `from workflowforge import azure_devops as ado`
- Generate ADO CI: `ado.python_ci_template_azure().save("azure-pipelines.yml")`
