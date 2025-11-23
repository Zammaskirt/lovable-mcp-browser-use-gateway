# 🔧 Production Configuration Guide

## Step 1: Generate Authentication State (auth.json)

The `save_auth_state.py` script opens a browser and waits for you to manually log in to Lovable. Follow these steps:

### Command
```bash
python scripts/save_auth_state.py ./auth.json
```

### What Happens
1. A browser window opens automatically
2. You'll see Lovable.dev loading
3. **Manually log in** with your Lovable credentials
4. The script waits up to 10 minutes for login detection
5. Once authenticated, it saves your session to `auth.json`

### Important Notes
- ✅ The browser window will stay open - this is normal
- ✅ Log in using your Lovable account (GitHub/Google/Email)
- ✅ The script detects login by looking for workspace indicators
- ✅ If detection fails, it still saves the state (you can proceed)
- ⚠️ **Keep `auth.json` secure** - it contains session cookies
- ⚠️ **Don't commit to git** - add to `.gitignore`

### After Generation
```bash
# For Fly.io deployment:
fly secrets set MCP_AUTH_STATE_PATH=@./auth.json

# Or set environment variable:
export MCP_AUTH_STATE_PATH=./auth.json
```

---

## Step 2: Configure Performance Settings

Based on your usage pattern (10 users daily, multiple requests per user):

### Recommended Configuration

Add to your `.env` file:

```env
# Concurrency: Handle 5 concurrent browser tasks
# Rationale: 10 users × 5 concurrent = 50 concurrent capacity
# Default (3) is conservative; 5 handles occasional spikes
MCP_AGENT_CONCURRENCY=5

# Rate Limiting: 30 requests per minute per IP
# Rationale: Allows 0.5 req/sec per user, handles bursts
# Default (10) may be too restrictive if users share IP
MCP_RATE_LIMIT_PER_MIN=30

# Timeout: 900 seconds (15 minutes)
# Rationale: Handles complex builds with retries
# Default (600s) is 10 min; 15 min provides buffer
MCP_AGENT_TIMEOUT_SEC=900

# Retry: Keep default of 2 retries
# Rationale: Handles transient failures without excessive delays
MCP_AGENT_RETRY_MAX=2
```

---

## Step 3: Capacity Planning

### Your Usage Profile
- **Daily Users**: 10
- **Requests per User**: ~5-10 (estimated)
- **Total Daily Requests**: 50-100
- **Peak Requests/Hour**: 20-30 (assuming 8-hour business day)

### Recommended Settings Breakdown

| Setting | Value | Reasoning |
|---------|-------|-----------|
| `MCP_AGENT_CONCURRENCY` | 5 | Handles 5 simultaneous builds |
| `MCP_RATE_LIMIT_PER_MIN` | 30 | ~0.5 req/sec per IP, allows bursts |
| `MCP_AGENT_TIMEOUT_SEC` | 900 | 15 min for complex builds + retries |
| `MCP_AGENT_RETRY_MAX` | 2 | Retry transient failures |

### Scaling Guidance
- **If users increase to 50+**: Increase `MCP_AGENT_CONCURRENCY` to 10-15
- **If requests spike**: Increase `MCP_RATE_LIMIT_PER_MIN` to 50-100
- **If builds timeout**: Increase `MCP_AGENT_TIMEOUT_SEC` to 1200 (20 min)
- **Monitor**: Track actual execution times and adjust accordingly

---

## Step 4: Deployment Checklist

- [ ] Generated `auth.json` with Lovable login
- [ ] Set `MCP_BEARER_TOKEN` to secure random token
- [ ] Set `MCP_LLM_OPENROUTER_API_KEY` with valid API key
- [ ] Added concurrency/rate limit settings to `.env`
- [ ] Set `MCP_AGENT_TIMEOUT_SEC` to 900
- [ ] Tested locally: `python -m pytest tests/ -v`
- [ ] Ready for deployment to Fly.io

---

## Monitoring & Adjustment

After deployment, monitor these metrics:
- **Actual timeout frequency**: If >5% of requests timeout, increase `MCP_AGENT_TIMEOUT_SEC`
- **Queue depth**: If requests queue up, increase `MCP_AGENT_CONCURRENCY`
- **Rate limit hits**: If users hit limits, increase `MCP_RATE_LIMIT_PER_MIN`
- **Execution time**: Track p95/p99 build times to optimize timeout

