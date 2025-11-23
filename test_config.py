#!/usr/bin/env python3
import os
from dotenv import load_dotenv

load_dotenv()

print("Configuration Check:")
print(f"  MCP_AGENT_CONCURRENCY: {os.getenv('MCP_AGENT_CONCURRENCY')}")
print(f"  MCP_RATE_LIMIT_PER_MIN: {os.getenv('MCP_RATE_LIMIT_PER_MIN')}")
print(f"  MCP_AGENT_TIMEOUT_SEC: {os.getenv('MCP_AGENT_TIMEOUT_SEC')}")
print(f"  MCP_AUTH_STATE_PATH: {os.getenv('MCP_AUTH_STATE_PATH')}")
print(f"  MCP_BEARER_TOKEN: {os.getenv('MCP_BEARER_TOKEN')[:20]}...")
print(f"  MCP_LLM_OPENROUTER_API_KEY: {os.getenv('MCP_LLM_OPENROUTER_API_KEY')[:20]}...")

