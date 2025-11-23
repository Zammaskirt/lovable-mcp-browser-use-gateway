#!/usr/bin/env python
"""Search for storage_state usage in browser-use library."""

import os
import re
from pathlib import Path

browser_use_path = Path(".venv/Lib/site-packages/browser_use")

print("Searching for 'storage_state' in browser-use library...")
print("=" * 80)

found_files = []
for py_file in browser_use_path.rglob("*.py"):
    try:
        with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            if 'storage_state' in content.lower():
                found_files.append(py_file)
                print(f"\n✅ Found in: {py_file.relative_to(browser_use_path)}")
                
                # Find lines with storage_state
                for i, line in enumerate(content.split('\n'), 1):
                    if 'storage_state' in line.lower():
                        print(f"   Line {i}: {line.strip()[:100]}")
    except Exception as e:
        pass

print("\n" + "=" * 80)
print(f"Total files with 'storage_state': {len(found_files)}")

