#!/bin/bash
set -euo pipefail

# Encode auth.json to base64
AUTH_JSON_B64=$(cat auth.json | base64 -w 0)

# Set the secret using flyctl
flyctl secrets set AUTH_JSON_B64="${AUTH_JSON_B64}" --app lovable-mcp-gateway

echo "✓ AUTH_JSON_B64 secret set successfully"

