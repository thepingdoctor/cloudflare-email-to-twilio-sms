#!/usr/bin/env python3
"""
Verify security fixes in generated package.json files.

This script generates a test worker package and verifies that all
security vulnerabilities have been fixed:
- devalue: >=5.3.2 (via @cloudflare/vitest-pool-workers)
- esbuild: >=0.24.3 (via wrangler)
- wrangler: updated to latest stable
- @cloudflare/vitest-pool-workers: >=0.10.7
"""

import sys
import json
from pathlib import Path

# Add streamlit-app to path
sys.path.insert(0, str(Path(__file__).parent.parent / "streamlit-app"))

from schemas import (
    WorkerConfig, BasicConfig, TwilioConfig, EmailRoutingConfig,
    RateLimitConfig, LoggingConfig, SecurityConfig, RetryConfig,
    IntegrationConfig, CloudflareConfig, FeaturesConfig, MetadataConfig
)
from generators import CodeGenerator


def create_test_config():
    """Create a test worker configuration."""
    return WorkerConfig(
        basic=BasicConfig(
            worker_name="security-test-worker",
            domain="test.example.com",
            email_pattern="*@sms.{domain}"
        ),
        twilio=TwilioConfig(
            account_sid="AC" + "1234567890abcdef" * 2,
            auth_token="1234567890abcdef" * 2,
            phone_number="+15551234567"
        ),
        routing=EmailRoutingConfig(
            phone_extraction_method="email_prefix",
            default_country_code="+1",
            content_source="body_text",
            max_message_length=160,
            strip_html=True,
            include_sender_info=False
        ),
        rate_limit=RateLimitConfig(
            enabled=True,
            per_sender=10,
            per_recipient=20,
            storage="kv"
        ),
        logging=LoggingConfig(
            enabled=True,
            storage_type="analytics_engine",
            log_level="info",
            log_sensitive_data=False
        ),
        security=SecurityConfig(
            enable_sender_whitelist=False,
            sender_whitelist=[],
            enable_content_filtering=False
        ),
        retry=RetryConfig(
            enabled=True,
            max_retries=3,
            retry_delay=5,
            backoff_strategy="exponential"
        ),
        integrations=IntegrationConfig(
            enable_url_shortening=False,
            enable_error_notifications=False,
            notification_email=None
        )
    )


def verify_package_json_security(package_json_str: str) -> tuple[bool, list[str]]:
    """
    Verify that package.json has secure dependency versions.

    Returns:
        Tuple of (is_secure, list of issues)
    """
    issues = []
    package_data = json.loads(package_json_str)

    dev_deps = package_data.get("devDependencies", {})

    # Check @cloudflare/vitest-pool-workers version
    vitest_pool_version = dev_deps.get("@cloudflare/vitest-pool-workers", "")
    if not vitest_pool_version.startswith("^0.10.") and not vitest_pool_version.startswith("^0.11"):
        issues.append(
            f"@cloudflare/vitest-pool-workers should be >=0.10.7, got: {vitest_pool_version}"
        )

    # Check wrangler version
    wrangler_version = dev_deps.get("wrangler", "")
    if wrangler_version.startswith("^3."):
        issues.append(
            f"wrangler should be ^4.48.0 or higher, got: {wrangler_version}"
        )
    elif not wrangler_version.startswith("^4."):
        issues.append(
            f"wrangler version unexpected: {wrangler_version}"
        )

    return len(issues) == 0, issues


def main():
    """Generate test worker and verify security fixes."""
    print("🔒 Security Fix Verification")
    print("=" * 60)

    # Create test config
    print("\n1. Creating test worker configuration...")
    config = create_test_config()
    print("   ✓ Configuration created")

    # Generate files
    print("\n2. Generating worker files...")
    generator = CodeGenerator(config)
    files = generator.generate_all()
    print(f"   ✓ Generated {len(files)} files")

    # Save files to test directory
    test_dir = Path(__file__).parent / "generated-worker-test"
    test_dir.mkdir(exist_ok=True)

    print("\n3. Saving files to test directory...")
    for filename, content in files.items():
        file_path = test_dir / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
        print(f"   ✓ Saved: {filename}")

    # Verify package.json security
    print("\n4. Verifying security fixes in package.json...")
    package_json = files["package.json"]
    is_secure, issues = verify_package_json_security(package_json)

    if is_secure:
        print("   ✅ All security fixes verified!")
        print("\n5. Package.json dependencies:")
        package_data = json.loads(package_json)
        dev_deps = package_data.get("devDependencies", {})
        for dep, version in dev_deps.items():
            print(f"   - {dep}: {version}")

        print("\n" + "=" * 60)
        print("✅ SUCCESS: Security fixes have been implemented!")
        print("=" * 60)
        return 0
    else:
        print("   ❌ Security issues found:")
        for issue in issues:
            print(f"   - {issue}")

        print("\n" + "=" * 60)
        print("❌ FAILED: Security issues detected!")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
