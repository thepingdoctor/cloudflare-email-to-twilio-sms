# Testing Strategy for Python 3.12 Compatibility

## Overview

This document outlines the comprehensive testing strategy for ensuring Python 3.12 compatibility, particularly focusing on the removal of `distutils` and updated dependency requirements.

## Testing Objectives

1. **Version Verification**: Ensure Python 3.12+ is being used
2. **Dependency Compatibility**: Verify all dependencies work with Python 3.12
3. **Distutils Removal**: Confirm no code relies on deprecated distutils
4. **Runtime Behavior**: Validate application functions correctly
5. **Warning Detection**: Catch deprecation warnings early

## Test Categories

### 1. Python Version Tests

**Purpose**: Verify the runtime environment meets minimum requirements

**Tests**:
- `test_python_version()`: Checks Python >= 3.12
- `test_python_version_string()`: Validates version string format

**Critical**: These tests must pass first, as all other tests depend on correct Python version.

### 2. Dependency Import Tests

**Purpose**: Ensure all critical dependencies can be imported without errors

**Key Dependencies**:
- **numpy >= 1.26.0**: First version compatible with Python 3.12 (no distutils)
- **streamlit >= 1.28.0**: Compatible with numpy 1.26+
- **pydantic >= 2.0**: Required for Python 3.12 compatibility
- **jinja2**: Template engine
- **validators**: Data validation
- **phonenumbers**: Phone number parsing

**Tests**:
```python
def test_numpy_import():
    """Verify numpy >= 1.26 without distutils errors"""
    import numpy as np
    assert tuple(map(int, np.__version__.split('.')[:2])) >= (1, 26)

def test_streamlit_import():
    """Verify streamlit >= 1.28"""
    import streamlit as st
    assert tuple(map(int, st.__version__.split('.')[:2])) >= (1, 28)
```

### 3. Distutils Removal Tests

**Purpose**: Verify distutils is completely removed and not used

**Tests**:
- `test_no_distutils_dependency()`: Confirms distutils module doesn't exist
- `test_no_distutils_in_numpy()`: Verifies numpy doesn't use numpy.distutils
- `test_setuptools_available()`: Confirms setuptools (replacement) exists

**Why Critical**:
Python 3.12 removed distutils entirely. Any dependency on it will cause import errors.

### 4. Runtime Compatibility Tests

**Purpose**: Verify runtime behavior works correctly with Python 3.12

**Tests**:
- `test_subprocess_works()`: Subprocess module compatibility
- `test_pathlib_compatibility()`: Path operations
- `test_typing_extensions()`: Type hints and annotations

### 5. Warning Detection Tests

**Purpose**: Catch deprecation warnings that may indicate future issues

**Tests**:
```python
def test_no_deprecation_warnings():
    """Catch distutils-related warnings during imports"""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always", DeprecationWarning)
        import numpy, streamlit  # etc.
        distutils_warnings = [w for w in w if 'distutils' in str(w.message)]
        assert len(distutils_warnings) == 0
```

## Test Execution

### Running Tests

```bash
# Run all compatibility tests
pytest tests/test_python312_compat.py -v

# Run specific test class
pytest tests/test_python312_compat.py::TestDependencyImports -v

# Run with coverage
pytest tests/test_python312_compat.py --cov=. --cov-report=html

# Run verification script
bash scripts/verify_install.sh
```

### Test Environment Setup

```bash
# Create Python 3.12 environment
python3.12 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Install test dependencies
pip install pytest pytest-cov
```

## Continuous Integration

### GitHub Actions Configuration

```yaml
name: Python 3.12 Compatibility

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.12", "3.13"]

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run compatibility tests
        run: pytest tests/test_python312_compat.py -v

      - name: Run verification script
        run: bash scripts/verify_install.sh
```

## Test Coverage Requirements

- **Minimum Coverage**: 90% for compatibility tests
- **Critical Paths**: 100% coverage for import and version checks
- **Warning Detection**: Must catch all deprecation warnings

## Troubleshooting Common Issues

### Issue 1: numpy Import Error

**Symptom**: `ModuleNotFoundError: No module named 'numpy.distutils'`

**Solution**:
```bash
pip install --upgrade "numpy>=1.26.0"
```

### Issue 2: Streamlit Compatibility

**Symptom**: Streamlit fails with numpy version mismatch

**Solution**:
```bash
pip install --upgrade "streamlit>=1.28.0" "numpy>=1.26.0"
```

### Issue 3: Pydantic v1 Issues

**Symptom**: Pydantic validation errors or deprecation warnings

**Solution**:
```bash
pip install --upgrade "pydantic>=2.0"
```

## Test Maintenance

### When to Update Tests

1. **Python Version Changes**: When supporting Python 3.13+
2. **Dependency Updates**: When major versions of dependencies change
3. **New Features**: When adding features that use Python 3.12-specific capabilities
4. **Security Updates**: When dependencies have security patches

### Version Pinning Strategy

```
# requirements.txt
numpy>=1.26.0,<2.0.0
streamlit>=1.28.0,<2.0.0
pydantic>=2.0.0,<3.0.0
jinja2>=3.1.0
validators>=0.22.0
phonenumbers>=8.13.0
```

**Rationale**:
- Upper bounds prevent breaking changes
- Lower bounds ensure Python 3.12 compatibility
- Regular updates within bounds for security patches

## Performance Benchmarks

### Baseline Performance Tests

```python
def test_import_performance():
    """Verify imports complete within acceptable time"""
    import time
    start = time.time()
    import numpy, streamlit, jinja2, validators, pydantic
    duration = time.time() - start
    assert duration < 5.0, f"Imports took {duration}s (expected < 5s)"
```

## Security Considerations

1. **Dependency Scanning**: Run `pip audit` regularly
2. **CVE Monitoring**: Subscribe to security advisories for all dependencies
3. **Version Pinning**: Use exact versions in production
4. **Virtual Environments**: Always isolate environments

## Documentation

### Test Documentation Standards

Each test must include:
- Clear docstring explaining purpose
- Expected behavior
- Failure conditions
- Related dependencies

Example:
```python
def test_numpy_import(self):
    """
    Verify numpy imports without distutils errors.

    This test ensures numpy >= 1.26 is installed, which is the first
    version compatible with Python 3.12's removal of distutils.

    Failure indicates:
    - numpy < 1.26 is installed
    - numpy import fails due to missing dependencies
    - distutils-related import errors
    """
    import numpy as np
    assert tuple(map(int, np.__version__.split('.')[:2])) >= (1, 26)
```

## Metrics and Reporting

### Key Metrics

1. **Test Pass Rate**: Should be 100%
2. **Code Coverage**: Minimum 90%
3. **Execution Time**: All tests < 30 seconds
4. **Warning Count**: 0 deprecation warnings

### Reporting Format

```bash
# Generate test report
pytest tests/test_python312_compat.py \
    --html=reports/compatibility-report.html \
    --cov=. \
    --cov-report=html:reports/coverage \
    -v
```

## Future Considerations

### Python 3.13+ Preparation

- Monitor Python 3.13 alpha/beta releases
- Test with pre-release versions
- Update deprecated features proactively
- Plan migration timeline

### Dependency Evolution

- Track dependency roadmaps
- Participate in beta testing
- Monitor breaking changes
- Plan upgrades strategically

## References

- [Python 3.12 Release Notes](https://docs.python.org/3/whatsnew/3.12.html)
- [PEP 632 - Deprecate distutils](https://peps.python.org/pep-0632/)
- [numpy 1.26 Release Notes](https://numpy.org/doc/stable/release/1.26.0-notes.html)
- [Streamlit Python 3.12 Support](https://docs.streamlit.io/)
- [Pydantic v2 Migration Guide](https://docs.pydantic.dev/latest/migration/)

## Conclusion

This testing strategy ensures robust Python 3.12 compatibility through:
- Comprehensive test coverage
- Automated verification
- Continuous monitoring
- Clear documentation
- Proactive maintenance

By following this strategy, we maintain high confidence in our Python 3.12 compatibility while preparing for future Python versions.
