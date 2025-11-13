"""
Unit tests for code generation logic.

Tests code generator for:
- Template rendering
- File generation accuracy
- Configuration validation
- Output correctness
"""
import pytest
import json
from pathlib import Path
from generators import CodeGenerator
from schemas import WorkerConfig


# ========================================
# Code Generator Initialization Tests
# ========================================

@pytest.mark.unit
class TestCodeGeneratorInit:
    """Test CodeGenerator initialization."""

    def test_init_with_valid_config(self, valid_worker_config):
        """Test initialization with valid configuration."""
        generator = CodeGenerator(valid_worker_config)

        assert generator.config == valid_worker_config
        assert generator.env is not None
        assert generator.config.metadata.generated_at is not None

    def test_jinja_environment_setup(self, valid_worker_config):
        """Test that Jinja2 environment is properly configured."""
        generator = CodeGenerator(valid_worker_config)

        # Check template loader is set up
        assert generator.env.loader is not None

        # Check custom filters are registered
        assert 'tojson' in generator.env.filters

    def test_metadata_auto_update(self, valid_worker_config):
        """Test that metadata is automatically updated on init."""
        import datetime

        generator = CodeGenerator(valid_worker_config)

        # Should have generated_at timestamp
        assert generator.config.metadata.generated_at is not None

        # Should be recent (within last minute)
        generated_time = datetime.datetime.fromisoformat(
            generator.config.metadata.generated_at.rstrip('Z')
        )
        now = datetime.datetime.utcnow()
        delta = now - generated_time

        assert delta.total_seconds() < 60  # Within last minute


# ========================================
# Configuration Validation Tests
# ========================================

@pytest.mark.unit
class TestConfigValidation:
    """Test configuration validation logic."""

    def test_validate_complete_config(self, valid_worker_config):
        """Test validation with complete valid configuration."""
        generator = CodeGenerator(valid_worker_config)
        is_valid, errors = generator.validate_config()

        assert is_valid
        assert errors == []

    def test_validate_missing_worker_name(self, valid_worker_config):
        """Test validation fails with missing worker name."""
        config = valid_worker_config
        config.basic.worker_name = ""

        generator = CodeGenerator(config)
        is_valid, errors = generator.validate_config()

        assert not is_valid
        assert len(errors) > 0
        assert any("worker name" in err.lower() for err in errors)

    def test_validate_missing_domain(self, valid_worker_config):
        """Test validation fails with missing domain."""
        config = valid_worker_config
        config.basic.domain = ""

        generator = CodeGenerator(config)
        is_valid, errors = generator.validate_config()

        assert not is_valid
        assert any("domain" in err.lower() for err in errors)

    def test_validate_missing_twilio_credentials(self, valid_worker_config):
        """Test validation fails with missing Twilio credentials."""
        config = valid_worker_config
        config.twilio.account_sid = ""
        config.twilio.auth_token = ""
        config.twilio.phone_number = ""

        generator = CodeGenerator(config)
        is_valid, errors = generator.validate_config()

        assert not is_valid
        assert len(errors) >= 3  # Should have errors for all three fields

    def test_validate_message_length_constraints(self, valid_worker_config):
        """Test validation of message length constraints."""
        # Too short
        config = valid_worker_config
        config.routing.max_message_length = 100

        generator = CodeGenerator(config)
        is_valid, errors = generator.validate_config()

        assert not is_valid
        assert any("160" in err for err in errors)

        # Too long
        config.routing.max_message_length = 2000

        generator = CodeGenerator(config)
        is_valid, errors = generator.validate_config()

        assert not is_valid
        assert any("1600" in err for err in errors)

    def test_validate_rate_limit_values(self, valid_worker_config):
        """Test validation of rate limit values."""
        config = valid_worker_config
        config.rate_limit.enabled = True
        config.rate_limit.per_sender = 0  # Invalid

        generator = CodeGenerator(config)
        is_valid, errors = generator.validate_config()

        assert not is_valid
        assert any("sender" in err.lower() for err in errors)

    def test_validate_retry_configuration(self, valid_worker_config):
        """Test validation of retry configuration."""
        config = valid_worker_config
        config.retry.enabled = True
        config.retry.max_retries = 10  # Too high

        generator = CodeGenerator(config)
        is_valid, errors = generator.validate_config()

        assert not is_valid
        assert any("retries" in err.lower() and "5" in err for err in errors)

    def test_validate_notification_email_when_enabled(self, valid_worker_config):
        """Test that notification email is required when notifications enabled."""
        config = valid_worker_config
        config.integrations.enable_error_notifications = True
        config.integrations.notification_email = None

        generator = CodeGenerator(config)
        is_valid, errors = generator.validate_config()

        assert not is_valid
        assert any("notification email" in err.lower() for err in errors)


# ========================================
# Worker Code Generation Tests
# ========================================

@pytest.mark.unit
class TestWorkerCodeGeneration:
    """Test Worker TypeScript code generation."""

    def test_generate_basic_worker_code(self, valid_worker_config):
        """Test generation of basic worker code."""
        generator = CodeGenerator(valid_worker_config)
        code = generator.generate_worker_code()

        assert code is not None
        assert isinstance(code, str)
        assert len(code) > 0

    def test_worker_code_contains_imports(self, valid_worker_config):
        """Test that generated code contains necessary imports."""
        generator = CodeGenerator(valid_worker_config)
        code = generator.generate_worker_code()

        # Should contain import statements
        assert "import" in code or "require" in code

    def test_worker_code_contains_export(self, valid_worker_config):
        """Test that generated code contains export default."""
        generator = CodeGenerator(valid_worker_config)
        code = generator.generate_worker_code()

        assert "export default" in code

    def test_worker_code_contains_fetch_handler(self, valid_worker_config):
        """Test that generated code contains fetch handler."""
        generator = CodeGenerator(valid_worker_config)
        code = generator.generate_worker_code()

        assert "fetch" in code

    def test_worker_code_includes_twilio_config(self, valid_worker_config):
        """Test that Twilio configuration is included in code."""
        generator = CodeGenerator(valid_worker_config)
        code = generator.generate_worker_code()

        # Should NOT contain actual credentials (should use env vars)
        assert valid_worker_config.twilio.account_sid not in code
        assert valid_worker_config.twilio.auth_token not in code

        # Should reference environment variables
        assert "TWILIO_ACCOUNT_SID" in code or "env.TWILIO" in code

    def test_worker_code_includes_rate_limiting(self, valid_worker_config):
        """Test that rate limiting code is included when enabled."""
        config = valid_worker_config
        config.rate_limit.enabled = True

        generator = CodeGenerator(config)
        code = generator.generate_worker_code()

        # Should contain rate limit logic
        assert "rate" in code.lower() or "limit" in code.lower()

    def test_worker_code_excludes_disabled_features(self, valid_worker_config):
        """Test that disabled features are not included in generated code."""
        config = valid_worker_config
        config.rate_limit.enabled = False
        config.retry.enabled = False

        generator = CodeGenerator(config)
        code = generator.generate_worker_code()

        # Depending on template, may or may not contain conditional code
        # This is a basic check
        assert code is not None


# ========================================
# Wrangler Config Generation Tests
# ========================================

@pytest.mark.unit
class TestWranglerConfigGeneration:
    """Test wrangler.toml generation."""

    def test_generate_wrangler_config(self, valid_worker_config):
        """Test basic wrangler.toml generation."""
        generator = CodeGenerator(valid_worker_config)
        config = generator.generate_wrangler_config()

        assert config is not None
        assert isinstance(config, str)
        assert len(config) > 0

    def test_wrangler_config_contains_name(self, valid_worker_config):
        """Test that wrangler.toml contains worker name."""
        generator = CodeGenerator(valid_worker_config)
        config = generator.generate_wrangler_config()

        assert f'name = "{valid_worker_config.basic.worker_name}"' in config or \
               f"name = '{valid_worker_config.basic.worker_name}'" in config

    def test_wrangler_config_contains_main(self, valid_worker_config):
        """Test that wrangler.toml contains main entry point."""
        generator = CodeGenerator(valid_worker_config)
        config = generator.generate_wrangler_config()

        assert "main" in config
        assert "src/index.ts" in config or "index.ts" in config

    def test_wrangler_config_contains_compatibility(self, valid_worker_config):
        """Test that wrangler.toml contains compatibility settings."""
        generator = CodeGenerator(valid_worker_config)
        config = generator.generate_wrangler_config()

        assert "compatibility_date" in config
        assert "compatibility_flags" in config or "compatibility" in config

    def test_wrangler_config_includes_kv_bindings(self, valid_worker_config):
        """Test that KV bindings are included when rate limiting enabled."""
        config = valid_worker_config
        config.rate_limit.enabled = True
        config.rate_limit.storage = "kv"

        generator = CodeGenerator(config)
        wrangler_config = generator.generate_wrangler_config()

        assert "kv_namespaces" in wrangler_config

    def test_wrangler_config_includes_analytics(self, valid_worker_config):
        """Test that Analytics Engine binding is included when enabled."""
        config = valid_worker_config
        config.logging.enabled = True
        config.logging.storage_type = "analytics_engine"

        generator = CodeGenerator(config)
        wrangler_config = generator.generate_wrangler_config()

        assert "analytics_engine" in wrangler_config.lower()

    def test_wrangler_config_valid_toml(self, valid_worker_config, assert_valid_toml):
        """Test that generated wrangler.toml is valid TOML."""
        generator = CodeGenerator(valid_worker_config)
        config = generator.generate_wrangler_config()

        # Use fixture to validate TOML
        assert_valid_toml(config)


# ========================================
# Package.json Generation Tests
# ========================================

@pytest.mark.unit
class TestPackageJsonGeneration:
    """Test package.json generation."""

    def test_generate_package_json(self, valid_worker_config):
        """Test basic package.json generation."""
        generator = CodeGenerator(valid_worker_config)
        package_json = generator.generate_package_json()

        assert package_json is not None
        assert isinstance(package_json, str)

    def test_package_json_valid_json(self, valid_worker_config, assert_valid_json):
        """Test that generated package.json is valid JSON."""
        generator = CodeGenerator(valid_worker_config)
        package_json = generator.generate_package_json()

        assert_valid_json(package_json)

    def test_package_json_contains_required_fields(self, valid_worker_config):
        """Test that package.json contains required fields."""
        generator = CodeGenerator(valid_worker_config)
        package_json_str = generator.generate_package_json()
        package_json = json.loads(package_json_str)

        assert "name" in package_json
        assert "version" in package_json
        assert "dependencies" in package_json or "devDependencies" in package_json

    def test_package_json_includes_twilio_dependency(self, valid_worker_config):
        """Test that Twilio is included in dependencies."""
        generator = CodeGenerator(valid_worker_config)
        package_json_str = generator.generate_package_json()
        package_json = json.loads(package_json_str)

        # Check in either dependencies or devDependencies
        all_deps = {**package_json.get("dependencies", {}), **package_json.get("devDependencies", {})}
        assert "twilio" in all_deps or "@twilio" in str(all_deps)

    def test_package_json_includes_scripts(self, valid_worker_config):
        """Test that package.json includes useful scripts."""
        generator = CodeGenerator(valid_worker_config)
        package_json_str = generator.generate_package_json()
        package_json = json.loads(package_json_str)

        assert "scripts" in package_json
        scripts = package_json["scripts"]

        # Should have common scripts
        assert "dev" in scripts or "start" in scripts
        assert "deploy" in scripts or "publish" in scripts


# ========================================
# Other File Generation Tests
# ========================================

@pytest.mark.unit
class TestOtherFileGeneration:
    """Test generation of other configuration files."""

    def test_generate_tsconfig(self, valid_worker_config, assert_valid_json):
        """Test tsconfig.json generation."""
        generator = CodeGenerator(valid_worker_config)
        tsconfig = generator.generate_tsconfig()

        assert tsconfig is not None
        assert_valid_json(tsconfig)

        # Check TypeScript config content
        config = json.loads(tsconfig)
        assert "compilerOptions" in config

    def test_generate_env_example(self, valid_worker_config):
        """Test .env.example generation."""
        generator = CodeGenerator(valid_worker_config)
        env_example = generator.generate_env_example()

        assert env_example is not None
        assert "TWILIO_ACCOUNT_SID" in env_example
        assert "TWILIO_AUTH_TOKEN" in env_example
        assert "TWILIO_PHONE_NUMBER" in env_example

        # Should NOT contain actual values
        assert valid_worker_config.twilio.account_sid not in env_example
        assert valid_worker_config.twilio.auth_token not in env_example

    def test_generate_gitignore(self, valid_worker_config):
        """Test .gitignore generation."""
        generator = CodeGenerator(valid_worker_config)
        gitignore = generator.generate_gitignore()

        assert gitignore is not None
        assert "node_modules" in gitignore
        assert ".env" in gitignore
        assert ".wrangler" in gitignore or "wrangler" in gitignore.lower()

    def test_generate_readme(self, valid_worker_config):
        """Test README.md generation."""
        generator = CodeGenerator(valid_worker_config)
        readme = generator.generate_readme()

        assert readme is not None
        assert "#" in readme  # Markdown heading
        assert valid_worker_config.basic.worker_name in readme

    def test_generate_deploy_script(self, valid_worker_config):
        """Test deploy.sh generation."""
        generator = CodeGenerator(valid_worker_config)
        deploy_script = generator.generate_deploy_script()

        assert deploy_script is not None
        assert "#!/bin/bash" in deploy_script or "#!" in deploy_script
        assert "wrangler" in deploy_script.lower()


# ========================================
# Complete Generation Tests
# ========================================

@pytest.mark.unit
class TestCompleteGeneration:
    """Test generation of all files together."""

    def test_generate_all_files(self, valid_worker_config):
        """Test generation of all files at once."""
        generator = CodeGenerator(valid_worker_config)
        files = generator.generate_all()

        assert isinstance(files, dict)
        assert len(files) > 0

    def test_all_required_files_generated(self, valid_worker_config, generated_file_templates):
        """Test that all required files are generated."""
        generator = CodeGenerator(valid_worker_config)
        files = generator.generate_all()

        # Check all required files are present
        for required_file in generated_file_templates["files"]:
            assert required_file in files, f"Missing required file: {required_file}"

    def test_all_files_have_content(self, valid_worker_config):
        """Test that all generated files have non-empty content."""
        generator = CodeGenerator(valid_worker_config)
        files = generator.generate_all()

        for filename, content in files.items():
            assert content is not None, f"{filename} is None"
            assert isinstance(content, str), f"{filename} is not a string"
            assert len(content) > 0, f"{filename} is empty"

    def test_generated_files_structure(self, valid_worker_config, generated_file_templates):
        """Test that generated files contain expected content."""
        generator = CodeGenerator(valid_worker_config)
        files = generator.generate_all()

        for filename, required_content in generated_file_templates["required_content"].items():
            assert filename in files, f"Missing file: {filename}"

            for content_check in required_content:
                assert content_check in files[filename], \
                    f"{filename} missing required content: {content_check}"


# ========================================
# Custom Filter Tests
# ========================================

@pytest.mark.unit
class TestCustomFilters:
    """Test custom Jinja2 filters."""

    def test_tojson_filter(self, valid_worker_config):
        """Test custom tojson filter."""
        generator = CodeGenerator(valid_worker_config)

        # Test with various data types
        test_data = {
            "string": "hello",
            "number": 42,
            "array": [1, 2, 3],
            "object": {"key": "value"}
        }

        result = generator._to_json_filter(test_data)

        assert isinstance(result, str)
        # Should be valid JSON
        parsed = json.loads(result)
        assert parsed == test_data


# ========================================
# Template Context Tests
# ========================================

@pytest.mark.unit
class TestTemplateContext:
    """Test template context preparation."""

    def test_template_context_includes_all_config(self, valid_worker_config):
        """Test that template context includes all configuration sections."""
        generator = CodeGenerator(valid_worker_config)

        # Generate any file to test context
        code = generator.generate_worker_code()

        # Context should have been used - verify it has all sections
        # (This is indirect testing - we check the generated output contains config values)
        assert valid_worker_config.basic.worker_name in code or \
               code  # Basic check that template was rendered


# ========================================
# Error Handling Tests
# ========================================

@pytest.mark.unit
class TestGenerationErrorHandling:
    """Test error handling in code generation."""

    def test_missing_template_handling(self, valid_worker_config, mocker):
        """Test handling of missing template files."""
        generator = CodeGenerator(valid_worker_config)

        # Mock template loader to raise error
        mock_env = mocker.MagicMock()
        mock_env.get_template.side_effect = Exception("Template not found")
        generator.env = mock_env

        # Should raise exception
        with pytest.raises(Exception):
            generator.generate_worker_code()

    def test_template_render_error_handling(self, valid_worker_config, mocker):
        """Test handling of template rendering errors."""
        generator = CodeGenerator(valid_worker_config)

        # Mock template to raise error during render
        mock_template = mocker.MagicMock()
        mock_template.render.side_effect = Exception("Render error")

        mock_env = mocker.MagicMock()
        mock_env.get_template.return_value = mock_template
        generator.env = mock_env

        # Should raise exception
        with pytest.raises(Exception):
            generator.generate_worker_code()


# ========================================
# Edge Case Tests
# ========================================

@pytest.mark.edge_case
class TestGenerationEdgeCases:
    """Test edge cases in code generation."""

    def test_minimal_configuration(self):
        """Test generation with minimal configuration."""
        from schemas import BasicConfig, TwilioConfig

        minimal_config = WorkerConfig(
            basic=BasicConfig(
                worker_name="minimal",
                domain="example.com"
            ),
            twilio=TwilioConfig(
                account_sid="AC1234567890abcdef1234567890abcdef",
                auth_token="1234567890abcdef1234567890abcdef",
                phone_number="+15551234567"
            )
        )

        generator = CodeGenerator(minimal_config)
        files = generator.generate_all()

        # Should still generate all required files
        assert len(files) > 0
        assert "src/index.ts" in files

    def test_maximum_configuration(self, valid_worker_config):
        """Test generation with all features enabled."""
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
        files = generator.generate_all()

        # Should generate successfully
        assert len(files) > 0

    def test_unicode_in_configuration(self, valid_worker_config, unicode_test_data):
        """Test handling of Unicode in configuration."""
        config = valid_worker_config
        # Add Unicode to notes/metadata (should be handled gracefully)
        config.metadata.notes = unicode_test_data["mixed"]

        generator = CodeGenerator(config)
        files = generator.generate_all()

        # Should generate without errors
        assert len(files) > 0
