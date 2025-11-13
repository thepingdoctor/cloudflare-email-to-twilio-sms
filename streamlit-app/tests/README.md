# Streamlit App Test Suite

Comprehensive test suite for the Email-to-SMS Streamlit code generator.

## 📋 Test Structure

```
tests/
├── conftest.py              # Pytest configuration and fixtures
├── pytest.ini               # Pytest settings
├── requirements-test.txt    # Test dependencies
├── test_validators.py       # Validation logic tests (>85% coverage)
├── test_generators.py       # Code generation tests
├── test_components.py       # UI component tests
├── test_integration.py      # End-to-end integration tests
├── test_edge_cases.py       # Edge cases and boundary tests
└── test_utils.py            # Test utility functions
```

## 🚀 Running Tests

### Install Test Dependencies

```bash
pip install -r requirements-test.txt
```

### Run All Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html --cov-report=term-missing

# Run with verbose output
pytest -v
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# UI tests (requires Streamlit testing framework)
pytest -m ui

# Security tests
pytest -m security

# Performance tests
pytest -m performance

# Edge case tests
pytest -m edge_case

# Exclude slow tests
pytest -m "not slow"
```

### Run Specific Test Files

```bash
# Run validator tests only
pytest tests/test_validators.py

# Run generator tests only
pytest tests/test_generators.py

# Run specific test class
pytest tests/test_validators.py::TestWorkerNameValidation

# Run specific test function
pytest tests/test_validators.py::TestWorkerNameValidation::test_valid_worker_names
```

### Parallel Execution

```bash
# Run tests in parallel (requires pytest-xdist)
pytest -n auto
```

## 📊 Coverage Report

Generate coverage report:

```bash
# HTML report
pytest --cov=. --cov-report=html
# Open htmlcov/index.html in browser

# Terminal report
pytest --cov=. --cov-report=term-missing

# XML report (for CI/CD)
pytest --cov=. --cov-report=xml
```

### Coverage Goals

- **Overall**: >85%
- **Validators**: >90%
- **Generators**: >85%
- **Components**: >80%

## 🧪 Test Categories

### Unit Tests (`@pytest.mark.unit`)
Tests for individual functions and methods:
- Validation functions
- Code generation logic
- Template rendering
- Configuration handling

### Integration Tests (`@pytest.mark.integration`)
Tests for component interaction:
- Form → Generator → Files pipeline
- Configuration serialization
- ZIP file creation
- Multi-component workflows

### UI Tests (`@pytest.mark.ui`)
Tests for Streamlit UI components:
- Form rendering
- Input validation feedback
- User interaction flows
- Download functionality

**Note**: UI tests require Streamlit >= 1.28.0 with testing framework.

### Security Tests (`@pytest.mark.security`)
Security-focused tests:
- XSS payload rejection
- SQL injection prevention
- Template injection handling
- Path traversal protection
- Credential sanitization

### Performance Tests (`@pytest.mark.performance`)
Performance and benchmarking:
- Validation speed (<100ms)
- Code generation speed (<2s)
- Large input handling
- Concurrent operations

### Edge Case Tests (`@pytest.mark.edge_case`)
Boundary conditions and special cases:
- Unicode handling
- Boundary values
- Empty inputs
- Large configurations

## 📝 Writing New Tests

### Test Naming Convention

```python
class TestComponentName:
    """Test description."""

    def test_expected_behavior_when_condition(self):
        """Test that X does Y when Z."""
        # Arrange
        setup_data = ...

        # Act
        result = function_under_test(setup_data)

        # Assert
        assert result == expected_value
```

### Using Fixtures

```python
def test_with_fixtures(valid_worker_config, unicode_test_data):
    """Use fixtures from conftest.py."""
    # Fixtures are automatically injected
    assert valid_worker_config.basic.worker_name
```

### Adding Markers

```python
@pytest.mark.unit
@pytest.mark.security
def test_xss_prevention():
    """Mark tests with appropriate categories."""
    pass
```

## 🔧 Available Fixtures

### Configuration Fixtures
- `valid_basic_config` - Valid basic settings
- `valid_twilio_config` - Valid Twilio credentials
- `valid_worker_config` - Complete valid configuration
- `invalid_worker_name_configs` - Invalid worker names
- `invalid_domains` - Invalid domain formats
- `invalid_emails` - Invalid email formats
- `invalid_phone_numbers` - Invalid phone formats

### Test Data Fixtures
- `security_payloads` - XSS, SQL injection, etc.
- `unicode_test_data` - Unicode and emoji strings
- `boundary_values` - Min/max values
- `generated_file_templates` - Expected file structure

### Utility Fixtures
- `temp_test_dir` - Temporary directory
- `assert_valid_typescript` - TypeScript validation
- `assert_valid_toml` - TOML validation
- `assert_valid_json` - JSON validation

## 🐛 Debugging Tests

### Run with debugging output

```bash
# Show print statements
pytest -s

# Show local variables on failure
pytest -l

# Drop into debugger on failure
pytest --pdb

# More verbose output
pytest -vv
```

### Run single failing test

```bash
pytest tests/test_validators.py::test_failing_test -vv
```

## 📈 Continuous Integration

### GitHub Actions Example

```yaml
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

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r tests/requirements-test.txt

      - name: Run tests
        run: pytest --cov=. --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## 📚 Best Practices

1. **Test First**: Write tests before implementation (TDD)
2. **One Assertion**: Each test should verify one behavior
3. **Descriptive Names**: Test names should explain what and why
4. **AAA Pattern**: Arrange, Act, Assert structure
5. **Use Fixtures**: Avoid test interdependence
6. **Mock External Deps**: Keep tests isolated
7. **Fast Tests**: Unit tests should run in <100ms
8. **Clear Failures**: Assertion messages should be helpful

## 🎯 Test Coverage Goals

### Current Coverage
Run `pytest --cov=. --cov-report=term-missing` to see current coverage.

### Areas Requiring Coverage
- [ ] All validator functions >90%
- [ ] All generator methods >85%
- [ ] All UI components >80%
- [ ] Edge cases >75%
- [ ] Integration flows >85%

## 🔍 Test Metrics

```bash
# Generate test metrics
pytest --verbose --tb=no | grep -E "passed|failed|errors"

# Count tests by marker
pytest --collect-only -m unit | grep "test session"
pytest --collect-only -m integration | grep "test session"
pytest --collect-only -m security | grep "test session"
```

## 📞 Support

For questions about tests:
1. Check test docstrings for expected behavior
2. Review conftest.py for available fixtures
3. See TESTING_STRATEGY.md for overall approach
4. Consult pytest documentation: https://docs.pytest.org/

## 🔄 Updating Tests

When adding new features:
1. Add test fixtures in `conftest.py`
2. Write unit tests in appropriate `test_*.py` file
3. Add integration test if needed
4. Update this README if adding new patterns
5. Ensure coverage stays above 85%

---

**Remember**: Good tests are the safety net for confident refactoring!
