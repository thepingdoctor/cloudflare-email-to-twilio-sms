# Email-to-SMS Code Generator

A Streamlit web application that generates production-ready Cloudflare Worker code for converting emails to SMS messages using Twilio.

## Features

- 🎨 **User-friendly Interface** - Intuitive configuration forms
- 📝 **Code Generation** - Automatic Worker code generation
- 🎯 **Customizable** - Full control over features and settings
- 📦 **One-Click Download** - Download all files as ZIP
- 🔐 **Secure** - Built-in validation and security features
- 📊 **Real-time Preview** - See generated code instantly

## Quick Start

### Installation

#### Option 1: Using Poetry (Recommended)

```bash
# Clone repository
git clone <repository-url>
cd streamlit-app

# Install Poetry (if not already installed)
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Run application
poetry run streamlit run app.py

# Or activate virtual environment first
poetry shell
streamlit run app.py
```

#### Option 2: Using pip

```bash
# Clone repository
git clone <repository-url>
cd streamlit-app

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run app.py
```

### Docker Deployment

```bash
# Build image
docker build -t email2sms-generator .

# Run container
docker run -p 8501:8501 email2sms-generator
```

### Access Application

Open your browser to: http://localhost:8501

## Usage

1. **Configure Settings**
   - Enter your domain and worker name
   - Add Twilio credentials
   - Customize routing and features

2. **Generate Code**
   - Click "Generate Code" button
   - Review generated files

3. **Download**
   - Download ZIP archive
   - Extract and deploy to Cloudflare

4. **Deploy**
   - Follow deployment instructions
   - Configure Email Routing in Cloudflare
   - Test your setup

## Configuration Options

### Basic Settings
- Worker name
- Domain
- Email pattern

### Twilio Configuration
- Account SID
- Auth Token
- Phone number

### Email Routing
- Phone extraction method
- Content source
- Max message length

### Advanced Features
- Rate limiting
- Logging
- Security (whitelist, content filtering)
- Retry logic
- Error notifications

## Generated Files

The application generates:
- `src/index.ts` - Main Worker code
- `wrangler.toml` - Cloudflare configuration
- `package.json` - npm dependencies
- `tsconfig.json` - TypeScript configuration
- `.env.example` - Environment template
- `.gitignore` - Git ignore rules
- `README.md` - Documentation
- `deploy.sh` - Deployment script

## Package Management

This project supports both **Poetry** (recommended) and **pip** for dependency management.

### Why Poetry?

- **Deterministic builds** with `poetry.lock`
- **Dependency resolution** with conflict detection
- **Virtual environment management** automatically
- **All-in-one** configuration in `pyproject.toml`
- **Easy publishing** to PyPI

See [POETRY.md](POETRY.md) for comprehensive Poetry documentation.

### Common Poetry Commands

```bash
# Install dependencies
poetry install

# Add new dependency
poetry add package-name

# Update dependencies
poetry update

# Run tests
poetry run pytest

# Format code
poetry run black .

# Export to requirements.txt
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

## Development

### Project Structure

```
streamlit-app/
├── app.py                 # Main application
├── components/            # UI components
│   ├── input_form.py
│   ├── code_display.py
│   └── download_manager.py
├── generators/            # Code generators
│   └── code_generator.py
├── templates/             # Jinja2 templates
│   ├── worker/
│   ├── config/
│   └── docs/
├── utils/                 # Utilities
│   ├── validators.py
│   ├── helpers.py
│   └── constants.py
├── schemas/               # Data schemas
│   └── config_schema.py
└── requirements.txt       # Dependencies
```

### Testing

#### Using Poetry

```bash
# Install test dependencies
poetry install --with test

# Run tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov

# Type checking
poetry run mypy .

# Linting
poetry run flake8

# Format code
poetry run black .
poetry run isort .

# Or use Makefile shortcuts
make test
make coverage
```

#### Using pip

```bash
# Install test dependencies
pip install -r tests/requirements-test.txt

# Run tests
pytest

# Run tests with coverage
pytest --cov

# Type checking
mypy .

# Linting
flake8
```

## Requirements

- Python 3.8+ (3.11+ recommended)
- Streamlit 1.31.0
- Poetry 1.0.0+ (optional but recommended)
- See `pyproject.toml` or `requirements.txt` for full dependency list

## License

MIT

## Support

For issues and questions, please open an issue on GitHub.

## Credits

Built with:
- [Streamlit](https://streamlit.io/)
- [Jinja2](https://jinja.palletsprojects.com/)
- [Pygments](https://pygments.org/)
- [Cloudflare Workers](https://workers.cloudflare.com/)
- [Twilio](https://www.twilio.com/)
