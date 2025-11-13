#!/usr/bin/env python3
"""Test form validation blocking functionality"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'streamlit-app'))

from schemas import WorkerConfig, BasicConfig, TwilioConfig, EmailRoutingConfig
from schemas import RateLimitConfig, LoggingConfig, SecurityConfig, RetryConfig, IntegrationConfig
from utils import validate_worker_name, validate_domain, validate_twilio_sid, validate_twilio_token, validate_phone_number


def simulate_validation_errors():
    """Simulate validation scenarios that should block generation."""

    test_cases = [
        {
            "name": "Invalid Worker Name (contains spaces)",
            "worker_name": "my worker name",
            "domain": "example.com",
            "twilio_sid": "AC1234567890abcdef1234567890abcdef",
            "twilio_token": "abc123def456",
            "twilio_phone": "+15551234567",
            "should_have_errors": True
        },
        {
            "name": "Invalid Domain (no TLD)",
            "worker_name": "my-worker",
            "domain": "notadomain",
            "twilio_sid": "AC1234567890abcdef1234567890abcdef",
            "twilio_token": "abc123def456",
            "twilio_phone": "+15551234567",
            "should_have_errors": True
        },
        {
            "name": "Invalid Twilio SID (wrong prefix)",
            "worker_name": "my-worker",
            "domain": "example.com",
            "twilio_sid": "XX1234567890abcdef1234567890abcdef",
            "twilio_token": "abc123def456",
            "twilio_phone": "+15551234567",
            "should_have_errors": True
        },
        {
            "name": "Invalid Phone Number (no country code)",
            "worker_name": "my-worker",
            "domain": "example.com",
            "twilio_sid": "AC1234567890abcdef1234567890abcdef",
            "twilio_token": "abc123def456",
            "twilio_phone": "5551234567",
            "should_have_errors": True
        },
        {
            "name": "Valid Configuration",
            "worker_name": "my-worker",
            "domain": "example.com",
            "twilio_sid": "AC1234567890abcdef1234567890abcdef",
            "twilio_token": "abc123def456",
            "twilio_phone": "+15551234567",
            "should_have_errors": False
        },
        {
            "name": "Template Injection Attempt in Worker Name",
            "worker_name": "worker-{{ injection }}",
            "domain": "example.com",
            "twilio_sid": "AC1234567890abcdef1234567890abcdef",
            "twilio_token": "abc123def456",
            "twilio_phone": "+15551234567",
            "should_have_errors": True  # Should fail validation due to special chars
        },
    ]

    print("=" * 70)
    print("🧪 Testing Form Validation Blocking")
    print("=" * 70)

    for test in test_cases:
        print(f"\n📋 Test: {test['name']}")
        print(f"   Worker Name: {test['worker_name']}")
        print(f"   Domain: {test['domain']}")
        print(f"   Twilio SID: {test['twilio_sid']}")
        print(f"   Twilio Phone: {test['twilio_phone']}")

        validation_errors = []

        # Validate worker name
        if test['worker_name']:
            is_valid, error = validate_worker_name(test['worker_name'])
            if not is_valid:
                validation_errors.append(f"Worker Name: {error}")
                print(f"   ❌ Worker Name Error: {error}")

        # Validate domain
        if test['domain']:
            is_valid, error = validate_domain(test['domain'])
            if not is_valid:
                validation_errors.append(f"Domain: {error}")
                print(f"   ❌ Domain Error: {error}")
        else:
            validation_errors.append("Domain is required")
            print(f"   ❌ Domain is required")

        # Validate Twilio SID
        if test['twilio_sid']:
            is_valid, error = validate_twilio_sid(test['twilio_sid'])
            if not is_valid:
                validation_errors.append(f"Twilio SID: {error}")
                print(f"   ❌ Twilio SID Error: {error}")

        # Validate Twilio Token
        if test['twilio_token']:
            is_valid, error = validate_twilio_token(test['twilio_token'])
            if not is_valid:
                validation_errors.append(f"Twilio Token: {error}")
                print(f"   ❌ Twilio Token Error: {error}")

        # Validate phone number
        if test['twilio_phone']:
            is_valid, error = validate_phone_number(test['twilio_phone'])
            if not is_valid:
                validation_errors.append(f"Twilio Phone: {error}")
                print(f"   ❌ Twilio Phone Error: {error}")

        # Check if errors match expectation
        has_errors = len(validation_errors) > 0

        if has_errors == test['should_have_errors']:
            print(f"   ✅ PASS: Validation {'blocked' if has_errors else 'allowed'} as expected")
            print(f"   📊 Total Errors: {len(validation_errors)}")
            if has_errors:
                print(f"   🚫 Button would be DISABLED")
            else:
                print(f"   ✅ Button would be ENABLED")
        else:
            print(f"   ❌ FAIL: Expected {'errors' if test['should_have_errors'] else 'no errors'}, got {'errors' if has_errors else 'no errors'}")
            return False

    return True


def test_injection_sanitization():
    """Test that injection attempts are sanitized even if they pass validation."""

    print("\n" + "=" * 70)
    print("🛡️  Testing Injection Sanitization")
    print("=" * 70)

    # Import the code generator
    from generators.code_generator import CodeGenerator

    injection_attempts = [
        "{{ config.secrets }}",
        "{% include '/etc/passwd' %}",
        "{# malicious comment #}",
    ]

    for attempt in injection_attempts:
        print(f"\n🔍 Testing sanitization of: {attempt}")

        config = WorkerConfig(
            basic=BasicConfig(
                worker_name="test-worker",
                domain="example.com",
                email_pattern=attempt  # Try injection in email pattern
            ),
            twilio=TwilioConfig(
                account_sid="AC1234567890abcdef1234567890abcdef",
                auth_token="test_token",
                phone_number="+15551234567"
            )
        )

        generator = CodeGenerator(config)
        sanitized = generator._sanitize_value(attempt)

        # Check that injection delimiters are escaped
        if '{{' in attempt and r'\{\{' not in sanitized:
            print("   ❌ FAIL: {{ not properly escaped")
            return False

        if '{%' in attempt and r'\{\%' not in sanitized:
            print("   ❌ FAIL: {% not properly escaped")
            return False

        print(f"   ✅ PASS: Sanitized to: {sanitized}")

    return True


if __name__ == '__main__':
    try:
        # Test validation blocking
        if not simulate_validation_errors():
            print("\n❌ Validation blocking tests FAILED")
            sys.exit(1)

        print("\n✅ All validation blocking tests PASSED")

        # Test injection sanitization
        if not test_injection_sanitization():
            print("\n❌ Injection sanitization tests FAILED")
            sys.exit(1)

        print("\n✅ All injection sanitization tests PASSED")

        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED - SECURITY FIXES VERIFIED")
        print("=" * 70)
        print("\n✅ FIX 9: Input Sanitization - WORKING")
        print("✅ FIX 10: Form Validation Blocking - WORKING")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
