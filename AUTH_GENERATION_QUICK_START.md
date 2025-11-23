# 🔐 Auth.json Generation - Quick Start

## TL;DR - 3 Steps

### 1️⃣ Run the Script
```bash
python scripts/save_auth_state.py ./auth.json
```

### 2️⃣ Log In When Browser Opens
- Browser window opens automatically
- Log in to Lovable with your credentials
- Wait for the script to detect login (up to 10 minutes)
- Script automatically saves `auth.json`

### 3️⃣ Deploy the Auth File
```bash
# For Fly.io:
fly secrets set MCP_AUTH_STATE_PATH=@./auth.json

# For local testing:
export MCP_AUTH_STATE_PATH=./auth.json
```

---

## What the Script Does

```
┌─────────────────────────────────────────┐
│ python scripts/save_auth_state.py       │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│ 1. Launch browser (headless=false)      │
│ 2. Navigate to lovable.dev              │
│ 3. Wait for manual login (10 min max)   │
│ 4. Detect login via workspace selector  │
│ 5. Save session cookies to auth.json    │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│ auth.json created with:                 │
│ - Cookies                               │
│ - Local storage                         │
│ - Session state                         │
└─────────────────────────────────────────┘
```

---

## Troubleshooting

### Browser doesn't open
- Check if Playwright is installed: `pip install playwright`
- Install browser: `playwright install chromium`

### Login detection times out
- Script still saves auth.json - you can proceed
- Verify you're actually logged in before continuing
- Check browser console for errors

### "Permission denied" error
- Make sure script is executable: `chmod +x scripts/save_auth_state.py`
- Or run with python explicitly: `python scripts/save_auth_state.py ./auth.json`

### Auth expires in production
- Lovable sessions expire periodically (typically 30-90 days)
- Regenerate auth.json monthly or when you see AUTH_EXPIRED errors
- Redeploy with: `fly secrets set MCP_AUTH_STATE_PATH=@./auth.json`

---

## Security Notes

⚠️ **Important**: `auth.json` contains session cookies
- ✅ Add to `.gitignore` - never commit to git
- ✅ Store securely - treat like a password
- ✅ Use Fly.io secrets for production
- ✅ Rotate periodically (monthly recommended)
- ✅ Don't share with untrusted parties

---

## Next Steps After Generation

1. Verify `auth.json` was created:
   ```bash
   ls -la auth.json
   ```

2. Test locally:
   ```bash
   export MCP_AUTH_STATE_PATH=./auth.json
   python -m pytest tests/ -v
   ```

3. Deploy to Fly.io:
   ```bash
   fly secrets set MCP_AUTH_STATE_PATH=@./auth.json
   fly deploy
   ```

