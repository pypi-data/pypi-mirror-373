# Pre-commit Setup for WorkflowForge

## What is Pre-commit?

Pre-commit hooks automatically run checks before each commit to ensure code quality and consistency.

## Installation

```bash
# Install dependencies
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install
pre-commit install --hook-type commit-msg
```

## What Gets Checked

### Code Quality

- **Black**: Code formatting
- **isort**: Import sorting
- **Flake8**: Style and syntax checking
- **Bandit**: Security vulnerability scanning
- **PyUpgrade**: Modern Python syntax

### File Quality

- Trailing whitespace removal
- End-of-file fixing
- YAML/TOML validation
- Large file detection
- Merge conflict detection

### Commit Messages

- **Conventional Commits**: Enforces format like `feat:`, `fix:`, `docs:`

## Commit Message Format

Use conventional commit format:

```xml
<type>: <description>

[optional body]

[optional footer]
```

**Types:**

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples:**

```bash
git commit -m "feat: add AI documentation generation"
git commit -m "fix: resolve import conflicts in tests"
git commit -m "docs: update README with installation guide"
```

## Manual Run

```bash
# Run on all files
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files
```

## Skip Hooks (Emergency)

```bash
# Skip all hooks
git commit --no-verify -m "emergency fix"

# Skip specific hook
SKIP=bandit git commit -m "fix: temporary security bypass"
```
