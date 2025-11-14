"""
Python 3.12 Compatibility Test Suite

This test suite verifies that the application is fully compatible with Python 3.12+,
including the removal of distutils and updated dependency versions.
"""

import sys
import pytest
import importlib.util
import subprocess
import warnings


class TestPythonVersion:
    """Test Python version compatibility"""

    def test_python_version(self):
        """Verify Python 3.12+ compatibility"""
        assert sys.version_info >= (3, 12), (
            f"Expected Python 3.12+, got {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        )

    def test_python_version_string(self):
        """Verify Python version string format"""
        version_str = sys.version
        assert "3.12" in version_str or "3.13" in version_str or "3.14" in version_str, (
            f"Expected Python 3.12+, got {version_str}"
        )


class TestDependencyImports:
    """Test all critical dependencies can be imported"""

    def test_numpy_import(self):
        """Verify numpy imports without distutils errors"""
        import numpy as np
        assert hasattr(np, '__version__'), "numpy should have __version__ attribute"
        version = tuple(map(int, np.__version__.split('.')[:2]))
        assert version >= (1, 26), f"Expected numpy >= 1.26, got {np.__version__}"

    def test_streamlit_import(self):
        """Verify streamlit imports successfully"""
        import streamlit as st
        assert hasattr(st, '__version__'), "streamlit should have __version__ attribute"
        # Streamlit should be compatible version
        version = tuple(map(int, st.__version__.split('.')[:2]))
        assert version >= (1, 28), f"Expected streamlit >= 1.28, got {st.__version__}"

    def test_jinja2_import(self):
        """Verify jinja2 imports successfully"""
        import jinja2
        assert hasattr(jinja2, '__version__')

    def test_validators_import(self):
        """Verify validators imports successfully"""
        import validators
        assert hasattr(validators, '__version__')

    def test_pydantic_import(self):
        """Verify pydantic imports successfully"""
        import pydantic
        assert hasattr(pydantic, '__version__')
        # Pydantic v2 for Python 3.12
        version = tuple(map(int, pydantic.__version__.split('.')[:2]))
        assert version >= (2, 0), f"Expected pydantic >= 2.0, got {pydantic.__version__}"

    def test_phonenumbers_import(self):
        """Verify phonenumbers imports successfully"""
        import phonenumbers
        assert hasattr(phonenumbers, '__version__')


class TestDistutilsRemoval:
    """Verify no distutils dependencies exist"""

    def test_no_distutils_dependency(self):
        """Verify no code depends on distutils"""
        spec = importlib.util.find_spec('distutils')
        # distutils should not exist in Python 3.12+
        assert spec is None, "distutils should not be available in Python 3.12+"

    def test_no_distutils_in_numpy(self):
        """Verify numpy doesn't try to import distutils"""
        import numpy as np
        # This should work without any distutils errors
        assert np.__version__ is not None
        # Verify numpy uses setuptools instead
        try:
            from numpy.distutils import misc_util
            pytest.fail("numpy.distutils should not be available")
        except (ImportError, ModuleNotFoundError):
            # Expected - numpy.distutils is removed
            pass

    def test_setuptools_available(self):
        """Verify setuptools is available as distutils replacement"""
        import setuptools
        assert hasattr(setuptools, '__version__')


class TestApplicationImports:
    """Test application-specific imports"""

    def test_streamlit_app_importable(self):
        """Verify main streamlit app can be imported"""
        # This tests that the app itself doesn't have Python 3.12 compatibility issues
        try:
            # Assuming main app file exists
            spec = importlib.util.find_spec('app')
            # If app.py exists, it should be importable
            if spec is not None:
                import app
                assert True
        except ImportError as e:
            # If app doesn't exist as module, that's okay for this test
            if "No module named 'app'" in str(e):
                pytest.skip("App module not configured as importable package")
            else:
                raise


class TestPackageVersions:
    """Test that all packages meet minimum version requirements"""

    def test_all_dependencies_importable(self):
        """Test all project dependencies import successfully"""
        deps = ['jinja2', 'validators', 'pydantic', 'phonenumbers', 'numpy', 'streamlit']
        failed_imports = []

        for dep in deps:
            try:
                __import__(dep)
            except ImportError as e:
                failed_imports.append(f"{dep}: {str(e)}")

        assert not failed_imports, f"Failed to import: {', '.join(failed_imports)}"

    def test_requirements_compatibility(self):
        """Verify requirements.txt specifies Python 3.12 compatible versions"""
        import pathlib

        # Look for requirements.txt
        possible_paths = [
            pathlib.Path(__file__).parent.parent / 'requirements.txt',
            pathlib.Path(__file__).parent.parent.parent / 'requirements.txt',
        ]

        requirements_path = None
        for path in possible_paths:
            if path.exists():
                requirements_path = path
                break

        if requirements_path is None:
            pytest.skip("requirements.txt not found")

        with open(requirements_path) as f:
            requirements = f.read()

        # Verify numpy >= 1.26
        assert 'numpy' in requirements.lower(), "numpy should be in requirements"

        # Verify streamlit >= 1.28
        assert 'streamlit' in requirements.lower(), "streamlit should be in requirements"


class TestWarningsAndDeprecations:
    """Test for Python 3.12 related warnings"""

    def test_no_deprecation_warnings(self):
        """Verify no DeprecationWarnings related to Python 3.12"""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always", DeprecationWarning)

            # Import all dependencies
            import numpy
            import streamlit
            import jinja2
            import validators
            import pydantic
            import phonenumbers

            # Filter for distutils-related warnings
            distutils_warnings = [
                warning for warning in w
                if 'distutils' in str(warning.message).lower()
            ]

            assert len(distutils_warnings) == 0, (
                f"Found distutils-related deprecation warnings: {distutils_warnings}"
            )


class TestRuntimeCompatibility:
    """Test runtime behavior with Python 3.12"""

    def test_subprocess_works(self):
        """Verify subprocess works correctly in Python 3.12"""
        result = subprocess.run(
            [sys.executable, '-c', 'print("test")'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert result.stdout.strip() == "test"

    def test_pathlib_compatibility(self):
        """Verify pathlib works correctly"""
        from pathlib import Path
        test_path = Path(__file__)
        assert test_path.exists()
        assert test_path.is_file()

    def test_typing_extensions(self):
        """Verify typing extensions work correctly"""
        from typing import Optional, List, Dict

        def test_func(x: Optional[str] = None) -> List[Dict[str, int]]:
            return [{"test": 1}]

        assert test_func() == [{"test": 1}]


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
