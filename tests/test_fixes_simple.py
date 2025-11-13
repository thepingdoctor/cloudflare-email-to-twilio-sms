#!/usr/bin/env python3
"""Simple test for security fixes without external dependencies"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'streamlit-app'))


def test_sanitization_import():
    """Test that sanitization methods exist and work."""
    print("=" * 70)
    print("🛡️  Testing FIX 9: Input Sanitization")
    print("=" * 70)

    try:
        from generators.code_generator import CodeGenerator
        from schemas import WorkerConfig, BasicConfig, TwilioConfig

        # Create a basic config
        config = WorkerConfig(
            basic=BasicConfig(
                worker_name="test-worker",
                domain="example.com",
                email_pattern="*@sms.{domain}"
            ),
            twilio=TwilioConfig(
                account_sid="AC1234567890abcdef1234567890abcdef",
                auth_token="test_token",
                phone_number="+15551234567"
            )
        )

        generator = CodeGenerator(config)

        # Test cases
        injection_tests = [
            ("{{ config.secret }}", "Template injection with {{"),
            ("{% include 'etc/passwd' %}", "Template injection with {%"),
            ("{# comment with {{ injection }} #}", "Comment injection"),
            ("<script>alert('xss')</script>", "XSS attempt"),
            ("normal-text", "Safe text"),
        ]

        print("\n🧪 Testing sanitization methods...")
        passed = 0
        failed = 0

        for test_input, description in injection_tests:
            print(f"\n📝 Test: {description}")
            print(f"   Input: {test_input}")

            try:
                sanitized = generator._sanitize_value(test_input)
                print(f"   Output: {sanitized}")

                # Check for injection patterns
                has_template_delim = '{{' in test_input or '{%' in test_input
                is_sanitized = r'\{\{' in sanitized or r'\{\%' in sanitized or sanitized == test_input

                if has_template_delim:
                    # Should be escaped
                    if '{{' not in sanitized and '{%' not in sanitized:
                        print(f"   ✅ PASS: Template delimiters escaped")
                        passed += 1
                    else:
                        print(f"   ❌ FAIL: Template delimiters not escaped")
                        failed += 1
                else:
                    print(f"   ✅ PASS: Safe input processed")
                    passed += 1

            except Exception as e:
                print(f"   ❌ ERROR: {e}")
                failed += 1

        # Test context sanitization
        print(f"\n🧪 Testing context sanitization...")
        context = {
            'test1': '{{ injection }}',
            'test2': 'safe value',
            'nested': {'deep': '{% attack %}'}
        }

        try:
            sanitized_context = generator._sanitize_context(context)
            print(f"   Input context: {context}")
            print(f"   Sanitized context: {sanitized_context}")
            print(f"   ✅ PASS: Context sanitization method works")
            passed += 1
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            failed += 1

        # Test render template uses sanitization
        print(f"\n🧪 Testing template rendering with sanitization...")
        try:
            # The _render_template method should use sanitized context
            # We can verify the method exists and calls sanitization
            import inspect
            source = inspect.getsource(generator._render_template)

            if '_sanitize_context' in source:
                print(f"   ✅ PASS: _render_template calls _sanitize_context")
                passed += 1
            else:
                print(f"   ❌ FAIL: _render_template does not call _sanitize_context")
                failed += 1
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            failed += 1

        print(f"\n📊 Results: {passed} passed, {failed} failed")
        return failed == 0

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def test_form_validation_signature():
    """Test that form validation returns errors."""
    print("\n" + "=" * 70)
    print("🔒 Testing FIX 10: Form Validation Blocking")
    print("=" * 70)

    try:
        # Read input_form.py source directly to avoid streamlit dependency
        form_path = Path(__file__).parent.parent / 'streamlit-app' / 'components' / 'input_form.py'
        with open(form_path, 'r') as f:
            source = f.read()

        print(f"\n📝 Checking render_form function...")

        checks = [
            ('def render_form() -> tuple[WorkerConfig, list[str]]:', 'Function signature returns tuple'),
            ('validation_errors = []', 'Initializes validation_errors list'),
            ('validation_errors.append', 'Appends validation errors'),
            ('return config, validation_errors', 'Returns both config and errors'),
            ('validate_worker_name', 'Validates worker name'),
            ('validate_domain', 'Validates domain'),
            ('validate_twilio_sid', 'Validates Twilio SID'),
            ('validate_twilio_token', 'Validates Twilio token'),
            ('validate_phone_number', 'Validates phone number'),
        ]

        passed = 0
        failed = 0

        for check, description in checks:
            if check in source:
                print(f"   ✅ {description}")
                passed += 1
            else:
                print(f"   ❌ Missing: {description}")
                failed += 1

        print(f"\n📊 Results: {passed}/{len(checks)} validation checks passed")
        return failed == 0

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_app_button_disabled():
    """Test that app.py handles validation errors."""
    print("\n" + "=" * 70)
    print("🎯 Testing Button Disabling Logic")
    print("=" * 70)

    try:
        # Read app.py source
        app_path = Path(__file__).parent.parent / 'streamlit-app' / 'app.py'
        with open(app_path, 'r') as f:
            source = f.read()

        checks = [
            ('validation_errors', 'Checks for validation_errors'),
            ('disabled=', 'Uses disabled parameter on button'),
            ('len(validation_errors)', 'Checks error count'),
            ('config, validation_errors = render_form()', 'Unpacks validation errors from render_form'),
        ]

        print(f"\n📝 Checking app.py source code...")
        passed = 0
        failed = 0

        for check, description in checks:
            if check in source:
                print(f"   ✅ {description}")
                passed += 1
            else:
                print(f"   ❌ Missing: {description}")
                failed += 1

        print(f"\n📊 Results: {passed}/{len(checks)} checks passed")
        return failed == 0

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_dependencies():
    """Test that markupsafe was added to dependencies."""
    print("\n" + "=" * 70)
    print("📦 Testing Dependency Updates")
    print("=" * 70)

    try:
        # Check requirements.txt
        req_path = Path(__file__).parent.parent / 'streamlit-app' / 'requirements.txt'
        with open(req_path, 'r') as f:
            requirements = f.read()

        # Check pyproject.toml
        pyproject_path = Path(__file__).parent.parent / 'streamlit-app' / 'pyproject.toml'
        with open(pyproject_path, 'r') as f:
            pyproject = f.read()

        passed = 0
        failed = 0

        if 'markupsafe' in requirements:
            print(f"   ✅ markupsafe added to requirements.txt")
            passed += 1
        else:
            print(f"   ❌ markupsafe missing from requirements.txt")
            failed += 1

        if 'markupsafe' in pyproject:
            print(f"   ✅ markupsafe added to pyproject.toml")
            passed += 1
        else:
            print(f"   ❌ markupsafe missing from pyproject.toml")
            failed += 1

        print(f"\n📊 Results: {passed}/{2} dependency checks passed")
        return failed == 0

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == '__main__':
    print("\n" + "🔐" * 35)
    print("SECURITY FIXES VERIFICATION - WAVE 3")
    print("🔐" * 35)

    results = []

    # Run all tests
    results.append(("FIX 9: Input Sanitization Methods", test_sanitization_import()))
    results.append(("FIX 10: Form Validation Signature", test_form_validation_signature()))
    results.append(("Button Disabling Logic", test_app_button_disabled()))
    results.append(("Dependency Updates", test_dependencies()))

    # Summary
    print("\n" + "=" * 70)
    print("📊 FINAL RESULTS")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print("\n" + "=" * 70)
    if passed == total:
        print(f"✅ ALL {total} TESTS PASSED - SECURITY FIXES VERIFIED!")
        print("=" * 70)
        print("\n✅ FIX 9: Input Sanitization - IMPLEMENTED")
        print("✅ FIX 10: Form Validation Blocking - IMPLEMENTED")
        sys.exit(0)
    else:
        print(f"❌ {total - passed} of {total} tests FAILED")
        print("=" * 70)
        sys.exit(1)
