"""
Saik0s delegation layer for browser automation.

This module delegates to the mcp-browser-cli CLI to avoid internal import instability.
All environment variables are read by Saik0s from the process environment.
"""

import asyncio
import os
import subprocess
import sys
import time
from typing import Any

import structlog
from dotenv import load_dotenv
from pydantic import BaseModel
from tenacity import RetryError, Retrying, stop_after_attempt, wait_fixed

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


def _run_saik0s_cli(task: str) -> str:
    """Run Saik0s CLI via subprocess with comprehensive diagnostics."""
    
    start_time = time.time()
    config = _get_agent_config()
    timeout = 30
    retry_max = max(1, config["retry_max"])

    # Load environment variables from .env file
    load_dotenv(dotenv_path='.env')
    
    # Build command with proper environment file loading
    cmd = ["mcp-server-browser-use", "-e", ".env", "run-browser-agent", task]
    
    # Get environment from loaded .env file and current environment
    cli_env = os.environ.copy()
    
    # Validate and set environment variables from .env
    openrouter_key = os.getenv('MCP_LLM_OPENROUTER_API_KEY', '')
    auth_path = os.getenv('MCP_AUTH_STATE_PATH', './auth.json')
    
    # Set critical environment variables
    cli_env['OPENAI_API_KEY'] = openrouter_key
    cli_env['PATIENT'] = 'true'
    cli_env['BROWSER_USE_STORAGE_STATE'] = auth_path
    
    # COMPREHENSIVE DIAGNOSTICS: Environment validation
    logger.info("=== CLI SUBPROCESS DIAGNOSTICS START ===")
    logger.info("Task execution started", task=task, timestamp=time.time())
    
    # Environment reload verification
    logger.info("ENVIRONMENT RELOAD VERIFICATION:")
    env_after_load = os.getenv('MCP_LLM_OPENROUTER_API_KEY', '')
    logger.info("Environment after .env load",
               api_key_length_after_load=len(env_after_load) if env_after_load else 0,
               has_key_after_load=bool(env_after_load and len(env_after_load) > 10))
    
    # Browser initialization checks
    logger.info("BROWSER INITIALIZATION DIAGNOSTICS:")
    browser_headless = os.getenv('MCP_BROWSER_HEADLESS', 'true')
    browser_width = os.getenv('MCP_BROWSER_WINDOW_WIDTH', '1440')
    browser_height = os.getenv('MCP_BROWSER_WINDOW_HEIGHT', '1080')
    logger.info("Browser config", headless=browser_headless, width=browser_width, height=browser_height)
    
    # Auth state validation
    logger.info("AUTHENTICATION DIAGNOSTICS:")
    auth_file_exists = os.path.exists(auth_path)
    auth_file_size = os.path.getsize(auth_path) if auth_file_exists else 0
    logger.info("Auth state validation",
               auth_file_path=auth_path,
               auth_file_exists=auth_file_exists,
               auth_file_size_bytes=auth_file_size)
    
    # LLM API validation
    logger.info("LLM API DIAGNOSTICS:")
    llm_provider = os.getenv('MCP_LLM_PROVIDER', 'openrouter')
    llm_model = os.getenv('MCP_LLM_MODEL_NAME', 'openai/gpt-5-mini')
    llm_temp = os.getenv('MCP_LLM_TEMPERATURE', '0.2')
    has_api_key = bool(openrouter_key and len(openrouter_key) > 10)
    logger.info("LLM config validation",
               provider=llm_provider,
               model=llm_model,
               temperature=llm_temp,
               has_api_key=has_api_key,
               api_key_length=len(openrouter_key) if openrouter_key else 0)
    
    # Subprocess preparation
    logger.info("SUBPROCESS PREPARATION:")
    logger.info("Command assembly", cmd=cmd)
    logger.info("Environment setup", env_vars_count=len(cli_env), critical_env_vars=['OPENAI_API_KEY', 'PATIENT', 'BROWSER_USE_STORAGE_STATE'])
    
    retryer = Retrying(
        stop=stop_after_attempt(retry_max),
        wait=wait_fixed(2),
        reraise=True,
    )

    for attempt in retryer:
        with attempt:
            attempt_start = time.time()
            logger.info(f"Attempt {attempt.retry_state.attempt_number} started",
                       attempt_time=attempt_start - start_time)
            
            try:
                # COMPREHENSIVE SUBPROCESS EXECUTION WITH DETAILED MONITORING
                logger.info("Subprocess execution started",
                           timeout=timeout,
                           working_directory=os.getcwd(),
                           python_executable=sys.executable)
                
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    env=cli_env,
                    cwd=os.getcwd()
                )
                
                logger.info("Process spawned",
                           process_id=process.pid,
                           creation_time=time.time())
                
                try:
                    # Monitor subprocess with timeout
                    stdout, stderr = process.communicate(timeout=timeout)
                    elapsed = time.time() - attempt_start
                    
                    logger.info("=== SUBPROCESS LIFECYCLE COMPLETE ===")
                    logger.info("Process completion",
                               process_id=process.pid,
                               elapsed_time=elapsed,
                               return_code=process.returncode,
                               stdout_length=len(stdout) if stdout else 0,
                               stderr_length=len(stderr) if stderr else 0)
                    
                    # COMPREHENSIVE OUTPUT ANALYSIS
                    combined_output = (stdout or "") + (stderr or "")
                    
                    if stdout:
                        logger.info("STDOUT ANALYSIS (first 1000 chars)",
                                   stdout_preview=stdout[:1000] + ("..." if len(stdout) > 1000 else ""))
                    if stderr:
                        logger.info("STDERR ANALYSIS (first 1000 chars)",
                                   stderr_preview=stderr[:1000] + ("..." if len(stderr) > 1000 else ""))
                    
                    # ERROR ANALYSIS BY DOMAIN
                    if process.returncode != 0:
                        logger.error("=== CLI FAILURE ANALYSIS ===")
                        logger.error("Return code analysis", returncode=process.returncode)
                        
                        # Browser initialization failures
                        if "browser" in stderr.lower() or "playwright" in stderr.lower():
                            logger.error("BROWSER DOMAIN FAILURE detected", browser_error=True)
                        elif "chromium" in stderr.lower() or "chrome" in stderr.lower():
                            logger.error("CHROMIUM DOMAIN FAILURE detected", chromium_error=True)
                        
                        # LLM API failures
                        if "api" in stderr.lower() or "openrouter" in stderr.lower():
                            logger.error("LLM API DOMAIN FAILURE detected", api_error=True)
                        elif "key" in stderr.lower() or "auth" in stderr.lower():
                            logger.error("API AUTH DOMAIN FAILURE detected", api_auth_error=True)
                        
                        # Authentication failures
                        if "auth" in stderr.lower() or "login" in stderr.lower():
                            logger.error("AUTHENTICATION DOMAIN FAILURE detected", auth_error=True)
                        elif "session" in stderr.lower() or "token" in stderr.lower():
                            logger.error("SESSION MANAGEMENT DOMAIN FAILURE detected", session_error=True)
                        
                        logger.error("CLI failure details",
                                   returncode=process.returncode,
                                   stderr=stderr[:1000],
                                   combined_output_preview=combined_output[:500])
                        
                        raise subprocess.CalledProcessError(
                            process.returncode, cmd, output=combined_output, stderr=stderr
                        )

                    logger.info("=== CLI SUCCESS ANALYSIS ===")
                    logger.info("Saik0s CLI succeeded",
                               output_length=len(combined_output),
                               success_time=time.time() - start_time)
                    return combined_output

                except subprocess.TimeoutExpired as e:
                    elapsed = time.time() - attempt_start
                    logger.error("=== CLI TIMEOUT ANALYSIS ===")
                    logger.error("Subprocess timeout",
                                timeout=timeout,
                                elapsed=elapsed,
                                process_id=process.pid)
                    
                    # Attempt to get partial output if any
                    try:
                        stdout_partial, stderr_partial = process.communicate(timeout=5)
                        logger.error("Partial output after timeout",
                                   stdout_partial_length=len(stdout_partial) if stdout_partial else 0,
                                   stderr_partial_length=len(stderr_partial) if stderr_partial else 0,
                                   stdout_preview=stdout_partial[:500] if stdout_partial else "",
                                   stderr_preview=stderr_partial[:500] if stderr_partial else "")
                    except:
                        logger.error("Could not retrieve partial output after timeout")
                    
                    # Kill process if still running
                    try:
                        process.kill()
                        process.wait(timeout=5)
                    except:
                        logger.error("Failed to kill process after timeout")
                    
                    raise TimeoutError(f"Saik0s CLI timed out after {timeout}s") from e

            except Exception as e:
                elapsed = time.time() - attempt_start
                logger.error("=== UNEXPECTED ERROR ANALYSIS ===")
                logger.error("Subprocess execution error",
                           error_type=type(e).__name__,
                           error_message=str(e),
                           elapsed=elapsed)
                raise

    logger.error("=== RETRY EXHAUSTION ===")
    logger.error("All retry attempts failed",
                total_elapsed=time.time() - start_time,
                max_retries=retry_max)
    raise RuntimeError("Unexpected: Saik0s CLI retry loop completed without return or raise.")

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
        logger.info("run_browser_agent called", task=task)
        result_text = _run_saik0s_cli(task)
        if not result_text.strip():
            logger.error("Saik0s CLI returned empty output")
            return {
                "ok": False,
                "result_text": result_text,
                "error": "Browser agent returned no output",
            }
        return {
            "ok": True,
            "result_text": result_text,
        }
    except (subprocess.CalledProcessError, TimeoutError, RetryError) as e:
        logger.error("Browser agent execution failed", error=str(e))
        return {
            "ok": False,
            "result_text": getattr(e, "output", ""),
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
