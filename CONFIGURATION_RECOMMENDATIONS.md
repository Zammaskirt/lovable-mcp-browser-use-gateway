# ⚙️ Configuration Recommendations for Your Deployment

## Your Usage Profile
- **Daily Users**: 10
- **Requests per User**: 5-10 (estimated)
- **Total Daily Requests**: 50-100
- **Peak Load**: 20-30 requests/hour (assuming 8-hour business day)
- **Average Load**: 6-12 requests/hour

---

## 🎯 Recommended Configuration

### Add These to Your `.env` File

```env
# ============================================================================
# PERFORMANCE TUNING FOR 10 USERS
# ============================================================================

# Concurrency: 5 concurrent browser tasks
# Why: Handles 5 simultaneous builds comfortably
# Default: 3 (too conservative for your load)
# Scaling: Increase to 10-15 if users grow to 50+
MCP_AGENT_CONCURRENCY=5

# Rate Limiting: 30 requests per minute per IP
# Why: Allows ~0.5 requests/second per user
# Default: 10 (may be too restrictive if users share corporate IP)
# Scaling: Increase to 50-100 if requests spike
MCP_RATE_LIMIT_PER_MIN=30

# Timeout: 900 seconds (15 minutes)
# Why: Handles complex builds with 2 retries (2 × 600s = 1200s max)
# Default: 600 (10 minutes - may be tight for complex builds)
# Scaling: Increase to 1200 (20 min) if builds frequently timeout
MCP_AGENT_TIMEOUT_SEC=900

# Retry: 2 attempts (keep default)
# Why: Handles transient failures without excessive delays
# Typical retry delay: 2 seconds between attempts
MCP_AGENT_RETRY_MAX=2
```

---

## 📊 Performance Analysis

### Concurrency Calculation
```
Users: 10
Avg requests per user: 7.5
Total daily requests: 75
Business hours: 8
Requests per hour: ~9
Requests per minute: ~0.15
Peak multiplier: 3x average
Peak requests per minute: ~0.45

Concurrent tasks needed: 1-2 (average), 3-5 (peak)
Recommended: 5 (handles spikes with headroom)
```

### Rate Limiting Calculation
```
Peak requests per minute: 0.45
Per-IP rate limit: 30/minute
Headroom: 66x (very comfortable)

If users share corporate IP:
- 10 users × 0.45 req/min = 4.5 req/min per IP
- 30/minute limit = 6.7x headroom (still comfortable)
```

### Timeout Calculation
```
Typical Lovable build: 5-10 minutes
Complex build: 10-15 minutes
With 2 retries: 2 × 15 min = 30 min max

Recommended timeout: 900s (15 min)
Max total time: 900s × 2 retries = 1800s (30 min)
Handles: Complex builds with retries ✅
```

---

## 🚀 Deployment Steps

### 1. Generate Auth State
```bash
python scripts/save_auth_state.py ./auth.json
# Log in when browser opens
# Wait for script to complete
```

### 2. Update .env File
```bash
# Add the recommended settings above to your .env
MCP_AGENT_CONCURRENCY=5
MCP_RATE_LIMIT_PER_MIN=30
MCP_AGENT_TIMEOUT_SEC=900
```

### 3. Test Locally
```bash
export MCP_AUTH_STATE_PATH=./auth.json
python -m pytest tests/ -v
```

### 4. Deploy to Fly.io
```bash
fly secrets set MCP_AUTH_STATE_PATH=@./auth.json
fly deploy --remote-only
```

---

## 📈 Scaling Guide

### If Users Grow to 50+
```env
MCP_AGENT_CONCURRENCY=10
MCP_RATE_LIMIT_PER_MIN=50
MCP_AGENT_TIMEOUT_SEC=900  # Keep same
```

### If Requests Frequently Timeout
```env
MCP_AGENT_TIMEOUT_SEC=1200  # 20 minutes
# Monitor actual execution times first
```

### If Rate Limiting Becomes Issue
```env
MCP_RATE_LIMIT_PER_MIN=100
# Only if users complain about 429 errors
```

---

## 📊 Monitoring Checklist

After deployment, monitor:
- [ ] Timeout frequency (target: <5% of requests)
- [ ] Queue depth (target: <2 requests waiting)
- [ ] Rate limit hits (target: 0 per day)
- [ ] Actual execution times (p95, p99)
- [ ] Auth expiration (regenerate monthly)

Adjust settings based on actual metrics, not predictions.

