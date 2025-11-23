#!/usr/bin/env python3
"""
Test script to debug the CLI subprocess call with enhanced diagnostics.
"""

import os
import sys
import time
import traceback
from typing import Any, Callable

# Add src to path
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

from agent_runner import run_browser_agent  # type: ignore[import-untyped]

# Type hint for the imported function
run_browser_agent: Callable[[str], dict[str, Any]]


def test_cli_with_diagnostics() -> None:
    """Test the CLI with comprehensive diagnostics."""
    print("=== STARTING CLI DIAGNOSTIC TEST ===")
    print(f"Working directory: {os.getcwd()}")
    print(f"Python executable: {sys.executable}")
    print(f"Environment variables check:")

    # Check key environment variables
    key_vars: list[str] = [
        'MCP_LLM_OPENROUTER_API_KEY',
        'MCP_AUTH_STATE_PATH',
        'MCP_LLM_PROVIDER',
        'MCP_BROWSER_HEADLESS'
    ]

    for var in key_vars:
        value = os.getenv(var)
        if var == 'MCP_LLM_OPENROUTER_API_KEY':
            print(f"  {var}: {'SET' if value and len(value) > 10 else 'MISSING/LENGTH_TOO_SHORT'}")
        else:
            print(f"  {var}: {value}")

    # Check auth file
    auth_path: str = os.getenv('MCP_AUTH_STATE_PATH', './auth.json')
    print(f"\nAuth file check:")
    print(f"  Path: {auth_path}")
    print(f"  Exists: {os.path.exists(auth_path)}")
    if os.path.exists(auth_path):
        print(f"  Size: {os.path.getsize(auth_path)} bytes")

    print(f"\n=== TESTING RUN_BROWSER_AGENT ===")
    start_time: float = time.time()

    try:
        result: dict[str, Any] = run_browser_agent("test")
        elapsed: float = time.time() - start_time
        print(f"\n=== TEST COMPLETED ===")
        print(f"Time elapsed: {elapsed:.1f}s")
        print(f"Result keys: {list(result.keys())}")
        print(f"Success: {result.get('ok', False)}")
        if not result.get('ok'):
            print(f"Error: {result.get('error', 'No error message')}")
        print(f"Output preview: {str(result.get('result_text', ''))[:200]}...")

    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n=== TEST FAILED ===")
        print(f"Time elapsed: {elapsed:.1f}s")
        print(f"Exception type: {type(e).__name__}")
        print(f"Exception message: {str(e)}")
        print(f"Traceback:")
        traceback.print_exc()


if __name__ == "__main__":
    test_cli_with_diagnostics()