# Poetry Package Management Guide

This document explains how to use Poetry for dependency management and packaging of the Email2SMS Generator Streamlit application.

## 📦 What is Poetry?

Poetry is a modern dependency management and packaging tool for Python that provides:
- **Deterministic builds** through `poetry.lock` file
- **Dependency resolution** with conflict detection
- **Virtual environment management** automatically
- **Build and publish** to PyPI with ease
- **All-in-one** configuration in `pyproject.toml`

## 🚀 Quick Start

### Install Poetry

```bash
# Install Poetry (official installer)
curl -sSL https://install.python-poetry.org | python3 -

# Or using pipx (recommended)
pipx install poetry

# Verify installation
poetry --version
```

### Install Dependencies

```bash
# Navigate to streamlit-app directory
cd /home/ruhroh/email2sms/streamlit-app

# Install all dependencies (main + dev + test)
poetry install

# Install only production dependencies
poetry install --only main

# Install with specific groups
poetry install --with test
poetry install --without dev
```

### Run the Application

```bash
# Activate Poetry's virtual environment
poetry shell

# Run Streamlit app
streamlit run app.py

# Or run without activating shell
poetry run streamlit run app.py
```

## 📋 Common Commands

### Dependency Management

```bash
# Add a new dependency
poetry add requests

# Add a development dependency
poetry add --group dev pylint

# Add a test dependency
poetry add --group test pytest-asyncio

# Add with version constraint
poetry add "streamlit>=1.30.0,<2.0.0"

# Update a specific dependency
poetry update streamlit

# Update all dependencies
poetry update

# Remove a dependency
poetry remove requests

# Show installed packages
poetry show

# Show dependency tree
poetry show --tree
```

### Virtual Environment

```bash
# Activate virtual environment
poetry shell

# Exit virtual environment
exit

# Run command in virtual environment
poetry run python script.py
poetry run pytest

# Show virtual environment info
poetry env info

# List virtual environments
poetry env list

# Remove virtual environment
poetry env remove python3.11
```

### Building and Publishing

```bash
# Build package (wheel + source distribution)
poetry build

# Check package before publishing
poetry check

# Publish to PyPI
poetry publish

# Build and publish in one command
poetry publish --build

# Publish to test PyPI
poetry config repositories.testpypi https://test.pypi.org/legacy/
poetry publish --repository testpypi
```

### Version Management

```bash
# Show current version
poetry version

# Bump patch version (1.0.0 → 1.0.1)
poetry version patch

# Bump minor version (1.0.0 → 1.1.0)
poetry version minor

# Bump major version (1.0.0 → 2.0.0)
poetry version major

# Set specific version
poetry version 1.2.3
```

### Export Dependencies

```bash
# Export to requirements.txt
poetry export -f requirements.txt --output requirements.txt --without-hashes

# Export only production dependencies
poetry export -f requirements.txt --output requirements.txt --without-hashes --only main

# Export with dev dependencies
poetry export -f requirements.txt --output requirements-dev.txt --with dev --without-hashes
```

## 🏗️ Project Structure

```
streamlit-app/
├── pyproject.toml          # Poetry configuration + all tool configs
├── poetry.lock             # Locked dependency versions (commit this!)
├── README.md
├── app.py                  # Main Streamlit entry point
├── components/             # UI components
├── generators/             # Code generation logic
├── schemas/               # Pydantic models
├── utils/                 # Utilities and validators
├── validators/            # Input validation
├── templates/             # Jinja2 templates
└── tests/                 # Pytest test files
```

## 🔧 Configuration

All configuration is centralized in `pyproject.toml`:

### Dependency Groups

- **`[tool.poetry.dependencies]`** - Production dependencies
- **`[tool.poetry.group.dev.dependencies]`** - Development tools (black, flake8, mypy)
- **`[tool.poetry.group.test.dependencies]`** - Testing tools (pytest, coverage)

### Tool Configurations

- **`[tool.black]`** - Code formatting
- **`[tool.isort]`** - Import sorting
- **`[tool.mypy]`** - Type checking
- **`[tool.pytest.ini_options]`** - Test configuration
- **`[tool.coverage.*]`** - Coverage reporting

## 📝 Development Workflow

### 1. Initial Setup

```bash
# Clone repository
git clone https://github.com/yourusername/email2sms.git
cd email2sms/streamlit-app

# Install dependencies
poetry install

# Activate environment
poetry shell
```

### 2. Daily Development

```bash
# Start development server (auto-reload enabled)
streamlit run app.py

# Run tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov

# Format code
poetry run black .
poetry run isort .

# Type checking
poetry run mypy .

# Lint code
poetry run flake8
```

### 3. Before Committing

```bash
# Run full test suite
make test

# Or manually:
poetry run black .
poetry run isort .
poetry run flake8
poetry run mypy .
poetry run pytest --cov
```

### 4. Updating Dependencies

```bash
# Check for outdated dependencies
poetry show --outdated

# Update specific dependency
poetry update streamlit

# Update all dependencies
poetry update

# Update poetry.lock without installing
poetry lock --no-update
```

## 🐳 Docker Integration

### Option 1: Export requirements.txt (Smaller Image)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Export and install dependencies
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes --only main && \
    pip install --no-cache-dir -r requirements.txt && \
    pip uninstall -y poetry

# Copy application
COPY . .

# Run Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Option 2: Use Poetry Directly (Easier)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry config virtualenvs.create false && \
    poetry install --only main --no-interaction --no-ansi

# Copy application
COPY . .

# Run Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

## 🔒 Lock File Management

The `poetry.lock` file ensures reproducible builds:

```bash
# Update lock file after manual pyproject.toml edits
poetry lock

# Update lock file without upgrading dependencies
poetry lock --no-update

# Install from lock file (production)
poetry install --only main

# Validate lock file
poetry check
```

**Important**: Always commit `poetry.lock` to version control!

## 🎯 Best Practices

### 1. Version Constraints

- **Streamlit**: Use exact version (`1.31.0`) for UI stability
- **Core libraries**: Use caret (`^2.6.0`) for compatible updates
- **Python**: Use range (`>=3.8,<4.0`) for broad compatibility

### 2. Dependency Groups

- Use `--group dev` for development tools (linters, formatters)
- Use `--group test` for testing tools (pytest, coverage)
- Keep production dependencies minimal

### 3. Virtual Environments

- Let Poetry manage virtual environments automatically
- Don't mix `pip install` with Poetry environments
- Use `poetry shell` or `poetry run` for isolation

### 4. CI/CD

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install Poetry
        run: pip install poetry
      - name: Install dependencies
        run: poetry install
      - name: Run tests
        run: poetry run pytest --cov
```

## 🆘 Troubleshooting

### Poetry Not Found

```bash
# Add Poetry to PATH
export PATH="$HOME/.local/bin:$PATH"

# Or reinstall
curl -sSL https://install.python-poetry.org | python3 -
```

### Dependency Conflicts

```bash
# Show dependency tree
poetry show --tree

# Update specific dependency
poetry update problematic-package

# Clear cache and reinstall
poetry cache clear pypi --all
rm poetry.lock
poetry install
```

### Virtual Environment Issues

```bash
# Remove virtual environment
poetry env remove python3.11

# List environments
poetry env list

# Recreate environment
poetry install
```

### Lock File Out of Sync

```bash
# Update lock file
poetry lock

# Install with updated lock
poetry install
```

## 📚 Resources

- **Poetry Documentation**: https://python-poetry.org/docs/
- **pyproject.toml Spec**: https://python-poetry.org/docs/pyproject/
- **Dependency Management**: https://python-poetry.org/docs/managing-dependencies/
- **CLI Reference**: https://python-poetry.org/docs/cli/
- **Configuration**: https://python-poetry.org/docs/configuration/

## 🎓 Migration from pip

If you're migrating from pip + requirements.txt:

```bash
# Import from requirements.txt
poetry add $(cat requirements.txt)

# Or manually for better organization
poetry add streamlit==1.31.0
poetry add jinja2 pygments validators
poetry add --group test pytest pytest-cov
poetry add --group dev black flake8 mypy

# Generate lock file
poetry lock

# Test installation
poetry install
```

---

**Note**: Once you're comfortable with Poetry, you can remove `requirements.txt` and use Poetry exclusively. Keep `requirements.txt` temporarily for backward compatibility during the transition period.
