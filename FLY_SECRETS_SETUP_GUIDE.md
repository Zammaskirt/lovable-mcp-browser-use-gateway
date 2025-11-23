# Fly.io Secrets Setup Guide - N8N Integration Fix

## Problem
N8N is getting "Browser agent returned no output" error because required environment variables are not set in Fly.io.

## Solution
Set all required secrets in Fly.io using `fly secrets set` command.

---

## Step 1: Verify Current Secrets

```bash
fly secrets list
```

This shows which secrets are already set (values are hidden for security).

---

## Step 2: Set Required Secrets

### Critical Secrets (MUST SET)

```bash
# LLM Configuration
fly secrets set MCP_LLM_OPENROUTER_API_KEY=sk-or-your-actual-key-here
fly secrets set MCP_LLM_PROVIDER=openrouter
fly secrets set MCP_LLM_MODEL_NAME=anthropic/claude-3.5-sonnet-20241022

# Authentication
fly secrets set MCP_BEARER_TOKEN=your-secure-bearer-token-here

# Auth State (Lovable login)
fly secrets set MCP_AUTH_STATE_PATH=/app/auth_state/auth.json
```

### Recommended Secrets (SHOULD SET)

```bash
# Browser Configuration
fly secrets set MCP_BROWSER_HEADLESS=true
fly secrets set MCP_BROWSER_WINDOW_WIDTH=1440
fly secrets set MCP_BROWSER_WINDOW_HEIGHT=1080

# Agent Configuration
fly secrets set MCP_AGENT_TIMEOUT_SEC=600
fly secrets set MCP_AGENT_RETRY_MAX=2
fly secrets set MCP_AGENT_TOOL_USE_VISION=false

# Rate Limiting
fly secrets set MCP_RATE_LIMIT_PER_MIN=10
fly secrets set MCP_AGENT_CONCURRENCY=3
```

---

## Step 3: Deploy with New Secrets

After setting secrets, redeploy:

```bash
fly deploy
```

Or use the GitHub Actions workflow (automatic on push).

---

## Step 4: Verify Deployment

### Check Logs
```bash
fly logs
```

Look for:
- "ENVIRONMENT VALIDATION:" messages
- "has_key_after_load=true" (indicates API key is set)
- "auth_file_exists=true" (indicates auth.json is available)

### Test Health Endpoint
```bash
curl https://your-app.fly.dev/health
```

Should return:
```json
{
  "ok": true,
  "version": "0.1.0",
  "concurrency": 3,
  "rate_limit_per_min": 10
}
```

### Test Browser Agent
```bash
curl -X POST https://your-app.fly.dev/tools/run_browser_agent \
  -H "Authorization: Bearer your-secure-bearer-token-here" \
  -H "Content-Type: application/json" \
  -d '{"task": "Navigate to lovable.dev and report the page title"}'
```

Should return:
```json
{
  "ok": true,
  "status": "done",
  "raw": "...",
  "preview_url": "...",
  "elapsed_sec": 15.5
}
```

---

## Step 5: Troubleshooting

### If Still Getting "Browser agent returned no output"

1. **Check logs for missing variables:**
   ```bash
   fly logs | grep "CRITICAL"
   ```

2. **Verify secrets are set:**
   ```bash
   fly secrets list
   ```

3. **Check auth.json exists:**
   ```bash
   fly ssh console
   ls -la /app/auth_state/auth.json
   ```

4. **Increase logging:**
   ```bash
   fly secrets set MCP_SERVER_LOGGING_LEVEL=DEBUG
   fly deploy
   fly logs
   ```

---

## Environment Variable Reference

| Variable | Purpose | Example |
|----------|---------|---------|
| `MCP_LLM_OPENROUTER_API_KEY` | OpenRouter API key | `sk-or-...` |
| `MCP_LLM_PROVIDER` | LLM provider | `openrouter` |
| `MCP_LLM_MODEL_NAME` | Model to use | `anthropic/claude-3.5-sonnet-20241022` |
| `MCP_BEARER_TOKEN` | API authentication | `your-secure-token` |
| `MCP_AUTH_STATE_PATH` | Lovable auth file | `/app/auth_state/auth.json` |
| `MCP_BROWSER_HEADLESS` | Headless mode | `true` |
| `MCP_AGENT_TIMEOUT_SEC` | Task timeout | `600` |

---

## Notes

- Secrets are encrypted in Fly.io's vault
- Available as environment variables at runtime
- No `.env` file needed in production
- Changes require `fly deploy` to take effect
- Use `fly secrets unset NAME` to remove a secret

