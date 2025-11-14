#!/usr/bin/env python3
"""Generate test worker for security validation."""
import sys
import os
from pathlib import Path

# Add streamlit-app to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'streamlit-app'))

from schemas import (
    WorkerConfig, BasicConfig, TwilioConfig, EmailRoutingConfig,
    RateLimitConfig, LoggingConfig, SecurityConfig, RetryConfig,
    IntegrationConfig, CloudflareConfig, FeaturesConfig, MetadataConfig
)
from generators import CodeGenerator


def generate_test_worker(output_dir: str = 'test-worker-output'):
    """Generate a test worker with minimal configuration."""

    # Create minimal config for testing
    config = WorkerConfig(
        basic=BasicConfig(
            worker_name="test-email-to-sms",
            domain="test.example.com",
            email_pattern="*@sms.test.example.com"
        ),
        twilio=TwilioConfig(
            account_sid="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            auth_token="test_auth_token_xxxxxxxxxxxx",
            phone_number="+15551234567"
        ),
        routing=EmailRoutingConfig(
            phone_extraction_method="email_prefix",
            default_country_code="+1",
            content_source="body_text",
            max_message_length=160
        ),
        rate_limit=RateLimitConfig(
            enabled=True,
            per_sender=10,
            per_recipient=20
        ),
        logging=LoggingConfig(
            enabled=True,
            log_level="info"
        ),
        security=SecurityConfig(
            enable_sender_whitelist=False,
            enable_content_filtering=False
        ),
        retry=RetryConfig(
            enabled=True,
            max_retries=3
        ),
        integrations=IntegrationConfig(
            enable_error_notifications=False
        ),
        cloudflare=CloudflareConfig(
            compatibility_date="2024-10-22"
        ),
        features=FeaturesConfig(
            enable_bidirectional=False,
            enable_mms=False
        ),
        metadata=MetadataConfig(
            version="1.0.0",
            generated_by="security-validation-test",
            author="tester-agent"
        )
    )

    # Generate files
    generator = CodeGenerator(config)
    files = generator.generate_all()

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Write all files
    for filename, content in files.items():
        file_path = output_path / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding='utf-8')
        print(f"✓ Generated: {filename}")

    print(f"\n✅ Test worker generated successfully in: {output_dir}")
    return output_path


if __name__ == "__main__":
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "test-worker-output"
    generate_test_worker(output_dir)
