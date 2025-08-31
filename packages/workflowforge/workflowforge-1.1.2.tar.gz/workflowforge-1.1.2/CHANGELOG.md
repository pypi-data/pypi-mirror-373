# Changelog

All notable changes to WorkflowForge will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.2] - 2025-08-30

### Changed

- README: update usage guide and examples; clarified AI docs and visualization sections
- Policy: reinforce English-only for code, docs, and commits

## [1.1.0] - 2025-08-29

### Added

- Azure DevOps YAML support (`workflowforge.azure_devops`): pipeline/job/steps/task modeling and YAML emitter
- Python CI template for Azure Pipelines with multi-OS matrix (Ubuntu/Windows/macOS) and pip caching via Cache@2
- Minimal Azure DevOps hello-world template and examples under `examples/azure_devops/`

### Changed

- Exported `azure_devops` from public API for `from workflowforge import azure_devops`
- Consistent YAML indentation for Azure Pipelines emitter to improve readability

### Security

- CI/CD remains on GitHub Actions with tag/version guard and idempotent PyPI/TestPyPI publishing (`skip-existing`)

## [1.0.0] - 2025-08-29

### Changed

- Promote project to stable release (1.0.0)
- Update classifiers to Production/Stable

### Fixed

- Correct GitHub Actions matrix variable references:
    - Use `matrix.python_version` instead of `matrix.python-version`
    - Use `matrix.node_version` instead of `matrix.node-version`
- Align examples and CI workflow with corrected matrix variable names

## [1.0b7] - 2025-08-27

### Changed

- Regenerated examples (python_matrix) and validated with yamllint
- Maintenance: version bump to 1.0b7

## [1.0b6] - 2025-08-27

### Changed

- Removed legacy references in docs and comments
- Cleaned egg-info artifacts from repo
- Ensured examples generate YAML/Jenkinsfile without lingering images

## [1.0b5] - 2024-12-19

### Added

- Complete mypy compliance with strict type checking (51 → 0 errors)
- Enterprise-grade type safety across all modules
- Enhanced type annotations for visualization, triggers, strategy, step modules
- Type guards for safe type checking in AI documentation
- Professional-grade code quality with comprehensive type validation

### Changed

- All modules now use proper dict[str, Any] typing for flexible data structures
- Enhanced IDE support with strict type annotations
- Improved code reliability through comprehensive type checking
- Elevated code quality to enterprise standards

### Fixed

- All mypy type errors resolved across entire codebase
- Proper return types and function annotations implemented
- Type assignment issues in codebuild.py resolved
- Enhanced type safety in templates.py with factory functions

## [1.0b4] - 2024-12-19

### Added

- TRUE dogfooding: WorkflowForge generates its own GitHub Actions workflows
- Professional CI/CD pipeline with Python 3.11, 3.12, 3.13 test matrix
- Security scanning integration with Bandit and Safety tools
- OIDC trusted publishing for PyPI deployment (no API tokens needed)
- Automated TestPyPI publishing on main branch merges
- Complete mypy compliance with strict type checking (51 → 0 errors)
- Type safety across all modules with proper annotations

### Changed

- Enhanced publish workflow with comprehensive quality checks
- Integrated security scanning into CI/CD pipeline
- Improved project automation with self-generated workflows
- Migrated all type annotations to strict mypy compliance
- Enhanced type safety with proper dict[str, Any] annotations

### Fixed

- Removed generated diagram artifacts to maintain clean repository
- Eliminated image pollution in project structure
- Fixed all mypy type errors across visualization, triggers, strategy, step modules
- Corrected return types and function annotations for complete type safety
- Resolved codebuild.py type assignment issues with proper dict typing

## [1.0b3] - 2024-12-19

### Added

- Strict mypy configuration with Pydantic plugin for enhanced type safety
- Professional quality badges in README (mypy, black, isort, ruamel.yaml)
- Comprehensive pre-commit hooks including yamllint for generated files
- GitHub Actions publish workflow with proper ruamel.yaml formatting

### Changed

- **BREAKING**: Migrated from PyYAML to ruamel.yaml for superior YAML generation
- **BREAKING**: Removed top-level import compatibility – use platform-specific modules only
- Translated all Spanish docstrings and comments to English for professional codebase
- Improved YAML formatting with precise indentation (mapping=2, sequence=4, offset=2)
- Enhanced code quality with flake8, black, and isort integration
- Streamlined module exports to platform-specific imports only

### Fixed

- All flake8 code style issues resolved (F541, E501, E712, E999)
- YAML validation now passes with proper indentation and formatting
- Boolean comparisons in tests simplified to Pythonic style
- Line length violations fixed across entire codebase
- Pre-commit hooks now pass successfully on all files

### Removed

- Top-level backwards compatibility imports from __init__.py
- Spanish language docstrings and comments
- PyYAML dependency in favor of ruamel.yaml
- npm-groovy-lint from pre-commit (simplified validation)

## [1.0b2] - 2024-12-18

### Added

- Initial release with GitHub Actions, Jenkins, and AWS CodeBuild support
- Pydantic-based models for type safety and validation
- AI-powered documentation generation with Ollama
- Pipeline visualization with Graphviz
- Comprehensive examples and templates
- Pre-commit hooks for code quality

### Features

- Platform-specific modules: github_actions, jenkins_platform, aws_codebuild
- Type-safe pipeline generation with IDE autocompletion
- YAML/Groovy output with validation
- Modular architecture with clean API design

## [1.1.1] - 2025-08-30

### Changed

- Version bump for TestPyPI publication and minor documentation/tooling updates
