# v1.0.0 — Stable Release

## Summary
Stable 1.0.0 release of WorkflowForge. This promotes the library from beta to production-ready, fixes a release‑blocking CI matrix variable bug, and confirms clean tests across Python 3.11–3.13.

## Highlights
- Type safety: Strict typing with mypy and Pydantic across modules
- Multi‑platform: Generate GitHub Actions, Jenkins, and AWS CodeBuild specs
- Quality gates: Black/Isort/Flake8/Mypy/pytest with coverage in CI
- Security: Bandit + Safety scans in CI; no embedded secrets detected
- Docs & visuals: Optional AI README with Ollama; automatic pipeline diagrams

## Fixes
- Matrix variables: Use `matrix.python_version`/`matrix.node_version` (previously hyphenated). Aligned templates, examples, and CI
- Tests: Added assertions to enforce correct matrix variable references

## Compatibility
- Python: 3.11, 3.12, 3.13
- Breaking changes: None since latest beta. Note older betas removed legacy top‑level imports in favor of platform‑specific modules

## Upgrade Notes
- If you referenced old hyphenated matrix vars in custom workflows, update to `matrix.python_version` and `matrix.node_version`
- Regenerate example workflows to reflect v1.0.0 behavior

## CI/CD & Publishing
- OIDC‑based publishing to PyPI on GitHub “release published” events
- TestPyPI publishes on `main` push

## Security
- CI runs Bandit and Safety. Keep dependencies current to maintain posture

## Links
- Changelog: CHANGELOG.md:10
- CI workflow: .github/workflows/publish.yml:19
- Version bump: pyproject.toml:7, src/workflowforge/__init__.py:13
