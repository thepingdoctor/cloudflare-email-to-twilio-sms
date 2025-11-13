"""Input validation functions."""
import re
from typing import Optional, Tuple
import validators as val
import phonenumbers
from phonenumbers import NumberParseException


def validate_worker_name(name: str) -> Tuple[bool, Optional[str]]:
    """
    Validate Cloudflare Worker name.

    Args:
        name: Worker name to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not name:
        return False, "Worker name is required"

    if not re.match(r'^[a-z0-9-]{1,63}$', name):
        return False, "Worker name must be lowercase, 1-63 characters, letters/numbers/hyphens only"

    if name.startswith('-') or name.endswith('-'):
        return False, "Worker name cannot start or end with hyphen"

    if '--' in name:
        return False, "Worker name cannot contain consecutive hyphens"

    return True, None


def validate_domain(domain: str) -> Tuple[bool, Optional[str]]:
    """
    Validate domain name.

    Args:
        domain: Domain to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not domain:
        return False, "Domain is required"

    if val.domain(domain):
        return True, None

    return False, "Invalid domain format (e.g., example.com)"


def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """
    Validate email address.

    Args:
        email: Email to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not email:
        return False, "Email is required"

    if val.email(email):
        return True, None

    return False, "Invalid email format"


def validate_phone_number(phone: str) -> Tuple[bool, Optional[str]]:
    """
    Validate phone number in E.164 format.

    Args:
        phone: Phone number to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not phone:
        return False, "Phone number is required"

    try:
        parsed = phonenumbers.parse(phone, None)
        if phonenumbers.is_valid_number(parsed):
            return True, None
        return False, "Invalid phone number"
    except NumberParseException:
        return False, "Invalid phone number format (use E.164: +15551234567)"


def validate_twilio_sid(sid: str) -> Tuple[bool, Optional[str]]:
    """
    Validate Twilio Account SID.

    Args:
        sid: Twilio SID to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not sid:
        return False, "Twilio Account SID is required"

    if not sid.startswith('AC'):
        return False, "Twilio SID must start with 'AC'"

    if len(sid) != 34:
        return False, "Twilio SID must be exactly 34 characters"

    if not re.match(r'^AC[a-f0-9]{32}$', sid, re.IGNORECASE):
        return False, "Invalid Twilio SID format"

    return True, None


def validate_twilio_token(token: str) -> Tuple[bool, Optional[str]]:
    """
    Validate Twilio Auth Token.

    Args:
        token: Auth token to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not token:
        return False, "Twilio Auth Token is required"

    if len(token) < 32:
        return False, "Twilio Auth Token must be at least 32 characters"

    return True, None


def validate_email_pattern(pattern: str) -> Tuple[bool, Optional[str]]:
    """
    Validate email pattern.

    Args:
        pattern: Email pattern to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not pattern:
        return False, "Email pattern is required"

    if '@' not in pattern:
        return False, "Email pattern must contain @ symbol"

    # Allow wildcards and {domain} placeholder
    cleaned = pattern.replace('*', 'a').replace('{domain}', 'example.com')

    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', cleaned):
        return False, "Invalid email pattern format"

    return True, None


def validate_url(url: str) -> Tuple[bool, Optional[str]]:
    """
    Validate URL.

    Args:
        url: URL to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not url:
        return False, "URL is required"

    if val.url(url):
        return True, None

    return False, "Invalid URL format"


def validate_positive_integer(value: int, min_val: int = 1, max_val: int = None) -> Tuple[bool, Optional[str]]:
    """
    Validate positive integer within range.

    Args:
        value: Value to validate
        min_val: Minimum allowed value
        max_val: Maximum allowed value

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(value, int):
        return False, "Value must be an integer"

    if value < min_val:
        return False, f"Value must be at least {min_val}"

    if max_val and value > max_val:
        return False, f"Value must be at most {max_val}"

    return True, None


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe download.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Remove unsafe characters
    safe = re.sub(r'[^\w\s.-]', '', filename)
    # Remove leading/trailing spaces and dots
    safe = safe.strip('. ')
    # Replace spaces with hyphens
    safe = safe.replace(' ', '-')
    # Remove consecutive hyphens
    safe = re.sub(r'-+', '-', safe)
    return safe.lower()


def validate_sender_whitelist(whitelist_text: str) -> Tuple[bool, Optional[str], list]:
    """
    Validate sender whitelist (one email per line).

    Args:
        whitelist_text: Whitelist text to validate

    Returns:
        Tuple of (is_valid, error_message, validated_emails)
    """
    if not whitelist_text.strip():
        return True, None, []

    emails = [email.strip() for email in whitelist_text.split('\n') if email.strip()]
    validated_emails = []

    for email in emails:
        is_valid, error = validate_email(email)
        if not is_valid:
            return False, f"Invalid email: {email}", []
        validated_emails.append(email)

    return True, None, validated_emails
