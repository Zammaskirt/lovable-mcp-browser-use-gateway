# 🚀 Complete Deployment Steps

## Prerequisites ✅
- [x] `MCP_BEARER_TOKEN` - Set to secure random token
- [x] `MCP_LLM_OPENROUTER_API_KEY` - Set with valid API key
- [x] All tests passing (55/55 ✅)
- [x] Code coverage at 95% ✅

---

## Phase 1: Generate Authentication (5 minutes)

### Step 1.1: Run Auth Generation Script
```bash
python scripts/save_auth_state.py ./auth.json
```

**Expected Output:**
```
🔐 Lovable Authentication State Generator
📁 Output: /path/to/auth.json

🌐 Opening Lovable.dev...
⏳ Waiting for manual login...
   Please log in to Lovable in the browser window.
   This script will continue once you're authenticated.
```

### Step 1.2: Log In to Lovable
- Browser window opens automatically
- Log in with your Lovable credentials (GitHub/Google/Email)
- Wait for script to detect login (shows "✅ Login detected!")
- Script automatically saves `auth.json`

### Step 1.3: Verify Auth File
```bash
ls -la auth.json
# Should show file size > 1KB
cat auth.json | head -20
# Should show JSON with cookies and storage
```

---

## Phase 2: Configure Performance (2 minutes)

### Step 2.1: Update .env File
```bash
# Edit your .env file and add/update these values:

MCP_AGENT_CONCURRENCY=5
MCP_RATE_LIMIT_PER_MIN=30
MCP_AGENT_TIMEOUT_SEC=900
MCP_AGENT_RETRY_MAX=2
```

### Step 2.2: Verify Configuration
```bash
# Check that .env has all required variables
grep "MCP_" .env | sort
```

**Expected Output:**
```
MCP_AGENT_CONCURRENCY=5
MCP_AGENT_RETRY_MAX=2
MCP_AGENT_TIMEOUT_SEC=900
MCP_AUTH_STATE_PATH=./auth.json
MCP_BEARER_TOKEN=<your-secure-token>
MCP_LLM_OPENROUTER_API_KEY=<your-api-key>
MCP_LLM_MODEL_NAME=anthropic/claude-3.5-sonnet-20241022
MCP_RATE_LIMIT_PER_MIN=30
```

---

## Phase 3: Local Testing (5 minutes)

### Step 3.1: Set Environment Variable
```bash
export MCP_AUTH_STATE_PATH=./auth.json
```

### Step 3.2: Run Full Test Suite
```bash
python -m pytest tests/ -v --cov=src --cov-report=term-missing
```

**Expected Result:**
```
======================= 55 passed in ~28s =======================
TOTAL                                249     12    95%
```

### Step 3.3: Test Health Endpoint
```bash
# In one terminal, start the server:
python -m uvicorn src.server:app --reload

# In another terminal, test:
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "ok": true,
  "version": "0.1.0",
  "concurrency": 5,
  "rate_limit_per_min": 30
}
```

---

## Phase 4: Deploy to Fly.io (5 minutes)

### Step 4.1: Set Fly.io Secrets
```bash
# Set authentication
fly secrets set MCP_BEARER_TOKEN=<your-secure-token>
fly secrets set MCP_LLM_OPENROUTER_API_KEY=<your-api-key>

# Set auth state (from file)
fly secrets set MCP_AUTH_STATE_PATH=@./auth.json

# Set performance tuning
fly secrets set MCP_AGENT_CONCURRENCY=5
fly secrets set MCP_RATE_LIMIT_PER_MIN=30
fly secrets set MCP_AGENT_TIMEOUT_SEC=900
```

### Step 4.2: Deploy Application
```bash
# Deploy using remote builder (recommended for large images)
fly deploy --remote-only
```

### Step 4.3: Verify Deployment
```bash
# Check app status
fly status

# View logs
fly logs

# Test health endpoint
curl https://<your-app>.fly.dev/health
```

---

## Phase 5: Post-Deployment Verification (5 minutes)

### Step 5.1: Health Check
```bash
curl -s https://<your-app>.fly.dev/health | jq .
```

### Step 5.2: Authentication Test
```bash
# Should fail without token
curl -X POST https://<your-app>.fly.dev/tools/run_browser_agent \
  -H "Content-Type: application/json" \
  -d '{"task": "test"}' \
  # Expected: 401 Unauthorized

# Should succeed with token
curl -X POST https://<your-app>.fly.dev/tools/run_browser_agent \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{"task": "build a todo app"}' \
  # Expected: 200 OK with response
```

### Step 5.3: Monitor Logs
```bash
fly logs --follow
# Watch for any errors or warnings
```

---

## ✅ Deployment Complete!

Your Lovable MCP Gateway is now live and ready for production use.

### Next Steps
1. **Monitor**: Watch logs for errors
2. **Test**: Have users test with real tasks
3. **Adjust**: Tune settings based on actual metrics
4. **Maintain**: Regenerate auth.json monthly

### Support
- Check logs: `fly logs`
- View metrics: `fly metrics`
- Troubleshoot: See CONFIGURATION_GUIDE.md

