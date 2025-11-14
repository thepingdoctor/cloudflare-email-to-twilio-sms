#!/bin/bash
# Installation Verification Script for Python 3.12 Compatibility
# This script verifies that all dependencies are correctly installed and compatible

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Python 3.12 Installation Verification"
echo "=========================================="
echo ""

# Function to print success message
success() {
    echo -e "${GREEN}✓${NC} $1"
}

# Function to print error message
error() {
    echo -e "${RED}✗${NC} $1"
}

# Function to print warning message
warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Function to print info message
info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# Check Python version
echo "1. Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 12 ]; then
    success "Python $PYTHON_VERSION detected (3.12+ required)"
else
    error "Python $PYTHON_VERSION detected (3.12+ required)"
    exit 1
fi
echo ""

# Check if distutils is NOT available (expected in Python 3.12+)
echo "2. Verifying distutils removal..."
if python3 -c "import distutils" 2>/dev/null; then
    warning "distutils is still available (should be removed in Python 3.12+)"
else
    success "distutils correctly removed from Python 3.12+"
fi
echo ""

# Check if setuptools is available
echo "3. Checking setuptools availability..."
if python3 -c "import setuptools" 2>/dev/null; then
    SETUPTOOLS_VERSION=$(python3 -c "import setuptools; print(setuptools.__version__)")
    success "setuptools $SETUPTOOLS_VERSION installed"
else
    error "setuptools not found (required as distutils replacement)"
    exit 1
fi
echo ""

# Check pip
echo "4. Checking pip..."
if python3 -m pip --version >/dev/null 2>&1; then
    PIP_VERSION=$(python3 -m pip --version | awk '{print $2}')
    success "pip $PIP_VERSION installed"
else
    error "pip not found"
    exit 1
fi
echo ""

# Check virtual environment (if active)
echo "5. Checking virtual environment..."
if [ -n "$VIRTUAL_ENV" ]; then
    success "Virtual environment active: $VIRTUAL_ENV"
else
    warning "No virtual environment detected (recommended)"
fi
echo ""

# Check critical dependencies
echo "6. Checking critical dependencies..."

# numpy
if python3 -c "import numpy; print(numpy.__version__)" >/dev/null 2>&1; then
    NUMPY_VERSION=$(python3 -c "import numpy; print(numpy.__version__)")
    success "numpy $NUMPY_VERSION installed"
else
    error "numpy not found or failed to import"
    exit 1
fi

# streamlit
if python3 -c "import streamlit; print(streamlit.__version__)" >/dev/null 2>&1; then
    STREAMLIT_VERSION=$(python3 -c "import streamlit; print(streamlit.__version__)")
    success "streamlit $STREAMLIT_VERSION installed"
else
    error "streamlit not found or failed to import"
    exit 1
fi

# jinja2
if python3 -c "import jinja2; print(jinja2.__version__)" >/dev/null 2>&1; then
    JINJA2_VERSION=$(python3 -c "import jinja2; print(jinja2.__version__)")
    success "jinja2 $JINJA2_VERSION installed"
else
    error "jinja2 not found or failed to import"
    exit 1
fi

# validators
if python3 -c "import validators; print(validators.__version__)" >/dev/null 2>&1; then
    VALIDATORS_VERSION=$(python3 -c "import validators; print(validators.__version__)")
    success "validators $VALIDATORS_VERSION installed"
else
    error "validators not found or failed to import"
    exit 1
fi

# pydantic
if python3 -c "import pydantic; print(pydantic.__version__)" >/dev/null 2>&1; then
    PYDANTIC_VERSION=$(python3 -c "import pydantic; print(pydantic.__version__)")
    success "pydantic $PYDANTIC_VERSION installed"
else
    error "pydantic not found or failed to import"
    exit 1
fi

# phonenumbers
if python3 -c "import phonenumbers; print(phonenumbers.__version__)" >/dev/null 2>&1; then
    PHONENUMBERS_VERSION=$(python3 -c "import phonenumbers; print(phonenumbers.__version__)")
    success "phonenumbers $PHONENUMBERS_VERSION installed"
else
    error "phonenumbers not found or failed to import"
    exit 1
fi
echo ""

# Run compatibility tests if pytest is available
echo "7. Running compatibility tests..."
if python3 -m pytest --version >/dev/null 2>&1; then
    info "Running pytest compatibility tests..."

    # Find the test file
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    TEST_FILE="$SCRIPT_DIR/../tests/test_python312_compat.py"

    if [ -f "$TEST_FILE" ]; then
        if python3 -m pytest "$TEST_FILE" -v --tb=short; then
            success "All compatibility tests passed"
        else
            error "Some compatibility tests failed"
            exit 1
        fi
    else
        warning "Test file not found: $TEST_FILE"
    fi
else
    warning "pytest not installed, skipping automated tests"
    info "Install pytest with: pip install pytest"
fi
echo ""

# Check for common issues
echo "8. Checking for common issues..."

# Check numpy distutils usage
if python3 -c "import numpy.distutils" 2>/dev/null; then
    error "numpy still using distutils (incompatible with Python 3.12)"
    info "Update numpy to version >= 1.26.0"
    exit 1
else
    success "numpy not using deprecated distutils"
fi

# Check for __pycache__ directories that might have old compiled code
PYCACHE_COUNT=$(find . -type d -name "__pycache__" 2>/dev/null | wc -l)
if [ "$PYCACHE_COUNT" -gt 0 ]; then
    warning "Found $PYCACHE_COUNT __pycache__ directories"
    info "Consider cleaning with: find . -type d -name '__pycache__' -exec rm -rf {} +"
else
    success "No stale __pycache__ directories found"
fi
echo ""

# Summary
echo "=========================================="
echo "Verification Summary"
echo "=========================================="
echo ""
success "Python $PYTHON_VERSION"
success "All critical dependencies installed"
success "No distutils dependencies detected"
success "Installation is Python 3.12 compatible"
echo ""

# Additional recommendations
echo "Recommendations:"
info "1. Keep dependencies updated regularly"
info "2. Use virtual environments for isolation"
info "3. Run tests before deployment: pytest tests/"
info "4. Monitor deprecation warnings"
echo ""

echo -e "${GREEN}Installation verification complete!${NC}"
exit 0
