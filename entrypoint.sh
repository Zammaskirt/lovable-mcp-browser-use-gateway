#!/bin/sh
set -euo pipefail

# Lovable MCP Gateway Entrypoint
# Starts the FastAPI server with proper configuration

# Validate required environment variables
if [ -z "${MCP_BEARER_TOKEN:-}" ]; then
    echo "❌ Error: MCP_BEARER_TOKEN is not set"
    exit 1
fi

if [ -z "${MCP_LLM_PROVIDER:-}" ]; then
    echo "❌ Error: MCP_LLM_PROVIDER is not set"
    exit 1
fi

# Log startup information
echo "🚀 Starting Lovable MCP Gateway"
echo "📊 Configuration:"
echo "   - Port: ${PORT:-8080}"
echo "   - LLM Provider: ${MCP_LLM_PROVIDER}"
echo "   - Rate Limit: ${MCP_RATE_LIMIT_PER_MIN:-10}/min"
echo "   - Concurrency: ${MCP_AGENT_CONCURRENCY:-3}"
echo ""

# Start the FastAPI server
exec uvicorn src.server:app \
    --host 0.0.0.0 \
    --port "${PORT:-8080}" \
    --workers 1 \
    --loop uvloop \
    --log-level info

