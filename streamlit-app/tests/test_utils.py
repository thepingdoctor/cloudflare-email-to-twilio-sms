"""
Utility functions for tests.

Helper functions used across test suites.
"""
import json
import tempfile
from pathlib import Path
from typing import Dict


def create_temp_config_file(config_data: Dict) -> Path:
    """
    Create a temporary configuration file.

    Args:
        config_data: Configuration dictionary

    Returns:
        Path to temporary file
    """
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
    json.dump(config_data, temp_file)
    temp_file.close()
    return Path(temp_file.name)


def compare_files(file1_content: str, file2_content: str) -> bool:
    """
    Compare two file contents.

    Args:
        file1_content: First file content
        file2_content: Second file content

    Returns:
        True if files match
    """
    return file1_content.strip() == file2_content.strip()


def extract_imports(typescript_code: str) -> list:
    """
    Extract import statements from TypeScript code.

    Args:
        typescript_code: TypeScript code content

    Returns:
        List of import statements
    """
    imports = []
    for line in typescript_code.split('\n'):
        if line.strip().startswith('import '):
            imports.append(line.strip())
    return imports


def count_functions(typescript_code: str) -> int:
    """
    Count function definitions in TypeScript code.

    Args:
        typescript_code: TypeScript code content

    Returns:
        Number of function definitions
    """
    count = 0
    for line in typescript_code.split('\n'):
        if 'function ' in line or 'const ' in line and '=>' in line:
            count += 1
    return count


def validate_json_structure(json_str: str, required_keys: list) -> tuple:
    """
    Validate JSON structure has required keys.

    Args:
        json_str: JSON string
        required_keys: List of required keys

    Returns:
        Tuple of (is_valid, missing_keys)
    """
    try:
        data = json.loads(json_str)
        missing = [key for key in required_keys if key not in data]
        return len(missing) == 0, missing
    except json.JSONDecodeError:
        return False, required_keys


def validate_toml_structure(toml_str: str, required_keys: list) -> tuple:
    """
    Validate TOML structure has required keys.

    Args:
        toml_str: TOML string
        required_keys: List of required keys

    Returns:
        Tuple of (is_valid, missing_keys)
    """
    try:
        import tomli
        data = tomli.loads(toml_str)
        missing = [key for key in required_keys if key not in data]
        return len(missing) == 0, missing
    except Exception:
        return False, required_keys


def strip_comments(code: str, language: str = 'typescript') -> str:
    """
    Strip comments from code.

    Args:
        code: Source code
        language: Programming language

    Returns:
        Code without comments
    """
    lines = []
    in_multiline = False

    for line in code.split('\n'):
        if language in ['typescript', 'javascript']:
            # Remove // comments
            if '//' in line:
                line = line[:line.index('//')]
            # Handle /* */ comments
            if '/*' in line:
                in_multiline = True
            if '*/' in line:
                in_multiline = False
                continue
            if not in_multiline:
                lines.append(line)
        else:
            lines.append(line)

    return '\n'.join(lines)


def count_lines_of_code(code: str) -> int:
    """
    Count non-empty, non-comment lines of code.

    Args:
        code: Source code

    Returns:
        Number of lines of code
    """
    stripped = strip_comments(code)
    lines = [line.strip() for line in stripped.split('\n') if line.strip()]
    return len(lines)


def extract_environment_variables(code: str) -> list:
    """
    Extract environment variable references from code.

    Args:
        code: Source code

    Returns:
        List of environment variable names
    """
    import re
    # Match patterns like env.VAR_NAME or process.env.VAR_NAME
    pattern = r'(?:env\.|process\.env\.)([A-Z_]+)'
    matches = re.findall(pattern, code)
    return list(set(matches))


def validate_bash_script(script: str) -> tuple:
    """
    Basic validation of bash script.

    Args:
        script: Bash script content

    Returns:
        Tuple of (is_valid, errors)
    """
    errors = []

    # Check for shebang
    if not script.startswith('#!'):
        errors.append("Missing shebang line")

    # Check for basic syntax errors
    if script.count('{') != script.count('}'):
        errors.append("Unmatched braces")

    if script.count('(') != script.count(')'):
        errors.append("Unmatched parentheses")

    return len(errors) == 0, errors


def simulate_user_input(inputs: Dict[str, str]) -> Dict[str, str]:
    """
    Simulate user form input.

    Args:
        inputs: Dictionary of field names to values

    Returns:
        Validated input dictionary
    """
    # This would validate inputs and return clean data
    # For testing purposes, just return as-is
    return inputs


def create_mock_files(file_dict: Dict[str, str], base_dir: Path) -> None:
    """
    Create mock files in a directory.

    Args:
        file_dict: Dictionary mapping filenames to content
        base_dir: Base directory to create files in
    """
    for filename, content in file_dict.items():
        file_path = base_dir / filename

        # Create parent directories if needed
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        file_path.write_text(content)


def verify_file_structure(base_dir: Path, expected_files: list) -> tuple:
    """
    Verify that expected files exist in directory.

    Args:
        base_dir: Base directory to check
        expected_files: List of expected file paths

    Returns:
        Tuple of (all_present, missing_files)
    """
    missing = []
    for file_path in expected_files:
        full_path = base_dir / file_path
        if not full_path.exists():
            missing.append(file_path)

    return len(missing) == 0, missing


def measure_execution_time(func, *args, **kwargs) -> tuple:
    """
    Measure function execution time.

    Args:
        func: Function to execute
        *args: Function arguments
        **kwargs: Function keyword arguments

    Returns:
        Tuple of (result, duration_ms)
    """
    import time

    start = time.time()
    result = func(*args, **kwargs)
    duration_ms = (time.time() - start) * 1000

    return result, duration_ms


def generate_test_credentials() -> Dict[str, str]:
    """
    Generate test Twilio credentials.

    Returns:
        Dictionary of test credentials
    """
    return {
        "account_sid": "AC1234567890abcdef1234567890abcdef",
        "auth_token": "1234567890abcdef1234567890abcdef",
        "phone_number": "+15551234567"
    }


def generate_test_config() -> Dict:
    """
    Generate complete test configuration.

    Returns:
        Test configuration dictionary
    """
    return {
        "basic": {
            "worker_name": "test-worker",
            "domain": "example.com",
            "email_pattern": "*@sms.{domain}"
        },
        "twilio": generate_test_credentials(),
        "routing": {
            "phone_extraction_method": "email_prefix",
            "default_country_code": "+1",
            "content_source": "body_text",
            "max_message_length": 160,
            "strip_html": True,
            "include_sender_info": False
        },
        "rate_limit": {
            "enabled": True,
            "per_sender": 10,
            "per_recipient": 20,
            "storage": "kv"
        },
        "logging": {
            "enabled": True,
            "storage_type": "analytics_engine",
            "log_level": "info",
            "log_sensitive_data": False
        },
        "security": {
            "enable_sender_whitelist": False,
            "sender_whitelist": [],
            "enable_content_filtering": False
        },
        "retry": {
            "enabled": True,
            "max_retries": 3,
            "retry_delay": 5,
            "backoff_strategy": "exponential"
        },
        "integrations": {
            "enable_url_shortening": False,
            "enable_error_notifications": False,
            "notification_email": None
        }
    }
