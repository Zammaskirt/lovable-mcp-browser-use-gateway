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

# Write to a temporary file
temp_file = 'auth_secret_temp.txt'
with open(temp_file, 'w') as f:
    f.write(auth_json_b64)

print(f"Setting AUTH_JSON_B64 secret ({len(auth_json_b64)} characters)...")

# Use flyctl with the file content
# We'll use environment variable approach
os.environ['AUTH_JSON_B64'] = auth_json_b64

# Try using flyctl with stdin
cmd = ['flyctl', 'secrets', 'set', 'AUTH_JSON_B64', '--app', 'lovable-mcp-gateway']

try:
    result = subprocess.run(cmd, input=auth_json_b64, capture_output=True, text=True, timeout=30)
    
    if result.returncode == 0:
        print("✓ AUTH_JSON_B64 secret set successfully")
        print(result.stdout)
    else:
        print("✗ Failed to set secret")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        sys.exit(1)
finally:
    # Clean up
    if os.path.exists(temp_file):
        os.remove(temp_file)

