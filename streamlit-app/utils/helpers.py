"""General helper functions."""
import json
import re
from typing import Any, Dict, Optional
from datetime import datetime
import phonenumbers


def format_phone_e164(phone: str, default_country: str = "US") -> Optional[str]:
    """
    Format phone number to E.164 format.

    Args:
        phone: Phone number to format
        default_country: Default country code

    Returns:
        Formatted phone number or None if invalid
    """
    try:
        parsed = phonenumbers.parse(phone, default_country)
        return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except Exception:
        return None


def parse_email_pattern(pattern: str, domain: str) -> str:
    """
    Parse email pattern and replace placeholders.

    Args:
        pattern: Email pattern with placeholders
        domain: Domain to substitute

    Returns:
        Parsed email pattern
    """
    return pattern.replace('{domain}', domain)


def deep_get(dictionary: dict, path: str, default: Any = None) -> Any:
    """
    Get nested dictionary value using dot notation.

    Args:
        dictionary: Dictionary to search
        path: Dot-separated path (e.g., "basic.worker_name")
        default: Default value if not found

    Returns:
        Value at path or default
    """
    keys = path.split('.')
    value = dictionary

    for key in keys:
        if isinstance(value, dict):
            value = value.get(key)
            if value is None:
                return default
        else:
            return default

    return value


def merge_configs(base: dict, override: dict) -> dict:
    """
    Deep merge two configuration dictionaries.

    Args:
        base: Base configuration
        override: Override configuration

    Returns:
        Merged configuration
    """
    result = base.copy()

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value

    return result


def generate_kv_namespace_name(worker_name: str) -> str:
    """
    Generate KV namespace name from worker name.

    Args:
        worker_name: Worker name

    Returns:
        KV namespace name
    """
    return f"{worker_name.upper().replace('-', '_')}_KV"


def generate_analytics_dataset_name(worker_name: str) -> str:
    """
    Generate Analytics Engine dataset name from worker name.

    Args:
        worker_name: Worker name

    Returns:
        Analytics dataset name
    """
    return f"{worker_name.upper().replace('-', '_')}_ANALYTICS"


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate string to max length with suffix.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def extract_phone_from_email_prefix(email: str) -> Optional[str]:
    """
    Extract phone number from email prefix.

    Args:
        email: Email address (e.g., 15551234567@sms.example.com)

    Returns:
        Phone number or None
    """
    match = re.match(r'^(\+?\d+)@', email)
    if match:
        phone = match.group(1)
        if not phone.startswith('+'):
            phone = f'+{phone}'
        return phone
    return None


def extract_phone_from_subject(subject: str) -> Optional[str]:
    """
    Extract phone number from email subject.

    Args:
        subject: Email subject (e.g., "To: +15551234567")

    Returns:
        Phone number or None
    """
    patterns = [
        r'to:\s*(\+?\d[\d\s-]+)',
        r'phone:\s*(\+?\d[\d\s-]+)',
        r'number:\s*(\+?\d[\d\s-]+)',
        r'(\+?\d{10,15})'
    ]

    for pattern in patterns:
        match = re.search(pattern, subject.lower())
        if match:
            phone = re.sub(r'[^\d+]', '', match.group(1))
            return phone

    return None


def format_timestamp() -> str:
    """
    Get current timestamp in ISO format.

    Returns:
        ISO formatted timestamp
    """
    return datetime.utcnow().isoformat() + 'Z'


def json_serialize(obj: Any) -> str:
    """
    Serialize object to JSON string.

    Args:
        obj: Object to serialize

    Returns:
        JSON string
    """
    return json.dumps(obj, indent=2, default=str)


def json_deserialize(json_str: str) -> Dict:
    """
    Deserialize JSON string to dictionary.

    Args:
        json_str: JSON string

    Returns:
        Deserialized dictionary
    """
    return json.loads(json_str)


def calculate_sms_segments(text: str, encoding: str = 'GSM-7') -> int:
    """
    Calculate number of SMS segments needed.

    Args:
        text: Message text
        encoding: Character encoding (GSM-7 or UCS-2)

    Returns:
        Number of segments
    """
    length = len(text)

    if encoding == 'GSM-7':
        if length <= 160:
            return 1
        return (length - 1) // 153 + 1
    else:  # UCS-2
        if length <= 70:
            return 1
        return (length - 1) // 67 + 1


def strip_html_tags(html: str) -> str:
    """
    Remove HTML tags from string.

    Args:
        html: HTML string

    Returns:
        Plain text
    """
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', html)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def generate_example_email(pattern: str, domain: str) -> str:
    """
    Generate example email from pattern.

    Args:
        pattern: Email pattern
        domain: Domain

    Returns:
        Example email
    """
    example = pattern.replace('{domain}', domain)
    example = example.replace('*', '15551234567')
    return example


def mask_sensitive_value(value: str, show_chars: int = 4) -> str:
    """
    Mask sensitive value for display.

    Args:
        value: Sensitive value to mask
        show_chars: Number of characters to show at start/end

    Returns:
        Masked value
    """
    if not value or len(value) <= show_chars * 2:
        return "****"

    return f"{value[:show_chars]}{'*' * (len(value) - show_chars * 2)}{value[-show_chars:]}"


def validate_no_hardcoded_secrets(code: str) -> tuple[bool, list[str]]:
    """
    Check generated code for hardcoded secrets.

    Args:
        code: Generated code to check

    Returns:
        Tuple of (is_safe, list of warnings)
    """
    warnings = []

    # Patterns to detect hardcoded secrets
    patterns = {
        'Twilio SID': r'AC[a-f0-9]{32}',
        'API Key': r'["\']sk_[a-zA-Z0-9]{32,}["\']',
        'Auth Token': r'["\'][a-f0-9]{32,}["\']',
        'Password': r'password\s*=\s*["\'][^"\']+["\']',
    }

    for secret_type, pattern in patterns.items():
        import re
        if re.search(pattern, code, re.IGNORECASE):
            warnings.append(f"Potential hardcoded {secret_type} detected")

    return len(warnings) == 0, warnings


def sanitize_config_for_export(config_dict: dict) -> dict:
    """
    Sanitize configuration for safe export (remove sensitive data).

    Args:
        config_dict: Configuration dictionary

    Returns:
        Sanitized configuration
    """
    import copy
    safe_config = copy.deepcopy(config_dict)

    # Remove sensitive fields
    sensitive_paths = [
        ('twilio', 'account_sid'),
        ('twilio', 'auth_token'),
        ('twilio', 'phone_number'),
        ('cloudflare', 'api_token'),
        ('integrations', 'notification_email')
    ]

    for path in sensitive_paths:
        current = safe_config
        for key in path[:-1]:
            if key in current and isinstance(current[key], dict):
                current = current[key]
            else:
                break
        else:
            # Replace with placeholder
            if path[-1] in current:
                current[path[-1]] = f"<{path[-1].upper()}_PLACEHOLDER>"

    return safe_config
