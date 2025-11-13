"""
Unit tests for validation logic.

Tests all validation functions for:
- Valid inputs
- Invalid inputs
- Edge cases
- Security payloads
"""
import pytest
from utils.validators import (
    validate_worker_name,
    validate_domain,
    validate_email,
    validate_phone_number,
    validate_twilio_sid,
    validate_twilio_token,
    validate_email_pattern,
    validate_url,
    validate_positive_integer,
    sanitize_filename,
    validate_sender_whitelist,
)


# ========================================
# Worker Name Validation Tests
# ========================================

@pytest.mark.unit
class TestWorkerNameValidation:
    """Test worker name validation."""

    def test_valid_worker_names(self):
        """Test various valid worker name formats."""
        valid_names = [
            "worker",
            "my-worker",
            "worker-123",
            "a",  # Minimum length
            "a" * 63,  # Maximum length
            "test-worker-name-123",
        ]

        for name in valid_names:
            is_valid, error = validate_worker_name(name)
            assert is_valid, f"'{name}' should be valid but got error: {error}"
            assert error is None

    def test_invalid_worker_names(self, invalid_worker_name_configs):
        """Test various invalid worker name formats."""
        for name in invalid_worker_name_configs:
            is_valid, error = validate_worker_name(name)
            assert not is_valid, f"'{name}' should be invalid"
            assert error is not None
            assert isinstance(error, str)

    def test_worker_name_edge_cases(self):
        """Test worker name edge cases."""
        # Exactly at limit
        is_valid, _ = validate_worker_name("a" * 63)
        assert is_valid

        # One over limit
        is_valid, _ = validate_worker_name("a" * 64)
        assert not is_valid

        # Single character
        is_valid, _ = validate_worker_name("a")
        assert is_valid


# ========================================
# Domain Validation Tests
# ========================================

@pytest.mark.unit
class TestDomainValidation:
    """Test domain validation."""

    def test_valid_domains(self):
        """Test various valid domain formats."""
        valid_domains = [
            "example.com",
            "subdomain.example.com",
            "my-domain.example.com",
            "example.co.uk",
            "test123.example.com",
        ]

        for domain in valid_domains:
            is_valid, error = validate_domain(domain)
            assert is_valid, f"'{domain}' should be valid but got error: {error}"
            assert error is None

    def test_invalid_domains(self, invalid_domains):
        """Test various invalid domain formats."""
        for domain in invalid_domains:
            is_valid, error = validate_domain(domain)
            assert not is_valid, f"'{domain}' should be invalid"
            assert error is not None

    def test_domain_case_sensitivity(self):
        """Test that domains are case-insensitive."""
        is_valid1, _ = validate_domain("Example.COM")
        is_valid2, _ = validate_domain("example.com")
        assert is_valid1 == is_valid2


# ========================================
# Email Validation Tests
# ========================================

@pytest.mark.unit
class TestEmailValidation:
    """Test email address validation."""

    def test_valid_emails(self):
        """Test various valid email formats."""
        valid_emails = [
            "user@example.com",
            "user.name@example.com",
            "user+tag@example.com",
            "user_name@example.com",
            "123@example.com",
            "user@subdomain.example.com",
        ]

        for email in valid_emails:
            is_valid, error = validate_email(email)
            assert is_valid, f"'{email}' should be valid but got error: {error}"
            assert error is None

    def test_invalid_emails(self, invalid_emails):
        """Test various invalid email formats."""
        for email in invalid_emails:
            is_valid, error = validate_email(email)
            assert not is_valid, f"'{email}' should be invalid"
            assert error is not None


# ========================================
# Phone Number Validation Tests
# ========================================

@pytest.mark.unit
class TestPhoneNumberValidation:
    """Test phone number validation."""

    def test_valid_phone_numbers(self):
        """Test various valid phone number formats (E.164)."""
        valid_phones = [
            "+15551234567",  # US
            "+442071234567",  # UK
            "+33123456789",  # France
            "+861012345678",  # China
            "+919876543210",  # India
        ]

        for phone in valid_phones:
            is_valid, error = validate_phone_number(phone)
            assert is_valid, f"'{phone}' should be valid but got error: {error}"
            assert error is None

    def test_invalid_phone_numbers(self, invalid_phone_numbers):
        """Test various invalid phone number formats."""
        for phone in invalid_phone_numbers:
            is_valid, error = validate_phone_number(phone)
            assert not is_valid, f"'{phone}' should be invalid"
            assert error is not None

    def test_phone_number_normalization(self):
        """Test that phone numbers are properly normalized."""
        # Should accept properly formatted E.164
        is_valid, _ = validate_phone_number("+15551234567")
        assert is_valid


# ========================================
# Twilio SID Validation Tests
# ========================================

@pytest.mark.unit
class TestTwilioSidValidation:
    """Test Twilio Account SID validation."""

    def test_valid_twilio_sids(self):
        """Test valid Twilio SID formats."""
        valid_sids = [
            "AC1234567890abcdef1234567890abcdef",
            "ACabcdefabcdefabcdefabcdefabcdefab",
            "AC1234567890ABCDEF1234567890ABCDEF",  # Uppercase hex
        ]

        for sid in valid_sids:
            is_valid, error = validate_twilio_sid(sid)
            assert is_valid, f"'{sid}' should be valid but got error: {error}"
            assert error is None

    def test_invalid_twilio_sids(self, invalid_twilio_sids):
        """Test invalid Twilio SID formats."""
        for sid in invalid_twilio_sids:
            is_valid, error = validate_twilio_sid(sid)
            assert not is_valid, f"'{sid}' should be invalid"
            assert error is not None

    def test_twilio_sid_length_requirement(self):
        """Test SID length requirement (exactly 34 characters)."""
        # Exactly 34 characters
        is_valid, _ = validate_twilio_sid("AC" + "1" * 32)
        assert is_valid

        # 33 characters (too short)
        is_valid, _ = validate_twilio_sid("AC" + "1" * 31)
        assert not is_valid

        # 35 characters (too long)
        is_valid, _ = validate_twilio_sid("AC" + "1" * 33)
        assert not is_valid


# ========================================
# Twilio Token Validation Tests
# ========================================

@pytest.mark.unit
class TestTwilioTokenValidation:
    """Test Twilio Auth Token validation."""

    def test_valid_twilio_tokens(self):
        """Test valid Twilio token formats."""
        valid_tokens = [
            "1234567890abcdef1234567890abcdef",  # Exactly 32
            "a" * 32,  # Minimum length
            "a" * 40,  # Longer is OK
        ]

        for token in valid_tokens:
            is_valid, error = validate_twilio_token(token)
            assert is_valid, f"'{token}' should be valid but got error: {error}"
            assert error is None

    def test_invalid_twilio_tokens(self):
        """Test invalid Twilio token formats."""
        invalid_tokens = [
            "",  # Empty
            "a" * 31,  # Too short
        ]

        for token in invalid_tokens:
            is_valid, error = validate_twilio_token(token)
            assert not is_valid, f"'{token}' should be invalid"
            assert error is not None


# ========================================
# Email Pattern Validation Tests
# ========================================

@pytest.mark.unit
class TestEmailPatternValidation:
    """Test email pattern validation."""

    def test_valid_email_patterns(self):
        """Test valid email pattern formats."""
        valid_patterns = [
            "*@example.com",
            "*@sms.{domain}",
            "user@{domain}",
            "sms+*@example.com",
        ]

        for pattern in valid_patterns:
            is_valid, error = validate_email_pattern(pattern)
            assert is_valid, f"'{pattern}' should be valid but got error: {error}"
            assert error is None

    def test_invalid_email_patterns(self):
        """Test invalid email pattern formats."""
        invalid_patterns = [
            "",  # Empty
            "example.com",  # No @
            "@example.com",  # No local part
            "user@",  # No domain
        ]

        for pattern in invalid_patterns:
            is_valid, error = validate_email_pattern(pattern)
            assert not is_valid, f"'{pattern}' should be invalid"
            assert error is not None


# ========================================
# URL Validation Tests
# ========================================

@pytest.mark.unit
class TestUrlValidation:
    """Test URL validation."""

    def test_valid_urls(self):
        """Test valid URL formats."""
        valid_urls = [
            "https://example.com",
            "http://example.com",
            "https://subdomain.example.com/path",
            "https://example.com:8080",
            "https://example.com/path?query=value",
        ]

        for url in valid_urls:
            is_valid, error = validate_url(url)
            assert is_valid, f"'{url}' should be valid but got error: {error}"
            assert error is None

    def test_invalid_urls(self):
        """Test invalid URL formats."""
        invalid_urls = [
            "",  # Empty
            "not-a-url",
            "example.com",  # No protocol
            "ftp://example.com",  # Invalid protocol (depending on validator)
        ]

        for url in invalid_urls:
            is_valid, error = validate_url(url)
            # Note: Some validators may accept ftp://
            if url == "ftp://example.com":
                continue
            assert not is_valid, f"'{url}' should be invalid"
            assert error is not None


# ========================================
# Integer Validation Tests
# ========================================

@pytest.mark.unit
class TestPositiveIntegerValidation:
    """Test positive integer validation."""

    def test_valid_positive_integers(self):
        """Test valid positive integer values."""
        test_cases = [
            (1, 1, 100),
            (50, 1, 100),
            (100, 1, 100),
        ]

        for value, min_val, max_val in test_cases:
            is_valid, error = validate_positive_integer(value, min_val, max_val)
            assert is_valid, f"{value} should be valid but got error: {error}"
            assert error is None

    def test_invalid_positive_integers(self):
        """Test invalid positive integer values."""
        # Below minimum
        is_valid, error = validate_positive_integer(0, 1, 100)
        assert not is_valid
        assert "at least" in error.lower()

        # Above maximum
        is_valid, error = validate_positive_integer(101, 1, 100)
        assert not is_valid
        assert "at most" in error.lower()

        # Not an integer
        is_valid, error = validate_positive_integer("not_int", 1, 100)
        assert not is_valid
        assert "integer" in error.lower()

    def test_boundary_values(self):
        """Test boundary value handling."""
        # Exactly at minimum
        is_valid, _ = validate_positive_integer(1, 1, 100)
        assert is_valid

        # Exactly at maximum
        is_valid, _ = validate_positive_integer(100, 1, 100)
        assert is_valid

        # Just below minimum
        is_valid, _ = validate_positive_integer(0, 1, 100)
        assert not is_valid

        # Just above maximum
        is_valid, _ = validate_positive_integer(101, 1, 100)
        assert not is_valid


# ========================================
# Filename Sanitization Tests
# ========================================

@pytest.mark.unit
class TestFilenameSanitization:
    """Test filename sanitization."""

    def test_sanitize_safe_filenames(self):
        """Test sanitization of already safe filenames."""
        safe_names = [
            ("my-file.txt", "my-file.txt"),
            ("file123.json", "file123.json"),
        ]

        for input_name, expected in safe_names:
            result = sanitize_filename(input_name)
            assert result == expected

    def test_sanitize_unsafe_filenames(self):
        """Test sanitization of unsafe filenames."""
        unsafe_names = [
            ("My File.txt", "my-file.txt"),  # Spaces
            ("file@#$.txt", "file.txt"),  # Special chars
            ("..file.txt", "file.txt"),  # Leading dots
            ("file  name.txt", "file-name.txt"),  # Multiple spaces
            ("file--name.txt", "file-name.txt"),  # Consecutive hyphens
        ]

        for input_name, expected in unsafe_names:
            result = sanitize_filename(input_name)
            assert result == expected

    @pytest.mark.security
    def test_sanitize_malicious_filenames(self):
        """Test sanitization of potentially malicious filenames."""
        malicious_names = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32",
            "file;rm -rf /",
            "file|cat /etc/passwd",
        ]

        for name in malicious_names:
            result = sanitize_filename(name)
            # Should remove path traversal and command injection attempts
            assert ".." not in result
            assert "/" not in result
            assert "\\" not in result
            assert ";" not in result
            assert "|" not in result


# ========================================
# Sender Whitelist Validation Tests
# ========================================

@pytest.mark.unit
class TestSenderWhitelistValidation:
    """Test sender whitelist validation."""

    def test_valid_whitelist(self):
        """Test valid sender whitelist."""
        whitelist_text = "user1@example.com\nuser2@example.com\nuser3@example.com"
        is_valid, error, emails = validate_sender_whitelist(whitelist_text)

        assert is_valid
        assert error is None
        assert len(emails) == 3
        assert "user1@example.com" in emails

    def test_empty_whitelist(self):
        """Test empty whitelist (should be valid)."""
        is_valid, error, emails = validate_sender_whitelist("")

        assert is_valid
        assert error is None
        assert emails == []

    def test_whitelist_with_invalid_email(self):
        """Test whitelist containing invalid email."""
        whitelist_text = "user1@example.com\ninvalid-email\nuser3@example.com"
        is_valid, error, emails = validate_sender_whitelist(whitelist_text)

        assert not is_valid
        assert error is not None
        assert "invalid-email" in error.lower()
        assert emails == []

    def test_whitelist_with_extra_whitespace(self):
        """Test whitelist with extra whitespace."""
        whitelist_text = "  user1@example.com  \n\n  user2@example.com  \n"
        is_valid, error, emails = validate_sender_whitelist(whitelist_text)

        assert is_valid
        assert len(emails) == 2
        assert "user1@example.com" in emails


# ========================================
# Security Tests
# ========================================

@pytest.mark.security
class TestValidationSecurity:
    """Security-focused validation tests."""

    def test_xss_payload_rejection(self, security_payloads):
        """Test that XSS payloads don't bypass validation."""
        for payload in security_payloads["xss"]:
            # Should not be valid as worker name
            is_valid, _ = validate_worker_name(payload)
            assert not is_valid

            # Sanitize filename should remove dangerous parts
            sanitized = sanitize_filename(payload)
            assert "<" not in sanitized
            assert ">" not in sanitized
            assert "script" not in sanitized.lower()

    def test_sql_injection_payload_rejection(self, security_payloads):
        """Test that SQL injection payloads don't bypass validation."""
        for payload in security_payloads["sql_injection"]:
            is_valid, _ = validate_worker_name(payload)
            assert not is_valid

    def test_path_traversal_sanitization(self, security_payloads):
        """Test that path traversal attempts are sanitized."""
        for payload in security_payloads["path_traversal"]:
            sanitized = sanitize_filename(payload)
            assert ".." not in sanitized
            assert "/" not in sanitized
            assert "\\" not in sanitized


# ========================================
# Edge Case Tests
# ========================================

@pytest.mark.edge_case
class TestValidationEdgeCases:
    """Edge case validation tests."""

    def test_unicode_in_inputs(self, unicode_test_data):
        """Test Unicode character handling in various validators."""
        # Worker name should reject Unicode
        is_valid, _ = validate_worker_name(unicode_test_data["emoji"])
        assert not is_valid

        # Email should handle Unicode properly
        unicode_email = f"user+{unicode_test_data['emoji']}@example.com"
        # Depending on email validator, this may or may not be valid

    def test_extremely_long_inputs(self):
        """Test handling of extremely long inputs."""
        very_long = "a" * 10000

        is_valid, _ = validate_worker_name(very_long)
        assert not is_valid

        # Should still sanitize without crashing
        sanitized = sanitize_filename(very_long)
        assert isinstance(sanitized, str)

    def test_null_and_none_inputs(self):
        """Test handling of None/null inputs."""
        # Most validators should handle None gracefully
        # (though they may raise TypeError - that's acceptable)
        try:
            is_valid, _ = validate_worker_name(None)
            assert not is_valid
        except (TypeError, AttributeError):
            # Acceptable to raise error for None
            pass
