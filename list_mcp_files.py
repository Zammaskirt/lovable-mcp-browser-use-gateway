#!/usr/bin/env python
"""List files in mcp_server_browser_use package."""

from pathlib import Path

mcp_path = Path(".venv/Lib/site-packages/mcp_server_browser_use")

print("Files in mcp_server_browser_use:")
print("=" * 80)
for py_file in sorted(mcp_path.rglob("*.py")):
    print(f"  {py_file.relative_to(mcp_path)}")

print("\n" + "=" * 80)
print("Searching for 'storage_state' in mcp_server_browser_use...")
print("=" * 80)

for py_file in mcp_path.rglob("*.py"):
    try:
        with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            if 'storage_state' in content.lower():
                print(f"\n✅ Found in: {py_file.relative_to(mcp_path)}")
                for i, line in enumerate(content.split('\n'), 1):
                    if 'storage_state' in line.lower():
                        print(f"   Line {i}: {line.strip()[:100]}")
    except Exception as e:
        pass

