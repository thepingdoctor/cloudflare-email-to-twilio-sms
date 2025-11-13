"""
Pytest configuration and shared fixtures for Streamlit tests.
"""
import pytest
import sys
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from schemas import (
    WorkerConfig, BasicConfig, TwilioConfig, EmailRoutingConfig,
    RateLimitConfig, LoggingConfig, SecurityConfig, RetryConfig,
    IntegrationConfig, CloudflareConfig, FeaturesConfig, MetadataConfig
)


# ========================================
# Configuration Fixtures
# ========================================

@pytest.fixture
def valid_basic_config():
    """Valid basic configuration."""
    return BasicConfig(
        worker_name="test-worker",
        domain="example.com",
        email_pattern="*@sms.{domain}"
    )


@pytest.fixture
def valid_twilio_config():
    """Valid Twilio configuration."""
    return TwilioConfig(
        account_sid="AC1234567890abcdef1234567890abcdef",
        auth_token="1234567890abcdef1234567890abcdef",
        phone_number="+15551234567"
    )


@pytest.fixture
def valid_routing_config():
    """Valid email routing configuration."""
    return EmailRoutingConfig(
        phone_extraction_method="email_prefix",
        default_country_code="+1",
        content_source="body_text",
        max_message_length=160,
        strip_html=True,
        include_sender_info=False
    )


@pytest.fixture
def valid_rate_limit_config():
    """Valid rate limiting configuration."""
    return RateLimitConfig(
        enabled=True,
        per_sender=10,
        per_recipient=20,
        storage="kv"
    )


@pytest.fixture
def valid_logging_config():
    """Valid logging configuration."""
    return LoggingConfig(
        enabled=True,
        storage_type="analytics_engine",
        log_level="info",
        log_sensitive_data=False
    )


@pytest.fixture
def valid_security_config():
    """Valid security configuration."""
    return SecurityConfig(
        enable_sender_whitelist=False,
        sender_whitelist=[],
        enable_content_filtering=False
    )


@pytest.fixture
def valid_retry_config():
    """Valid retry configuration."""
    return RetryConfig(
        enabled=True,
        max_retries=3,
        retry_delay=5,
        backoff_strategy="exponential"
    )


@pytest.fixture
def valid_integration_config():
    """Valid integration configuration."""
    return IntegrationConfig(
        enable_url_shortening=False,
        enable_error_notifications=False,
        notification_email=None
    )


@pytest.fixture
def valid_worker_config(
    valid_basic_config,
    valid_twilio_config,
    valid_routing_config,
    valid_rate_limit_config,
    valid_logging_config,
    valid_security_config,
    valid_retry_config,
    valid_integration_config
):
    """Complete valid worker configuration."""
    return WorkerConfig(
        basic=valid_basic_config,
        twilio=valid_twilio_config,
        routing=valid_routing_config,
        rate_limit=valid_rate_limit_config,
        logging=valid_logging_config,
        security=valid_security_config,
        retry=valid_retry_config,
        integrations=valid_integration_config
    )


# ========================================
# Invalid Configuration Fixtures
# ========================================

@pytest.fixture
def invalid_worker_name_configs():
    """Various invalid worker name scenarios."""
    return [
        "",  # Empty
        "Worker-Name",  # Uppercase
        "worker_name",  # Underscore
        "-worker",  # Leading hyphen
        "worker-",  # Trailing hyphen
        "worker--name",  # Consecutive hyphens
        "a" * 64,  # Too long
        "worker@name",  # Special character
        "worker name",  # Space
    ]


@pytest.fixture
def invalid_domains():
    """Various invalid domain scenarios."""
    return [
        "",  # Empty
        "example",  # No TLD
        "example.",  # Trailing dot
        ".example.com",  # Leading dot
        "exam ple.com",  # Space
        "example..com",  # Double dot
        "http://example.com",  # With protocol
        "-example.com",  # Leading hyphen
    ]


@pytest.fixture
def invalid_emails():
    """Various invalid email scenarios."""
    return [
        "",  # Empty
        "invalid",  # No @
        "@example.com",  # No local part
        "user@",  # No domain
        "user@@example.com",  # Double @
        "user @example.com",  # Space
        "user@exam ple.com",  # Space in domain
    ]


@pytest.fixture
def invalid_phone_numbers():
    """Various invalid phone number scenarios."""
    return [
        "",  # Empty
        "1234567890",  # No country code
        "+1555",  # Too short
        "+1 (555) 123-4567",  # Invalid format
        "555-1234567",  # No country code
        "+1abcdefghij",  # Letters
        "+1234567890123456789",  # Too long
    ]


@pytest.fixture
def invalid_twilio_sids():
    """Various invalid Twilio SID scenarios."""
    return [
        "",  # Empty
        "AC12345",  # Too short
        "BC1234567890abcdef1234567890abcdef",  # Wrong prefix
        "ac1234567890abcdef1234567890abcdef",  # Lowercase
        "AC1234567890abcdef1234567890abcdefg",  # Too long
        "AC1234567890XXXXXX1234567890abcdef",  # Invalid characters
    ]


# ========================================
# Test Data Fixtures
# ========================================

@pytest.fixture
def security_payloads():
    """Security test payloads for XSS, SQL injection, etc."""
    return {
        "xss": [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>",
        ],
        "sql_injection": [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "admin'--",
            "' UNION SELECT * FROM users--",
        ],
        "template_injection": [
            "{{7*7}}",
            "${process.env.SECRET}",
            "#{7*7}",
            "<%= 7*7 %>",
        ],
        "path_traversal": [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "....//....//etc/passwd",
        ],
        "command_injection": [
            "; ls -la",
            "| cat /etc/passwd",
            "& whoami",
            "`id`",
        ],
    }


@pytest.fixture
def unicode_test_data():
    """Unicode and special character test data."""
    return {
        "emoji": "Hello 🎉 World 🚀",
        "chinese": "你好世界",
        "arabic": "مرحبا بالعالم",
        "russian": "Привет мир",
        "japanese": "こんにちは世界",
        "korean": "안녕하세요 세계",
        "mixed": "Hello世界🌍مرحبا",
        "special_chars": "Café résumé naïve",
    }


@pytest.fixture
def boundary_values():
    """Boundary value test cases."""
    return {
        "message_lengths": {
            "empty": "",
            "single_char": "a",
            "exact_sms": "a" * 160,
            "over_sms": "a" * 161,
            "max_allowed": "a" * 1600,
            "over_max": "a" * 1601,
        },
        "rate_limits": {
            "min": 1,
            "low": 5,
            "medium": 50,
            "high": 500,
            "max": 1000,
        },
        "retry_values": {
            "min_retries": 1,
            "max_retries": 5,
            "over_max": 6,
            "min_delay": 1,
            "max_delay": 60,
        },
    }


@pytest.fixture
def generated_file_templates():
    """Expected file structure for generated code."""
    return {
        "files": [
            "src/index.ts",
            "wrangler.toml",
            "package.json",
            "tsconfig.json",
            ".env.example",
            ".gitignore",
            "README.md",
            "deploy.sh",
        ],
        "required_content": {
            "src/index.ts": ["import", "export default", "fetch"],
            "wrangler.toml": ["name", "main", "compatibility_date"],
            "package.json": ["name", "version", "dependencies"],
            ".env.example": ["TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN"],
        },
    }


# ========================================
# Mock Data Fixtures
# ========================================

@pytest.fixture
def mock_streamlit_session():
    """Mock Streamlit session state."""
    return {
        'generated_files': {},
        'current_config': None,
        'worker_name': 'test-worker',
        'domain': 'example.com',
        'twilio_sid': 'AC1234567890abcdef1234567890abcdef',
        'twilio_token': '1234567890abcdef1234567890abcdef',
        'twilio_phone': '+15551234567',
    }


@pytest.fixture
def sample_generated_files():
    """Sample generated files for testing."""
    return {
        "src/index.ts": "// TypeScript Worker Code\nexport default { fetch() {} }",
        "wrangler.toml": "name = 'test-worker'\nmain = 'src/index.ts'",
        "package.json": '{"name": "test-worker", "version": "1.0.0"}',
        "README.md": "# Test Worker\n\nGenerated worker code.",
    }


# ========================================
# Utility Fixtures
# ========================================

@pytest.fixture
def temp_test_dir(tmp_path):
    """Temporary directory for test files."""
    test_dir = tmp_path / "test_output"
    test_dir.mkdir()
    return test_dir


@pytest.fixture
def mock_jinja_env(mocker):
    """Mock Jinja2 environment for template testing."""
    mock_template = mocker.MagicMock()
    mock_template.render.return_value = "rendered content"

    mock_env = mocker.MagicMock()
    mock_env.get_template.return_value = mock_template

    return mock_env


# ========================================
# Test Helpers
# ========================================

@pytest.fixture
def assert_valid_typescript():
    """Helper to validate TypeScript syntax."""
    def _assert(code: str):
        """Check TypeScript code for basic validity."""
        # Basic checks
        assert "export" in code or "import" in code, "Should contain export/import"
        assert code.count("{") == code.count("}"), "Unbalanced braces"
        assert code.count("(") == code.count(")"), "Unbalanced parentheses"
        # No obvious syntax errors
        assert not code.strip().endswith(","), "Trailing comma"
    return _assert


@pytest.fixture
def assert_valid_toml():
    """Helper to validate TOML syntax."""
    def _assert(content: str):
        """Check TOML content for basic validity."""
        import tomli
        try:
            tomli.loads(content)
        except Exception as e:
            pytest.fail(f"Invalid TOML: {e}")
    return _assert


@pytest.fixture
def assert_valid_json():
    """Helper to validate JSON syntax."""
    def _assert(content: str):
        """Check JSON content for validity."""
        import json
        try:
            json.loads(content)
        except json.JSONDecodeError as e:
            pytest.fail(f"Invalid JSON: {e}")
    return _assert


# ========================================
# Performance Testing Fixtures
# ========================================

@pytest.fixture
def performance_thresholds():
    """Performance test thresholds."""
    return {
        "validation_max_ms": 100,
        "generation_max_ms": 2000,
        "template_render_max_ms": 500,
    }


# ========================================
# Parametrize Helpers
# ========================================

def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "ui: UI/component tests")
    config.addinivalue_line("markers", "security: Security tests")
    config.addinivalue_line("markers", "performance: Performance tests")
    config.addinivalue_line("markers", "edge_case: Edge case tests")
    config.addinivalue_line("markers", "slow: Slow-running tests")
