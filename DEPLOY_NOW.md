# 🚀 Deploy Now - Copy & Paste Commands

Your Lovable MCP Gateway is ready for production deployment. Follow these exact commands:

---

## Step 1: Set Fly.io Secrets (Copy & Paste)

```bash
# Set authentication token
fly secrets set MCP_BEARER_TOKEN=aqkAsrGmsLBDFx5yfRba1MMW3BZFhTiMRY49puh3XLhzajXk9TIuIeYCpWrxHPbQzFBiwhG1Pdjf1TLfHL95q0gDh

# Set OpenRouter API key
fly secrets set MCP_LLM_OPENROUTER_API_KEY=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

# Set auth state from file
fly secrets set MCP_AUTH_STATE_PATH=@./auth.json

# Set performance tuning
fly secrets set MCP_AGENT_CONCURRENCY=5
fly secrets set MCP_RATE_LIMIT_PER_MIN=30
fly secrets set MCP_AGENT_TIMEOUT_SEC=900
```

---

## Step 2: Deploy Application

```bash
# Deploy using remote builder (recommended for large Docker images)
fly deploy --remote-only
```

---

## Step 3: Verify Deployment

```bash
# Check app status
fly status

# View recent logs
fly logs

# Test health endpoint
curl https://<your-app>.fly.dev/health
```

---

## Step 4: Test Authentication

```bash
# Get your app URL
APP_URL=$(fly info -j | jq -r '.app.name')
echo "Testing: https://${APP_URL}.fly.dev"

# Test without token (should fail with 401)
curl -X POST https://${APP_URL}.fly.dev/tools/run_browser_agent \
  -H "Content-Type: application/json" \
  -d '{"task": "test"}' \
  -w "\nStatus: %{http_code}\n"

# Test with token (should succeed)
curl -X POST https://${APP_URL}.fly.dev/tools/run_browser_agent \
  -H "Authorization: Bearer aqkAsrGmsLBDFx5yfRba1MMW3BZFhTiMRY49puh3XLhzajXk9TIuIeYCpWrxHPbQzFBiwhG1Pdjf1TLfHL95q0gDh" \
  -H "Content-Type: application/json" \
  -d '{"task": "build a todo app"}' \
  -w "\nStatus: %{http_code}\n"
```

---

## ✅ Deployment Checklist

- [ ] Ran `fly secrets set` commands (Step 1)
- [ ] Ran `fly deploy --remote-only` (Step 2)
- [ ] Verified with `fly status` (Step 3)
- [ ] Tested health endpoint (Step 3)
- [ ] Tested authentication (Step 4)
- [ ] Checked logs for errors: `fly logs`

---

## 📊 Current Configuration

| Setting | Value | Purpose |
|---------|-------|---------|
| `MCP_BEARER_TOKEN` | aqkAsrGmsLBDFx5yfRba1MMW3BZFhTiMRY49puh3XLhzajXk9TIuIeYCpWrxHPbQzFBiwhG1Pdjf1TLfHL95q0gDh | API authentication |
| `MCP_LLM_OPENROUTER_API_KEY` | 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 | LLM provider |
| `MCP_AGENT_CONCURRENCY` | 5 | Concurrent builds |
| `MCP_RATE_LIMIT_PER_MIN` | 30 | Requests per minute |
| `MCP_AGENT_TIMEOUT_SEC` | 900 | Task timeout (15 min) |

---

## 🆘 Troubleshooting

### Deployment fails
```bash
# Check logs
fly logs

# Rebuild from scratch
fly deploy --remote-only --force-machines
```

### Auth fails
```bash
# Verify secrets are set
fly secrets list

# Check if token is correct
echo "aqkAsrGmsLBDFx5yfRba1MMW3BZFhTiMRY49puh3XLhzajXk9TIuIeYCpWrxHPbQzFBiwhG1Pdjf1TLfHL95q0gDh"
```

### Auth.json expired
```bash
# Regenerate auth.json
python scripts/save_auth_state_v2.py ./auth.json

# Update secret
fly secrets set MCP_AUTH_STATE_PATH=@./auth.json

# Redeploy
fly deploy --remote-only
```

---

## 📞 Support

- **Test Results**: See `DEPLOYMENT_READY_SUMMARY.md`
- **Configuration**: See `CONFIGURATION_RECOMMENDATIONS.md`
- **Production Readiness**: See `PRODUCTION_READINESS_REPORT.md`

**You're ready to go! 🚀**

