# Contributing to yalje

Thank you for your interest in contributing to yalje!

## Development Setup

```bash
# Clone the repository
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

## Code Style

We use:
- **ruff** for code formatting and linting (replaces black, isort, flake8)
- **mypy** for type checking
- **tox** for running all quality checks

Run all checks with tox (recommended):
```bash
# Run all quality checks (recommended during development)
tox -e dev

# Run all checks with full coverage report
tox -e all

# Run specific checks
tox -e lint          # Linting and formatting checks
tox -e typecheck     # Type checking
tox -e format        # Auto-format code (utility)
```

Or run tools directly:
```bash
# Lint code
ruff check src/ tests/

# Format code
ruff format src/ tests/

# Auto-fix linting issues
ruff check --fix src/ tests/

# Type check
mypy src/yalje
```

## Running Tests

With tox (recommended):
```bash
# Run tests on current Python version
tox -e py312

# Run tests on all Python versions (3.9, 3.10, 3.11, 3.12)
tox
```

Or run pytest directly:
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=yalje

# Run specific test
pytest tests/unit/test_models.py::test_post_jitemid_calculation
```

## Project Structure

See [Architecture](architecture.md) for detailed module organization.

Key files:
- `src/yalje/models/` - Add new data models here
- `src/yalje/api/` - Add new API clients here
- `src/yalje/parsers/` - Add new parsers here
- `src/yalje/exporters/` - Add new export formats here
- `src/yalje/cli/commands/` - Add new CLI commands here

## Making Changes

1. **Create a branch**
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Make your changes**
   - Write code
   - Add tests
   - Update documentation

3. **Test your changes**
   ```bash
   # Recommended: Run all checks with tox
   tox -e dev

   # Or run individually
   pytest
   ruff check --fix src/ tests/
   ruff format src/ tests/
   mypy src/yalje
   ```

4. **Commit**
   ```bash
   git add .
   git commit -m "Add feature: description"
   ```

5. **Push and create PR**
   ```bash
   git push origin feature/my-feature
   ```

## Commit Messages

Use clear, descriptive commit messages:
- `feat: Add inbox download functionality`
- `fix: Correct jitemid calculation for posts`
- `docs: Update API documentation`
- `test: Add tests for XML parser`
- `refactor: Simplify authentication flow`

## Adding New Features

### Adding a New API Endpoint

1. Create client in `src/yalje/api/`
2. Create parser in `src/yalje/parsers/`
3. Create model in `src/yalje/models/`
4. Add to `LJExport` model
5. Update CLI commands
6. Add tests
7. Update documentation

### Adding a New Export Format

1. Create exporter in `src/yalje/exporters/`
2. Implement `export()` and `load()` methods
3. Add CLI command
4. Add tests
5. Update documentation

## Documentation

Update relevant documentation:
- **README.md** - User-facing features
- **docs/api/** - API endpoint details
- **docs/schema.md** - Data format changes
- **docs/architecture.md** - Design decisions
- **Docstrings** - Function/class documentation

## Questions?

- Open an issue for bugs or feature requests
- Start a discussion for questions
- Check existing issues before creating new ones

## Code of Conduct

Be respectful, constructive, and welcoming to all contributors.

Thank you for contributing to yalje!
