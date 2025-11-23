#!/usr/bin/env python3
import base64
import subprocess
import json
import os

# Read auth.json
with open('auth.json', 'rb') as f:
    auth_json_bytes = f.read()

# Encode to base64
auth_json_b64 = base64.b64encode(auth_json_bytes).decode('utf-8')

print(f"Setting AUTH_JSON_B64 secret ({len(auth_json_b64)} characters)...")

# Get the FLY_API_TOKEN from flyctl
result = subprocess.run(['flyctl', 'auth', 'token'], capture_output=True, text=True)
if result.returncode != 0:
    print("Failed to get auth token")
    print(result.stderr)
    exit(1)

fly_api_token = result.stdout.strip()

# GraphQL mutation to set secret
mutation = """
mutation SetSecrets($input: SetSecretsInput!) {
  setSecrets(input: $input) {
    release {
      id
    }
  }
}
"""

variables = {
    "input": {
        "appId": "lovable-mcp-gateway",
        "secrets": [
            {
                "key": "AUTH_JSON_B64",
                "value": auth_json_b64
            }
        ]
    }
}

# Create the GraphQL request
graphql_request = {
    "query": mutation,
    "variables": variables
}

# Write to a file
with open('graphql_request.json', 'w') as f:
    json.dump(graphql_request, f)

# Use curl to send the request
cmd = [
    'curl',
    '-X', 'POST',
    'https://api.fly.io/graphql',
    '-H', f'Authorization: Bearer {fly_api_token}',
    '-H', 'Content-Type: application/json',
    '-d', '@graphql_request.json'
]

try:
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    
    if result.returncode == 0:
        response = json.loads(result.stdout)
        if 'errors' in response and response['errors']:
            print("✗ GraphQL error:")
            print(json.dumps(response['errors'], indent=2))
            exit(1)
        else:
            print("✓ AUTH_JSON_B64 secret set successfully")
            print(json.dumps(response, indent=2))
    else:
        print("✗ Failed to set secret")
        print("STDERR:", result.stderr)
        exit(1)
except Exception as e:
    print(f"Error: {e}")
    exit(1)

