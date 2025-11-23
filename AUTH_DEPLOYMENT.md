# Authentication Deployment Guide

This document explains how to deploy and manage `auth.json` (Playwright storage state) to the Lovable MCP Gateway production environment on Fly.io.

## Overview

The `auth.json` file contains Playwright browser session state (cookies, local storage, etc.) needed for the browser agent to authenticate with Lovable.dev. This file is deployed to production via Fly.io secrets and persisted using a volume mount.

## Deployment Process

### Automatic Deployment (GitHub Actions)

When you push changes to the `main` branch:

1. **CI Workflow** runs tests and builds the Docker image
2. **Deploy Workflow** automatically:
   - Encodes `auth.json` to base64
   - Sets it as a Fly.io secret (`AUTH_JSON_B64`)
   - Deploys the application to Fly.io
   - The entrypoint script decodes the secret and writes it to the volume mount

### Manual Deployment

If you need to manually set the auth.json secret:

```bash
# Encode auth.json to base64
AUTH_JSON_B64=$(cat auth.json | base64 -w 0)

# Set as Fly.io secret
flyctl secrets set AUTH_JSON_B64="${AUTH_JSON_B64}" --app lovable-mcp-gateway

# Redeploy the application
flyctl deploy --remote-only --app lovable-mcp-gateway
```

## Updating auth.json When It Expires

The current `auth.json` has cookies expiring on **2026-11-23**. When you need to update it:

### Step 1: Generate New auth.json Locally

```bash
# Run the save_auth_state.py script to generate a fresh auth.json
python scripts/save_auth_state.py
```

This will:
- Launch a browser
- Prompt you to log in to Lovable.dev
- Save the authenticated session to `auth.json`

### Step 2: Verify the New auth.json

```bash
# Run the auth validity test
python -m pytest test_auth_validity.py -v
```

### Step 3: Deploy to Production

```bash
# Commit and push the new auth.json
git add auth.json
git commit -m "chore: update auth.json with fresh session"
git push origin main
```

The GitHub Actions workflow will automatically:
- Encode the new `auth.json`
- Set it as the `AUTH_JSON_B64` secret
- Deploy to Fly.io

## Architecture

### File Paths

- **Local Development**: `./auth.json` (in repository root)
- **Production Volume**: `/app/auth_state/auth.json` (Fly.io persistent volume)
- **Environment Variable**: `AUTH_JSON_B64` (base64-encoded auth.json)

### Entrypoint Script Flow

1. Check if `AUTH_JSON_B64` environment variable is set
2. If set:
   - Create `/app/auth_state` directory
   - Decode base64 and write to `/app/auth_state/auth.json`
   - Set `MCP_AUTH_STATE_PATH` environment variable
3. If not set:
   - Use default path `./auth.json`
4. Start the Uvicorn server

### Fly.io Configuration

- **Volume Mount**: `lovable_auth_state` → `/app/auth_state`
- **Secret**: `AUTH_JSON_B64` (set by GitHub Actions)
- **Persistence**: Auth state persists across machine restarts

## Troubleshooting

### Auth.json Not Found in Production

Check Fly.io logs:

```bash
flyctl logs --app lovable-mcp-gateway --limit 100
```

Look for messages like:
- `✓ auth.json successfully deployed` (success)
- `✗ Failed to create auth.json` (error)
- `Note: AUTH_JSON_B64 environment variable not set` (warning)

### Browser Agent Cannot Authenticate

1. Verify `auth.json` exists in production:
   ```bash
   flyctl ssh console --app lovable-mcp-gateway
   cat /app/auth_state/auth.json
   ```

2. Check if cookies are expired:
   ```bash
   python test_auth_validity.py
   ```

3. If expired, regenerate and redeploy (see "Updating auth.json" section)

### Volume Mount Issues

If the volume doesn't exist, create it:

```bash
flyctl volumes create lovable_auth_state --app lovable-mcp-gateway --region cdg
```

## Security Notes

- ✅ `auth.json` is NOT committed to git (in `.gitignore`)
- ✅ Secrets are stored securely in Fly.io
- ✅ Base64 encoding is for safe transmission, not encryption
- ⚠️ Never commit `auth.json` to the repository
- ⚠️ Rotate credentials if the file is accidentally exposed

## Related Files

- `entrypoint.sh` - Decodes and deploys auth.json
- `fly.toml` - Defines volume mount
- `.github/workflows/deploy.yml` - Encodes and sets secret
- `scripts/save_auth_state.py` - Generates fresh auth.json
- `test_auth_validity.py` - Validates auth.json

