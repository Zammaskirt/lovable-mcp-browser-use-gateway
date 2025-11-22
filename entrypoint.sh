#!/bin/sh
set -euo pipefail

exec uvicorn src.server:app --host 0.0.0.0 --port "${PORT:-8080}"

