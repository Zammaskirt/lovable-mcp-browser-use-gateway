#!/usr/bin/env python
"""Check auth.json format."""

import json

with open('auth.json') as f:
    data = json.load(f)

print(f"Type: {type(data)}")
if isinstance(data, dict):
    print(f"Keys: {list(data.keys())}")
    print(f"Cookies: {len(data.get('cookies', []))}")
    print(f"Origins: {len(data.get('origins', []))}")
elif isinstance(data, list):
    print(f"Length: {len(data)}")
    if data:
        print(f"First item type: {type(data[0])}")
        if isinstance(data[0], dict):
            print(f"First item keys: {list(data[0].keys())}")

