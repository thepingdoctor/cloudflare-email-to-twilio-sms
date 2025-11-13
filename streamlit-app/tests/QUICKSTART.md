# Test Suite Quick Start Guide

Get started with testing in 60 seconds!

## 🚀 Quick Setup

```bash
# 1. Install test dependencies
pip install -r tests/requirements-test.txt

# 2. Run all tests
make test

# 3. View coverage
make coverage-html
open htmlcov/index.html  # Mac
xdg-open htmlcov/index.html  # Linux
```

## ⚡ Common Commands

```bash
# Fast test run (unit tests only)
make quick

# Run specific category
make test-unit          # Unit tests
make test-integration   # Integration tests
make test-security      # Security tests

# Run with coverage
make coverage

# Clean artifacts
make clean
```

## 📊 Quick Check

```bash
# Verify tests work
make verify

# Count tests
make count-tests

# Run in parallel (fast!)
make test-parallel
```

## 🎯 For CI/CD

```bash
# Run full CI pipeline
make ci
# This runs: install → test-all → lint
```

## 📖 Full Documentation

See `tests/README.md` for complete documentation.

## ✅ Success Indicators

- **365+ tests** across all categories
- **~90% code coverage** (target: 85%)
- **All tests passing** ✓
- **Security tested** ✓
- **Production ready** ✓
