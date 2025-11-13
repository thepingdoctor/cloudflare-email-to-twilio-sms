# Python Dependencies - Streamlit Email-to-SMS Code Generator

## Core Dependencies

### Runtime Requirements

```txt
# requirements.txt

# Web Framework
streamlit==1.31.0
# Modern data app framework for Python
# Used for: Main UI framework, form handling, layout

# Template Engine
jinja2==3.1.3
# Template engine for Python
# Used for: Code generation templates, dynamic content

# Syntax Highlighting
pygments==2.17.2
# Python syntax highlighter
# Used for: Code syntax highlighting in UI

# Validation
validators==0.22.0
# Python data validation library
# Used for: Email, domain, URL validation

pydantic==2.6.0
# Data validation using Python type annotations
# Used for: Configuration schema validation, type safety

# Type Hints
typing-extensions==4.9.0
# Backport of typing module enhancements
# Used for: Advanced type hints, dataclasses

# Environment Variables
python-dotenv==1.0.1
# Read key-value pairs from .env file
# Used for: Loading environment variables, configuration

# File Operations
zipfile36==0.1.3
# Enhanced zipfile module
# Used for: Creating ZIP archives for download

# String Utilities
python-slugify==8.0.4
# Convert strings to URL-friendly slugs
# Used for: Sanitizing worker names, file names

# Phone Number Handling
phonenumbers==8.13.29
# Parse and format phone numbers
# Used for: Phone number validation, E.164 formatting

# Date/Time
python-dateutil==2.8.2
# Extensions to datetime module
# Used for: Timestamp handling, date formatting
```

### Development Dependencies

```txt
# requirements-dev.txt

# Code Formatting
black==24.1.1
# Python code formatter
# Used for: Auto-formatting generated Python code

isort==5.13.2
# Import statement sorter
# Used for: Organizing imports in generated code

# Linting
pylint==3.0.3
# Python code analyzer
# Used for: Code quality checks

flake8==7.0.0
# Python linting tool
# Used for: Style guide enforcement

mypy==1.8.0
# Static type checker
# Used for: Type checking, catching type errors

# Testing
pytest==8.0.0
# Testing framework
# Used for: Unit and integration testing

pytest-cov==4.1.0
# Coverage plugin for pytest
# Used for: Test coverage reporting

pytest-mock==3.12.0
# Mock/stub plugin for pytest
# Used for: Mocking in tests

# Documentation
sphinx==7.2.6
# Documentation generator
# Used for: API documentation

sphinx-rtd-theme==2.0.0
# ReadTheDocs Sphinx theme
# Used for: Documentation styling

# Pre-commit Hooks
pre-commit==3.6.0
# Git pre-commit hook framework
# Used for: Automated code quality checks
```

### Optional Dependencies

```txt
# requirements-optional.txt

# Enhanced UI Components
streamlit-code-editor==0.1.16
# Code editor component for Streamlit
# Used for: Interactive code editing

streamlit-extras==0.3.6
# Additional Streamlit components
# Used for: Enhanced UI widgets, utilities

streamlit-option-menu==0.3.12
# Custom option menu component
# Used for: Better navigation menus

# Syntax Highlighting (Alternative)
prismjs==1.29.0
# JavaScript syntax highlighter
# Used for: Alternative syntax highlighting

# Markdown
markdown==3.5.2
# Python Markdown implementation
# Used for: Rendering markdown documentation

markdown-it-py==3.0.0
# Markdown parser
# Used for: Advanced markdown features

# JSON Handling
orjson==3.9.13
# Fast JSON library
# Used for: Faster JSON serialization

# TOML Parsing
toml==0.10.2
# TOML parser
# Used for: Parsing wrangler.toml files

tomli==2.0.1
# TOML parser (Python 3.11+)
# Used for: Modern TOML parsing

# Code Formatting (TypeScript)
black-ts==0.1.0
# TypeScript code formatter
# Used for: Formatting generated TypeScript

# HTTP Requests
requests==2.31.0
# HTTP library
# Used for: API calls, webhooks

httpx==0.26.0
# Async HTTP client
# Used for: Async API operations

# Caching
streamlit-cache==0.1.0
# Enhanced caching for Streamlit
# Used for: Performance optimization

# Session Management
streamlit-session-browser-storage==0.0.3
# Browser storage for Streamlit
# Used for: Persistent session data

# Analytics
google-analytics-data==0.18.7
# Google Analytics Data API
# Used for: Usage analytics (optional)
```

## Dependency Categories

### 1. UI Framework (Streamlit)
```python
streamlit==1.31.0
streamlit-code-editor==0.1.16
streamlit-extras==0.3.6
streamlit-option-menu==0.3.12
```

**Purpose:** Core UI framework and components

### 2. Code Generation
```python
jinja2==3.1.3
black==24.1.1
isort==5.13.2
```

**Purpose:** Template rendering and code formatting

### 3. Validation
```python
pydantic==2.6.0
validators==0.22.0
phonenumbers==8.13.29
```

**Purpose:** Input validation and data integrity

### 4. File Handling
```python
zipfile36==0.1.3
python-dotenv==1.0.1
toml==0.10.2
```

**Purpose:** File operations and configuration

### 5. Syntax Highlighting
```python
pygments==2.17.2
prismjs==1.29.0
```

**Purpose:** Code display with syntax highlighting

### 6. Testing
```python
pytest==8.0.0
pytest-cov==4.1.0
pytest-mock==3.12.0
```

**Purpose:** Testing framework and tools

### 7. Documentation
```python
sphinx==7.2.6
sphinx-rtd-theme==2.0.0
markdown==3.5.2
```

**Purpose:** Documentation generation

## Installation

### Basic Installation

```bash
# Install core dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Install optional dependencies
pip install -r requirements-optional.txt
```

### Docker Installation

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt requirements-dev.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements-dev.txt

# Copy application
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "src/streamlit/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Virtual Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

## Version Pinning Strategy

### Strict Pinning (Production)
```txt
# Pin exact versions for reproducibility
streamlit==1.31.0
jinja2==3.1.3
```

### Flexible Pinning (Development)
```txt
# Allow minor version updates
streamlit>=1.31.0,<2.0.0
jinja2>=3.1.0,<4.0.0
```

### Latest (Testing)
```txt
# Use latest versions for testing
streamlit
jinja2
```

## Dependency Management

### Using pip-tools

```bash
# Install pip-tools
pip install pip-tools

# Compile requirements
pip-compile requirements.in -o requirements.txt

# Sync environment
pip-sync requirements.txt
```

### Using Poetry

```toml
# pyproject.toml
[tool.poetry]
name = "email-to-sms-generator"
version = "1.0.0"

[tool.poetry.dependencies]
python = "^3.11"
streamlit = "^1.31.0"
jinja2 = "^3.1.3"
pydantic = "^2.6.0"

[tool.poetry.dev-dependencies]
pytest = "^8.0.0"
black = "^24.1.1"
```

```bash
# Install with Poetry
poetry install

# Add dependency
poetry add streamlit

# Update dependencies
poetry update
```

## Security Considerations

### Vulnerability Scanning

```bash
# Install safety
pip install safety

# Check for vulnerabilities
safety check --json

# Check with pip-audit
pip install pip-audit
pip-audit
```

### Dependency Updates

```bash
# Check outdated packages
pip list --outdated

# Update specific package
pip install --upgrade streamlit

# Update all packages (careful!)
pip install --upgrade -r requirements.txt
```

## Platform-Specific Notes

### Windows
```txt
# Additional Windows dependencies
pywin32==306
# Required for some system operations
```

### Linux
```txt
# No additional dependencies usually needed
```

### macOS
```txt
# May need specific versions for M1/M2
# Use native builds when available
```

## Troubleshooting

### Common Issues

**Issue: Streamlit not found**
```bash
# Solution: Ensure correct environment
which python
which streamlit
```

**Issue: Module import errors**
```bash
# Solution: Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

**Issue: Version conflicts**
```bash
# Solution: Use virtual environment
python -m venv fresh-env
source fresh-env/bin/activate
pip install -r requirements.txt
```

## Performance Optimization

### Caching Dependencies

```bash
# Use pip cache
pip cache info

# Download wheels for offline install
pip download -r requirements.txt -d wheels/

# Install from wheels
pip install --no-index --find-links=wheels/ -r requirements.txt
```

### Minimal Installation

```txt
# requirements-minimal.txt
# Only essential dependencies for production
streamlit==1.31.0
jinja2==3.1.3
pydantic==2.6.0
validators==0.22.0
```

## License Information

All dependencies are open-source with compatible licenses:
- Streamlit: Apache 2.0
- Jinja2: BSD-3-Clause
- Pydantic: MIT
- Pygments: BSD-2-Clause
- Validators: MIT

## Update Schedule

- **Security updates**: Immediate
- **Minor updates**: Monthly review
- **Major updates**: Quarterly evaluation
- **Dependency audit**: Bi-annually

## References

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Jinja2 Documentation](https://jinja.palletsprojects.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Python Packaging Guide](https://packaging.python.org/)
