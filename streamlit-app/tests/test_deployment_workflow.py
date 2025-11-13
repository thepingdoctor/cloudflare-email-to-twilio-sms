"""
Deployment workflow integration tests.

Tests the complete deployment workflow including:
- Poetry installation
- Streamlit configuration
- Code generation
- Wrangler deployment
- Twilio integration
"""
import pytest
import subprocess
import json
from pathlib import Path
from typing import Dict, Any


# ========================================
# Poetry Installation Tests
# ========================================

@pytest.mark.integration
class TestPoetryInstallation:
    """Test Poetry installation and dependency management."""

    def test_poetry_installed(self):
        """Test that Poetry is installed and accessible."""
        try:
            result = subprocess.run(
                ["poetry", "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            assert "Poetry" in result.stdout or "poetry" in result.stdout
        except FileNotFoundError:
            pytest.skip("Poetry not installed in test environment")
        except subprocess.CalledProcessError as e:
            pytest.fail(f"Poetry version check failed: {e}")

    def test_pyproject_toml_valid(self):
        """Test that pyproject.toml is valid and parseable."""
        import tomli

        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"

        assert pyproject_path.exists(), "pyproject.toml not found"

        with open(pyproject_path, "rb") as f:
            config = tomli.load(f)

        # Verify required sections
        assert "tool" in config
        assert "poetry" in config["tool"]
        assert "dependencies" in config["tool"]["poetry"]
        assert "streamlit" in config["tool"]["poetry"]["dependencies"]

    def test_poetry_lock_exists(self):
        """Test that poetry.lock exists for reproducible builds."""
        lock_path = Path(__file__).parent.parent / "poetry.lock"
        assert lock_path.exists(), "poetry.lock not found - run 'poetry lock'"

    @pytest.mark.slow
    def test_poetry_check(self):
        """Test poetry check for configuration validation."""
        try:
            result = subprocess.run(
                ["poetry", "check"],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent,
                check=False
            )
            # poetry check returns 0 if valid
            assert result.returncode == 0, f"Poetry check failed: {result.stderr}"
        except FileNotFoundError:
            pytest.skip("Poetry not installed")


# ========================================
# Streamlit Configuration Tests
# ========================================

@pytest.mark.integration
class TestStreamlitConfiguration:
    """Test Streamlit UI configuration and startup."""

    def test_streamlit_config_exists(self):
        """Test that .streamlit/config.toml exists."""
        config_path = Path(__file__).parent.parent / ".streamlit" / "config.toml"
        # Config file is optional, but if it exists, it should be valid
        if config_path.exists():
            import tomli
            with open(config_path, "rb") as f:
                config = tomli.load(f)
            assert isinstance(config, dict)

    def test_app_module_importable(self):
        """Test that app module can be imported."""
        try:
            import sys
            app_dir = Path(__file__).parent.parent
            if str(app_dir) not in sys.path:
                sys.path.insert(0, str(app_dir))

            import app

            # Check key functions exist
            assert hasattr(app, "main")
            assert hasattr(app, "initialize_session_state")
        except ImportError as e:
            pytest.fail(f"Failed to import app module: {e}")

    def test_all_dependencies_importable(self):
        """Test that all required dependencies can be imported."""
        required_modules = [
            "streamlit",
            "jinja2",
            "validators",
            "pydantic",
            "phonenumbers",
        ]

        missing_modules = []
        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                missing_modules.append(module)

        assert len(missing_modules) == 0, f"Missing modules: {missing_modules}"


# ========================================
# Code Generation Workflow Tests
# ========================================

@pytest.mark.integration
class TestCodeGenerationWorkflow:
    """Test complete code generation workflow."""

    def test_end_to_end_generation(self, valid_worker_config):
        """Test complete workflow from config to files."""
        from generators import CodeGenerator

        # Step 1: Create generator
        generator = CodeGenerator(valid_worker_config)

        # Step 2: Validate configuration
        is_valid, errors = generator.validate_config()
        assert is_valid, f"Validation failed: {errors}"

        # Step 3: Generate all files
        files = generator.generate_all()

        # Step 4: Verify all required files generated
        required_files = [
            "src/index.ts",
            "wrangler.toml",
            "package.json",
            "tsconfig.json",
            ".env.example",
            ".gitignore",
            "README.md",
            "deploy.sh"
        ]

        for required_file in required_files:
            assert required_file in files, f"Missing file: {required_file}"
            assert len(files[required_file]) > 0, f"Empty file: {required_file}"

    def test_generated_files_deployable(self, valid_worker_config, tmp_path):
        """Test that generated files can be deployed (structure check)."""
        from generators import CodeGenerator

        generator = CodeGenerator(valid_worker_config)
        files = generator.generate_all()

        # Write files to temp directory
        for filename, content in files.items():
            file_path = tmp_path / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)

        # Verify structure
        assert (tmp_path / "src" / "index.ts").exists()
        assert (tmp_path / "wrangler.toml").exists()
        assert (tmp_path / "package.json").exists()

        # Verify package.json is valid
        package_json = json.loads((tmp_path / "package.json").read_text())
        assert "name" in package_json
        assert "dependencies" in package_json or "devDependencies" in package_json


# ========================================
# Wrangler Configuration Tests
# ========================================

@pytest.mark.integration
class TestWranglerConfiguration:
    """Test Wrangler configuration validation."""

    def test_wrangler_toml_structure(self, valid_worker_config):
        """Test that generated wrangler.toml has correct structure."""
        from generators import CodeGenerator
        import tomli

        generator = CodeGenerator(valid_worker_config)
        wrangler_toml = generator.generate_wrangler_config()

        # Parse TOML
        config = tomli.loads(wrangler_toml)

        # Verify required fields
        assert "name" in config
        assert "main" in config
        assert "compatibility_date" in config

        # Verify name matches config
        assert config["name"] == valid_worker_config.basic.worker_name

    def test_wrangler_toml_bindings(self, valid_worker_config):
        """Test that Wrangler bindings are correctly configured."""
        from generators import CodeGenerator
        import tomli

        # Enable features that require bindings
        config = valid_worker_config
        config.rate_limit.enabled = True
        config.rate_limit.storage = "kv"
        config.logging.enabled = True
        config.logging.storage_type = "analytics_engine"

        generator = CodeGenerator(config)
        wrangler_toml = generator.generate_wrangler_config()

        toml_config = tomli.loads(wrangler_toml)

        # Check for KV namespace binding
        assert "kv_namespaces" in toml_config or \
               "[[kv_namespaces]]" in wrangler_toml

        # Check for Analytics Engine binding
        assert "analytics_engine" in wrangler_toml.lower()

    def test_wrangler_env_vars_reference(self, valid_worker_config):
        """Test that wrangler.toml doesn't contain hardcoded secrets."""
        from generators import CodeGenerator

        generator = CodeGenerator(valid_worker_config)
        wrangler_toml = generator.generate_wrangler_config()

        # Verify no hardcoded secrets
        assert valid_worker_config.twilio.account_sid not in wrangler_toml
        assert valid_worker_config.twilio.auth_token not in wrangler_toml
        assert valid_worker_config.twilio.phone_number not in wrangler_toml


# ========================================
# Credential Security Tests
# ========================================

@pytest.mark.integration
@pytest.mark.security
class TestCredentialSecurity:
    """Test that credentials are handled securely throughout workflow."""

    def test_no_credentials_in_generated_code(self, valid_worker_config):
        """Test that actual credentials never appear in generated code."""
        from generators import CodeGenerator

        generator = CodeGenerator(valid_worker_config)
        files = generator.generate_all()

        sensitive_values = [
            valid_worker_config.twilio.account_sid,
            valid_worker_config.twilio.auth_token,
            valid_worker_config.twilio.phone_number,
        ]

        for filename, content in files.items():
            for sensitive_value in sensitive_values:
                assert sensitive_value not in content, \
                    f"Credential found in {filename}: {sensitive_value[:10]}..."

    def test_env_example_has_placeholders(self, valid_worker_config):
        """Test that .env.example uses placeholders."""
        from generators import CodeGenerator

        generator = CodeGenerator(valid_worker_config)
        env_example = generator.generate_env_example()

        # Should have variable names
        assert "TWILIO_ACCOUNT_SID" in env_example
        assert "TWILIO_AUTH_TOKEN" in env_example
        assert "TWILIO_PHONE_NUMBER" in env_example

        # Should NOT have actual values
        assert valid_worker_config.twilio.account_sid not in env_example
        assert valid_worker_config.twilio.auth_token not in env_example

    def test_gitignore_excludes_secrets(self, valid_worker_config):
        """Test that .gitignore properly excludes secret files."""
        from generators import CodeGenerator

        generator = CodeGenerator(valid_worker_config)
        gitignore = generator.generate_gitignore()

        # Should exclude sensitive files
        assert ".env" in gitignore
        assert "!.env.example" in gitignore or ".env.example" not in gitignore.split("\n.env")[0]
        assert "secrets" in gitignore.lower() or "secret" in gitignore.lower()


# ========================================
# Deployment Validation Tests
# ========================================

@pytest.mark.integration
class TestDeploymentValidation:
    """Test deployment validation and readiness checks."""

    def test_package_json_scripts(self, valid_worker_config):
        """Test that package.json has required deployment scripts."""
        from generators import CodeGenerator

        generator = CodeGenerator(valid_worker_config)
        package_json_str = generator.generate_package_json()
        package_json = json.loads(package_json_str)

        assert "scripts" in package_json
        scripts = package_json["scripts"]

        # Should have dev and deploy scripts
        assert "dev" in scripts or "start" in scripts
        assert "deploy" in scripts or "publish" in scripts

    def test_deploy_script_executable(self, valid_worker_config):
        """Test that deploy script has proper structure."""
        from generators import CodeGenerator

        generator = CodeGenerator(valid_worker_config)
        deploy_script = generator.generate_deploy_script()

        # Should have shebang
        assert deploy_script.startswith("#!") or "#!/bin/bash" in deploy_script

        # Should have wrangler commands
        assert "wrangler" in deploy_script.lower()
        assert "deploy" in deploy_script.lower() or "publish" in deploy_script.lower()

    def test_readme_deployment_instructions(self, valid_worker_config):
        """Test that README includes deployment instructions."""
        from generators import CodeGenerator

        generator = CodeGenerator(valid_worker_config)
        readme = generator.generate_readme()

        # Should have deployment section
        assert "deploy" in readme.lower()
        assert "wrangler" in readme.lower() or "cloudflare" in readme.lower()

        # Should mention email routing setup
        assert "email routing" in readme.lower() or "email" in readme.lower()


# ========================================
# Error Handling Tests
# ========================================

@pytest.mark.integration
class TestDeploymentErrorHandling:
    """Test error handling in deployment workflow."""

    def test_invalid_config_prevents_generation(self):
        """Test that invalid config prevents code generation."""
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

    def test_missing_required_fields_validation(self):
        """Test validation of missing required fields."""
        from generators import CodeGenerator
        from schemas import WorkerConfig, BasicConfig, TwilioConfig

        # Missing worker name
        config = WorkerConfig(
            basic=BasicConfig(worker_name="", domain="example.com"),
            twilio=TwilioConfig(
                account_sid="AC1234567890abcdef1234567890abcdef",
                auth_token="1234567890abcdef1234567890abcdef",
                phone_number="+15551234567"
            )
        )

        generator = CodeGenerator(config)
        is_valid, errors = generator.validate_config()

        assert not is_valid
        assert any("worker name" in err.lower() for err in errors)


# ========================================
# Integration Test Scenarios
# ========================================

@pytest.mark.integration
class TestUserWorkflowScenarios:
    """Test complete user workflow scenarios."""

    def test_scenario_basic_deployment(self, valid_worker_config):
        """Test basic deployment scenario: minimal config to deployment."""
        from generators import CodeGenerator

        # User configures basic settings
        config = valid_worker_config
        config.rate_limit.enabled = False
        config.logging.enabled = False
        config.retry.enabled = False

        # Generate code
        generator = CodeGenerator(config)
        is_valid, _ = generator.validate_config()
        assert is_valid

        files = generator.generate_all()
        assert len(files) >= 8

    def test_scenario_full_featured_deployment(self, valid_worker_config):
        """Test full-featured deployment: all features enabled."""
        from generators import CodeGenerator

        # User enables all features
        config = valid_worker_config
        config.rate_limit.enabled = True
        config.logging.enabled = True
        config.retry.enabled = True
        config.security.enable_sender_whitelist = True
        config.security.sender_whitelist = ["allowed@example.com"]
        config.integrations.enable_error_notifications = True
        config.integrations.notification_email = "admin@example.com"

        # Generate code
        generator = CodeGenerator(config)
        is_valid, _ = generator.validate_config()
        assert is_valid

        files = generator.generate_all()
        assert len(files) >= 8

    def test_scenario_rate_limited_deployment(self, valid_worker_config):
        """Test rate-limited deployment scenario."""
        from generators import CodeGenerator
        import tomli

        # User enables rate limiting
        config = valid_worker_config
        config.rate_limit.enabled = True
        config.rate_limit.per_sender = 5
        config.rate_limit.storage = "kv"

        # Generate code
        generator = CodeGenerator(config)
        files = generator.generate_all()

        # Verify KV namespace in wrangler.toml
        wrangler_config = tomli.loads(files["wrangler.toml"])
        assert "kv_namespaces" in wrangler_config or \
               "[[kv_namespaces]]" in files["wrangler.toml"]


# ========================================
# Performance Tests
# ========================================

@pytest.mark.integration
@pytest.mark.performance
class TestDeploymentPerformance:
    """Test deployment workflow performance."""

    def test_generation_performance(self, valid_worker_config):
        """Test that code generation completes quickly."""
        import time
        from generators import CodeGenerator

        start = time.time()

        generator = CodeGenerator(valid_worker_config)
        generator.validate_config()
        files = generator.generate_all()

        duration = time.time() - start

        # Should complete in under 2 seconds
        assert duration < 2.0, f"Generation took {duration:.2f}s (too slow)"
        assert len(files) > 0

    def test_validation_performance(self, valid_worker_config):
        """Test that config validation is fast."""
        import time
        from generators import CodeGenerator

        start = time.time()

        generator = CodeGenerator(valid_worker_config)
        is_valid, errors = generator.validate_config()

        duration = time.time() - start

        # Should validate in under 100ms
        assert duration < 0.1, f"Validation took {duration*1000:.2f}ms (too slow)"
        assert is_valid
