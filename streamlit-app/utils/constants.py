"""Application constants and configuration defaults."""

# Application Info
APP_TITLE = "Email-to-SMS Code Generator"
APP_SUBTITLE = "Cloudflare Workers + Twilio Integration"
APP_VERSION = "1.0.0"

# Default Values
DEFAULT_WORKER_NAME = "email-to-sms-worker"
DEFAULT_EMAIL_PATTERN = "*@sms.{domain}"
DEFAULT_COUNTRY_CODE = "+1"
DEFAULT_MAX_MESSAGE_LENGTH = 160
DEFAULT_RATE_LIMIT_SENDER = 10
DEFAULT_RATE_LIMIT_RECIPIENT = 20
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 5

# Phone Extraction Methods
PHONE_EXTRACTION_METHODS = {
    "email_prefix": "Email prefix (15551234567@sms.domain.com)",
    "subject_line": "Subject line (Subject: To: 555-123-4567)",
    "custom_header": "Custom header (X-SMS-To: +15551234567)",
    "all_methods": "All methods (try all in order)"
}

# Content Source Options
CONTENT_SOURCE_OPTIONS = {
    "body_text": "Email body (text only)",
    "body_html": "Email body (HTML allowed)",
    "subject": "Email subject",
    "subject_and_body": "Email subject + body"
}

# Log Storage Types
LOG_STORAGE_TYPES = {
    "console": "Console only",
    "kv": "KV Namespace",
    "analytics_engine": "Analytics Engine"
}

# Backoff Strategies
BACKOFF_STRATEGIES = {
    "fixed": "Fixed delay",
    "exponential": "Exponential backoff",
    "linear": "Linear backoff"
}

# Language to MIME type mapping
MIME_TYPES = {
    ".ts": "application/typescript",
    ".js": "application/javascript",
    ".json": "application/json",
    ".toml": "application/toml",
    ".md": "text/markdown",
    ".sh": "application/x-sh",
    ".txt": "text/plain"
}

# Syntax highlighting themes
PYGMENTS_THEMES = [
    "monokai",
    "github-dark",
    "dracula",
    "nord",
    "one-dark"
]

# File icons for display
FILE_ICONS = {
    "index.ts": "📜",
    "wrangler.toml": "⚙️",
    "package.json": "📦",
    "README.md": "📖",
    ".env.example": "🔐",
    "deploy.sh": "🚀",
    "tsconfig.json": "🔧"
}

# Help text
HELP_TEXT = {
    "worker_name": "Lowercase letters, numbers, and hyphens only. Max 63 characters.",
    "domain": "The domain where you'll receive emails (e.g., example.com)",
    "email_pattern": "Use * as wildcard. {domain} will be replaced with your domain.",
    "twilio_sid": "Found in your Twilio Console dashboard. Starts with 'AC'.",
    "twilio_token": "Your Twilio Auth Token. Keep this secret!",
    "twilio_phone": "Your Twilio phone number in E.164 format (+15551234567)",
    "phone_extraction": "How to determine the recipient phone number from the email",
    "content_source": "Which part of the email to send as SMS text",
    "rate_limiting": "Prevent abuse by limiting messages per sender/recipient",
    "logging": "Track messages and errors for debugging and monitoring",
    "whitelist": "Only allow specific email addresses to send SMS",
    "retries": "Automatically retry failed SMS sends",
    "url_shortening": "Convert long URLs to short links to save characters"
}

# Validation patterns
VALIDATION_PATTERNS = {
    "worker_name": r"^[a-z0-9-]{1,63}$",
    "domain": r"^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?(\.[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?)*$",
    "twilio_sid": r"^AC[a-z0-9]{32}$",
    "phone_e164": r"^\+[1-9]\d{1,14}$",
    "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
}

# npm dependencies versions
NPM_DEPENDENCIES = {
    "hono": "^4.6.8",
    "twilio": "^5.3.5",
    "@cloudflare/workers-types": "^4.20241022.0"
}

NPM_DEV_DEPENDENCIES = {
    "typescript": "^5.5.2",
    "wrangler": "^3.84.1",
    "@cloudflare/vitest-pool-workers": "^0.5.2",
    "vitest": "2.0.5"
}

# Cloudflare compatibility
CLOUDFLARE_COMPATIBILITY_DATE = "2024-10-22"
CLOUDFLARE_COMPATIBILITY_FLAGS = ["nodejs_compat"]
