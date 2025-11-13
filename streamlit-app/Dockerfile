# Multi-stage Dockerfile for Cloudflare Email-to-Twilio-SMS Generator
# Supports both pip (requirements.txt) and Poetry (pyproject.toml)
# Use: docker build -t cloudflare-email-to-twilio-sms-generator .
# Or with Poetry: docker build -f Dockerfile.poetry -t cloudflare-email-to-twilio-sms-generator .

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
COPY components/ ./components/
COPY generators/ ./generators/
COPY schemas/ ./schemas/
COPY utils/ ./utils/
COPY validators/ ./validators/
COPY templates/ ./templates/
COPY assets/ ./assets/
COPY .streamlit/ ./.streamlit/

# Create non-root user for security
RUN useradd -m -u 1000 streamlit && \
    chown -R streamlit:streamlit /app

# Switch to non-root user
USER streamlit

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
