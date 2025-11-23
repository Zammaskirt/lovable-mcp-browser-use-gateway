#!/usr/bin/env python3
import base64
import subprocess
import sys

# Read auth.json
with open('auth.json', 'rb') as f:
    auth_json_bytes = f.read()

# Encode to base64
auth_json_b64 = base64.b64encode(auth_json_bytes).decode('utf-8')

# Set the secret using flyctl
cmd = [
    'flyctl', 'secrets', 'set',
    f'AUTH_JSON_B64={auth_json_b64}',
    '--app', 'lovable-mcp-gateway'
]

print(f"Setting AUTH_JSON_B64 secret ({len(auth_json_b64)} characters)...")
result = subprocess.run(cmd, capture_output=True, text=True)

if result.returncode == 0:
    print("✓ AUTH_JSON_B64 secret set successfully")
    print(result.stdout)
else:
    print("✗ Failed to set secret")
    print(result.stderr)
    sys.exit(1)

