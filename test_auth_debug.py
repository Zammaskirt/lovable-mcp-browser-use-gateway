#!/usr/bin/env python
"""Test authentication with debug output."""

import os
import sys
import logging

# Configure logging to show all messages
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)-8s] %(name)s: %(message)s'
)

# Set environment variables before importing
os.environ['MCP_LLM_OPENROUTER_API_KEY'] = os.getenv('MCP_LLM_OPENROUTER_API_KEY', '')
os.environ['MCP_AUTH_STATE_PATH'] = './auth.json'
os.environ['BROWSER_USE_STORAGE_STATE'] = os.path.abspath('./auth.json')

print("=" * 80)
print("TESTING AUTHENTICATION WITH DEBUG OUTPUT")
print("=" * 80)
print(f"BROWSER_USE_STORAGE_STATE={os.environ.get('BROWSER_USE_STORAGE_STATE')}")
print()

from src.agent_runner import run_browser_agent

task = "Navigate to https://lovable.dev and check if you are logged in. Report the current user or login status."

print(f"Task: {task}")
print()
print("Starting agent execution...")
print()

result = run_browser_agent(task)

print()
print("=" * 80)
print("EXECUTION COMPLETED")
print("=" * 80)
print()

if result['ok']:
    print("[SUCCESS] Task completed successfully!")
    print(f"Result: {result['result_text'][:500]}...")
else:
    print("[FAILED] Task failed!")
    print(f"Error: {result.get('error', 'Unknown error')}")

