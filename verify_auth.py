#!/usr/bin/env python3
"""Verify auth.json file structure and content."""

import json
import os

auth_path = "./auth.json"

if not os.path.exists(auth_path):
    print(f"ERROR: Auth file not found at {auth_path}")
    exit(1)

try:
    with open(auth_path, 'r') as f:
        data = json.load(f)
    
    print("[OK] Auth file is valid JSON")
    print(f"\nAuth file structure:")
    print(f"  - File size: {os.path.getsize(auth_path)} bytes")
    print(f"  - Top-level keys: {list(data.keys())}")

    if 'cookies' in data:
        cookies = data['cookies']
        print(f"\n[OK] Cookies section:")
        print(f"  - Total cookies: {len(cookies)}")
        if cookies:
            first_cookie = cookies[0]
            print(f"  - First cookie name: {first_cookie.get('name', 'N/A')}")
            print(f"  - First cookie domain: {first_cookie.get('domain', 'N/A')}")
            print(f"  - First cookie path: {first_cookie.get('path', 'N/A')}")
            print(f"  - First cookie has value: {'value' in first_cookie}")

    if 'origins' in data:
        origins = data['origins']
        print(f"\n[OK] Origins section:")
        print(f"  - Total origins: {len(origins)}")
        if origins:
            first_origin = origins[0]
            print(f"  - First origin URL: {first_origin.get('origin', 'N/A')}")

    print("\n[OK] Auth file is valid and contains authentication data")
    
except json.JSONDecodeError as e:
    print(f"ERROR: Auth file is not valid JSON: {e}")
    exit(1)
except Exception as e:
    print(f"ERROR: {e}")
    exit(1)

