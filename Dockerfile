# Optimized Dockerfile for Lovable MCP Gateway
# Minimal Python image with Playwright dependencies installed

# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install --no-cache-dir uv

# Copy project files
COPY pyproject.toml uv.lock* README.md ./

# Build dependencies
RUN uv sync --frozen --no-dev

# Stage 2: Runtime - minimal Python with Playwright dependencies
FROM python:3.11-slim

WORKDIR /app

# Install Playwright system dependencies and curl
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libxkbcommon0 \
    libdbus-1-3 \
    libatspi2.0-0 \
    libxcb1 \
    libxcb-shm0 \
    libxcb-render0 \
    libxcb-xfixes0 \
    libxcb-shape0 \
    libxcb-xinerama0 \
    libxcb-xkb1 \
    libxkbcommon-x11-0 \
    libfontconfig1 \
    libfreetype6 \
    libharfbuzz0b \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libpixman-1-0 \
    libgdk-pixbuf-2.0-0 \
    libgtk-3-0 \
    libsecret-1-0 \
    libxss1 \
    libgbm1 \
    libnss3 \
    libnspr4 \
    fonts-liberation \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy only necessary application files
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY entrypoint.sh .
COPY README.md .

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PORT=8080 \
    PYTHONDONTWRITEBYTECODE=1

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run application
CMD ["sh", "entrypoint.sh"]

