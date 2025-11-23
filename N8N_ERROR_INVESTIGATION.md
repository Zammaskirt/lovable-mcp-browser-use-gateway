# N8N Error Investigation: "Browser agent returned no output"

## Error Details
```json
{
  "ok": false,
  "status": "error",
  "raw": "",
  "error_code": "UNKNOWN_ERROR",
  "message": "Browser agent returned no output",
  "elapsed_sec": 7.619542360305786
}
```

## Root Cause Analysis

### Issue #1: Missing `.env` File in Production
**Severity:** 🔴 CRITICAL

The code in `agent_runner.py` line 47 tries to load `.env`:
```python
load_dotenv(dotenv_path='.env')
```

**Problem:**
- `.env` file is NOT in the repository (it's in `.gitignore`)
- `.env` is NOT copied to the Docker image in `Dockerfile`
- In production, `load_dotenv()` silently fails (returns False)
- Environment variables are NOT loaded from `.env`

**Result:**
- `MCP_LLM_OPENROUTER_API_KEY` is empty
- `mcp-server-browser-use` CLI runs but fails silently
- Returns empty stdout/stderr with return code 0
- Agent returns "Browser agent returned no output"

### Issue #2: Incorrect CLI Command Syntax
**Severity:** 🟡 HIGH

Line 50 in `agent_runner.py`:
```python
cmd = ["mcp-server-browser-use", "-e", ".env", "run-browser-agent", task]
```

**Problem:**
- The `-e .env` flag is trying to load a file that doesn't exist
- The actual CLI command should be: `mcp-server-browser-use run-browser-agent`
- Environment variables should be passed via `os.environ`, not via `-e` flag

**Correct approach:**
```python
cmd = ["mcp-server-browser-use", "run-browser-agent", task]
```

### Issue #3: Environment Variables Not Set in Production
**Severity:** 🔴 CRITICAL

In `entrypoint.sh`, only `MCP_AUTH_STATE_PATH` is set:
```bash
export MCP_AUTH_STATE_PATH="${AUTH_DIR}/auth.json"
```

**Missing in production:**
- `MCP_LLM_OPENROUTER_API_KEY` - NOT set via Fly.io secrets
- `MCP_LLM_PROVIDER` - NOT set
- `MCP_LLM_MODEL_NAME` - NOT set
- `MCP_BROWSER_HEADLESS` - NOT set
- `MCP_AGENT_TOOL_USE_VISION` - NOT set

These must be set as Fly.io secrets or environment variables.

## Solution

### Step 1: Fix agent_runner.py
Remove the `.env` file loading and `-e` flag:

```python
# REMOVE THIS:
load_dotenv(dotenv_path='.env')
cmd = ["mcp-server-browser-use", "-e", ".env", "run-browser-agent", task]

# REPLACE WITH:
cmd = ["mcp-server-browser-use", "run-browser-agent", task]
```

### Step 2: Set Environment Variables in Fly.io
```bash
fly secrets set MCP_LLM_OPENROUTER_API_KEY=sk-or-...
fly secrets set MCP_LLM_PROVIDER=openrouter
fly secrets set MCP_LLM_MODEL_NAME=anthropic/claude-3.5-sonnet-20241022
fly secrets set MCP_BROWSER_HEADLESS=true
fly secrets set MCP_AGENT_TOOL_USE_VISION=false
```

### Step 3: Verify Environment Variables
Add logging to verify all required variables are set before running CLI.

## Testing

After fixes:
1. Deploy to Fly.io
2. Check logs: `fly logs`
3. Test endpoint with curl
4. Verify N8N integration works

