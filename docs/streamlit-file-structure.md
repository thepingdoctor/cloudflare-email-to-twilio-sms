# Streamlit Application File Structure

## Complete Directory Layout

```
email2sms/
├── src/
│   └── streamlit/                      # Streamlit application root
│       ├── app.py                      # Main entry point
│       ├── config.py                   # App configuration
│       ├── __init__.py
│       │
│       ├── components/                 # UI components
│       │   ├── __init__.py
│       │   ├── input_form.py          # Input form components
│       │   ├── code_display.py        # Code display tabs
│       │   ├── download_manager.py    # Download functionality
│       │   ├── sidebar.py             # Sidebar navigation
│       │   ├── header.py              # Page header
│       │   └── footer.py              # Page footer
│       │
│       ├── generators/                 # Code generation logic
│       │   ├── __init__.py
│       │   ├── code_generator.py      # Main generator orchestrator
│       │   ├── worker_generator.py    # Worker code generation
│       │   ├── config_generator.py    # Config file generation
│       │   ├── docs_generator.py      # Documentation generation
│       │   └── template_loader.py     # Template loading utility
│       │
│       ├── templates/                  # Jinja2 templates
│       │   ├── worker/                # Worker code templates
│       │   │   ├── index.ts.j2
│       │   │   ├── email-handler.ts.j2
│       │   │   ├── twilio-service.ts.j2
│       │   │   ├── phone-parser.ts.j2
│       │   │   ├── content-processor.ts.j2
│       │   │   ├── validator.ts.j2
│       │   │   ├── rate-limiter.ts.j2
│       │   │   ├── logger.ts.j2
│       │   │   └── types.ts.j2
│       │   │
│       │   ├── config/                # Configuration templates
│       │   │   ├── wrangler.toml.j2
│       │   │   ├── package.json.j2
│       │   │   ├── tsconfig.json.j2
│       │   │   ├── .env.example.j2
│       │   │   └── .gitignore.j2
│       │   │
│       │   └── docs/                  # Documentation templates
│       │       ├── README.md.j2
│       │       ├── SETUP.md.j2
│       │       ├── DEPLOYMENT.md.j2
│       │       └── deploy.sh.j2
│       │
│       ├── utils/                      # Utility functions
│       │   ├── __init__.py
│       │   ├── validators.py          # Input validation
│       │   ├── formatters.py          # Code formatting
│       │   ├── helpers.py             # General helpers
│       │   ├── file_utils.py          # File operations
│       │   └── constants.py           # Application constants
│       │
│       ├── schemas/                    # Data schemas
│       │   ├── __init__.py
│       │   ├── config_schema.py       # Configuration dataclasses
│       │   └── validation_schema.py   # Pydantic models
│       │
│       ├── assets/                     # Static assets
│       │   ├── styles/
│       │   │   ├── main.css           # Main stylesheet
│       │   │   ├── code.css           # Code display styles
│       │   │   └── form.css           # Form styles
│       │   ├── images/
│       │   │   ├── logo.png
│       │   │   ├── cloudflare-logo.png
│       │   │   └── twilio-logo.png
│       │   └── icons/
│       │       ├── copy.svg
│       │       ├── download.svg
│       │       └── check.svg
│       │
│       ├── pages/                      # Multi-page app (optional)
│       │   ├── 1_Home.py
│       │   ├── 2_Configuration.py
│       │   ├── 3_Code_Preview.py
│       │   └── 4_About.py
│       │
│       └── tests/                      # Tests
│           ├── __init__.py
│           ├── test_generators.py
│           ├── test_validators.py
│           ├── test_formatters.py
│           └── fixtures/
│               ├── sample_config.json
│               └── expected_output.ts
│
├── docs/                               # Project documentation
│   ├── cloudflare-worker-architecture.md
│   ├── streamlit-ui-architecture.md
│   ├── variable-schema.json
│   ├── python-dependencies.md
│   └── api-reference.md
│
├── examples/                           # Example configurations
│   ├── basic-config.json
│   ├── advanced-config.json
│   └── custom-config.json
│
├── scripts/                            # Utility scripts
│   ├── setup.sh
│   ├── run-dev.sh
│   └── deploy.sh
│
├── .streamlit/                         # Streamlit configuration
│   ├── config.toml
│   └── secrets.toml
│
├── requirements.txt                    # Core dependencies
├── requirements-dev.txt                # Development dependencies
├── requirements-optional.txt           # Optional dependencies
├── .gitignore
├── .env.example
├── README.md
├── LICENSE
└── pyproject.toml                     # Poetry configuration (optional)
```

## File Descriptions

### Main Application Files

#### `src/streamlit/app.py`
Main entry point for the Streamlit application. Handles page routing and overall app structure.

```python
# app.py structure
- Import statements
- Page configuration
- Session state initialization
- Main layout rendering
- Component orchestration
```

#### `src/streamlit/config.py`
Application-wide configuration and constants.

```python
# config.py contents
- App settings (title, description)
- Default values
- Feature flags
- API endpoints
- Environment variable loading
```

### Component Files

#### `components/input_form.py`
All input form components and sections.

**Functions:**
- `render_basic_settings()` → Basic config inputs
- `render_twilio_config()` → Twilio credentials
- `render_routing_options()` → Email routing settings
- `render_advanced_features()` → Advanced options
- `render_form()` → Complete form orchestrator

#### `components/code_display.py`
Code display and syntax highlighting components.

**Functions:**
- `render_code_tab(code, language)` → Single code tab
- `render_code_tabs(files)` → Multiple code tabs
- `syntax_highlight(code, lang)` → Apply highlighting
- `add_line_numbers(code)` → Add line numbers

#### `components/download_manager.py`
File download and clipboard functionality.

**Functions:**
- `create_download_button(file, content)` → Single file download
- `create_zip_download(files)` → ZIP archive download
- `copy_to_clipboard(text)` → Clipboard functionality
- `download_all_files(files)` → Batch download

### Generator Files

#### `generators/code_generator.py`
Main code generation orchestrator.

**Class:** `CodeGenerator`

**Methods:**
- `__init__(config)` → Initialize with config
- `generate_all()` → Generate all files
- `generate_worker_code()` → Generate Worker TS
- `generate_configs()` → Generate config files
- `generate_docs()` → Generate documentation
- `validate_output()` → Validate generated code

#### `generators/worker_generator.py`
Cloudflare Worker code generation.

**Functions:**
- `generate_main_handler()` → Main index.ts
- `generate_email_handler()` → Email handler
- `generate_twilio_service()` → Twilio integration
- `generate_utils()` → Utility functions
- `assemble_worker_code()` → Combine all parts

#### `generators/config_generator.py`
Configuration file generation.

**Functions:**
- `generate_wrangler_toml()` → Wrangler config
- `generate_package_json()` → Package file
- `generate_tsconfig()` → TypeScript config
- `generate_env_example()` → Environment template

#### `generators/docs_generator.py`
Documentation generation.

**Functions:**
- `generate_readme()` → README.md
- `generate_setup_guide()` → SETUP.md
- `generate_deployment_guide()` → DEPLOYMENT.md
- `generate_deploy_script()` → deploy.sh

### Template Files

All templates use Jinja2 syntax with `.j2` extension.

**Common Template Variables:**
- `{{ config.worker_name }}` → Worker name
- `{{ config.domain }}` → Domain
- `{{ config.twilio.* }}` → Twilio settings
- `{% if config.rate_limit.enabled %}` → Conditional blocks

### Utility Files

#### `utils/validators.py`
Input validation functions.

**Functions:**
- `validate_worker_name(name)` → Worker name validation
- `validate_domain(domain)` → Domain validation
- `validate_email(email)` → Email validation
- `validate_phone_number(phone)` → Phone validation
- `validate_twilio_sid(sid)` → Twilio SID validation

#### `utils/formatters.py`
Code formatting utilities.

**Functions:**
- `format_typescript(code)` → Format TS code
- `format_toml(config)` → Format TOML
- `format_json(data)` → Format JSON
- `format_markdown(text)` → Format Markdown

#### `utils/helpers.py`
General helper functions.

**Functions:**
- `sanitize_filename(name)` → Clean filenames
- `parse_email_pattern(pattern)` → Parse patterns
- `merge_configs(base, override)` → Merge configs
- `deep_get(dict, path)` → Nested dict access

### Schema Files

#### `schemas/config_schema.py`
Dataclass definitions for configuration.

**Classes:**
- `BasicConfig` → Basic settings
- `TwilioConfig` → Twilio settings
- `EmailRoutingConfig` → Routing settings
- `RateLimitConfig` → Rate limit settings
- `WorkerConfig` → Complete config

#### `schemas/validation_schema.py`
Pydantic models for validation.

**Models:**
- `WorkerNameModel` → Worker name validation
- `DomainModel` → Domain validation
- `PhoneNumberModel` → Phone validation
- `ConfigModel` → Complete config validation

### Test Files

#### `tests/test_generators.py`
Tests for code generators.

```python
def test_worker_generation()
def test_config_generation()
def test_template_rendering()
```

#### `tests/test_validators.py`
Tests for validators.

```python
def test_worker_name_validation()
def test_domain_validation()
def test_phone_number_validation()
```

### Configuration Files

#### `.streamlit/config.toml`
Streamlit app configuration.

```toml
[theme]
primaryColor = "#FF6B35"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"

[server]
port = 8501
enableCORS = false
```

#### `.streamlit/secrets.toml`
Secrets (not committed to git).

```toml
# Example secrets
ANALYTICS_KEY = "your_key_here"
```

## File Size Guidelines

- **app.py**: ~300 lines
- **Component files**: ~200-400 lines each
- **Generator files**: ~300-500 lines each
- **Template files**: ~100-300 lines each
- **Utility files**: ~100-200 lines each
- **Test files**: ~200-400 lines each

## Import Structure

### Example Import Pattern

```python
# app.py
from components.input_form import render_form
from components.code_display import render_code_tabs
from components.download_manager import create_zip_download
from generators.code_generator import CodeGenerator
from utils.validators import validate_worker_name
from schemas.config_schema import WorkerConfig
```

## Development Workflow

1. **Edit templates** in `templates/`
2. **Update generators** in `generators/`
3. **Modify UI** in `components/`
4. **Test changes** in `tests/`
5. **Update docs** in `docs/`
6. **Run app**: `streamlit run src/streamlit/app.py`

## Deployment Structure

### Docker Deployment
```
Dockerfile
docker-compose.yml
.dockerignore
```

### Cloud Deployment (Streamlit Cloud)
```
requirements.txt
.streamlit/config.toml
README.md (with demo link)
```

## Best Practices

1. **Modularity**: Each file has single responsibility
2. **Naming**: Clear, descriptive file names
3. **Organization**: Logical directory structure
4. **Testing**: Test files mirror source structure
5. **Documentation**: Inline comments and docstrings
6. **Configuration**: Separate config from code

## File Creation Order

Recommended order for building the application:

1. `config.py` → App configuration
2. `schemas/` → Data structures
3. `utils/validators.py` → Validation functions
4. `templates/` → Jinja2 templates
5. `generators/` → Code generation logic
6. `components/` → UI components
7. `app.py` → Main application
8. `tests/` → Test suite
9. `docs/` → Documentation

## Version Control

### Git Structure
```
.gitignore        # Ignore generated files, secrets
.github/          # GitHub Actions workflows
CONTRIBUTING.md   # Contribution guidelines
CHANGELOG.md      # Version history
```

### .gitignore Contents
```gitignore
# Python
__pycache__/
*.py[cod]
venv/
.pytest_cache/

# Streamlit
.streamlit/secrets.toml

# IDE
.vscode/
.idea/

# Generated
dist/
build/
*.zip

# Environment
.env
.env.local
```

This file structure provides a clean, maintainable, and scalable foundation for the Streamlit application!
