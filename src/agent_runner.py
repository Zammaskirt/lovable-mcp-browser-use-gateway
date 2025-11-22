"""
Saik0s delegation layer for browser automation.

This module delegates to the mcp-browser-cli CLI to avoid internal import instability.
All environment variables are read by Saik0s from the process environment.
"""

import asyncio
import os
import subprocess
import sys
from typing import Any

import structlog
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_fixed

logger = structlog.get_logger(__name__)


class RunBrowserAgentInput(BaseModel):
    """Input model for browser agent execution."""

    task: str
    context: dict[str, Any] | None = None


def _get_agent_config() -> dict[str, Any]:
    """Get agent configuration from environment."""
    return {
        "timeout_sec": int(os.getenv("MCP_AGENT_TIMEOUT_SEC", "600")),
        "retry_max": int(os.getenv("MCP_AGENT_RETRY_MAX", "2")),
    }


@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def _run_saik0s_cli(task: str) -> str:
    """
    Run Saik0s CLI via subprocess.

    Args:
        task: The task description for the browser agent.

    Returns:
        Raw stdout from Saik0s CLI.

    Raises:
        subprocess.CalledProcessError: If CLI execution fails.
        TimeoutError: If execution exceeds timeout.
    """
    config = _get_agent_config()
    timeout = config["timeout_sec"]

    # Build command: use uvx to run mcp-browser-cli
    cmd = [
        sys.executable,
        "-m",
        "mcp_server_browser_use.cli",
        "run-browser-agent",
        task,
    ]

    logger.info("Running Saik0s CLI", cmd=cmd, timeout=timeout)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=os.environ.copy(),
        )

        if result.returncode != 0:
            logger.error(
                "Saik0s CLI failed",
                returncode=result.returncode,
                stderr=result.stderr,
            )
            raise subprocess.CalledProcessError(
                result.returncode, cmd, output=result.stdout, stderr=result.stderr
            )

        logger.info("Saik0s CLI succeeded", output_len=len(result.stdout))
        return result.stdout

    except subprocess.TimeoutExpired as e:
        logger.error("Saik0s CLI timeout", timeout=timeout)
        raise TimeoutError(f"Saik0s CLI timed out after {timeout}s") from e


def run_browser_agent(task: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Run a browser automation task via Saik0s.

    Args:
        task: The task description.
        context: Optional context dictionary (not used in CLI mode).

    Returns:
        Dictionary with keys:
        - ok: bool
        - result_text: str (raw Saik0s output)
        - error: str (if ok=False)

    Raises:
        TimeoutError: If execution exceeds timeout.
        subprocess.CalledProcessError: If CLI fails.
    """
    try:
        result_text = _run_saik0s_cli(task)
        return {
            "ok": True,
            "result_text": result_text,
        }
    except (subprocess.CalledProcessError, TimeoutError) as e:
        logger.error("Browser agent execution failed", error=str(e))
        return {
            "ok": False,
            "result_text": "",
            "error": str(e),
        }


async def run_browser_agent_async(
    task: str, context: dict[str, Any] | None = None
) -> dict[str, Any]:
    """
    Async wrapper for run_browser_agent.

    Runs the blocking CLI call in a thread pool.
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, run_browser_agent, task, context)
