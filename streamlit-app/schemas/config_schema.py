"""Configuration dataclass schemas."""
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict
from datetime import datetime


@dataclass
class BasicConfig:
    """Basic worker configuration."""
    worker_name: str = "email-to-sms-worker"
    domain: str = ""
    email_pattern: str = "*@sms.{domain}"


@dataclass
class TwilioConfig:
    """Twilio API configuration."""
    account_sid: str = ""
    auth_token: str = ""
    phone_number: str = ""


@dataclass
class EmailRoutingConfig:
    """Email routing and parsing configuration."""
    phone_extraction_method: str = "email_prefix"
    default_country_code: str = "+1"
    content_source: str = "body_text"
    max_message_length: int = 160
    strip_html: bool = True
    include_sender_info: bool = False


@dataclass
class RateLimitConfig:
    """Rate limiting configuration."""
    enabled: bool = True
    per_sender: int = 10
    per_recipient: int = 20
    global_limit: int = 1000
    storage: str = "kv"


@dataclass
class LoggingConfig:
    """Logging and monitoring configuration."""
    enabled: bool = True
    storage_type: str = "analytics_engine"
    log_level: str = "info"
    log_sensitive_data: bool = False


@dataclass
class SecurityConfig:
    """Security and validation settings."""
    enable_sender_whitelist: bool = False
    sender_whitelist: List[str] = field(default_factory=list)
    enable_domain_whitelist: bool = False
    domain_whitelist: List[str] = field(default_factory=list)
    enable_content_filtering: bool = False
    require_spf: bool = False
    require_dkim: bool = False


@dataclass
class RetryConfig:
    """Retry logic for failed sends."""
    enabled: bool = True
    max_retries: int = 3
    retry_delay: int = 5
    backoff_strategy: str = "exponential"


@dataclass
class IntegrationConfig:
    """Optional integrations and features."""
    enable_url_shortening: bool = False
    url_shortener_service: str = "bitly"
    enable_error_notifications: bool = False
    notification_email: Optional[str] = None
    notification_webhook: Optional[str] = None
    custom_headers: Dict[str, str] = field(default_factory=dict)


@dataclass
class CloudflareConfig:
    """Cloudflare-specific settings."""
    kv_namespace_id: Optional[str] = None
    analytics_dataset_name: str = "EMAIL_SMS_ANALYTICS"
    compatibility_date: str = "2024-10-22"
    compatibility_flags: List[str] = field(default_factory=lambda: ["nodejs_compat"])


@dataclass
class FeaturesConfig:
    """Feature flags for optional functionality."""
    enable_bidirectional: bool = False
    enable_mms: bool = False
    enable_scheduling: bool = False
    enable_templates: bool = False
    enable_analytics_dashboard: bool = False


@dataclass
class MetadataConfig:
    """Metadata about this configuration."""
    version: str = "1.0.0"
    generated_by: str = "email-to-sms-streamlit-generator"
    generated_at: Optional[str] = None
    author: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class WorkerConfig:
    """Complete worker configuration."""
    basic: BasicConfig = field(default_factory=BasicConfig)
    twilio: TwilioConfig = field(default_factory=TwilioConfig)
    routing: EmailRoutingConfig = field(default_factory=EmailRoutingConfig)
    rate_limit: RateLimitConfig = field(default_factory=RateLimitConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    retry: RetryConfig = field(default_factory=RetryConfig)
    integrations: IntegrationConfig = field(default_factory=IntegrationConfig)
    cloudflare: CloudflareConfig = field(default_factory=CloudflareConfig)
    features: FeaturesConfig = field(default_factory=FeaturesConfig)
    metadata: MetadataConfig = field(default_factory=MetadataConfig)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'WorkerConfig':
        """Create from dictionary."""
        return cls(
            basic=BasicConfig(**data.get('basic', {})),
            twilio=TwilioConfig(**data.get('twilio', {})),
            routing=EmailRoutingConfig(**data.get('routing', {})),
            rate_limit=RateLimitConfig(**data.get('rate_limit', {})),
            logging=LoggingConfig(**data.get('logging', {})),
            security=SecurityConfig(**data.get('security', {})),
            retry=RetryConfig(**data.get('retry', {})),
            integrations=IntegrationConfig(**data.get('integrations', {})),
            cloudflare=CloudflareConfig(**data.get('cloudflare', {})),
            features=FeaturesConfig(**data.get('features', {})),
            metadata=MetadataConfig(**data.get('metadata', {}))
        )

    def update_metadata(self):
        """Update metadata with current timestamp."""
        self.metadata.generated_at = datetime.utcnow().isoformat() + 'Z'

    def get_kv_namespace_name(self) -> str:
        """Get KV namespace name."""
        return f"{self.basic.worker_name.upper().replace('-', '_')}_KV"

    def get_analytics_dataset_name(self) -> str:
        """Get Analytics Engine dataset name."""
        if self.cloudflare.analytics_dataset_name:
            return self.cloudflare.analytics_dataset_name
        return f"{self.basic.worker_name.upper().replace('-', '_')}_ANALYTICS"

    def get_parsed_email_pattern(self) -> str:
        """Get email pattern with domain substituted."""
        return self.basic.email_pattern.replace('{domain}', self.basic.domain)
