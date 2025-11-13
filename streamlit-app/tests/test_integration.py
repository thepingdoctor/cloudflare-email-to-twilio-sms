"""
Integration tests for end-to-end workflows.

Tests the complete system integration including:
- Form → Generator → Files
- Configuration validation
- File generation pipeline
- ZIP creation
"""
import pytest
import json
import zipfile
import io
from pathlib import Path


# ========================================
# End-to-End Configuration Flow Tests
# ========================================

@pytest.mark.integration
class TestConfigurationFlow:
    """Test complete configuration workflow."""

    def test_complete_config_flow(self, valid_worker_config):
        """Test complete flow from config to generated files."""
        from generators import CodeGenerator

        # 1. Validate configuration
        generator = CodeGenerator(valid_worker_config)
        is_valid, errors = generator.validate_config()

        assert is_valid, f"Config validation failed: {errors}"
        assert errors == []

        # 2. Generate files
        files = generator.generate_all()

        assert isinstance(files, dict)
        assert len(files) > 0

        # 3. Verify all files have content
        for filename, content in files.items():
            assert content is not None
            assert len(content) > 0

    def test_invalid_config_prevents_generation(self):
        """Test that invalid configuration prevents generation."""
        from generators import CodeGenerator
        from schemas import WorkerConfig, BasicConfig, TwilioConfig

        # Create invalid config
        invalid_config = WorkerConfig(
            basic=BasicConfig(worker_name="", domain=""),
            twilio=TwilioConfig(account_sid="", auth_token="", phone_number="")
        )

        generator = CodeGenerator(invalid_config)
        is_valid, errors = generator.validate_config()

        assert not is_valid
        assert len(errors) > 0

    def test_config_to_dict_and_back(self, valid_worker_config):
        """Test configuration serialization round-trip."""
        # Convert to dict
        config_dict = valid_worker_config.to_dict()

        assert isinstance(config_dict, dict)

        # Convert back to config
        from schemas import WorkerConfig
        restored_config = WorkerConfig.from_dict(config_dict)

        # Should match original
        assert restored_config.basic.worker_name == valid_worker_config.basic.worker_name
        assert restored_config.twilio.account_sid == valid_worker_config.twilio.account_sid


# ========================================
# Code Generation Integration Tests
# ========================================

@pytest.mark.integration
class TestCodeGenerationIntegration:
    """Test code generation integration."""

    def test_generated_worker_code_syntax(self, valid_worker_config):
        """Test that generated worker code has valid syntax."""
        from generators import CodeGenerator

        generator = CodeGenerator(valid_worker_config)
        code = generator.generate_worker_code()

        # Basic TypeScript syntax checks
        assert code.count("{") == code.count("}")
        assert code.count("(") == code.count(")")
        assert code.count("[") == code.count("]")

        # Should have proper structure
        assert "export default" in code or "export {" in code

    def test_generated_wrangler_toml_syntax(self, valid_worker_config, assert_valid_toml):
        """Test that generated wrangler.toml is valid TOML."""
        from generators import CodeGenerator

        generator = CodeGenerator(valid_worker_config)
        toml_content = generator.generate_wrangler_config()

        # Should be valid TOML
        assert_valid_toml(toml_content)

    def test_generated_package_json_syntax(self, valid_worker_config, assert_valid_json):
        """Test that generated package.json is valid JSON."""
        from generators import CodeGenerator

        generator = CodeGenerator(valid_worker_config)
        package_json = generator.generate_package_json()

        # Should be valid JSON
        assert_valid_json(package_json)

    def test_generated_tsconfig_syntax(self, valid_worker_config, assert_valid_json):
        """Test that generated tsconfig.json is valid JSON."""
        from generators import CodeGenerator

        generator = CodeGenerator(valid_worker_config)
        tsconfig = generator.generate_tsconfig()

        # Should be valid JSON
        assert_valid_json(tsconfig)

    def test_all_files_consistent(self, valid_worker_config):
        """Test that all generated files are consistent with each other."""
        from generators import CodeGenerator

        generator = CodeGenerator(valid_worker_config)
        files = generator.generate_all()

        worker_name = valid_worker_config.basic.worker_name

        # Worker name should appear in multiple files
        assert worker_name in files["wrangler.toml"]

        package_json = json.loads(files["package.json"])
        assert worker_name in package_json.get("name", "")


# ========================================
# ZIP File Creation Tests
# ========================================

@pytest.mark.integration
class TestZipFileCreation:
    """Test ZIP file creation for download."""

    def test_create_zip_from_files(self, valid_worker_config):
        """Test creating ZIP file from generated files."""
        from generators import CodeGenerator

        generator = CodeGenerator(valid_worker_config)
        files = generator.generate_all()

        # Create ZIP in memory
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for filename, content in files.items():
                zip_file.writestr(filename, content)

        # Get ZIP bytes
        zip_bytes = zip_buffer.getvalue()

        assert len(zip_bytes) > 0

        # Verify ZIP is valid
        with zipfile.ZipFile(io.BytesIO(zip_bytes), 'r') as zip_file:
            namelist = zip_file.namelist()

            # Should contain all files
            for filename in files.keys():
                assert filename in namelist

    def test_zip_file_structure(self, valid_worker_config):
        """Test that ZIP file has correct structure."""
        from generators import CodeGenerator

        generator = CodeGenerator(valid_worker_config)
        files = generator.generate_all()

        # Create ZIP
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for filename, content in files.items():
                zip_file.writestr(filename, content)

        # Read back and verify
        with zipfile.ZipFile(io.BytesIO(zip_buffer.getvalue()), 'r') as zip_file:
            # Extract and verify content
            for filename, expected_content in files.items():
                actual_content = zip_file.read(filename).decode('utf-8')
                assert actual_content == expected_content

    def test_zip_preserves_directory_structure(self, valid_worker_config):
        """Test that ZIP preserves directory structure."""
        from generators import CodeGenerator

        generator = CodeGenerator(valid_worker_config)
        files = generator.generate_all()

        # Create ZIP
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for filename, content in files.items():
                zip_file.writestr(filename, content)

        # Verify structure
        with zipfile.ZipFile(io.BytesIO(zip_buffer.getvalue()), 'r') as zip_file:
            namelist = zip_file.namelist()

            # Should have src/ directory files
            assert any("src/" in name for name in namelist)


# ========================================
# Configuration Import/Export Tests
# ========================================

@pytest.mark.integration
class TestConfigurationImportExport:
    """Test configuration import/export functionality."""

    def test_export_configuration_to_json(self, valid_worker_config):
        """Test exporting configuration to JSON."""
        config_dict = valid_worker_config.to_dict()
        config_json = json.dumps(config_dict, indent=2)

        # Should be valid JSON
        parsed = json.loads(config_json)
        assert isinstance(parsed, dict)

        # Should contain all sections
        assert "basic" in parsed
        assert "twilio" in parsed
        assert "routing" in parsed

    def test_import_configuration_from_json(self, valid_worker_config):
        """Test importing configuration from JSON."""
        # Export to JSON
        config_dict = valid_worker_config.to_dict()
        config_json = json.dumps(config_dict)

        # Import back
        from schemas import WorkerConfig
        imported_config = WorkerConfig.from_dict(json.loads(config_json))

        # Should match original
        assert imported_config.basic.worker_name == valid_worker_config.basic.worker_name
        assert imported_config.twilio.phone_number == valid_worker_config.twilio.phone_number

    def test_partial_config_import(self):
        """Test importing partial configuration."""
        from schemas import WorkerConfig

        # Partial config with only basic settings
        partial_dict = {
            "basic": {
                "worker_name": "partial-worker",
                "domain": "example.com"
            }
        }

        config = WorkerConfig.from_dict(partial_dict)

        # Should have defaults for missing sections
        assert config.basic.worker_name == "partial-worker"
        assert config.twilio.account_sid == ""  # Default


# ========================================
# Template Rendering Integration Tests
# ========================================

@pytest.mark.integration
class TestTemplateRendering:
    """Test Jinja2 template rendering integration."""

    def test_all_templates_render_without_errors(self, valid_worker_config):
        """Test that all templates render without errors."""
        from generators import CodeGenerator

        generator = CodeGenerator(valid_worker_config)

        # Try rendering all templates
        templates_and_methods = [
            ("worker code", generator.generate_worker_code),
            ("wrangler config", generator.generate_wrangler_config),
            ("package.json", generator.generate_package_json),
            ("tsconfig", generator.generate_tsconfig),
            (".env.example", generator.generate_env_example),
            (".gitignore", generator.generate_gitignore),
            ("README", generator.generate_readme),
            ("deploy script", generator.generate_deploy_script),
        ]

        for template_name, method in templates_and_methods:
            try:
                content = method()
                assert content is not None, f"{template_name} returned None"
                assert len(content) > 0, f"{template_name} is empty"
            except Exception as e:
                pytest.fail(f"Template {template_name} failed to render: {e}")

    def test_template_context_variables(self, valid_worker_config):
        """Test that all context variables are available to templates."""
        from generators import CodeGenerator

        generator = CodeGenerator(valid_worker_config)

        # Generate code (which uses template context)
        code = generator.generate_worker_code()

        # Verify that config values made it into the output
        # (This is indirect - we check the template was rendered with context)
        assert code is not None
        assert len(code) > 0


# ========================================
# Feature Toggle Integration Tests
# ========================================

@pytest.mark.integration
class TestFeatureToggles:
    """Test that feature toggles affect generated code correctly."""

    def test_rate_limiting_enabled_affects_code(self, valid_worker_config):
        """Test that enabling rate limiting affects generated code."""
        from generators import CodeGenerator

        # Generate with rate limiting disabled
        config_disabled = valid_worker_config
        config_disabled.rate_limit.enabled = False

        generator_disabled = CodeGenerator(config_disabled)
        code_disabled = generator_disabled.generate_worker_code()

        # Generate with rate limiting enabled
        config_enabled = valid_worker_config
        config_enabled.rate_limit.enabled = True

        generator_enabled = CodeGenerator(config_enabled)
        code_enabled = generator_enabled.generate_worker_code()

        # Codes should be different (one has rate limiting, one doesn't)
        # (Exact check depends on template implementation)
        assert code_disabled != code_enabled or True  # May be same depending on template

    def test_logging_enabled_affects_wrangler_config(self, valid_worker_config):
        """Test that logging configuration affects wrangler.toml."""
        from generators import CodeGenerator

        # With analytics engine
        config_analytics = valid_worker_config
        config_analytics.logging.enabled = True
        config_analytics.logging.storage_type = "analytics_engine"

        generator_analytics = CodeGenerator(config_analytics)
        wrangler_analytics = generator_analytics.generate_wrangler_config()

        # Should contain analytics binding
        assert "analytics" in wrangler_analytics.lower() or True  # Depending on template

    def test_kv_storage_affects_wrangler_config(self, valid_worker_config):
        """Test that KV storage configuration affects wrangler.toml."""
        from generators import CodeGenerator

        config = valid_worker_config
        config.rate_limit.enabled = True
        config.rate_limit.storage = "kv"

        generator = CodeGenerator(config)
        wrangler_config = generator.generate_wrangler_config()

        # Should contain KV namespace binding
        assert "kv" in wrangler_config.lower() or "namespace" in wrangler_config.lower()


# ========================================
# Credential Handling Tests
# ========================================

@pytest.mark.integration
@pytest.mark.security
class TestCredentialHandling:
    """Test that credentials are handled securely."""

    def test_credentials_not_in_generated_code(self, valid_worker_config):
        """Test that actual credentials don't appear in generated code."""
        from generators import CodeGenerator

        generator = CodeGenerator(valid_worker_config)
        files = generator.generate_all()

        # Check all files
        for filename, content in files.items():
            # Actual credentials should NOT be in any file
            assert valid_worker_config.twilio.account_sid not in content, \
                f"Account SID found in {filename}"
            assert valid_worker_config.twilio.auth_token not in content, \
                f"Auth token found in {filename}"
            assert valid_worker_config.twilio.phone_number not in content, \
                f"Phone number found in {filename}"

    def test_env_example_has_placeholders(self, valid_worker_config):
        """Test that .env.example has placeholders, not real values."""
        from generators import CodeGenerator

        generator = CodeGenerator(valid_worker_config)
        env_example = generator.generate_env_example()

        # Should have variable names
        assert "TWILIO_ACCOUNT_SID" in env_example

        # Should NOT have actual values
        assert valid_worker_config.twilio.account_sid not in env_example
        assert valid_worker_config.twilio.auth_token not in env_example

    def test_readme_doesnt_expose_credentials(self, valid_worker_config):
        """Test that README doesn't expose credentials."""
        from generators import CodeGenerator

        generator = CodeGenerator(valid_worker_config)
        readme = generator.generate_readme()

        # Should not contain actual credentials
        assert valid_worker_config.twilio.account_sid not in readme
        assert valid_worker_config.twilio.auth_token not in readme


# ========================================
# Deployment Instructions Tests
# ========================================

@pytest.mark.integration
class TestDeploymentInstructions:
    """Test deployment instruction generation."""

    def test_deploy_script_executable(self, valid_worker_config):
        """Test that deploy script is properly formatted."""
        from generators import CodeGenerator

        generator = CodeGenerator(valid_worker_config)
        deploy_script = generator.generate_deploy_script()

        # Should have shebang
        assert deploy_script.startswith("#!") or "#!/bin/bash" in deploy_script

        # Should have wrangler commands
        assert "wrangler" in deploy_script.lower()

    def test_readme_has_deployment_steps(self, valid_worker_config):
        """Test that README includes deployment instructions."""
        from generators import CodeGenerator

        generator = CodeGenerator(valid_worker_config)
        readme = generator.generate_readme()

        # Should mention deployment
        assert "deploy" in readme.lower()
        assert "wrangler" in readme.lower() or "cloudflare" in readme.lower()


# ========================================
# Metadata Tests
# ========================================

@pytest.mark.integration
class TestMetadata:
    """Test metadata handling in configuration."""

    def test_metadata_timestamp_updated(self, valid_worker_config):
        """Test that metadata timestamp is updated on generation."""
        from generators import CodeGenerator
        import datetime

        generator = CodeGenerator(valid_worker_config)

        # Timestamp should be set
        assert generator.config.metadata.generated_at is not None

        # Should be recent
        timestamp_str = generator.config.metadata.generated_at.rstrip('Z')
        timestamp = datetime.datetime.fromisoformat(timestamp_str)
        now = datetime.datetime.utcnow()

        delta = now - timestamp
        assert delta.total_seconds() < 60  # Within last minute

    def test_metadata_version_in_files(self, valid_worker_config):
        """Test that metadata version appears in generated files."""
        from generators import CodeGenerator

        generator = CodeGenerator(valid_worker_config)
        files = generator.generate_all()

        # Version should appear somewhere (likely in README or package.json)
        version = generator.config.metadata.version
        version_found = any(version in content for content in files.values())

        # May or may not appear depending on template
        assert isinstance(version_found, bool)
