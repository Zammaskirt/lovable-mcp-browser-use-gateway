"""
Saik0s delegation layer for browser automation.

This module directly calls the mcp_server_browser_use.run_agents.run_browser_agent function
to execute browser automation tasks. All environment variables are read from the process environment.
"""

import asyncio
import os
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
    """Run browser agent using the mcp_server_browser_use Python API directly."""

    start_time = time.time()
    config = _get_agent_config()
    timeout = int(os.getenv("MCP_AGENT_TIMEOUT_SEC", "600"))
    retry_max = max(1, config["retry_max"])

    # Load environment variables from .env file if it exists
    # In production, environment variables are set via Fly.io secrets
    load_dotenv(dotenv_path='.env', override=False)

    # Validate and set environment variables
    openrouter_key = os.getenv('MCP_LLM_OPENROUTER_API_KEY', '')
    auth_path = os.getenv('MCP_AUTH_STATE_PATH', './auth.json')

    # Set critical environment variables
    os.environ['OPENAI_API_KEY'] = openrouter_key
    os.environ['PATIENT'] = 'true'
    os.environ['BROWSER_USE_STORAGE_STATE'] = auth_path

    # COMPREHENSIVE DIAGNOSTICS: Environment validation
    logger.info("=== BROWSER AGENT EXECUTION START ===")
    logger.info("Task execution started", task=task, timestamp=time.time())

    # Environment validation - check for required variables
    logger.info("ENVIRONMENT VALIDATION:")
    env_after_load = os.getenv('MCP_LLM_OPENROUTER_API_KEY', '')
    has_api_key = bool(env_after_load and len(env_after_load) > 10)

    if not has_api_key:
        logger.error("CRITICAL: MCP_LLM_OPENROUTER_API_KEY not set or too short",
                    api_key_length=len(env_after_load) if env_after_load else 0)

    logger.info("Environment after .env load",
               api_key_length_after_load=len(env_after_load) if env_after_load else 0,
               has_key_after_load=has_api_key)

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

    # Direct Python API execution
    logger.info("DIRECT PYTHON API EXECUTION:")
    logger.info("Using mcp_server_browser_use.run_agents.run_browser_agent")

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
                # Import and call the run_browser_agent function directly
                from mcp_server_browser_use.run_agents import run_browser_agent

                logger.info("Calling run_browser_agent directly",
                           timeout=timeout,
                           task=task)

                # Get configuration from environment
                llm_provider = os.getenv('MCP_LLM_PROVIDER', 'openrouter')
                llm_model_name = os.getenv('MCP_LLM_MODEL_NAME', 'openai/gpt-5-mini')
                llm_num_ctx = int(os.getenv('MCP_LLM_NUM_CTX', '8000'))
                llm_temperature = float(os.getenv('MCP_LLM_TEMPERATURE', '0.2'))
                llm_base_url = os.getenv('MCP_LLM_BASE_URL', 'https://openrouter.ai/api/v1')
                llm_api_key = os.getenv('MCP_LLM_OPENROUTER_API_KEY', '')

                browser_headless = os.getenv('MCP_BROWSER_HEADLESS', 'true').lower() == 'true'
                browser_width = int(os.getenv('MCP_BROWSER_WINDOW_WIDTH', '1440'))
                browser_height = int(os.getenv('MCP_BROWSER_WINDOW_HEIGHT', '1080'))

                # Create temporary directories for agent history and traces
                import tempfile
                temp_dir = tempfile.gettempdir()
                agent_history_dir = os.path.join(temp_dir, 'browser_agent_history')
                os.makedirs(agent_history_dir, exist_ok=True)

                # Call the function directly with all required parameters
                result = asyncio.run(asyncio.wait_for(
                    run_browser_agent(
                        agent_type='org',
                        llm_provider=llm_provider,
                        llm_model_name=llm_model_name,
                        llm_num_ctx=llm_num_ctx,
                        llm_temperature=llm_temperature,
                        llm_base_url=llm_base_url,
                        llm_api_key=llm_api_key,
                        use_own_browser=False,
                        keep_browser_open=False,
                        headless=browser_headless,
                        disable_security=False,
                        window_w=browser_width,
                        window_h=browser_height,
                        save_recording_path=None,
                        save_agent_history_path=agent_history_dir,
                        save_trace_path=None,
                        enable_recording=False,
                        task=task,
                        add_infos='',
                        max_steps=100,
                        use_vision=True,
                        max_actions_per_step=10,
                        tool_calling_method='auto',
                        chrome_cdp=None,
                        max_input_tokens=8000
                    ),
                    timeout=timeout
                ))

                elapsed = time.time() - attempt_start

                logger.info("=== EXECUTION COMPLETE ===")
                logger.info("Browser agent execution succeeded",
                           elapsed_time=elapsed,
                           result_type=type(result).__name__)

                # Convert result to string if needed
                result_text = str(result) if result else ""

                logger.info("=== EXECUTION SUCCESS ===")
                logger.info("Browser agent succeeded",
                           output_length=len(result_text),
                           success_time=time.time() - start_time)
                return result_text

            except asyncio.TimeoutError as e:
                elapsed = time.time() - attempt_start
                logger.error("=== EXECUTION TIMEOUT ===")
                logger.error("Browser agent timeout",
                            timeout=timeout,
                            elapsed=elapsed)
                raise TimeoutError(f"Browser agent timed out after {timeout}s") from e

            except Exception as e:
                elapsed = time.time() - attempt_start
                logger.error("=== EXECUTION ERROR ===")
                logger.error("Browser agent execution error",
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
            logger.error("Saik0s CLI returned empty output - check environment variables",
                        api_key_set=bool(os.getenv('MCP_LLM_OPENROUTER_API_KEY')),
                        auth_path=os.getenv('MCP_AUTH_STATE_PATH'))
            return {
                "ok": False,
                "result_text": result_text,
                "error": "Browser agent returned no output - check MCP_LLM_OPENROUTER_API_KEY and MCP_AUTH_STATE_PATH",
            }
        return {
            "ok": True,
            "result_text": result_text,
        }
    except (TimeoutError, RetryError) as e:
        logger.error("Browser agent execution failed", error=str(e))
        return {
            "ok": False,
            "result_text": "",
            "error": str(e),
        }
    except Exception as e:
        logger.error("Browser agent execution failed with unexpected error", error=str(e), error_type=type(e).__name__)
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
