"""Input form components for configuration."""
import streamlit as st
from schemas import WorkerConfig, BasicConfig, TwilioConfig, EmailRoutingConfig
from schemas import RateLimitConfig, LoggingConfig, SecurityConfig, RetryConfig, IntegrationConfig
from utils import (
    validate_worker_name, validate_domain, validate_email,
    validate_phone_number, validate_twilio_sid, validate_twilio_token,
    validate_email_pattern, validate_sender_whitelist,
    PHONE_EXTRACTION_METHODS, CONTENT_SOURCE_OPTIONS,
    LOG_STORAGE_TYPES, BACKOFF_STRATEGIES, HELP_TEXT,
    generate_example_email
)


def render_basic_settings() -> BasicConfig:
    """
    Render basic settings section.

    Returns:
        BasicConfig dataclass
    """
    st.subheader("📋 Basic Settings")

    col1, col2 = st.columns(2)

    with col1:
        worker_name = st.text_input(
            "Worker Name",
            value=st.session_state.get('worker_name', 'email-to-sms-worker'),
            help=HELP_TEXT['worker_name'],
            key='worker_name_input'
        )

        # Validate worker name
        is_valid, error = validate_worker_name(worker_name)
        if not is_valid and worker_name:
            st.error(f"❌ {error}")
        elif worker_name:
            st.success("✅ Valid worker name")

    with col2:
        domain = st.text_input(
            "Your Domain",
            value=st.session_state.get('domain', ''),
            placeholder="example.com",
            help=HELP_TEXT['domain'],
            key='domain_input'
        )

        # Validate domain
        is_valid, error = validate_domain(domain)
        if not is_valid and domain:
            st.error(f"❌ {error}")
        elif domain:
            st.success("✅ Valid domain")

    email_pattern = st.text_input(
        "Email Pattern",
        value=st.session_state.get('email_pattern', '*@sms.{domain}'),
        help=HELP_TEXT['email_pattern'],
        key='email_pattern_input'
    )

    # Show example email
    if domain:
        example = generate_example_email(email_pattern, domain)
        st.info(f"📧 Example: `{example}`")

    return BasicConfig(
        worker_name=worker_name,
        domain=domain,
        email_pattern=email_pattern
    )


def render_twilio_config() -> TwilioConfig:
    """
    Render Twilio configuration section.

    Returns:
        TwilioConfig dataclass
    """
    with st.expander("🔐 Twilio Configuration", expanded=True):
        st.markdown("Get your credentials from [Twilio Console](https://console.twilio.com/)")

        account_sid = st.text_input(
            "Twilio Account SID",
            value=st.session_state.get('twilio_sid', ''),
            type="password",
            placeholder="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            help=HELP_TEXT['twilio_sid'],
            key='twilio_sid_input'
        )

        # Validate Twilio SID
        is_valid, error = validate_twilio_sid(account_sid)
        if not is_valid and account_sid:
            st.error(f"❌ {error}")
        elif account_sid:
            st.success("✅ Valid Twilio SID")

        auth_token = st.text_input(
            "Twilio Auth Token",
            value=st.session_state.get('twilio_token', ''),
            type="password",
            help=HELP_TEXT['twilio_token'],
            key='twilio_token_input'
        )

        # Validate auth token
        is_valid, error = validate_twilio_token(auth_token)
        if not is_valid and auth_token:
            st.error(f"❌ {error}")
        elif auth_token:
            st.success("✅ Valid auth token")

        phone_number = st.text_input(
            "Twilio Phone Number",
            value=st.session_state.get('twilio_phone', ''),
            placeholder="+15551234567",
            help=HELP_TEXT['twilio_phone'],
            key='twilio_phone_input'
        )

        # Validate phone number
        is_valid, error = validate_phone_number(phone_number)
        if not is_valid and phone_number:
            st.error(f"❌ {error}")
        elif phone_number:
            st.success("✅ Valid phone number")

    return TwilioConfig(
        account_sid=account_sid,
        auth_token=auth_token,
        phone_number=phone_number
    )


def render_routing_options() -> EmailRoutingConfig:
    """
    Render email routing options section.

    Returns:
        EmailRoutingConfig dataclass
    """
    with st.expander("📬 Email Routing Options", expanded=False):
        phone_extraction = st.selectbox(
            "Phone Number Extraction Method",
            options=list(PHONE_EXTRACTION_METHODS.keys()),
            format_func=lambda x: PHONE_EXTRACTION_METHODS[x],
            index=0,
            help=HELP_TEXT['phone_extraction'],
            key='phone_extraction_input'
        )

        col1, col2 = st.columns(2)

        with col1:
            default_country_code = st.text_input(
                "Default Country Code",
                value="+1",
                help="Added to numbers without country code",
                key='country_code_input'
            )

        with col2:
            content_source = st.selectbox(
                "Content Source",
                options=list(CONTENT_SOURCE_OPTIONS.keys()),
                format_func=lambda x: CONTENT_SOURCE_OPTIONS[x],
                index=0,
                help=HELP_TEXT['content_source'],
                key='content_source_input'
            )

        max_length = st.slider(
            "Max Message Length",
            min_value=160,
            max_value=1600,
            value=160,
            step=160,
            help="160=standard SMS, 320/480/etc=concatenated, 1600=max",
            key='max_length_input'
        )

        st.caption(f"📏 Approximately {max_length // 160} SMS segment(s)")

        col1, col2 = st.columns(2)

        with col1:
            strip_html = st.checkbox(
                "Strip HTML tags",
                value=True,
                help="Remove HTML formatting from content",
                key='strip_html_input'
            )

        with col2:
            include_sender = st.checkbox(
                "Include sender info in SMS",
                value=False,
                help="Add sender email to message",
                key='include_sender_input'
            )

    return EmailRoutingConfig(
        phone_extraction_method=phone_extraction,
        default_country_code=default_country_code,
        content_source=content_source,
        max_message_length=max_length,
        strip_html=strip_html,
        include_sender_info=include_sender
    )


def render_advanced_features() -> tuple[RateLimitConfig, LoggingConfig, SecurityConfig, RetryConfig, IntegrationConfig]:
    """
    Render advanced features section.

    Returns:
        Tuple of (RateLimitConfig, LoggingConfig, SecurityConfig, RetryConfig, IntegrationConfig)
    """
    with st.expander("⚙️ Advanced Features", expanded=False):
        # Rate Limiting
        st.markdown("### 🚦 Rate Limiting")

        enable_rate_limiting = st.checkbox(
            "Enable Rate Limiting",
            value=True,
            help=HELP_TEXT['rate_limiting'],
            key='rate_limit_enabled_input'
        )

        if enable_rate_limiting:
            col1, col2 = st.columns(2)

            with col1:
                rate_per_sender = st.number_input(
                    "Messages per sender/hour",
                    min_value=1,
                    max_value=1000,
                    value=10,
                    key='rate_sender_input'
                )

            with col2:
                rate_per_recipient = st.number_input(
                    "Messages per recipient/hour",
                    min_value=1,
                    max_value=1000,
                    value=20,
                    key='rate_recipient_input'
                )

            rate_storage = st.selectbox(
                "Rate Limit Storage",
                options=['kv', 'memory'],
                index=0,
                help="KV = persistent, Memory = resets on worker restart",
                key='rate_storage_input'
            )
        else:
            rate_per_sender = 10
            rate_per_recipient = 20
            rate_storage = 'kv'

        # Logging
        st.markdown("### 📊 Logging")

        enable_logging = st.checkbox(
            "Enable Logging",
            value=True,
            help=HELP_TEXT['logging'],
            key='logging_enabled_input'
        )

        if enable_logging:
            log_storage = st.selectbox(
                "Log Storage",
                options=list(LOG_STORAGE_TYPES.keys()),
                format_func=lambda x: LOG_STORAGE_TYPES[x],
                index=2,
                key='log_storage_input'
            )

            log_level = st.selectbox(
                "Log Level",
                options=['debug', 'info', 'warn', 'error'],
                index=1,
                key='log_level_input'
            )

            log_sensitive = st.checkbox(
                "Log sensitive data (phone numbers, content)",
                value=False,
                help="⚠️ Not recommended for production",
                key='log_sensitive_input'
            )
        else:
            log_storage = 'console'
            log_level = 'info'
            log_sensitive = False

        # Security
        st.markdown("### 🔒 Security")

        enable_whitelist = st.checkbox(
            "Enable Sender Whitelist",
            value=False,
            help=HELP_TEXT['whitelist'],
            key='whitelist_enabled_input'
        )

        whitelist_emails = []
        if enable_whitelist:
            whitelist_text = st.text_area(
                "Allowed Sender Emails (one per line)",
                placeholder="user1@example.com\nuser2@example.com",
                help="Only these emails can send SMS",
                key='whitelist_input'
            )

            # Validate whitelist
            is_valid, error, emails = validate_sender_whitelist(whitelist_text)
            if not is_valid:
                st.error(f"❌ {error}")
            elif emails:
                st.success(f"✅ {len(emails)} email(s) in whitelist")
                whitelist_emails = emails

        enable_content_filter = st.checkbox(
            "Enable Content Filtering",
            value=False,
            help="Basic spam/profanity filtering",
            key='content_filter_input'
        )

        # Retry Logic
        st.markdown("### 🔄 Retry Logic")

        enable_retries = st.checkbox(
            "Enable Automatic Retries",
            value=True,
            help=HELP_TEXT['retries'],
            key='retries_enabled_input'
        )

        if enable_retries:
            col1, col2 = st.columns(2)

            with col1:
                max_retries = st.slider(
                    "Max Retries",
                    min_value=1,
                    max_value=5,
                    value=3,
                    key='max_retries_input'
                )

            with col2:
                retry_delay = st.slider(
                    "Retry Delay (seconds)",
                    min_value=1,
                    max_value=60,
                    value=5,
                    key='retry_delay_input'
                )

            backoff_strategy = st.selectbox(
                "Backoff Strategy",
                options=list(BACKOFF_STRATEGIES.keys()),
                format_func=lambda x: BACKOFF_STRATEGIES[x],
                index=1,
                key='backoff_input'
            )
        else:
            max_retries = 3
            retry_delay = 5
            backoff_strategy = 'exponential'

        # Optional Integrations
        st.markdown("### 🔌 Optional Integrations")

        enable_url_shortening = st.checkbox(
            "Enable URL Shortening",
            value=False,
            help=HELP_TEXT['url_shortening'],
            key='url_shorten_input'
        )

        enable_error_notifications = st.checkbox(
            "Enable Error Notifications",
            value=False,
            help="Get notified when SMS fails",
            key='error_notify_input'
        )

        notification_email = None
        if enable_error_notifications:
            notification_email = st.text_input(
                "Notification Email",
                placeholder="admin@example.com",
                key='notify_email_input'
            )

            # Validate notification email
            if notification_email:
                is_valid, error = validate_email(notification_email)
                if not is_valid:
                    st.error(f"❌ {error}")
                else:
                    st.success("✅ Valid email")

    return (
        RateLimitConfig(
            enabled=enable_rate_limiting,
            per_sender=rate_per_sender,
            per_recipient=rate_per_recipient,
            storage=rate_storage
        ),
        LoggingConfig(
            enabled=enable_logging,
            storage_type=log_storage,
            log_level=log_level,
            log_sensitive_data=log_sensitive
        ),
        SecurityConfig(
            enable_sender_whitelist=enable_whitelist,
            sender_whitelist=whitelist_emails,
            enable_content_filtering=enable_content_filter
        ),
        RetryConfig(
            enabled=enable_retries,
            max_retries=max_retries,
            retry_delay=retry_delay,
            backoff_strategy=backoff_strategy
        ),
        IntegrationConfig(
            enable_url_shortening=enable_url_shortening,
            enable_error_notifications=enable_error_notifications,
            notification_email=notification_email
        )
    )


def render_form() -> WorkerConfig:
    """
    Render complete configuration form.

    Returns:
        Complete WorkerConfig
    """
    # Render all sections
    basic = render_basic_settings()
    twilio = render_twilio_config()
    routing = render_routing_options()
    rate_limit, logging, security, retry, integrations = render_advanced_features()

    # Build complete config
    config = WorkerConfig(
        basic=basic,
        twilio=twilio,
        routing=routing,
        rate_limit=rate_limit,
        logging=logging,
        security=security,
        retry=retry,
        integrations=integrations
    )

    return config
