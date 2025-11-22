# Lovable MCP Gateway

Production-ready HTTP gateway for Lovable automation using the Saik0s `mcp-server-browser-use` engine. Now trimmed for Fly.io's <8 GB image limit with a multi-stage build and minimal runtime dependencies.

## What This Service Does
- FastAPI gateway with bearer auth, per-IP rate limiting (slowapi), and global concurrency control
- Delegates automation to the Saik0s `mcp-browser-cli` (installed in the image at build time)
- Uses Playwright + Chromium with a pre-generated `auth.json` storage state for Lovable.dev
- Structured JSON responses with preview URL extraction
- Deployable to Fly.io with GitHub Actions CI/CD

## Runtime Environment
Key environment variables (set via `.env` locally or `fly secrets set` in production):

- `MCP_BEARER_TOKEN` **(required)** – bearer token for the API
- `MCP_RATE_LIMIT_PER_MIN` (default `10`)
- `MCP_AGENT_CONCURRENCY` (default `3`)
- `MCP_AGENT_TIMEOUT_SEC` (default `600`)
- `MCP_AGENT_RETRY_MAX` (default `2`)
- `MCP_LLM_PROVIDER`, `MCP_LLM_OPENROUTER_API_KEY`, `MCP_LLM_MODEL_NAME` – Saik0s LLM configuration
- `MCP_AUTH_STATE_PATH` – path to the Playwright storage state (`./auth.json`)
- `MCP_AGENT_TOOL_USE_VISION` – set to `true` only when using a vision-capable model on OpenRouter

See `.env.example` for all options.

## Local Development
1. **Install dependencies & Playwright browsers**
   ```bash
   uv sync
   python -m playwright install chromium
   ```
2. **Create environment file**
   ```bash
   cp .env.example .env
   # fill in secrets (Bearer token, OpenRouter key, etc.)
   ```
3. **Generate Lovable auth state**
   ```bash
   python scripts/save_auth_state.py ./auth.json
   ```
   A browser window opens; sign in to Lovable. The storage state is saved automatically.
4. **Run the gateway**
   ```bash
   uv run uvicorn src.server:app --host 0.0.0.0 --port 8080
   ```
5. **Health check** – visit `http://localhost:8080/health`.

## HTTP API
- `GET /health`
- `POST /tools/run_browser_agent` (Bearer token required)

Example:
```bash
auth_token="your-token"
curl -X POST http://localhost:8080/tools/run_browser_agent \
  -H "Authorization: Bearer ${auth_token}" \
  -H "Content-Type: application/json" \
  -d '{"task": "Create a Lovable project and build a todo app"}'
```

Successful response shape:
```json
{
  "ok": true,
  "run_id": "uuid",
  "preview_url": "https://abc123.lovable.dev",
  "status": "done",
  "steps": [],
  "debug": {},
  "raw": "...Saik0s output...",
  "elapsed_sec": 42.0
}
```

## Docker (slim multi-stage)
The new multi-stage Dockerfile installs only runtime dependencies (Saik0s engine, FastAPI stack, Playwright + Chromium) and strips build caches. Target size: <2 GB compressed.

Build locally:
```bash
docker build -t lovable-mcp-gateway:latest .
```
Run locally:
```bash
docker run --rm -p 8080:8080 \
  -e MCP_BEARER_TOKEN=your-token \
  -e MCP_LLM_PROVIDER=openrouter \
  -e MCP_LLM_OPENROUTER_API_KEY=sk-or-your-key \
  -e MCP_LLM_MODEL_NAME=anthropic/claude-3.5-sonnet-20241022 \
  -e MCP_AUTH_STATE_PATH=/app/auth.json \
  -v $(pwd)/auth.json:/app/auth.json:ro \
  lovable-mcp-gateway:latest
```

If a Docker build log still shows CUDA/ML packages (e.g., `torch`, `nvidia-*`, `transformers`), run the helper script to confirm
what's being pulled from `uv.lock`:

```bash
python scripts/inspect_lock.py
```

Today the Saik0s engine depends on `browser-use`, which pins `sentence-transformers` and `torch`. Those transitives will install
until an upstream release drops them and the lockfile is regenerated. The gateway itself does not import these ML stacks, but
they remain in the image because they're locked.

## Fly.io Deployment
1. Copy and edit the sample config:
   ```bash
   cp fly.toml.example fly.toml
   # update app name and region
   ```
2. Generate `auth.json` as above and set secrets (sample):
   ```bash
   fly secrets set MCP_BEARER_TOKEN=your-token \
       MCP_LLM_PROVIDER=openrouter \
       MCP_LLM_OPENROUTER_API_KEY=sk-or-your-key \
       MCP_LLM_MODEL_NAME=anthropic/claude-3.5-sonnet-20241022 \
       MCP_AGENT_CONCURRENCY=3 \
       MCP_RATE_LIMIT_PER_MIN=10 \
       MCP_AGENT_TIMEOUT_SEC=600 \
       MCP_AGENT_RETRY_MAX=2 \
       MCP_AGENT_TOOL_USE_VISION=false \
       MCP_AUTH_STATE_PATH=/app/auth.json
   ```
   Supply `auth.json` to Fly either by baking it into the image during deploy (`fly deploy --build-secret auth_state=./auth.json` and copy to `/app/auth.json` in the Dockerfile) or by mounting it from a volume. Ensure the file is readable at the `MCP_AUTH_STATE_PATH` you set above.
3. Deploy:
   ```bash
   fly deploy
   ```

## Why the Image Is Smaller (Strada B)
- Removed heavy ML/LLM dependencies (torch, transformers, langchain, faiss, etc.). Only FastAPI, Saik0s CLI, Playwright, and supporting libs remain.
- Multi-stage Dockerfile installs dependencies once in the builder stage and copies only `/usr/local` plus the Playwright browser cache to the runtime stage.
- Build caches and apt/pip caches are cleaned to avoid bloat.
- The gateway invokes `mcp-browser-cli` directly (no `uvx` at runtime), preventing duplicate installations inside the container.

## Troubleshooting
- **Auth expired**: regenerate `auth.json` with `python scripts/save_auth_state.py ./auth.json` and redeploy.
- **TIMEOUT_BUILD**: raise `MCP_AGENT_TIMEOUT_SEC`.
- **Rate limited**: increase `MCP_RATE_LIMIT_PER_MIN` or `MCP_AGENT_CONCURRENCY` carefully.
- **Vision tools**: enable only when the selected OpenRouter model supports vision (`MCP_AGENT_TOOL_USE_VISION=true`). Heavy vision/ML stacks are intentionally omitted from the base image.

## Testing
Run unit tests locally:
```bash
uv run pytest -v
```
CI (`.github/workflows/ci.yml`) runs linting and tests on push.
