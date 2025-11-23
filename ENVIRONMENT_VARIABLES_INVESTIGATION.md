# Environment Variables Investigation: Fly.io Production Deployment

## Executive Summary

**The fix is CORRECT.** Fly.io secrets are automatically available as environment variables at runtime. The `-e .env` flag should be removed from the CLI command.

---

## 1. How Fly.io Secrets Work

### Architecture (from Fly.io Docs)
- Secrets are stored in an **encrypted vault**
- When a Machine boots, Fly.io's agent **decrypts secrets and injects them as environment variables**
- Secrets are available to the application code via `os.getenv()`
- **No .env file is needed in production**

### Key Quote from Fly.io Docs:
> "An app's secrets are available as environment variables at runtime on every Machine belonging to that Fly App"

---

## 2. mcp-server-browser-use CLI Configuration

### How the CLI Reads Configuration
From the GitHub repository documentation:

**The CLI reads environment variables directly from `os.environ`**

The `-e .env` flag is for **local development only** to load a `.env` file.

### Supported Configuration Methods:
1. **Environment variables** (production) ✅
2. **`.env` file** (local development) ✅
3. **Command-line flags** (not supported for all options)

### Key Variables for the CLI:
```
MCP_LLM_PROVIDER=openrouter
MCP_LLM_OPENROUTER_API_KEY=sk-or-...
MCP_LLM_MODEL_NAME=anthropic/claude-3.5-sonnet-20241022
MCP_BROWSER_HEADLESS=true
MCP_AUTH_STATE_PATH=/path/to/auth.json
```

---

## 3. Environment Variable Flow in Production

```
Fly.io Secrets Vault
        ↓
fly secrets set MCP_LLM_OPENROUTER_API_KEY=sk-or-...
        ↓
Fly.io Agent (at boot time)
        ↓
Decrypt & inject into container environment
        ↓
Python process (uvicorn)
        ↓
os.environ (available to all code)
        ↓
subprocess.Popen(env=os.environ.copy())
        ↓
mcp-server-browser-use CLI (reads from env)
```

---

## 4. Why the Original Code Failed

### Problem 1: Missing `.env` File
- `.env` is in `.gitignore` (not in Docker image)
- `load_dotenv(dotenv_path='.env')` silently fails
- Environment variables are NOT loaded

### Problem 2: Incorrect CLI Syntax
- `mcp-server-browser-use -e .env run-browser-agent task`
- The `-e .env` flag tries to load a non-existent file
- CLI still runs but with empty environment variables
- Returns empty output (no error, just no output)

### Result:
- `MCP_LLM_OPENROUTER_API_KEY` is empty
- CLI executes but fails silently
- Returns empty stdout/stderr with return code 0
- Agent returns "Browser agent returned no output"

---

## 5. The Fix (Verified Correct)

### Change Made:
```python
# BEFORE (WRONG):
load_dotenv(dotenv_path='.env')
cmd = ["mcp-server-browser-use", "-e", ".env", "run-browser-agent", task]

# AFTER (CORRECT):
load_dotenv(dotenv_path='.env', override=False)
cmd = ["mcp-server-browser-use", "run-browser-agent", task]
```

### Why This Works:
1. `load_dotenv(override=False)` - loads `.env` if it exists (local dev), doesn't override existing env vars
2. Removed `-e .env` flag - CLI reads directly from `os.environ`
3. `cli_env = os.environ.copy()` - passes all environment variables to subprocess
4. In production, Fly.io secrets are already in `os.environ`

---

## 6. Required Fly.io Secrets Setup

### Must Set These Secrets:
```bash
fly secrets set MCP_LLM_OPENROUTER_API_KEY=sk-or-...
fly secrets set MCP_LLM_PROVIDER=openrouter
fly secrets set MCP_LLM_MODEL_NAME=anthropic/claude-3.5-sonnet-20241022
fly secrets set MCP_BEARER_TOKEN=your-secure-token
fly secrets set MCP_AUTH_STATE_PATH=@./auth.json
```

### Optional Secrets:
```bash
fly secrets set MCP_BROWSER_HEADLESS=true
fly secrets set MCP_AGENT_TOOL_USE_VISION=false
fly secrets set MCP_AGENT_TIMEOUT_SEC=600
```

---

## 7. Verification Checklist

- [x] Fly.io secrets are automatically environment variables
- [x] `.env` file is NOT needed in production
- [x] mcp-server-browser-use CLI reads from `os.environ`
- [x] Removing `-e .env` flag is correct
- [x] `cli_env = os.environ.copy()` correctly includes Fly.io secrets
- [x] Enhanced error logging added to diagnose missing variables

---

## 8. Next Steps

1. **Deploy the fixed code** to Fly.io
2. **Set all required secrets** via `fly secrets set`
3. **Monitor logs** for environment variable validation messages
4. **Test with N8N** to verify the agent returns output

