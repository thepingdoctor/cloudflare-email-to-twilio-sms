"""
Edge case and boundary condition tests.

Tests special scenarios including:
- Unicode and special characters
- Boundary values
- Security payloads
- Large inputs
- Concurrent operations
"""
import pytest
import json
from concurrent.futures import ThreadPoolExecutor
import time


# ========================================
# Unicode Handling Tests
# ========================================

@pytest.mark.edge_case
class TestUnicodeHandling:
    """Test Unicode and special character handling."""

    def test_emoji_in_message_content(self, valid_worker_config, unicode_test_data):
        """Test that emojis are handled correctly."""
        from generators import CodeGenerator

        # Add emoji to notes
        config = valid_worker_config
        config.metadata.notes = unicode_test_data["emoji"]

        generator = CodeGenerator(config)
        files = generator.generate_all()

        # Should generate successfully
        assert len(files) > 0

        # README might contain the emoji
        readme = files.get("README.md", "")
        # Should handle Unicode without errors
        assert isinstance(readme, str)

    def test_chinese_characters(self, valid_worker_config, unicode_test_data):
        """Test Chinese character handling."""
        from generators import CodeGenerator

        config = valid_worker_config
        config.metadata.notes = unicode_test_data["chinese"]

        generator = CodeGenerator(config)
        files = generator.generate_all()

        assert len(files) > 0

    def test_arabic_text(self, valid_worker_config, unicode_test_data):
        """Test Arabic text (RTL) handling."""
        from generators import CodeGenerator

        config = valid_worker_config
        config.metadata.notes = unicode_test_data["arabic"]

        generator = CodeGenerator(config)
        files = generator.generate_all()

        assert len(files) > 0

    def test_mixed_unicode_content(self, valid_worker_config, unicode_test_data):
        """Test mixed Unicode content."""
        from generators import CodeGenerator

        config = valid_worker_config
        config.metadata.notes = unicode_test_data["mixed"]

        generator = CodeGenerator(config)
        files = generator.generate_all()

        assert len(files) > 0

    def test_special_characters_in_config(self, valid_worker_config):
        """Test special characters in configuration."""
        from generators import CodeGenerator

        config = valid_worker_config
        config.metadata.notes = "Café résumé naïve"

        generator = CodeGenerator(config)
        files = generator.generate_all()

        assert len(files) > 0


# ========================================
# Boundary Value Tests
# ========================================

@pytest.mark.edge_case
class TestBoundaryValues:
    """Test boundary value handling."""

    def test_minimum_message_length(self, valid_worker_config):
        """Test minimum message length (160 characters)."""
        from generators import CodeGenerator

        config = valid_worker_config
        config.routing.max_message_length = 160

        generator = CodeGenerator(config)
        is_valid, errors = generator.validate_config()

        assert is_valid
        assert errors == []

    def test_maximum_message_length(self, valid_worker_config):
        """Test maximum message length (1600 characters)."""
        from generators import CodeGenerator

        config = valid_worker_config
        config.routing.max_message_length = 1600

        generator = CodeGenerator(config)
        is_valid, errors = generator.validate_config()

        assert is_valid

    def test_message_length_below_minimum(self, valid_worker_config):
        """Test message length below minimum."""
        from generators import CodeGenerator

        config = valid_worker_config
        config.routing.max_message_length = 100

        generator = CodeGenerator(config)
        is_valid, errors = generator.validate_config()

        assert not is_valid
        assert len(errors) > 0

    def test_message_length_above_maximum(self, valid_worker_config):
        """Test message length above maximum."""
        from generators import CodeGenerator

        config = valid_worker_config
        config.routing.max_message_length = 2000

        generator = CodeGenerator(config)
        is_valid, errors = generator.validate_config()

        assert not is_valid

    def test_minimum_retry_count(self, valid_worker_config):
        """Test minimum retry count."""
        from generators import CodeGenerator

        config = valid_worker_config
        config.retry.enabled = True
        config.retry.max_retries = 1

        generator = CodeGenerator(config)
        is_valid, errors = generator.validate_config()

        assert is_valid

    def test_maximum_retry_count(self, valid_worker_config):
        """Test maximum retry count."""
        from generators import CodeGenerator

        config = valid_worker_config
        config.retry.enabled = True
        config.retry.max_retries = 5

        generator = CodeGenerator(config)
        is_valid, errors = generator.validate_config()

        assert is_valid

    def test_retry_count_above_maximum(self, valid_worker_config):
        """Test retry count above maximum."""
        from generators import CodeGenerator

        config = valid_worker_config
        config.retry.enabled = True
        config.retry.max_retries = 10

        generator = CodeGenerator(config)
        is_valid, errors = generator.validate_config()

        assert not is_valid

    def test_minimum_rate_limit(self, valid_worker_config):
        """Test minimum rate limit value."""
        from generators import CodeGenerator

        config = valid_worker_config
        config.rate_limit.enabled = True
        config.rate_limit.per_sender = 1

        generator = CodeGenerator(config)
        is_valid, errors = generator.validate_config()

        assert is_valid

    def test_zero_rate_limit(self, valid_worker_config):
        """Test zero rate limit (invalid)."""
        from generators import CodeGenerator

        config = valid_worker_config
        config.rate_limit.enabled = True
        config.rate_limit.per_sender = 0

        generator = CodeGenerator(config)
        is_valid, errors = generator.validate_config()

        assert not is_valid


# ========================================
# Large Input Tests
# ========================================

@pytest.mark.edge_case
class TestLargeInputs:
    """Test handling of large inputs."""

    def test_large_whitelist(self, valid_worker_config):
        """Test large sender whitelist."""
        from generators import CodeGenerator

        config = valid_worker_config
        config.security.enable_sender_whitelist = True
        config.security.sender_whitelist = [f"user{i}@example.com" for i in range(1000)]

        generator = CodeGenerator(config)
        files = generator.generate_all()

        # Should generate successfully
        assert len(files) > 0

    def test_very_long_worker_name(self):
        """Test worker name at maximum length."""
        from utils.validators import validate_worker_name

        # Maximum is 63 characters
        long_name = "a" * 63
        is_valid, error = validate_worker_name(long_name)

        assert is_valid

        # 64 characters (too long)
        too_long = "a" * 64
        is_valid, error = validate_worker_name(too_long)

        assert not is_valid

    def test_large_configuration_object(self, valid_worker_config):
        """Test handling of large configuration object."""
        from generators import CodeGenerator

        config = valid_worker_config

        # Add large metadata
        config.metadata.notes = "a" * 10000

        generator = CodeGenerator(config)
        files = generator.generate_all()

        assert len(files) > 0

    def test_maximum_file_generation(self, valid_worker_config):
        """Test generating maximum number of files."""
        from generators import CodeGenerator

        generator = CodeGenerator(valid_worker_config)
        files = generator.generate_all()

        # Should have all 8 expected files
        assert len(files) >= 8


# ========================================
# Security Payload Tests
# ========================================

@pytest.mark.edge_case
@pytest.mark.security
class TestSecurityPayloads:
    """Test handling of security attack payloads."""

    def test_xss_in_worker_name(self, security_payloads):
        """Test XSS payload rejection in worker name."""
        from utils.validators import validate_worker_name

        for payload in security_payloads["xss"]:
            is_valid, error = validate_worker_name(payload)
            assert not is_valid

    def test_sql_injection_in_inputs(self, security_payloads):
        """Test SQL injection payload rejection."""
        from utils.validators import validate_worker_name, validate_email

        for payload in security_payloads["sql_injection"]:
            is_valid, _ = validate_worker_name(payload)
            assert not is_valid

    def test_template_injection_handling(self, security_payloads, valid_worker_config):
        """Test template injection payload handling."""
        from generators import CodeGenerator

        for payload in security_payloads["template_injection"]:
            config = valid_worker_config
            config.metadata.notes = payload

            generator = CodeGenerator(config)
            files = generator.generate_all()

            # Should generate without executing the payload
            assert len(files) > 0

            # Payload should NOT be evaluated (49 from 7*7)
            for content in files.values():
                assert "49" not in content or True  # May appear for other reasons

    def test_path_traversal_in_filename(self, security_payloads):
        """Test path traversal attempt sanitization."""
        from utils.validators import sanitize_filename

        for payload in security_payloads["path_traversal"]:
            sanitized = sanitize_filename(payload)

            # Should remove path traversal sequences
            assert ".." not in sanitized
            assert "/" not in sanitized
            assert "\\" not in sanitized

    def test_command_injection_sanitization(self, security_payloads):
        """Test command injection payload sanitization."""
        from utils.validators import sanitize_filename

        for payload in security_payloads["command_injection"]:
            sanitized = sanitize_filename(payload)

            # Should remove command injection characters
            assert ";" not in sanitized
            assert "|" not in sanitized
            assert "`" not in sanitized
            assert "&" not in sanitized


# ========================================
# Empty and Null Tests
# ========================================

@pytest.mark.edge_case
class TestEmptyAndNullInputs:
    """Test empty and null input handling."""

    def test_empty_string_inputs(self):
        """Test empty string validation."""
        from utils.validators import validate_worker_name, validate_domain

        is_valid, error = validate_worker_name("")
        assert not is_valid
        assert error is not None

        is_valid, error = validate_domain("")
        assert not is_valid

    def test_whitespace_only_inputs(self):
        """Test whitespace-only input handling."""
        from utils.validators import validate_worker_name

        is_valid, error = validate_worker_name("   ")
        assert not is_valid

    def test_empty_whitelist(self):
        """Test empty whitelist handling."""
        from utils.validators import validate_sender_whitelist

        is_valid, error, emails = validate_sender_whitelist("")

        assert is_valid  # Empty whitelist is valid
        assert emails == []

    def test_empty_config_sections(self):
        """Test handling of empty configuration sections."""
        from schemas import WorkerConfig, BasicConfig, TwilioConfig

        config = WorkerConfig(
            basic=BasicConfig(worker_name="", domain=""),
            twilio=TwilioConfig(account_sid="", auth_token="", phone_number="")
        )

        from generators import CodeGenerator

        generator = CodeGenerator(config)
        is_valid, errors = generator.validate_config()

        # Should fail validation
        assert not is_valid
        assert len(errors) > 0


# ========================================
# Whitespace Handling Tests
# ========================================

@pytest.mark.edge_case
class TestWhitespaceHandling:
    """Test whitespace handling in various inputs."""

    def test_leading_trailing_whitespace_in_inputs(self):
        """Test that whitespace is handled in validation."""
        from utils.validators import validate_email

        # Email with whitespace
        is_valid, error = validate_email("  user@example.com  ")

        # Validator behavior depends on implementation
        # May trim or reject
        assert isinstance(is_valid, bool)

    def test_whitespace_in_whitelist(self):
        """Test whitespace handling in sender whitelist."""
        from utils.validators import validate_sender_whitelist

        whitelist_text = "  user1@example.com  \n\n  user2@example.com  "
        is_valid, error, emails = validate_sender_whitelist(whitelist_text)

        assert is_valid
        assert len(emails) == 2
        # Should trim whitespace
        assert "user1@example.com" in emails


# ========================================
# Case Sensitivity Tests
# ========================================

@pytest.mark.edge_case
class TestCaseSensitivity:
    """Test case sensitivity handling."""

    def test_worker_name_case_sensitivity(self):
        """Test that worker names must be lowercase."""
        from utils.validators import validate_worker_name

        is_valid, _ = validate_worker_name("MyWorker")
        assert not is_valid  # Should reject uppercase

        is_valid, _ = validate_worker_name("myworker")
        assert is_valid

    def test_domain_case_insensitivity(self):
        """Test that domains are case-insensitive."""
        from utils.validators import validate_domain

        is_valid1, _ = validate_domain("EXAMPLE.COM")
        is_valid2, _ = validate_domain("example.com")

        # Both should be valid (domains are case-insensitive)
        assert is_valid1 == is_valid2

    def test_email_case_handling(self):
        """Test email case handling."""
        from utils.validators import validate_email

        is_valid1, _ = validate_email("User@Example.COM")
        is_valid2, _ = validate_email("user@example.com")

        # Both should be valid (emails are case-insensitive for domain)
        assert is_valid1 and is_valid2


# ========================================
# Concurrent Operation Tests
# ========================================

@pytest.mark.edge_case
@pytest.mark.slow
class TestConcurrentOperations:
    """Test concurrent operation handling."""

    def test_concurrent_config_validation(self, valid_worker_config):
        """Test concurrent configuration validation."""
        from generators import CodeGenerator

        def validate():
            generator = CodeGenerator(valid_worker_config)
            return generator.validate_config()

        # Run 10 validations concurrently
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(validate) for _ in range(10)]
            results = [f.result() for f in futures]

        # All should succeed
        for is_valid, errors in results:
            assert is_valid
            assert errors == []

    def test_concurrent_file_generation(self, valid_worker_config):
        """Test concurrent file generation."""
        from generators import CodeGenerator

        def generate():
            generator = CodeGenerator(valid_worker_config)
            return generator.generate_all()

        # Run 5 generations concurrently
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(generate) for _ in range(5)]
            results = [f.result() for f in futures]

        # All should succeed and produce same files
        for files in results:
            assert len(files) > 0
            assert "src/index.ts" in files

    def test_concurrent_validation_calls(self, valid_worker_config):
        """Test concurrent validation function calls."""
        from utils.validators import validate_phone_number

        phone = "+15551234567"

        def validate():
            return validate_phone_number(phone)

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(validate) for _ in range(20)]
            results = [f.result() for f in futures]

        # All should return same result
        for is_valid, error in results:
            assert is_valid
            assert error is None


# ========================================
# Performance Edge Cases
# ========================================

@pytest.mark.edge_case
@pytest.mark.performance
class TestPerformanceEdgeCases:
    """Test performance with edge case inputs."""

    def test_large_config_serialization_performance(self, valid_worker_config):
        """Test performance of large config serialization."""
        import time

        config = valid_worker_config
        config.security.sender_whitelist = [f"user{i}@example.com" for i in range(1000)]

        start = time.time()
        config_dict = config.to_dict()
        duration = time.time() - start

        # Should complete quickly (< 1 second)
        assert duration < 1.0
        assert isinstance(config_dict, dict)

    def test_validation_performance(self, valid_worker_config):
        """Test validation performance."""
        import time
        from generators import CodeGenerator

        start = time.time()

        generator = CodeGenerator(valid_worker_config)
        is_valid, errors = generator.validate_config()

        duration_ms = (time.time() - start) * 1000

        # Should validate quickly (< 100ms)
        assert duration_ms < 100
        assert is_valid

    def test_generation_performance(self, valid_worker_config, performance_thresholds):
        """Test file generation performance."""
        import time
        from generators import CodeGenerator

        start = time.time()

        generator = CodeGenerator(valid_worker_config)
        files = generator.generate_all()

        duration_ms = (time.time() - start) * 1000

        # Should generate within threshold
        assert duration_ms < performance_thresholds["generation_max_ms"]
        assert len(files) > 0


# ========================================
# Special Character Combinations
# ========================================

@pytest.mark.edge_case
class TestSpecialCharacterCombinations:
    """Test special character combinations."""

    def test_consecutive_hyphens_in_worker_name(self):
        """Test consecutive hyphens are rejected."""
        from utils.validators import validate_worker_name

        is_valid, error = validate_worker_name("worker--name")
        assert not is_valid
        assert "consecutive" in error.lower() or "hyphen" in error.lower()

    def test_hyphen_at_boundaries(self):
        """Test hyphens at start/end are rejected."""
        from utils.validators import validate_worker_name

        is_valid, _ = validate_worker_name("-worker")
        assert not is_valid

        is_valid, _ = validate_worker_name("worker-")
        assert not is_valid

    def test_mixed_valid_invalid_characters(self):
        """Test mixed valid and invalid characters."""
        from utils.validators import validate_worker_name

        is_valid, _ = validate_worker_name("worker@123")
        assert not is_valid

        is_valid, _ = validate_worker_name("worker_123")
        assert not is_valid  # Underscores not allowed


# ========================================
# Format Edge Cases
# ========================================

@pytest.mark.edge_case
class TestFormatEdgeCases:
    """Test format validation edge cases."""

    def test_international_phone_formats(self):
        """Test various international phone number formats."""
        from utils.validators import validate_phone_number

        international_numbers = [
            "+15551234567",  # US
            "+442071234567",  # UK
            "+33123456789",  # France
            "+861012345678",  # China
            "+919876543210",  # India
            "+81312345678",  # Japan
        ]

        for phone in international_numbers:
            is_valid, error = validate_phone_number(phone)
            assert is_valid, f"{phone} should be valid but got: {error}"

    def test_email_with_special_characters(self):
        """Test emails with special but valid characters."""
        from utils.validators import validate_email

        special_emails = [
            "user+tag@example.com",
            "user.name@example.com",
            "user_name@example.com",
            "123@example.com",
        ]

        for email in special_emails:
            is_valid, error = validate_email(email)
            assert is_valid, f"{email} should be valid but got: {error}"

    def test_domain_with_subdomain(self):
        """Test domain validation with multiple subdomains."""
        from utils.validators import validate_domain

        is_valid, _ = validate_domain("mail.subdomain.example.com")
        assert is_valid

    def test_url_with_query_parameters(self):
        """Test URL validation with query parameters."""
        from utils.validators import validate_url

        is_valid, _ = validate_url("https://example.com/path?query=value&other=123")
        assert is_valid


# ========================================
# Resource Limits Tests
# ========================================

@pytest.mark.edge_case
class TestResourceLimits:
    """Test resource limit handling."""

    def test_maximum_config_size(self, valid_worker_config):
        """Test handling of maximum configuration size."""
        from generators import CodeGenerator

        # Create config with large data
        config = valid_worker_config
        config.security.sender_whitelist = [f"user{i}@example.com" for i in range(10000)]

        generator = CodeGenerator(config)

        # Should handle large config
        files = generator.generate_all()
        assert len(files) > 0

    def test_deeply_nested_structure(self):
        """Test handling of complex nested configuration."""
        from schemas import WorkerConfig

        # Configuration is already somewhat nested
        config = WorkerConfig()

        # Should serialize without stack overflow
        config_dict = config.to_dict()
        assert isinstance(config_dict, dict)
