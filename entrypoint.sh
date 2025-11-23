#!/bin/sh
set -euo pipefail

# Trigger deployment to pick up AUTH_JSON_B64 secret
# Handle auth.json from environment variable if provided
if [ -n "${AUTH_JSON_B64:-}" ]; then
    echo "Decoding auth.json from environment variable..."

    # Use volume mount path in production, fallback to local path
    AUTH_DIR="${AUTH_DIR:-/app/auth_state}"
    mkdir -p "${AUTH_DIR}"

    # Decode base64 and write to file
    echo "${AUTH_JSON_B64}" | base64 -d > "${AUTH_DIR}/auth.json"

    # Verify the file was created
    if [ -f "${AUTH_DIR}/auth.json" ]; then
        echo "✓ auth.json successfully deployed to ${AUTH_DIR}/auth.json"
        # Also set MCP_AUTH_STATE_PATH for the application
        export MCP_AUTH_STATE_PATH="${AUTH_DIR}/auth.json"
    else
        echo "✗ Failed to create auth.json"
        exit 1
    fi
else
    echo "Note: AUTH_JSON_B64 environment variable not set. Using existing auth.json if available."
    # Set default path if not already set
    export MCP_AUTH_STATE_PATH="${MCP_AUTH_STATE_PATH:-.}/auth.json"
fi

exec uvicorn src.server:app --host 0.0.0.0 --port "${PORT:-8080}"

