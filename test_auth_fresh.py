#!/usr/bin/env python
"""Test authentication with fresh browser context."""

import os
import sys

# Set environment variables before importing
os.environ['MCP_LLM_OPENROUTER_API_KEY'] = os.getenv('MCP_LLM_OPENROUTER_API_KEY', '')
os.environ['MCP_AUTH_STATE_PATH'] = './auth.json'
os.environ['BROWSER_USE_STORAGE_STATE'] = os.path.abspath('./auth.json')

# Force reload of the module to get fresh context
if 'mcp_server_browser_use.run_agents' in sys.modules:
    del sys.modules['mcp_server_browser_use.run_agents']

from src.agent_runner import run_browser_agent

print("=" * 80)
print("TESTING AUTHENTICATION WITH FRESH CONTEXT")
print("=" * 80)
print()

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

