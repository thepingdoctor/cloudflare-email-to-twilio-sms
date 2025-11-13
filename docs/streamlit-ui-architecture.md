# Streamlit UI Architecture - Email-to-SMS Code Generator

## Overview

This document outlines the architecture for a Streamlit web application that generates complete, customized Cloudflare Worker code for Email-to-SMS functionality. Users input their configuration variables, and the app generates ready-to-deploy code.

## System Architecture

```
[Streamlit UI]
    ↓
[Input Form] → [Validation Layer]
    ↓
[Configuration Schema]
    ↓
[Code Generator Engine]
    ↓              ↓              ↓
[Worker Code] [Wrangler.toml] [Package.json]
    ↓
[Output Display] → [Syntax Highlighting]
    ↓
[Download/Copy Functions]
```

## UI Components

### 1. Application Layout

**Structure:**
```
┌─────────────────────────────────────┐
│  📧 Email-to-SMS Code Generator     │
│  Cloudflare Workers + Twilio        │
├─────────────────────────────────────┤
│  📋 Configuration Panel             │
│  ├─ Basic Settings (expanded)       │
│  ├─ Twilio Credentials              │
│  ├─ Email Routing Options           │
│  ├─ Advanced Features (collapsed)   │
│  └─ [Generate Code] Button          │
├─────────────────────────────────────┤
│  💻 Generated Code Tabs             │
│  ├─ Tab: index.ts                   │
│  ├─ Tab: wrangler.toml              │
│  ├─ Tab: package.json               │
│  ├─ Tab: README.md                  │
│  └─ Tab: Setup Instructions         │
├─────────────────────────────────────┤
│  ⬇️ Download & Deploy               │
│  ├─ [Download All Files (.zip)]     │
│  ├─ [Copy to Clipboard]             │
│  └─ [Deploy to Cloudflare] (future) │
└─────────────────────────────────────┘
```

### 2. Input Form Sections

#### Section 1: Basic Settings (Always Visible)

**Fields:**
- `worker_name` (text)
  - Label: "Worker Name"
  - Default: "email-to-sms-worker"
  - Help: "Name for your Cloudflare Worker"
  - Validation: lowercase, hyphens only

- `domain` (text)
  - Label: "Your Domain"
  - Placeholder: "example.com"
  - Help: "Domain where emails will be received"
  - Validation: valid domain format

- `email_pattern` (text)
  - Label: "Email Pattern"
  - Default: "*@sms.{domain}"
  - Help: "Pattern for incoming emails (use * for wildcard)"

#### Section 2: Twilio Configuration (Collapsible)

**Fields:**
- `twilio_account_sid` (text, password)
  - Label: "Twilio Account SID"
  - Help: "Found in Twilio Console"
  - Validation: starts with 'AC', 34 chars

- `twilio_auth_token` (text, password)
  - Label: "Twilio Auth Token"
  - Help: "Your Twilio Auth Token"
  - Validation: 32 chars minimum

- `twilio_phone_number` (text)
  - Label: "Twilio Phone Number"
  - Placeholder: "+15551234567"
  - Help: "Your Twilio phone number in E.164 format"
  - Validation: E.164 format (+[country][number])

#### Section 3: Email Routing Options (Collapsible)

**Fields:**
- `phone_extraction_method` (selectbox)
  - Options:
    - "Email prefix" (15551234567@sms.domain.com)
    - "Subject line" (Subject: To: 555-123-4567)
    - "Custom header" (X-SMS-To: +15551234567)
    - "All methods" (try all in order)
  - Default: "Email prefix"

- `default_country_code` (text)
  - Label: "Default Country Code"
  - Default: "+1"
  - Help: "Added to numbers without country code"

- `content_source` (selectbox)
  - Options:
    - "Email body (text only)"
    - "Email body (HTML allowed)"
    - "Email subject"
    - "Email subject + body"
  - Default: "Email body (text only)"

- `max_message_length` (slider)
  - Range: 160-1600 characters
  - Default: 160
  - Help: "Maximum SMS length (160=standard, 1600=concatenated)"

#### Section 4: Advanced Features (Collapsible)

**Rate Limiting:**
- `enable_rate_limiting` (checkbox)
  - Default: True
  - Enable/disable rate limiting

- `rate_limit_per_sender` (number)
  - Default: 10
  - Range: 1-1000
  - Help: "Messages per sender per hour"

- `rate_limit_per_recipient` (number)
  - Default: 20
  - Range: 1-1000
  - Help: "Messages per recipient per hour"

**Logging:**
- `enable_logging` (checkbox)
  - Default: True

- `log_storage` (selectbox)
  - Options:
    - "Console only"
    - "KV Namespace"
    - "Analytics Engine"
  - Default: "Analytics Engine"

**Security:**
- `enable_sender_whitelist` (checkbox)
  - Default: False

- `sender_whitelist` (text_area)
  - Placeholder: "user1@example.com\nuser2@example.com"
  - Help: "One email per line"
  - Shown only if whitelist enabled

- `enable_content_filtering` (checkbox)
  - Default: False
  - Help: "Basic profanity/spam filtering"

**Retry Logic:**
- `enable_retries` (checkbox)
  - Default: True

- `max_retries` (slider)
  - Range: 1-5
  - Default: 3

- `retry_delay` (slider)
  - Range: 1-60 seconds
  - Default: 5

#### Section 5: Optional Integrations (Collapsible)

**URL Shortening:**
- `enable_url_shortening` (checkbox)
  - Default: False
  - Help: "Automatically shorten URLs in messages"

**Notifications:**
- `enable_error_notifications` (checkbox)
  - Default: False

- `notification_email` (text)
  - Placeholder: "admin@example.com"
  - Shown if notifications enabled

**Custom Features:**
- `custom_headers` (text_area)
  - Placeholder: "X-Custom-Header: value"
  - Help: "Additional headers to include (one per line)"

### 3. Code Generation Engine

#### Component: `code_generator.py`

**Purpose:** Generate all necessary files based on user configuration

**Main Functions:**

```python
class CodeGenerator:
    def __init__(self, config: dict):
        self.config = config

    def generate_all(self) -> dict:
        """Generate all files and return as dict"""
        return {
            'index.ts': self.generate_worker_code(),
            'wrangler.toml': self.generate_wrangler_config(),
            'package.json': self.generate_package_json(),
            'README.md': self.generate_readme(),
            '.env.example': self.generate_env_example(),
            'deploy.sh': self.generate_deploy_script()
        }

    def generate_worker_code(self) -> str:
        """Generate main Worker TypeScript code"""

    def generate_wrangler_config(self) -> str:
        """Generate wrangler.toml configuration"""

    def generate_package_json(self) -> str:
        """Generate package.json with dependencies"""

    def generate_readme(self) -> str:
        """Generate README with setup instructions"""

    def generate_env_example(self) -> str:
        """Generate .env.example template"""

    def generate_deploy_script(self) -> str:
        """Generate deployment bash script"""
```

#### Template Engine

**Technology:** Jinja2 templates

**Template Structure:**
```
templates/
├── worker/
│   ├── index.ts.j2
│   ├── email-handler.ts.j2
│   ├── twilio-service.ts.j2
│   ├── phone-parser.ts.j2
│   └── validator.ts.j2
├── config/
│   ├── wrangler.toml.j2
│   ├── package.json.j2
│   └── tsconfig.json.j2
└── docs/
    ├── README.md.j2
    └── SETUP.md.j2
```

**Template Variables:**
- All user inputs from form
- Computed values (e.g., kv_namespace_name)
- Conditional blocks based on features enabled

#### Code Assembly Logic

**Process:**
1. Validate all inputs
2. Build configuration object
3. Load templates based on selected features
4. Render templates with configuration
5. Combine into complete files
6. Add comments and documentation
7. Format code (prettier/black equivalent)

### 4. Output Display

#### Tab System

**Tab 1: index.ts**
- Syntax highlighting (TypeScript)
- Line numbers
- Copy button (top-right)
- Download button
- Collapsible sections (imports, handlers, utils)

**Tab 2: wrangler.toml**
- Syntax highlighting (TOML)
- Configuration sections clearly marked
- Comments explaining each setting

**Tab 3: package.json**
- Syntax highlighting (JSON)
- Dependency versions highlighted
- Scripts section explained

**Tab 4: README.md**
- Markdown rendering
- Setup instructions customized to user's config
- Deployment checklist

**Tab 5: Setup Instructions**
- Step-by-step deployment guide
- Copy-paste commands
- Troubleshooting section

#### Syntax Highlighting

**Library:** `pygments` or `streamlit-code-editor`

**Languages:**
- TypeScript
- TOML
- JSON
- Bash
- Markdown

**Theme:** GitHub Dark (or user-selectable)

### 5. Download Functionality

#### Single File Download

**Function:**
```python
def download_file(filename: str, content: str):
    st.download_button(
        label=f"⬇️ Download {filename}",
        data=content,
        file_name=filename,
        mime=get_mime_type(filename)
    )
```

#### ZIP Archive Download

**Function:**
```python
def create_zip_archive(files: dict) -> bytes:
    """Create ZIP with all generated files"""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for filename, content in files.items():
            zip_file.writestr(filename, content)
    return zip_buffer.getvalue()
```

**Structure:**
```
email-to-sms-worker.zip
├── src/
│   ├── index.ts
│   ├── handlers/
│   │   └── email-handler.ts
│   ├── services/
│   │   └── twilio-service.ts
│   └── utils/
│       ├── phone-parser.ts
│       └── validator.ts
├── wrangler.toml
├── package.json
├── tsconfig.json
├── README.md
├── .env.example
└── deploy.sh
```

### 6. Copy to Clipboard

**Implementation:**
```python
import streamlit.components.v1 as components

def copy_to_clipboard(text: str, button_label: str):
    components.html(
        f"""
        <button onclick="navigator.clipboard.writeText(`{text}`)">
            {button_label}
        </button>
        """,
        height=50
    )
```

**Per-File Copy:**
- Each tab has "Copy Code" button
- Copies entire file content
- Shows "Copied!" confirmation

**All Files Copy:**
- Copies all files with separators
- Format:
  ```
  // ===== index.ts =====
  [content]

  // ===== wrangler.toml =====
  [content]
  ```

## File Structure

```
src/streamlit/
├── app.py                          # Main Streamlit app
├── components/
│   ├── input_form.py              # Form components
│   ├── code_display.py            # Code display tabs
│   └── download_manager.py        # Download functionality
├── generators/
│   ├── code_generator.py          # Main code generator
│   ├── worker_generator.py        # Worker code generation
│   ├── config_generator.py        # Config file generation
│   └── docs_generator.py          # Documentation generation
├── templates/
│   ├── worker/
│   │   ├── index.ts.j2
│   │   ├── email-handler.ts.j2
│   │   ├── twilio-service.ts.j2
│   │   ├── phone-parser.ts.j2
│   │   ├── content-processor.ts.j2
│   │   ├── validator.ts.j2
│   │   ├── rate-limiter.ts.j2
│   │   └── logger.ts.j2
│   ├── config/
│   │   ├── wrangler.toml.j2
│   │   ├── package.json.j2
│   │   ├── tsconfig.json.j2
│   │   └── .env.example.j2
│   └── docs/
│       ├── README.md.j2
│       ├── SETUP.md.j2
│       └── deploy.sh.j2
├── utils/
│   ├── validators.py              # Input validation
│   ├── formatters.py              # Code formatting
│   └── helpers.py                 # Utility functions
├── schemas/
│   └── config_schema.py           # Configuration schema
└── assets/
    ├── styles.css                 # Custom CSS
    └── logo.png                   # App logo
```

## Configuration Schema

### Variable Schema Definition

```python
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class BasicConfig:
    worker_name: str
    domain: str
    email_pattern: str

@dataclass
class TwilioConfig:
    account_sid: str
    auth_token: str
    phone_number: str

@dataclass
class EmailRoutingConfig:
    phone_extraction_method: str
    default_country_code: str
    content_source: str
    max_message_length: int

@dataclass
class RateLimitConfig:
    enabled: bool
    per_sender: int
    per_recipient: int

@dataclass
class LoggingConfig:
    enabled: bool
    storage_type: str

@dataclass
class SecurityConfig:
    enable_sender_whitelist: bool
    sender_whitelist: Optional[List[str]]
    enable_content_filtering: bool

@dataclass
class RetryConfig:
    enabled: bool
    max_retries: int
    retry_delay: int

@dataclass
class IntegrationConfig:
    enable_url_shortening: bool
    enable_error_notifications: bool
    notification_email: Optional[str]
    custom_headers: Optional[dict]

@dataclass
class WorkerConfig:
    basic: BasicConfig
    twilio: TwilioConfig
    routing: EmailRoutingConfig
    rate_limit: RateLimitConfig
    logging: LoggingConfig
    security: SecurityConfig
    retry: RetryConfig
    integrations: IntegrationConfig
```

### Validation Rules

```python
class ConfigValidator:
    @staticmethod
    def validate_worker_name(name: str) -> bool:
        """Lowercase, hyphens, 1-63 chars"""
        return bool(re.match(r'^[a-z0-9-]{1,63}$', name))

    @staticmethod
    def validate_domain(domain: str) -> bool:
        """Valid domain format"""
        pattern = r'^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?(\.[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?)*$'
        return bool(re.match(pattern, domain, re.IGNORECASE))

    @staticmethod
    def validate_twilio_sid(sid: str) -> bool:
        """Starts with AC, 34 chars"""
        return sid.startswith('AC') and len(sid) == 34

    @staticmethod
    def validate_phone_number(number: str) -> bool:
        """E.164 format"""
        return bool(re.match(r'^\+[1-9]\d{1,14}$', number))

    @staticmethod
    def validate_email(email: str) -> bool:
        """Valid email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
```

## Python Dependencies

### Core Dependencies

```python
# requirements.txt
streamlit==1.31.0              # Main framework
jinja2==3.1.3                  # Template engine
pygments==2.17.2               # Syntax highlighting
validators==0.22.0             # Input validation
python-dotenv==1.0.1           # Environment handling
pydantic==2.6.0                # Data validation
typing-extensions==4.9.0       # Type hints
```

### Optional Dependencies

```python
# requirements-dev.txt
black==24.1.1                  # Code formatting
pylint==3.0.3                  # Linting
pytest==8.0.0                  # Testing
streamlit-code-editor==0.1.0   # Enhanced code editor
streamlit-extras==0.3.6        # Additional components
```

### package.json for Generated Code

```json
{
  "dependencies": {
    "hono": "^4.6.8",
    "twilio": "^5.3.5",
    "@cloudflare/workers-types": "^4.20241022.0"
  },
  "devDependencies": {
    "typescript": "^5.5.2",
    "wrangler": "^3.84.1",
    "@cloudflare/vitest-pool-workers": "^0.5.2",
    "vitest": "2.0.5"
  }
}
```

## UI/UX Features

### 1. Real-time Validation

- Validate inputs as user types
- Show error messages inline
- Disable "Generate" button if invalid
- Green checkmarks for valid fields

### 2. Smart Defaults

- Pre-fill reasonable defaults
- Remember last used values (session state)
- Load from .env file (optional)
- Import from existing wrangler.toml

### 3. Help & Documentation

- Tooltip on every field
- "Learn more" expandable sections
- Example values shown
- Link to relevant docs

### 4. Preview Mode

- Live preview of generated email pattern
- Example phone number extraction
- Sample message formatting
- Test configuration button

### 5. Export/Import Configuration

- Save configuration as JSON
- Load previous configurations
- Share configurations via URL params
- Export as .env file

### 6. Deployment Helper

- Generate CLI commands
- Step-by-step checklist
- Copy commands with one click
- Track deployment progress

## Advanced Features

### 1. Code Customization

**Post-Generation Editing:**
- Inline code editor (optional)
- Syntax validation
- Format code button
- Reset to generated version

### 2. Template Library

**Pre-built Templates:**
- Basic email-to-SMS
- Email-to-SMS with rate limiting
- Advanced with all features
- Custom templates (user-created)

### 3. Testing Tools

**Built-in Testing:**
- Phone number parser tester
- Email pattern matcher
- Rate limit simulator
- Message length calculator

### 4. Version Control

**Code Versioning:**
- Track generation history
- Compare versions
- Rollback changes
- Export changelog

## Security & Privacy

### 1. Data Handling

- No data stored on server
- All processing client-side (where possible)
- Sensitive values masked in UI
- Clear data on session end

### 2. Best Practices

- Warning for hardcoded secrets
- Recommend using Cloudflare Secrets
- Security checklist before deploy
- HTTPS enforcement

## Performance

### 1. Optimization

- Lazy load templates
- Cache rendered code
- Minimize re-renders
- Efficient state management

### 2. Scalability

- Support large configurations
- Handle multiple users
- Fast code generation (<500ms)
- Responsive UI

## Deployment

### Streamlit Cloud

```bash
# Deploy to Streamlit Cloud
streamlit run src/streamlit/app.py
```

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/streamlit/ .
CMD ["streamlit", "run", "app.py"]
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run app
streamlit run src/streamlit/app.py

# Run with auto-reload
streamlit run src/streamlit/app.py --server.runOnSave true
```

## Future Enhancements

### Phase 2
- Visual workflow builder
- Drag-and-drop code blocks
- AI-powered code suggestions
- Multi-language support (Python, Go)

### Phase 3
- One-click Cloudflare deployment
- Integrated testing environment
- Live preview of Worker behavior
- Analytics dashboard

### Phase 4
- Marketplace for templates
- Community sharing
- Plugin system
- AI chatbot assistant

## References

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Jinja2 Template Designer](https://jinja.palletsprojects.com/)
- [Pygments Syntax Highlighting](https://pygments.org/)
- [Cloudflare Workers](https://developers.cloudflare.com/workers/)
