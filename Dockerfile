# Multi-stage build to keep runtime image small
# Stage 1: builder installs dependencies and Playwright browser
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl wget unzip gcc libc6-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock* ./

RUN uv sync --frozen --no-dev --system

RUN python -m playwright install --with-deps chromium \
    && rm -rf /var/lib/apt/lists/* /root/.cache/pip

# Stage 2: runtime image copies only what is needed
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PLAYWRIGHT_BROWSERS_PATH=/root/.cache/ms-playwright

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local /usr/local
COPY --from=builder /root/.cache/ms-playwright /root/.cache/ms-playwright

RUN python -m playwright install-deps chromium \
    && rm -rf /var/lib/apt/lists/*

COPY src ./src
COPY scripts ./scripts
COPY entrypoint.sh README.md pyproject.toml uv.lock* ./

EXPOSE 8080

CMD ["sh", "entrypoint.sh"]
