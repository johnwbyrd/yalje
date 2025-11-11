# Development Guide

## Setup

```bash
# Clone repository
git clone https://github.com/yourusername/yalje.git
cd yalje

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

## Code Quality Tools

### Ruff (Linting + Formatting)

Ruff is an extremely fast Python linter and formatter that replaces:
- black (formatter)
- isort (import sorting)
- flake8 (linting)

**Check code:**
```bash
ruff check src/ tests/
```

**Format code:**
```bash
ruff format src/ tests/
```

**Auto-fix issues:**
```bash
ruff check --fix src/ tests/
```

**Configuration:** See `[tool.ruff]` in [pyproject.toml](pyproject.toml)

### Mypy (Type Checking)

```bash
mypy src/yalje
```

**Configuration:** See `[tool.mypy]` in [pyproject.toml](pyproject.toml)

### Pre-commit Hooks

Automatically run checks before each commit:

```bash
# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

**Configuration:** See [.pre-commit-config.yaml](.pre-commit-config.yaml)

## Testing

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=yalje

# Run specific test
pytest tests/unit/test_models.py::test_post_jitemid_calculation

# Run with verbose output
pytest -v
```

**Configuration:** See `[tool.pytest.ini_options]` in [pyproject.toml](pyproject.toml)

### Coverage Reports

```bash
# Generate HTML coverage report
pytest --cov=yalje --cov-report=html

# View report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## Continuous Integration

GitHub Actions runs on every push and PR:

- **Linting:** `ruff check`
- **Formatting check:** `ruff format --check`
- **Type checking:** `mypy`
- **Tests:** `pytest` with coverage
- **Multiple Python versions:** 3.8, 3.9, 3.10, 3.11, 3.12

**Configuration:** See [.github/workflows/ci.yml](.github/workflows/ci.yml)

## Development Workflow

1. **Create feature branch**
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Make changes**
   - Write code
   - Add tests
   - Update documentation

3. **Run checks locally**
   ```bash
   # Format and fix issues
   ruff check --fix src/ tests/
   ruff format src/ tests/

   # Type check
   mypy src/yalje

   # Run tests
   pytest
   ```

4. **Commit**
   ```bash
   git add .
   git commit -m "feat: Add feature description"
   ```

   Pre-commit hooks will run automatically!

5. **Push and create PR**
   ```bash
   git push origin feature/my-feature
   ```

   CI will run on GitHub!

## Common Commands

```bash
# Full quality check
ruff check src/ tests/ && ruff format --check src/ tests/ && mypy src/yalje && pytest

# Quick format + fix
ruff check --fix src/ tests/ && ruff format src/ tests/

# Update dependencies
pip install -U -e ".[dev]"

# Clean build artifacts
rm -rf build/ dist/ *.egg-info htmlcov/ .coverage .pytest_cache/ .mypy_cache/ .ruff_cache/
```

## IDE Integration

### VS Code

Install extensions:
- [Ruff](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff)
- [Mypy Type Checker](https://marketplace.visualstudio.com/items?itemName=ms-python.mypy-type-checker)

Add to `.vscode/settings.json`:
```json
{
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll": true,
      "source.organizeImports": true
    }
  },
  "ruff.lint.enable": true,
  "ruff.format.enable": true
}
```

### PyCharm

1. Install Ruff plugin from marketplace
2. Enable Ruff in Settings → Tools → Ruff
3. Configure File Watchers for auto-format

## Troubleshooting

### Ruff not found
```bash
pip install ruff
# or
pip install -e ".[dev]"
```

### Pre-commit hooks failing
```bash
# Update hooks
pre-commit autoupdate

# Skip hooks (emergency only!)
git commit --no-verify
```

### Type checking errors
```bash
# Check specific file
mypy src/yalje/core/auth.py

# Ignore imports
mypy --ignore-missing-imports src/yalje
```

## See Also

- [Contributing Guide](docs/contributing.md)
- [Architecture Documentation](docs/architecture.md)
- [Project Structure](STRUCTURE.md)
