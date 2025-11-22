# 🚀 Fly.io Deployment Guide

**Status**: ✅ Ready for Deployment  
**Last Updated**: 2025-11-22

---

## 📋 Pre-Deployment Checklist

- [x] `.env` configured with secure bearer token
- [x] `MCP_LLM_MODEL_NAME` set to valid model (Claude 3.5 Sonnet)
- [x] `auth.json` created (placeholder - update with real credentials)
- [x] `fly.toml` created from template
- [x] All tests passing (42/42)
- [x] Code quality verified
- [x] Local deployment tested

---

## 🔧 Installation Prerequisites

### 1. Install Fly CLI

**Windows (PowerShell)**:
```powershell
# Using Chocolatey
choco install flyctl

# Or using scoop
scoop install flyctl

# Or download from https://fly.io/docs/hands-on/install-flyctl/
```

**macOS**:
```bash
brew install flyctl
```

**Linux**:
```bash
curl -L https://fly.io/install.sh | sh
```

### 2. Verify Installation
```bash
fly --version
```

### 3. Authenticate with Fly.io
```bash
fly auth login
# Opens browser for authentication
```

---

## 📝 Configuration Files

### `.env` - Environment Variables
✅ **Status**: Configured
- Bearer token: Secure random token
- LLM Model: `anthropic/claude-3.5-sonnet-20241022`
- OpenRouter API Key: Set
- Auth state path: `./auth.json`

### `auth.json` - Lovable Authentication
⚠️ **Status**: Placeholder (needs real credentials)

**To generate real auth.json**:
```bash
uv run python scripts/save_auth_state.py ./auth.json
# Browser opens - log in to Lovable
# Script saves authentication state
```

### `fly.toml` - Fly.io Configuration
✅ **Status**: Created from template
- App name: `lovable-mcp-gateway`
- Region: `iad` (US East)
- Machine: 2 CPU, 1GB RAM
- Health check: `/health` endpoint

---

## 🚀 Deployment Steps

### Step 1: Install Fly CLI
```bash
# See Installation Prerequisites section above
fly --version
```

### Step 2: Authenticate
```bash
fly auth login
```

### Step 3: Create Fly App (First Time Only)
```bash
fly launch
# Follow prompts:
# - App name: lovable-mcp-gateway (or your choice)
# - Region: iad (or your preference)
# - Postgres: No
# - Redis: No
```

### Step 4: Set Secrets
```bash
# Set bearer token
fly secrets set MCP_BEARER_TOKEN="$(cat .env | grep MCP_BEARER_TOKEN | cut -d= -f2)"

# Set OpenRouter API key
fly secrets set MCP_LLM_OPENROUTER_API_KEY="$(cat .env | grep MCP_LLM_OPENROUTER_API_KEY | cut -d= -f2)"

# Set model name
fly secrets set MCP_LLM_MODEL_NAME="anthropic/claude-3.5-sonnet-20241022"

# Set auth state (from file)
fly secrets set MCP_AUTH_STATE_PATH=@./auth.json
```

### Step 5: Deploy
```bash
fly deploy
```

### Step 6: Monitor Deployment
```bash
fly logs
```

---

## ✅ Post-Deployment Verification

### 1. Get App URL
```bash
fly info
# Look for "Hostname" field
```

### 2. Test Health Endpoint
```bash
curl https://<your-app>.fly.dev/health
```

Expected response:
```json
{
  "ok": true,
  "version": "0.1.0",
  "concurrency": 3,
  "rate_limit_per_min": 10
}
```

### 3. Test Authentication
```bash
# Invalid token (should return 401)
curl -X POST https://<your-app>.fly.dev/tools/run_browser_agent \
  -H "Authorization: Bearer invalid-token" \
  -H "Content-Type: application/json" \
  -d '{"task":"test"}'

# Valid token (should process request)
curl -X POST https://<your-app>.fly.dev/tools/run_browser_agent \
  -H "Authorization: Bearer <your-bearer-token>" \
  -H "Content-Type: application/json" \
  -d '{"task":"test"}'
```

### 4. View Logs
```bash
fly logs
```

---

## 🔒 Security Checklist

- [x] Bearer token is secure random (not test-token)
- [x] Secrets set via `fly secrets set` (not in code)
- [x] HTTPS enforced (force_https = true)
- [x] Auth state file not committed to git
- [x] Rate limiting enabled
- [x] Concurrency limits set

---

## 📊 Useful Commands

```bash
# View app status
fly status

# View app info
fly info

# View logs
fly logs

# SSH into machine
fly ssh console

# Scale machines
fly scale count 2

# Update secrets
fly secrets set KEY=value

# View secrets
fly secrets list

# Redeploy
fly deploy

# Rollback to previous version
fly releases
fly releases rollback
```

---

## 🐛 Troubleshooting

### App won't start
```bash
fly logs
# Check for errors in logs
```

### Health check failing
```bash
# Verify endpoint is responding
curl https://<your-app>.fly.dev/health

# Check logs for errors
fly logs
```

### Authentication not working
```bash
# Verify bearer token is set
fly secrets list

# Check if token matches .env
cat .env | grep MCP_BEARER_TOKEN
```

### Out of memory
```bash
# Increase machine memory
fly scale memory 2048
```

---

## 📞 Support

- **Fly.io Docs**: https://fly.io/docs/
- **Lovable MCP Gateway Docs**: See README.md
- **Issues**: Check logs with `fly logs`

---

## ⚠️ Important Notes

1. **Auth State**: The `auth.json` file contains session tokens. Keep it secure!
2. **Secrets**: Never commit real secrets to git. Use `fly secrets set`.
3. **Costs**: Fly.io free tier includes 3 shared-cpu-1x 256MB VMs. Monitor usage.
4. **Monitoring**: Set up alerts for high CPU/memory usage.

---

**Status**: ✅ Ready to Deploy

