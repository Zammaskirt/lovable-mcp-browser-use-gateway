# Optimized Dockerfile for Lovable MCP Gateway
# Minimal Python image with Playwright dependencies installed

# Stage 1: Builder (installs only runtime deps)
FROM python:3.11-slim AS builder

ENV UV_CACHE_DIR=/tmp/uv-cache
WORKDIR /app

# Minimal build tooling
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

# Copy dependency manifests and README (required for package build)
COPY pyproject.toml uv.lock* README.md ./

# Install production deps into a venv
RUN uv sync --frozen --no-dev \
    && rm -rf ${UV_CACHE_DIR}

# Stage 2: Runtime (thin gateway-only image)
FROM python:3.11-slim

WORKDIR /app

# Runtime utilities only (including base64 for auth.json decoding)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    coreutils \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Copy prebuilt venv and app code
# Cache bust: 2025-11-23-entrypoint-fix-v2
COPY --from=builder /app/.venv /app/.venv
COPY src/ ./src/
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
CMD ["bash", "entrypoint.sh"]
