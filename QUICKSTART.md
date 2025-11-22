# Quick Start Guide (5 Minutes)

## Prerequisites
- Python 3.11+
- `uv` package manager: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- OpenRouter API key: https://openrouter.ai

## Local Development (5 min)

### 1. Setup (1 min)
```bash
git clone <repo>
cd lovable-mcp-gateway
uv sync
```

### 2. Configure (1 min)
```bash
cp .env.example .env
# Edit .env:
# - MCP_BEARER_TOKEN=your-secure-token
# - MCP_LLM_OPENROUTER_API_KEY=sk-or-...
```

### 3. Generate Auth (2 min)
```bash
python scripts/save_auth_state.py ./auth.json
# Browser opens - log in to Lovable manually
# Auth state saved automatically
```

### 4. Run (1 min)
```bash
uv run uvicorn src.server:app --reload
# Visit: http://localhost:8080/health
```

### 5. Test
```bash
curl -X POST http://localhost:8080/tools/run_browser_agent \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{"task": "Create a Lovable project called TestApp"}'
```

---

## Fly.io Deployment (10 min)

### 1. Prepare (2 min)
```bash
cp fly.toml.example fly.toml
# Edit fly.toml: change app name to something unique
```

### 2. Generate Auth (2 min)
```bash
python scripts/save_auth_state.py ./auth.json
```

### 3. Deploy (6 min)
```bash
fly launch
fly secrets set MCP_BEARER_TOKEN=your-token
fly secrets set MCP_LLM_OPENROUTER_API_KEY=sk-or-...
fly secrets set MCP_LLM_MODEL_NAME=anthropic/claude-3.5-sonnet-20241022
fly secrets set MCP_AUTH_STATE_PATH=@./auth.json
fly deploy
```

### 4. Verify
```bash
fly status
fly logs
```

---

## Common Commands

### Local Testing
```bash
# Run tests
uv run pytest tests/ -v

# Format code
uv run black src tests

# Lint
uv run ruff check src tests

# Type check
uv run mypy src
```

### Fly.io Management
```bash
# View logs
fly logs

# SSH into machine
fly ssh console

# Redeploy
fly deploy

# Update secrets
fly secrets set KEY=value

# View secrets
fly secrets list
```

### Troubleshooting

**Auth expired?**
```bash
python scripts/save_auth_state.py ./auth.json
fly secrets set MCP_AUTH_STATE_PATH=@./auth.json
fly deploy
```

**Rate limited?**
Edit `.env`: `MCP_RATE_LIMIT_PER_MIN=20`

**Build timeout?**
Edit `.env`: `MCP_AGENT_TIMEOUT_SEC=900` (15 min)

**Check health**
```bash
curl https://your-app.fly.dev/health
```

---

## API Usage

### Request
```bash
curl -X POST https://your-app.fly.dev/tools/run_browser_agent \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Create a Lovable project called MyApp and build a todo list",
    "context": {}
  }'
```

### Success Response
```json
{
  "ok": true,
  "run_id": "abc-123",
  "preview_url": "https://xyz.lovable.dev",
  "status": "done",
  "raw": "...",
  "elapsed_sec": 45.2
}
```

### Error Response
```json
{
  "ok": false,
  "run_id": "abc-123",
  "error_code": "TIMEOUT_BUILD",
  "message": "Build timed out",
  "elapsed_sec": 600.0
}
```

---

## Error Codes

| Code | Meaning | Action |
|------|---------|--------|
| `TIMEOUT_BUILD` | Execution timeout | Increase `MCP_AGENT_TIMEOUT_SEC` |
| `AUTH_EXPIRED` | Login failed | Regenerate `auth.json` |
| `UI_CHANGED` | Selector not found | Update selectors in `src/lovable_adapter/` |
| `NETWORK_ERROR` | Connection issue | Check network/Lovable status |
| `UNKNOWN_ERROR` | Other failure | Check logs |

---

## Documentation

- **README.md** - Full documentation
- **SECURITY.md** - Security best practices
- **CHANGELOG.md** - Version history
- **RESEARCH_FINDINGS.md** - Architecture validation
- **IMPLEMENTATION_SUMMARY.md** - Complete implementation details

---

## Support

1. Check README.md "Troubleshooting" section
2. Review logs: `fly logs` or `uv run uvicorn ... --log-level debug`
3. Check SECURITY.md for security issues
4. See CHANGELOG.md for known limitations

