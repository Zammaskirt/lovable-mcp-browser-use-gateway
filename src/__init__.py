"""
Lovable MCP Gateway - Production HTTP gateway for Lovable automation.

This package provides a FastAPI HTTP gateway that wraps the Saik0s
mcp-server-browser-use engine for browser automation with Lovable.dev.

Main components:
- server.py: FastAPI application with auth, rate limiting, concurrency
- agent_runner.py: Saik0s CLI delegation layer
- lovable_adapter/: Optional deterministic Playwright helpers
"""

__version__ = "0.1.0"
__author__ = "Lovable MCP Team"
__license__ = "MIT"

from src.agent_runner import run_browser_agent, run_browser_agent_async
from src.server import app

__all__ = [
    "app",
    "run_browser_agent",
    "run_browser_agent_async",
    "__version__",
]
