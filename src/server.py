"""
Production HTTP gateway for Lovable automation MCP service.

Features:
- Bearer token authentication
- Per-IP rate limiting
- Global concurrency control
- Structured JSON logging
- PRD output contract
"""

import asyncio
import os
import re
import time
import uuid
from typing import Any

import structlog
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.agent_runner import run_browser_agent_async

logger = structlog.get_logger(__name__)

# Configuration
DEFAULT_BEARER_TOKEN = "test-token"
BEARER_TOKEN = os.getenv("MCP_BEARER_TOKEN") or DEFAULT_BEARER_TOKEN
RATE_LIMIT_PER_MIN = int(os.getenv("MCP_RATE_LIMIT_PER_MIN", "10"))
AGENT_CONCURRENCY = int(os.getenv("MCP_AGENT_CONCURRENCY", "3"))
VERSION = "0.1.0"

# Global concurrency semaphore
_concurrency_semaphore = asyncio.Semaphore(AGENT_CONCURRENCY)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# FastAPI app
app = FastAPI(
    title="Lovable MCP Gateway",
    version=VERSION,
    description="Production HTTP gateway for Lovable automation",
)

app.state.limiter = limiter


class RunBrowserAgentRequest(BaseModel):
    """Request model for browser agent execution."""

    task: str
    context: dict[str, Any] | None = None


class RunBrowserAgentResponse(BaseModel):
    """Success response model."""

    ok: bool = True
    run_id: str
    preview_url: str | None = None
    project_url: str | None = None
    status: str = "done"
    steps: list[dict[str, Any]] = Field(default_factory=list)
    debug: dict[str, Any] = Field(default_factory=dict)
    raw: str
    elapsed_sec: float


class ErrorResponse(BaseModel):
    """Error response model."""

    ok: bool = False
    run_id: str
    error_code: str
    message: str
    raw: str = ""
    elapsed_sec: float


def _extract_preview_url(text: str) -> str | None:
    """Extract preview URL from Saik0s output."""
    # Look for lovable preview URLs
    patterns = [
        r"https://[a-z0-9-]+\.lovable\.dev",
        r"https://preview\.lovable\.dev/[^\s]+",
        r"preview[_\s]url[:\s]+([^\s]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0) if match.lastindex is None else match.group(1)
    return None


def _map_error_code(error: str) -> str:
    """Map exception to error code."""
    error_lower = error.lower()
    if "timeout" in error_lower or "timed out" in error_lower:
        return "TIMEOUT_BUILD"
    if "auth" in error_lower or "login" in error_lower or "expired" in error_lower:
        return "AUTH_EXPIRED"
    if "selector" in error_lower or "element" in error_lower or "ui" in error_lower:
        return "UI_CHANGED"
    if "network" in error_lower or "connection" in error_lower:
        return "NETWORK_ERROR"
    return "UNKNOWN_ERROR"


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    """Verify Bearer token on protected endpoints."""
    if request.url.path in ["/health", "/docs", "/openapi.json"]:
        return await call_next(request)

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        logger.warning("Missing or invalid auth header", path=request.url.path)
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "Missing or invalid Authorization header"},
        )

    token = auth_header[7:]
    if token != BEARER_TOKEN:
        logger.warning("Invalid bearer token", path=request.url.path)
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "Invalid bearer token"},
        )

    return await call_next(request)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "ok": True,
        "version": VERSION,
        "concurrency": AGENT_CONCURRENCY,
        "rate_limit_per_min": RATE_LIMIT_PER_MIN,
    }


@app.post("/tools/run_browser_agent", response_model=RunBrowserAgentResponse)
@limiter.limit(f"{RATE_LIMIT_PER_MIN}/minute")
async def run_browser_agent_endpoint(
    request: Request, payload: RunBrowserAgentRequest
) -> RunBrowserAgentResponse | ErrorResponse:
    """
    Execute a browser automation task.

    Returns PRD-compliant response with preview URL extraction and error mapping.
    """
    run_id = str(uuid.uuid4())
    start_time = time.time()

    logger.info("Browser agent request", run_id=run_id, task=payload.task[:100])

    try:
        async with _concurrency_semaphore:
            result = await run_browser_agent_async(payload.task, payload.context)

        elapsed = time.time() - start_time

        if not result.get("ok"):
            error_msg = result.get("error", "Unknown error")
            error_code = _map_error_code(error_msg)
            logger.error(
                "Browser agent failed",
                run_id=run_id,
                error_code=error_code,
                elapsed=elapsed,
            )
            return ErrorResponse(
                run_id=run_id,
                error_code=error_code,
                message=error_msg,
                raw=result.get("result_text", ""),
                elapsed_sec=elapsed,
            )

        result_text = result.get("result_text", "")
        preview_url = _extract_preview_url(result_text)

        logger.info(
            "Browser agent succeeded",
            run_id=run_id,
            preview_url=preview_url,
            elapsed=elapsed,
        )

        return RunBrowserAgentResponse(
            ok=True,
            run_id=run_id,
            preview_url=preview_url,
            status="done",
            raw=result_text,
            elapsed_sec=elapsed,
        )

    except Exception as e:
        elapsed = time.time() - start_time
        error_code = _map_error_code(str(e))
        logger.exception(
            "Unexpected error in browser agent",
            run_id=run_id,
            error_code=error_code,
            elapsed=elapsed,
        )
        return ErrorResponse(
            run_id=run_id,
            error_code=error_code,
            message=str(e),
            elapsed_sec=elapsed,
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
