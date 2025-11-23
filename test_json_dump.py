#!/usr/bin/env python3
"""Test if json.dump is working correctly."""

import json
import tempfile
import os

# Create a test storage state
storage_state = {
    "cookies": [
        {"name": "test", "value": "value", "domain": "example.com", "path": "/"}
    ],
    "origins": [
        {
            "origin": "https://example.com",
            "localStorage": [
                {"name": "key1", "value": "value1"}
            ]
        }
    ]
}

# Save to a temporary file
with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
    temp_path = f.name
    json.dump(storage_state, f, indent=2)

# Check the file
file_size = os.path.getsize(temp_path)
print(f"File size: {file_size} bytes")

# Read it back
with open(temp_path, 'r') as f:
    data = json.load(f)

print(f"Type: {type(data).__name__}")
print(f"Has cookies: {'cookies' in data}")
print(f"Has origins: {'origins' in data}")

# Clean up
os.remove(temp_path)

