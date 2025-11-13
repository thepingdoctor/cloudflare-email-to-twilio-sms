"""Main code generator orchestrator."""
import os
from pathlib import Path
from typing import Dict
from jinja2 import Environment, FileSystemLoader, Template
from schemas import WorkerConfig


class CodeGenerator:
    """Main code generator for Cloudflare Worker."""

    def __init__(self, config: WorkerConfig):
        """
        Initialize code generator.

        Args:
            config: Worker configuration
        """
        self.config = config
        self.config.update_metadata()

        # Setup Jinja2 environment
        template_dir = Path(__file__).parent.parent / "templates"
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )

        # Custom filters
        self.env.filters['tojson'] = self._to_json_filter

    def _to_json_filter(self, value):
        """Convert Python value to JSON string."""
        import json
        return json.dumps(value)

    def _render_template(self, template_path: str) -> str:
        """
        Render a template with configuration.

        Args:
            template_path: Path to template file

        Returns:
            Rendered template content
        """
        template = self.env.get_template(template_path)

        # Prepare context
        context = {
            'basic': self.config.basic,
            'twilio': self.config.twilio,
            'routing': self.config.routing,
            'rate_limit': self.config.rate_limit,
            'logging': self.config.logging,
            'security': self.config.security,
            'retry': self.config.retry,
            'integrations': self.config.integrations,
            'cloudflare': self.config.cloudflare,
            'features': self.config.features,
            'metadata': self.config.metadata
        }

        return template.render(**context)

    def generate_worker_code(self) -> str:
        """
        Generate main Worker TypeScript code.

        Returns:
            TypeScript code
        """
        return self._render_template('worker/index.ts.j2')

    def generate_wrangler_config(self) -> str:
        """
        Generate wrangler.toml configuration.

        Returns:
            TOML configuration
        """
        return self._render_template('config/wrangler.toml.j2')

    def generate_package_json(self) -> str:
        """
        Generate package.json.

        Returns:
            JSON package file
        """
        return self._render_template('config/package.json.j2')

    def generate_tsconfig(self) -> str:
        """
        Generate tsconfig.json.

        Returns:
            TypeScript configuration
        """
        return self._render_template('config/tsconfig.json.j2')

    def generate_env_example(self) -> str:
        """
        Generate .env.example template.

        Returns:
            Environment file template
        """
        return self._render_template('config/.env.example.j2')

    def generate_gitignore(self) -> str:
        """
        Generate .gitignore file.

        Returns:
            Gitignore file
        """
        return self._render_template('config/.gitignore.j2')

    def generate_readme(self) -> str:
        """
        Generate README.md with setup instructions.

        Returns:
            Markdown documentation
        """
        return self._render_template('docs/README.md.j2')

    def generate_deploy_script(self) -> str:
        """
        Generate deployment bash script.

        Returns:
            Bash script
        """
        return self._render_template('docs/deploy.sh.j2')

    def generate_email_worker_code(self) -> str:
        """
        Generate Cloudflare Email Worker TypeScript code.

        Returns:
            TypeScript code for Email Worker
        """
        return self._render_template('email-worker/index.ts.j2')

    def generate_email_wrangler_config(self) -> str:
        """
        Generate wrangler.toml for Email Worker.

        Returns:
            TOML configuration for Email Worker
        """
        return self._render_template('email-worker/wrangler.toml.j2')

    def generate_email_package_json(self) -> str:
        """
        Generate package.json for Email Worker.

        Returns:
            JSON package file for Email Worker
        """
        return self._render_template('email-worker/package.json.j2')

    def generate_email_env_example(self) -> str:
        """
        Generate .env.example for Email Worker.

        Returns:
            Environment file template for Email Worker
        """
        return self._render_template('email-worker/.env.example.j2')

    def generate_email_readme(self) -> str:
        """
        Generate README.md for Email Worker.

        Returns:
            Markdown documentation for Email Worker
        """
        return self._render_template('email-worker/README.md.j2')

    def generate_email_deploy_script(self) -> str:
        """
        Generate deployment script for Email Worker.

        Returns:
            Bash script for Email Worker deployment
        """
        return self._render_template('email-worker/deploy.sh.j2')

    def generate_email_types(self) -> str:
        """
        Generate TypeScript type definitions for Email Worker.

        Returns:
            TypeScript types
        """
        return self._render_template('email-worker/types.ts.j2')

    def generate_email_utils(self) -> str:
        """
        Generate utility functions for Email Worker.

        Returns:
            TypeScript utilities
        """
        return self._render_template('email-worker/utils.ts.j2')

    def generate_all_email_worker(self) -> Dict[str, str]:
        """
        Generate all Email Worker files.

        Returns:
            Dictionary mapping filenames to content for Email Worker
        """
        files = {
            'src/index.ts': self.generate_email_worker_code(),
            'src/types.ts': self.generate_email_types(),
            'src/utils.ts': self.generate_email_utils(),
            'wrangler.toml': self.generate_email_wrangler_config(),
            'package.json': self.generate_email_package_json(),
            'tsconfig.json': self.generate_tsconfig(),
            '.env.example': self.generate_email_env_example(),
            '.gitignore': self.generate_gitignore(),
            'README.md': self.generate_email_readme(),
            'deploy.sh': self.generate_email_deploy_script()
        }

        return files

    def generate_all(self) -> Dict[str, str]:
        """
        Generate all files.

        Returns:
            Dictionary mapping filenames to content
        """
        files = {
            'src/index.ts': self.generate_worker_code(),
            'wrangler.toml': self.generate_wrangler_config(),
            'package.json': self.generate_package_json(),
            'tsconfig.json': self.generate_tsconfig(),
            '.env.example': self.generate_env_example(),
            '.gitignore': self.generate_gitignore(),
            'README.md': self.generate_readme(),
            'deploy.sh': self.generate_deploy_script()
        }

        return files

    def validate_config(self) -> tuple[bool, list[str]]:
        """
        Validate configuration.

        Returns:
            Tuple of (is_valid, list of errors)
        """
        errors = []

        # Validate basic config
        if not self.config.basic.worker_name:
            errors.append("Worker name is required")

        if not self.config.basic.domain:
            errors.append("Domain is required")

        # Validate Twilio config
        if not self.config.twilio.account_sid:
            errors.append("Twilio Account SID is required")

        if not self.config.twilio.auth_token:
            errors.append("Twilio Auth Token is required")

        if not self.config.twilio.phone_number:
            errors.append("Twilio phone number is required")

        # Validate routing
        if self.config.routing.max_message_length < 160:
            errors.append("Max message length must be at least 160")

        if self.config.routing.max_message_length > 1600:
            errors.append("Max message length cannot exceed 1600")

        # Validate rate limiting
        if self.config.rate_limit.enabled:
            if self.config.rate_limit.per_sender < 1:
                errors.append("Rate limit per sender must be at least 1")

            if self.config.rate_limit.per_recipient < 1:
                errors.append("Rate limit per recipient must be at least 1")

        # Validate retry config
        if self.config.retry.enabled:
            if self.config.retry.max_retries < 1 or self.config.retry.max_retries > 5:
                errors.append("Max retries must be between 1 and 5")

            if self.config.retry.retry_delay < 1:
                errors.append("Retry delay must be at least 1 second")

        # Validate integrations
        if self.config.integrations.enable_error_notifications:
            if not self.config.integrations.notification_email:
                errors.append("Notification email is required when error notifications are enabled")

        return len(errors) == 0, errors
