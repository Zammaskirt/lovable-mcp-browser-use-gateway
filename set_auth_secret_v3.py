#!/usr/bin/env python3
import base64
import subprocess
import sys
import json

# Read auth.json
with open('auth.json', 'rb') as f:
    auth_json_bytes = f.read()

# Encode to base64
auth_json_b64 = base64.b64encode(auth_json_bytes).decode('utf-8')

print(f"Setting AUTH_JSON_B64 secret ({len(auth_json_b64)} characters)...")

# Create a JSON file with the secret
secrets_data = {
    'AUTH_JSON_B64': auth_json_b64
}

with open('secrets.json', 'w') as f:
    json.dump(secrets_data, f)

# Use flyctl to set secrets from JSON
cmd = ['flyctl', 'secrets', 'set', '--app', 'lovable-mcp-gateway', f'AUTH_JSON_B64={auth_json_b64}']

# Try with stdin
try:
    # Write to a file and read it back
    with open('secret_value.txt', 'w') as f:
        f.write(auth_json_b64)
    
    # Read it back and pass via stdin
    with open('secret_value.txt', 'r') as f:
        secret_value = f.read()
    
    # Use flyctl with the value
    cmd = ['flyctl', 'secrets', 'set', 'AUTH_JSON_B64', '--app', 'lovable-mcp-gateway']
    result = subprocess.run(cmd, input=secret_value, capture_output=True, text=True, timeout=30)
    
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

