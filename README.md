# Lovable MCP Gateway

Production-ready HTTP gateway for Lovable automation using the Saik0s browser-use MCP engine.

**Start in 15 minutes** ⚡

## What This Is

A FastAPI HTTP gateway that:
- Wraps the Saik0s `mcp-server-browser-use` engine for browser automation
- Provides Bearer token authentication
- Implements per-IP rate limiting and global concurrency control
- Automates Lovable.dev project creation, prompt submission, and build triggering
- Returns structured JSON responses with preview URLs and error codes
- Deploys to Fly.io with Playwright Chromium support

## Quick Start (Local)

### 1. Clone and Setup
```bash
git clone <repo-url>
cd lovable-mcp-gateway
cp .env.example .env
```

### 2. Configure .env
```bash
# Required
MCP_BEARER_TOKEN=your-secure-token-here
MCP_LLM_PROVIDER=openrouter
MCP_LLM_OPENROUTER_API_KEY=sk-or-your-key
MCP_LLM_MODEL_NAME=anthropic/claude-3.5-sonnet-20241022

# Optional
MCP_RATE_LIMIT_PER_MIN=10
MCP_AGENT_CONCURRENCY=3
```

### 3. Generate Auth State
```bash
uv sync
python scripts/save_auth_state.py ./auth.json
# Browser opens - log in to Lovable manually
# Auth state saved automatically
```

### 4. Run Locally
```bash
uv run uvicorn src.server:app --reload
```

Visit: http://localhost:8080/health

## HTTP API Usage

### Health Check
```bash
curl http://localhost:8080/health
```

### Run Browser Agent
```bash
curl -X POST http://localhost:8080/tools/run_browser_agent \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Create a new Lovable project called MyApp and build a todo list"
  }'
```

### Response (Success)
```json
{
  "ok": true,
  "run_id": "uuid-here",
  "preview_url": "https://abc123.lovable.dev",
  "status": "done",
  "raw": "...saik0s output...",
  "elapsed_sec": 45.2
}
```

### Response (Error)
```json
{
  "ok": false,
  "run_id": "uuid-here",
  "error_code": "TIMEOUT_BUILD",
  "message": "Build timed out after 600 seconds",
  "elapsed_sec": 600.0
}
```

## Fly.io Deployment

### 1. Prepare
```bash
cp fly.toml.example fly.toml
# Edit fly.toml: change app name
```

### 2. Generate Auth State
```bash
python scripts/save_auth_state.py ./auth.json
```

### 3. Deploy
```bash
fly launch
fly secrets set MCP_BEARER_TOKEN=your-token
fly secrets set MCP_LLM_OPENROUTER_API_KEY=sk-or-...
fly secrets set MCP_LLM_MODEL_NAME=anthropic/claude-3.5-sonnet-20241022
fly secrets set MCP_AUTH_STATE_PATH=@./auth.json
fly deploy
```

## Configuration

See `.env.example` for all options:
- `MCP_BEARER_TOKEN` - API authentication (required)
- `MCP_RATE_LIMIT_PER_MIN` - Rate limit (default: 10)
- `MCP_AGENT_CONCURRENCY` - Max concurrent tasks (default: 3)
- `MCP_LLM_*` - Saik0s LLM configuration
- `MCP_BROWSER_*` - Browser settings
- `MCP_AUTH_STATE_PATH` - Path to auth.json

## Error Codes

- `TIMEOUT_BUILD` - Execution timeout
- `AUTH_EXPIRED` - Authentication failed
- `UI_CHANGED` - Selector/element not found
- `NETWORK_ERROR` - Connection issue
- `UNKNOWN_ERROR` - Other failures

## Testing

```bash
uv run pytest tests/ -v
```

## Architecture

```
FastAPI Gateway (Port 8080)
  ├─ Bearer Auth Middleware
  ├─ Rate Limiter (slowapi)
  ├─ Concurrency Semaphore (asyncio)
  └─ Saik0s CLI Delegation
       └─ mcp-browser-cli
            └─ Playwright + Chromium
                 └─ Lovable.dev
```

## Security

- **Bearer Token**: Required for all endpoints except `/health`
  - **Development**: Defaults to `test-token` if `MCP_BEARER_TOKEN` not set
  - **Production**: MUST explicitly set `MCP_BEARER_TOKEN` to a secure random token
  - Generate token: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- No secrets in code
- Rate limiting per IP
- Global concurrency limits
- See SECURITY.md for details

## Troubleshooting

**Auth state expired?**
```bash
python scripts/save_auth_state.py ./auth.json
fly secrets set MCP_AUTH_STATE_PATH=@./auth.json
```

**Build timeout?**
Increase `MCP_AGENT_TIMEOUT_SEC` in .env

**Rate limited?**
Increase `MCP_RATE_LIMIT_PER_MIN` in .env

See SECURITY.md and CHANGELOG.md for more.

