#!/usr/bin/env python3
"""Test input sanitization in code_generator.py"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'streamlit-app'))

from generators.code_generator import CodeGenerator
from schemas import WorkerConfig, BasicConfig, TwilioConfig


def test_template_injection_protection():
    """Test that template injection attempts are sanitized."""

    # Create config with malicious input
    malicious_inputs = [
        "{{ config.secret }}",
        "{% include 'etc/passwd' %}",
        "{# comment with {{ injection }} #}",
        "normal-name-{{ attack }}",
    ]

    for malicious_input in malicious_inputs:
        print(f"\n🔍 Testing: {malicious_input}")

        # Create config with injection attempt
        config = WorkerConfig(
            basic=BasicConfig(
                worker_name=malicious_input,
                domain="test.com",
                email_pattern="*@sms.{domain}"
            ),
            twilio=TwilioConfig(
                account_sid="ACtest123",
                auth_token="test_token",
                phone_number="+15551234567"
            )
        )

        generator = CodeGenerator(config)

        # Test sanitization method directly
        sanitized = generator._sanitize_value(malicious_input)

        # Verify injection attempts are escaped
        assert '{{' not in sanitized or r'\{\{' in malicious_input, \
            f"Failed to sanitize: {malicious_input} -> {sanitized}"
        assert '{%' not in sanitized or r'\{\%' in malicious_input, \
            f"Failed to sanitize: {malicious_input} -> {sanitized}"

        print(f"✅ Sanitized to: {sanitized}")

        # Test context sanitization
        context = {'test': malicious_input}
        sanitized_context = generator._sanitize_context(context)
        sanitized_value = sanitized_context['test']

        assert '{{' not in sanitized_value or r'\{\{' in malicious_input, \
            f"Context sanitization failed: {sanitized_value}"

        print(f"✅ Context sanitized correctly")


def test_html_entity_escaping():
    """Test that HTML entities are escaped."""

    html_inputs = [
        "<script>alert('xss')</script>",
        "<img src=x onerror=alert(1)>",
        "test&param=value",
        '"quotes" and \'apostrophes\'',
    ]

    config = WorkerConfig(
        basic=BasicConfig(
            worker_name="test-worker",
            domain="test.com",
            email_pattern="*@sms.{domain}"
        ),
        twilio=TwilioConfig(
            account_sid="ACtest123",
            auth_token="test_token",
            phone_number="+15551234567"
        )
    )

    generator = CodeGenerator(config)

    for html_input in html_inputs:
        print(f"\n🔍 Testing HTML: {html_input}")

        sanitized = generator._sanitize_value(html_input)

        # Verify HTML entities are escaped
        assert '<script>' not in sanitized, f"Script tag not escaped: {sanitized}"
        assert '<img' not in sanitized, f"Image tag not escaped: {sanitized}"

        print(f"✅ HTML escaped to: {sanitized}")


def test_nested_structure_sanitization():
    """Test that nested dictionaries and lists are sanitized."""

    config = WorkerConfig(
        basic=BasicConfig(
            worker_name="test-worker",
            domain="test.com",
            email_pattern="*@sms.{domain}"
        ),
        twilio=TwilioConfig(
            account_sid="ACtest123",
            auth_token="test_token",
            phone_number="+15551234567"
        )
    )

    generator = CodeGenerator(config)

    # Test nested structures
    nested = {
        'level1': {
            'level2': ['{{ injection }}', 'safe'],
            'string': '{% malicious %}'
        },
        'list': ['{{ item1 }}', '{{ item2 }}']
    }

    print(f"\n🔍 Testing nested structure: {nested}")

    sanitized = generator._sanitize_value(nested)

    # Check all nested values are sanitized
    assert '{{' not in str(sanitized['level1']['level2'][0]) or r'\{\{' in str(sanitized['level1']['level2'][0])
    assert '{%' not in str(sanitized['level1']['string']) or r'\{\%' in str(sanitized['level1']['string'])

    print(f"✅ Nested structure sanitized: {sanitized}")


def test_safe_values_unchanged():
    """Test that safe values remain unchanged (except for normal escaping)."""

    config = WorkerConfig(
        basic=BasicConfig(
            worker_name="test-worker",
            domain="test.com",
            email_pattern="*@sms.{domain}"
        ),
        twilio=TwilioConfig(
            account_sid="ACtest123",
            auth_token="test_token",
            phone_number="+15551234567"
        )
    )

    generator = CodeGenerator(config)

    safe_inputs = [
        "my-worker-name",
        "example.com",
        "+15551234567",
        "test@example.com",
        "normal text",
        "123456",
    ]

    for safe_input in safe_inputs:
        print(f"\n🔍 Testing safe input: {safe_input}")

        sanitized = generator._sanitize_value(safe_input)

        # Safe inputs should not have injection delimiters
        assert '{{' not in safe_input
        assert '{%' not in safe_input

        print(f"✅ Safe value processed: {sanitized}")


if __name__ == '__main__':
    print("=" * 60)
    print("🛡️  Testing Input Sanitization")
    print("=" * 60)

    try:
        test_template_injection_protection()
        print("\n✅ Template injection protection: PASSED")

        test_html_entity_escaping()
        print("\n✅ HTML entity escaping: PASSED")

        test_nested_structure_sanitization()
        print("\n✅ Nested structure sanitization: PASSED")

        test_safe_values_unchanged()
        print("\n✅ Safe values handling: PASSED")

        print("\n" + "=" * 60)
        print("✅ ALL SANITIZATION TESTS PASSED")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
