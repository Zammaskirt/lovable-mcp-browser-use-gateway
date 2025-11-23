#!/usr/bin/env python
"""Test if environment variable is set."""

import os
import sys

# Import the module
from mcp_server_browser_use.run_agents import _prepare_cookies_file

# Set the environment variable
os.environ['BROWSER_USE_STORAGE_STATE'] = os.path.abspath('./auth.json')

print(f"BROWSER_USE_STORAGE_STATE={os.environ.get('BROWSER_USE_STORAGE_STATE')}")
print(f"File exists: {os.path.exists(os.environ.get('BROWSER_USE_STORAGE_STATE'))}")

# Test the function
cookies_file = _prepare_cookies_file(os.environ.get('BROWSER_USE_STORAGE_STATE'))
print(f"Prepared cookies file: {cookies_file}")
print(f"Prepared file exists: {os.path.exists(cookies_file)}")

# Check the content
import json
with open(cookies_file, 'r') as f:
    data = json.load(f)
    print(f"Cookies in file: {len(data)}")
    if isinstance(data, list):
        print("✅ File contains a list of cookies (correct format)")
    else:
        print(f"❌ File contains {type(data)} (incorrect format)")

