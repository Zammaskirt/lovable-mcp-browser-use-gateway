#!/usr/bin/env python3
import base64
import subprocess
import sys
import os

# Read auth.json
with open('auth.json', 'rb') as f:
    auth_json_bytes = f.read()

# Encode to base64
auth_json_b64 = base64.b64encode(auth_json_bytes).decode('utf-8')

print(f"Setting AUTH_JSON_B64 secret ({len(auth_json_b64)} characters)...")

# Use flyctl with GraphQL API to set the secret
# First, get the app ID
cmd_get_app = ['flyctl', 'info', '--app', 'lovable-mcp-gateway', '--json']
result = subprocess.run(cmd_get_app, capture_output=True, text=True)

if result.returncode != 0:
    print("Failed to get app info")
    print(result.stderr)
    sys.exit(1)

import json
app_info = json.loads(result.stdout)
app_id = app_info.get('ID')

if not app_id:
    print("Could not find app ID")
    sys.exit(1)

print(f"App ID: {app_id}")

# Now set the secret using flyctl with the GraphQL mutation
# Create a temporary file with the secret value
with open('secret_input.txt', 'w') as f:
    f.write(f'AUTH_JSON_B64={auth_json_b64}')

# Read it back
with open('secret_input.txt', 'r') as f:
    secret_input = f.read()

# Try to set using flyctl
cmd = ['flyctl', 'secrets', 'set', '--app', 'lovable-mcp-gateway']

# Append the secret as an argument
cmd.append(secret_input)

try:
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    
    if result.returncode == 0:
        print("✓ AUTH_JSON_B64 secret set successfully")
        print(result.stdout)
    else:
        print("✗ Failed to set secret")
        print("STDERR:", result.stderr)
        sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

