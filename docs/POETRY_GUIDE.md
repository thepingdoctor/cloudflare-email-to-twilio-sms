# Poetry Package Management Guide for Email2SMS Project

This guide explains how to use Poetry for managing the Streamlit UI component of the Email2SMS project.

## 📦 Overview

Poetry is a modern Python package manager that provides:
- **Dependency resolution** - Automatically resolves conflicts
- **Lock file** - Ensures reproducible builds across environments
- **Virtual environments** - Manages isolated environments automatically
- **Publishing** - Easy PyPI publishing workflow
- **All-in-one config** - Single `pyproject.toml` file

## 🚀 Installation

### Install Poetry

```bash
# Using official installer (recommended)
curl -sSL https://install.python-poetry.org | python3 -

# Verify installation
poetry --version

# Add Poetry to PATH (if needed)
export PATH="$HOME/.local/bin:$PATH"
```

### Alternative Installation Methods

```bash
# Using pipx (isolated installation)
pipx install poetry

# Using pip (not recommended)
pip install poetry
```

## 📁 Project Setup

### For New Users

```bash
# Clone repository
git clone <repository-url>
cd email2sms/streamlit-app

# Install dependencies
poetry install

# Activate virtual environment
poetry shell

# Run application
streamlit run app.py
```

### For Contributors

```bash
# Install with dev dependencies
poetry install

# Install only production dependencies
poetry install --only main

# Install with specific groups
poetry install --with test --without docs
```

## 🎯 Common Workflows

### Running the Application

```bash
# Option 1: Using poetry run
poetry run streamlit run app.py

# Option 2: Activate shell first
poetry shell
streamlit run app.py

# Option 3: Run on specific port
poetry run streamlit run app.py --server.port=8501
```

### Managing Dependencies

```bash
# Add new dependency
poetry add requests

# Add dev dependency
poetry add --group dev black

# Add test dependency
poetry add --group test pytest-asyncio

# Add with version constraint
poetry add "streamlit>=1.30,<2.0"

# Update specific dependency
poetry update streamlit

# Update all dependencies
poetry update

# Remove dependency
poetry remove requests

# Show installed packages
poetry show

# Show dependency tree
poetry show --tree

# Show outdated packages
poetry show --outdated
```

### Development Commands

```bash
# Format code
poetry run black .
poetry run isort .

# Lint code
poetry run flake8

# Type checking
poetry run mypy .

# Run tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov

# Run tests in parallel
poetry run pytest -n auto
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

# Prerelease versions
poetry version prepatch  # 1.0.0 → 1.0.1-alpha.0
poetry version preminor  # 1.0.0 → 1.1.0-alpha.0
poetry version premajor  # 1.0.0 → 2.0.0-alpha.0
```

## 🏗️ Building and Publishing

### Build Package

```bash
# Build wheel and source distribution
poetry build

# Output:
# dist/email2sms_generator-1.0.0-py3-none-any.whl
# dist/email2sms_generator-1.0.0.tar.gz

# Check package contents
tar -tzf dist/email2sms_generator-1.0.0.tar.gz
```

### Publish to PyPI

```bash
# Configure PyPI credentials
poetry config pypi-token.pypi <your-token>

# Test build
poetry build

# Validate package
poetry check

# Publish to PyPI
poetry publish

# Build and publish in one step
poetry publish --build
```

### Publish to Test PyPI

```bash
# Configure TestPyPI repository
poetry config repositories.testpypi https://test.pypi.org/legacy/

# Configure TestPyPI token
poetry config pypi-token.testpypi <your-test-token>

# Build and publish to TestPyPI
poetry publish --build --repository testpypi

# Test installation
pip install --index-url https://test.pypi.org/simple/ email2sms-generator
```

## 🔧 Advanced Usage

### Virtual Environment Management

```bash
# Show environment info
poetry env info

# List all environments
poetry env list

# Remove environment
poetry env remove <python-version>
poetry env remove python3.11

# Use specific Python version
poetry env use python3.11
poetry env use 3.11
poetry env use /usr/bin/python3.11
```

### Configuration

```bash
# Show current configuration
poetry config --list

# Set configuration value
poetry config virtualenvs.in-project true
poetry config virtualenvs.create false

# Use local configuration
poetry config virtualenvs.in-project true --local

# Cache management
poetry cache list
poetry cache clear pypi --all
```

### Export Dependencies

```bash
# Export to requirements.txt
poetry export -f requirements.txt --output requirements.txt --without-hashes

# Export only production dependencies
poetry export -f requirements.txt --output requirements.txt --without-hashes --only main

# Export with dev dependencies
poetry export -f requirements.txt --output requirements-dev.txt --with dev --without-hashes

# Export with specific groups
poetry export -f requirements.txt --output requirements-test.txt --with test --without-hashes
```

## 🐳 Docker Integration

### Multi-stage Build (Recommended)

```dockerfile
# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Export dependencies
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes --only main

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Copy requirements from builder
COPY --from=builder /app/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run application
CMD ["streamlit", "run", "app.py"]
```

### Direct Poetry Usage

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies without virtualenv
RUN poetry config virtualenvs.create false && \
    poetry install --only main --no-interaction --no-ansi

# Copy application
COPY . .

# Run application
CMD ["streamlit", "run", "app.py"]
```

## 📊 pyproject.toml Structure

The `pyproject.toml` file contains all configuration:

```toml
[tool.poetry]
name = "email2sms-generator"
version = "1.0.0"
description = "Streamlit app for generating Cloudflare Worker code"
authors = ["Your Name <email@example.com>"]

[tool.poetry.dependencies]
python = "^3.8"
streamlit = "1.31.0"

[tool.poetry.group.dev.dependencies]
black = "^23.7.0"
flake8 = "^6.1.0"

[tool.poetry.group.test.dependencies]
pytest = "^7.4.0"
pytest-cov = "^4.1.0"

[tool.black]
line-length = 88

[tool.pytest.ini_options]
testpaths = ["tests"]
```

## 🛠️ Troubleshooting

### Poetry Not Found After Installation

```bash
# Add to PATH
export PATH="$HOME/.local/bin:$PATH"

# Make permanent (add to ~/.bashrc or ~/.zshrc)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Dependency Conflicts

```bash
# Update lock file
poetry lock

# Update specific package
poetry update problematic-package

# Clear cache
poetry cache clear pypi --all
rm poetry.lock
poetry install
```

### Virtual Environment Issues

```bash
# Remove and recreate environment
poetry env remove python3.11
poetry install

# Use system Python
poetry config virtualenvs.create false
```

### Lock File Out of Sync

```bash
# After manual pyproject.toml edits
poetry lock

# Update lock without upgrading
poetry lock --no-update

# Install from updated lock
poetry install
```

### Slow Dependency Resolution

```bash
# Clear cache
poetry cache clear pypi --all

# Use faster resolver
poetry install --no-cache
```

## 💡 Best Practices

### 1. Always Commit poetry.lock

The `poetry.lock` file ensures reproducible builds:
```bash
git add poetry.lock
git commit -m "Update dependencies"
```

### 2. Use Dependency Groups

Organize dependencies logically:
- `[tool.poetry.dependencies]` - Production
- `[tool.poetry.group.dev.dependencies]` - Development tools
- `[tool.poetry.group.test.dependencies]` - Testing tools

### 3. Pin Critical Dependencies

For UI frameworks like Streamlit:
```toml
streamlit = "1.31.0"  # Exact version for stability
```

For libraries:
```toml
jinja2 = "^3.1.3"  # Caret for compatible updates
```

### 4. Regular Updates

```bash
# Check for updates weekly
poetry show --outdated

# Update carefully
poetry update

# Test after updates
poetry run pytest
```

### 5. CI/CD Integration

```yaml
# .github/workflows/test.yml
- name: Install Poetry
  run: pip install poetry

- name: Install dependencies
  run: poetry install

- name: Run tests
  run: poetry run pytest --cov
```

## 📚 Resources

- **Official Documentation**: https://python-poetry.org/docs/
- **CLI Reference**: https://python-poetry.org/docs/cli/
- **Configuration**: https://python-poetry.org/docs/configuration/
- **pyproject.toml Spec**: https://python-poetry.org/docs/pyproject/
- **Dependency Management**: https://python-poetry.org/docs/managing-dependencies/

## 🤝 Contributing

When contributing to the project:

1. Install with dev dependencies:
   ```bash
   poetry install
   ```

2. Run pre-commit checks:
   ```bash
   poetry run black .
   poetry run isort .
   poetry run flake8
   poetry run mypy .
   ```

3. Run tests:
   ```bash
   poetry run pytest --cov
   ```

4. Update dependencies if needed:
   ```bash
   poetry add new-package
   poetry lock
   ```

5. Commit changes including poetry.lock:
   ```bash
   git add pyproject.toml poetry.lock
   git commit -m "Add new dependency"
   ```

## 🆘 Getting Help

- Check Poetry docs: https://python-poetry.org/docs/
- Open issue on GitHub: <repository-url>/issues
- See `streamlit-app/POETRY.md` for detailed commands
- Ask in project discussions

---

**Note**: This guide focuses on the Streamlit UI component. The Worker component uses npm/package.json for dependency management.
