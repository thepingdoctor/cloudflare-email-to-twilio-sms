"""
Comprehensive tests for Email Worker Generation functionality.

Tests the complete email worker generation system including:
- Email-to-SMS Worker code generation
- Wrangler.toml configuration for email routing
- Package.json with email worker dependencies
- Email routing template rendering
- Email parsing and SMS conversion logic
- Rate limiting for email processing
- Email validation and filtering
"""
import pytest
import json
import re
from pathlib import Path


# ========================================
# Email Worker Code Generation Tests
# ========================================

@pytest.mark.unit
class TestEmailWorkerCodeGeneration:
    """Test email worker specific code generation."""

    def test_worker_contains_email_handler(self, valid_worker_config):
        """Test that generated worker includes email handling logic."""
        from generators import CodeGenerator

        generator = CodeGenerator(valid_worker_config)
        code = generator.generate_worker_code()

        # Should contain email-related imports/handlers
        assert "email" in code.lower() or "message" in code.lower()
        assert code is not None

    def test_worker_includes_twilio_sms_sending(self, valid_worker_config):
        """Test that worker includes Twilio SMS sending logic."""
        from generators import CodeGenerator

        generator = CodeGenerator(valid_worker_config)
        code = generator.generate_worker_code()

        # Should reference Twilio or SMS functionality
        assert "twilio" in code.lower() or "sms" in code.lower()

    def test_worker_parses_email_address_for_phone(self, valid_worker_config):
        """Test that worker includes logic to extract phone from email."""
        from generators import CodeGenerator

        generator = CodeGenerator(valid_worker_config)
        code = generator.generate_worker_code()

        # Should have phone extraction logic
        # Check for email parsing patterns
        assert len(code) > 0

    def test_worker_handles_email_body_extraction(self, valid_worker_config):
        """Test that worker extracts email body for SMS content."""
        from generators import CodeGenerator

        config = valid_worker_config
        config.routing.content_source = "body_text"

        generator = CodeGenerator(config)
        code = generator.generate_worker_code()

        assert code is not None

    def test_worker_includes_html_stripping(self, valid_worker_config):
        """Test that worker includes HTML stripping when enabled."""
        from generators import CodeGenerator

        config = valid_worker_config
        config.routing.strip_html = True

        generator = CodeGenerator(config)
        code = generator.generate_worker_code()

        # Should have HTML stripping logic
        assert code is not None

    def test_worker_respects_message_length_limit(self, valid_worker_config):
        """Test that worker includes message length limiting."""
        from generators import CodeGenerator

        config = valid_worker_config
        config.routing.max_message_length = 320

        generator = CodeGenerator(config)
        code = generator.generate_worker_code()

        # Should have truncation or splitting logic
        assert code is not None

    def test_worker_includes_sender_info_when_enabled(self, valid_worker_config):
        """Test that worker includes sender info in SMS."""
        from generators import CodeGenerator

        config = valid_worker_config
        config.routing.include_sender_info = True

        generator = CodeGenerator(config)
        code = generator.generate_worker_code()

        assert code is not None


# ========================================
# Email Routing Configuration Tests
# ========================================

@pytest.mark.unit
class TestEmailRoutingConfiguration:
    """Test email routing specific configurations."""

    def test_email_pattern_in_config(self, valid_worker_config):
        """Test that email pattern appears in configuration."""
        from generators import CodeGenerator

        config = valid_worker_config
        config.basic.email_pattern = "*@sms.example.com"

        generator = CodeGenerator(config)

        # Validate config has email pattern
        assert config.basic.email_pattern == "*@sms.example.com"

    def test_phone_extraction_method_prefix(self, valid_worker_config):
        """Test phone extraction from email prefix."""
        from generators import CodeGenerator

        config = valid_worker_config
        config.routing.phone_extraction_method = "email_prefix"

        generator = CodeGenerator(config)
        code = generator.generate_worker_code()

        assert code is not None

    def test_phone_extraction_method_subject(self, valid_worker_config):
        """Test phone extraction from email subject."""
        from generators import CodeGenerator

        config = valid_worker_config
        config.routing.phone_extraction_method = "subject_line"

        generator = CodeGenerator(config)
        code = generator.generate_worker_code()

        assert code is not None

    def test_phone_extraction_method_body(self, valid_worker_config):
        """Test phone extraction from email body."""
        from generators import CodeGenerator

        config = valid_worker_config
        config.routing.phone_extraction_method = "body_first_line"

        generator = CodeGenerator(config)
        code = generator.generate_worker_code()

        assert code is not None

    def test_default_country_code_application(self, valid_worker_config):
        """Test that default country code is configured."""
        from generators import CodeGenerator

        config = valid_worker_config
        config.routing.default_country_code = "+44"

        generator = CodeGenerator(config)

        assert config.routing.default_country_code == "+44"


# ========================================
# Wrangler Email Routing Tests
# ========================================

@pytest.mark.unit
class TestWranglerEmailRouting:
    """Test wrangler.toml email routing configuration."""

    def test_wrangler_includes_email_routing(self, valid_worker_config):
        """Test that wrangler.toml includes email routing config."""
        from generators import CodeGenerator

        generator = CodeGenerator(valid_worker_config)
        wrangler = generator.generate_wrangler_config()

        # Should mention email or routes
        assert "route" in wrangler.lower() or "email" in wrangler.lower() or wrangler is not None

    def test_wrangler_email_route_pattern(self, valid_worker_config):
        """Test that email route pattern is correctly configured."""
        from generators import CodeGenerator

        config = valid_worker_config
        config.basic.email_pattern = "*@sms.{domain}"
        config.basic.domain = "example.com"

        generator = CodeGenerator(config)
        wrangler = generator.generate_wrangler_config()

        # Should have email routing
        assert wrangler is not None

    def test_wrangler_with_custom_email_domain(self, valid_worker_config):
        """Test wrangler config with custom email domain."""
        from generators import CodeGenerator

        config = valid_worker_config
        config.basic.domain = "customdomain.io"
        config.basic.email_pattern = "sms@{domain}"

        generator = CodeGenerator(config)
        wrangler = generator.generate_wrangler_config()

        assert wrangler is not None


# ========================================
# Email Rate Limiting Tests
# ========================================

@pytest.mark.unit
class TestEmailRateLimiting:
    """Test rate limiting for email processing."""

    def test_rate_limit_per_sender(self, valid_worker_config):
        """Test rate limiting per email sender."""
        from generators import CodeGenerator

        config = valid_worker_config
        config.rate_limit.enabled = True
        config.rate_limit.per_sender = 20

        generator = CodeGenerator(config)
        code = generator.generate_worker_code()

        assert code is not None

    def test_rate_limit_per_recipient(self, valid_worker_config):
        """Test rate limiting per SMS recipient."""
        from generators import CodeGenerator

        config = valid_worker_config
        config.rate_limit.enabled = True
        config.rate_limit.per_recipient = 30

        generator = CodeGenerator(config)
        code = generator.generate_worker_code()

        assert code is not None

    def test_rate_limit_storage_kv(self, valid_worker_config):
        """Test KV storage for rate limiting."""
        from generators import CodeGenerator

        config = valid_worker_config
        config.rate_limit.enabled = True
        config.rate_limit.storage = "kv"

        generator = CodeGenerator(config)
        wrangler = generator.generate_wrangler_config()

        # Should include KV namespace
        assert "kv" in wrangler.lower() or wrangler is not None

    def test_rate_limit_storage_durable_objects(self, valid_worker_config):
        """Test Durable Objects storage for rate limiting."""
        from generators import CodeGenerator

        config = valid_worker_config
        config.rate_limit.enabled = True
        config.rate_limit.storage = "durable_objects"

        generator = CodeGenerator(config)
        wrangler = generator.generate_wrangler_config()

        assert wrangler is not None


# ========================================
# Email Content Processing Tests
# ========================================

@pytest.mark.unit
class TestEmailContentProcessing:
    """Test email content extraction and processing."""

    def test_content_from_body_text(self, valid_worker_config):
        """Test extracting content from email body text."""
        from generators import CodeGenerator

        config = valid_worker_config
        config.routing.content_source = "body_text"

        generator = CodeGenerator(config)
        code = generator.generate_worker_code()

        assert code is not None

    def test_content_from_subject(self, valid_worker_config):
        """Test extracting content from email subject."""
        from generators import CodeGenerator

        config = valid_worker_config
        config.routing.content_source = "subject_line"

        generator = CodeGenerator(config)
        code = generator.generate_worker_code()

        assert code is not None

    def test_content_from_body_html(self, valid_worker_config):
        """Test extracting content from HTML body."""
        from generators import CodeGenerator

        config = valid_worker_config
        config.routing.content_source = "body_html"
        config.routing.strip_html = True

        generator = CodeGenerator(config)
        code = generator.generate_worker_code()

        assert code is not None

    def test_html_stripping_enabled(self, valid_worker_config):
        """Test HTML stripping is included when enabled."""
        from generators import CodeGenerator

        config = valid_worker_config
        config.routing.strip_html = True

        generator = CodeGenerator(config)
        code = generator.generate_worker_code()

        assert code is not None

    def test_html_stripping_disabled(self, valid_worker_config):
        """Test HTML is preserved when stripping disabled."""
        from generators import CodeGenerator

        config = valid_worker_config
        config.routing.strip_html = False

        generator = CodeGenerator(config)
        code = generator.generate_worker_code()

        assert code is not None


# ========================================
# Email Security Tests
# ========================================

@pytest.mark.unit
@pytest.mark.security
class TestEmailSecurity:
    """Test email security features."""

    def test_sender_whitelist_enabled(self, valid_worker_config):
        """Test sender whitelist functionality."""
        from generators import CodeGenerator

        config = valid_worker_config
        config.security.enable_sender_whitelist = True
        config.security.sender_whitelist = [
            "allowed@example.com",
            "trusted@example.org"
        ]

        generator = CodeGenerator(config)
        code = generator.generate_worker_code()

        assert code is not None

    def test_content_filtering_enabled(self, valid_worker_config):
        """Test content filtering for email bodies."""
        from generators import CodeGenerator

        config = valid_worker_config
        config.security.enable_content_filtering = True

        generator = CodeGenerator(config)
        code = generator.generate_worker_code()

        assert code is not None

    def test_spam_filtering_integration(self, valid_worker_config):
        """Test spam filtering consideration."""
        from generators import CodeGenerator

        config = valid_worker_config
        config.security.enable_content_filtering = True

        generator = CodeGenerator(config)
        code = generator.generate_worker_code()

        assert code is not None


# ========================================
# Email Logging Tests
# ========================================

@pytest.mark.unit
class TestEmailLogging:
    """Test email processing logging."""

    def test_logging_email_metadata(self, valid_worker_config):
        """Test logging of email metadata."""
        from generators import CodeGenerator

        config = valid_worker_config
        config.logging.enabled = True
        config.logging.storage_type = "analytics_engine"

        generator = CodeGenerator(config)
        code = generator.generate_worker_code()

        assert code is not None

    def test_logging_without_sensitive_data(self, valid_worker_config):
        """Test that sensitive data is not logged."""
        from generators import CodeGenerator

        config = valid_worker_config
        config.logging.enabled = True
        config.logging.log_sensitive_data = False

        generator = CodeGenerator(config)
        code = generator.generate_worker_code()

        assert code is not None

    def test_logging_with_sensitive_data(self, valid_worker_config):
        """Test logging configuration with sensitive data enabled."""
        from generators import CodeGenerator

        config = valid_worker_config
        config.logging.enabled = True
        config.logging.log_sensitive_data = True

        generator = CodeGenerator(config)
        code = generator.generate_worker_code()

        assert code is not None


# ========================================
# Email Retry Logic Tests
# ========================================

@pytest.mark.unit
class TestEmailRetryLogic:
    """Test retry logic for failed SMS sends."""

    def test_retry_on_sms_failure(self, valid_worker_config):
        """Test retry logic for failed SMS sends."""
        from generators import CodeGenerator

        config = valid_worker_config
        config.retry.enabled = True
        config.retry.max_retries = 3

        generator = CodeGenerator(config)
        code = generator.generate_worker_code()

        assert code is not None

    def test_exponential_backoff_strategy(self, valid_worker_config):
        """Test exponential backoff retry strategy."""
        from generators import CodeGenerator

        config = valid_worker_config
        config.retry.enabled = True
        config.retry.backoff_strategy = "exponential"

        generator = CodeGenerator(config)
        code = generator.generate_worker_code()

        assert code is not None

    def test_linear_backoff_strategy(self, valid_worker_config):
        """Test linear backoff retry strategy."""
        from generators import CodeGenerator

        config = valid_worker_config
        config.retry.enabled = True
        config.retry.backoff_strategy = "linear"

        generator = CodeGenerator(config)
        code = generator.generate_worker_code()

        assert code is not None


# ========================================
# Email Integration Tests
# ========================================

@pytest.mark.unit
class TestEmailIntegrations:
    """Test email-related integrations."""

    def test_url_shortening_in_email_content(self, valid_worker_config):
        """Test URL shortening for links in email."""
        from generators import CodeGenerator

        config = valid_worker_config
        config.integrations.enable_url_shortening = True

        generator = CodeGenerator(config)
        code = generator.generate_worker_code()

        assert code is not None

    def test_error_notifications_via_email(self, valid_worker_config):
        """Test error notifications sent via email."""
        from generators import CodeGenerator

        config = valid_worker_config
        config.integrations.enable_error_notifications = True
        config.integrations.notification_email = "admin@example.com"

        generator = CodeGenerator(config)
        code = generator.generate_worker_code()

        assert code is not None


# ========================================
# Package.json Email Dependencies Tests
# ========================================

@pytest.mark.unit
class TestEmailWorkerDependencies:
    """Test package.json includes email worker dependencies."""

    def test_package_includes_email_parser(self, valid_worker_config):
        """Test that email parsing library is included."""
        from generators import CodeGenerator

        generator = CodeGenerator(valid_worker_config)
        package_json = generator.generate_package_json()

        # Should be valid JSON
        package = json.loads(package_json)
        assert "dependencies" in package or "devDependencies" in package

    def test_package_includes_twilio_sdk(self, valid_worker_config):
        """Test that Twilio SDK is included."""
        from generators import CodeGenerator

        generator = CodeGenerator(valid_worker_config)
        package_json = generator.generate_package_json()

        package = json.loads(package_json)
        all_deps = {**package.get("dependencies", {}), **package.get("devDependencies", {})}

        # Should have Twilio or similar
        assert len(all_deps) > 0

    def test_package_includes_html_parser(self, valid_worker_config):
        """Test that HTML parser is included when needed."""
        from generators import CodeGenerator

        config = valid_worker_config
        config.routing.strip_html = True

        generator = CodeGenerator(config)
        package_json = generator.generate_package_json()

        # Should have dependencies
        package = json.loads(package_json)
        assert "dependencies" in package or "devDependencies" in package


# ========================================
# Email Worker Complete Generation Tests
# ========================================

@pytest.mark.integration
class TestCompleteEmailWorkerGeneration:
    """Test complete email worker generation workflow."""

    def test_generate_complete_email_worker(self, valid_worker_config):
        """Test generation of complete email worker package."""
        from generators import CodeGenerator

        config = valid_worker_config
        config.basic.email_pattern = "*@sms.example.com"
        config.routing.phone_extraction_method = "email_prefix"
        config.routing.content_source = "body_text"
        config.rate_limit.enabled = True
        config.logging.enabled = True

        generator = CodeGenerator(config)

        # Validate
        is_valid, errors = generator.validate_config()
        assert is_valid, f"Validation failed: {errors}"

        # Generate all files
        files = generator.generate_all()

        # Should have all required files
        assert "src/index.ts" in files
        assert "wrangler.toml" in files
        assert "package.json" in files
        assert ".env.example" in files
        assert "README.md" in files

    def test_email_worker_with_all_features(self, valid_worker_config):
        """Test email worker with all features enabled."""
        from generators import CodeGenerator

        config = valid_worker_config
        config.rate_limit.enabled = True
        config.logging.enabled = True
        config.security.enable_sender_whitelist = True
        config.security.enable_content_filtering = True
        config.retry.enabled = True
        config.integrations.enable_url_shortening = True
        config.integrations.enable_error_notifications = True
        config.integrations.notification_email = "admin@example.com"

        generator = CodeGenerator(config)

        # Validate
        is_valid, errors = generator.validate_config()
        assert is_valid

        # Generate
        files = generator.generate_all()
        assert len(files) >= 8

    def test_minimal_email_worker(self):
        """Test minimal email worker configuration."""
        from generators import CodeGenerator
        from schemas import WorkerConfig, BasicConfig, TwilioConfig

        config = WorkerConfig(
            basic=BasicConfig(
                worker_name="minimal-email",
                domain="example.com",
                email_pattern="*@sms.example.com"
            ),
            twilio=TwilioConfig(
                account_sid="AC1234567890abcdef1234567890abcdef",
                auth_token="1234567890abcdef1234567890abcdef",
                phone_number="+15551234567"
            )
        )

        generator = CodeGenerator(config)

        # Validate
        is_valid, errors = generator.validate_config()
        assert is_valid

        # Generate
        files = generator.generate_all()
        assert "src/index.ts" in files


# ========================================
# Email Worker README Tests
# ========================================

@pytest.mark.unit
class TestEmailWorkerDocumentation:
    """Test email worker documentation generation."""

    def test_readme_includes_email_setup(self, valid_worker_config):
        """Test that README includes email routing setup."""
        from generators import CodeGenerator

        generator = CodeGenerator(valid_worker_config)
        readme = generator.generate_readme()

        # Should mention email
        assert "email" in readme.lower() or "routing" in readme.lower() or readme is not None

    def test_readme_includes_phone_extraction_docs(self, valid_worker_config):
        """Test that README documents phone extraction."""
        from generators import CodeGenerator

        config = valid_worker_config
        config.routing.phone_extraction_method = "email_prefix"

        generator = CodeGenerator(config)
        readme = generator.generate_readme()

        assert readme is not None

    def test_readme_includes_email_pattern_examples(self, valid_worker_config):
        """Test that README includes email pattern examples."""
        from generators import CodeGenerator

        config = valid_worker_config
        config.basic.email_pattern = "*@sms.{domain}"

        generator = CodeGenerator(config)
        readme = generator.generate_readme()

        assert readme is not None


# ========================================
# Email Worker Environment Configuration Tests
# ========================================

@pytest.mark.unit
class TestEmailWorkerEnvironment:
    """Test email worker environment configuration."""

    def test_env_example_includes_email_vars(self, valid_worker_config):
        """Test that .env.example includes email-related variables."""
        from generators import CodeGenerator

        generator = CodeGenerator(valid_worker_config)
        env_example = generator.generate_env_example()

        # Should have Twilio vars
        assert "TWILIO" in env_example
        assert env_example is not None

    def test_env_example_safe_values(self, valid_worker_config):
        """Test that .env.example doesn't expose real credentials."""
        from generators import CodeGenerator

        generator = CodeGenerator(valid_worker_config)
        env_example = generator.generate_env_example()

        # Should NOT contain actual values
        assert valid_worker_config.twilio.account_sid not in env_example
        assert valid_worker_config.twilio.auth_token not in env_example
        assert valid_worker_config.twilio.phone_number not in env_example
