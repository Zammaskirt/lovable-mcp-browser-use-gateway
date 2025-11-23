#!/usr/bin/env python3
"""Check JWT token in session cookie."""

import json
import base64
from datetime import datetime

data = json.load(open('auth.json'))
cookies = data.get('cookies', [])

# Find the session ID cookie
for cookie in cookies:
    if cookie.get('name') == 'lovable-session-id.id':
        token = cookie.get('value', '')
        print(f"Token: {token[:50]}...")
        
        # JWT tokens have 3 parts separated by dots
        parts = token.split('.')
        if len(parts) == 3:
            # Decode the payload (second part)
            payload = parts[1]
            # Add padding if necessary
            padding = 4 - len(payload) % 4
            if padding != 4:
                payload += '=' * padding
            
            try:
                decoded = base64.urlsafe_b64decode(payload)
                payload_data = json.loads(decoded)
                print(f"\nJWT Payload:")
                for key, value in payload_data.items():
                    if key == 'exp':
                        exp_date = datetime.fromtimestamp(value)
                        now = datetime.now()
                        print(f"  {key}: {value} ({exp_date}) - {(exp_date - now).total_seconds()} seconds left")
                    else:
                        print(f"  {key}: {value}")
            except Exception as e:
                print(f"Error decoding JWT: {e}")
        break

