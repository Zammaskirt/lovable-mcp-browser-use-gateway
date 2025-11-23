#!/usr/bin/env python
"""Check the signature of run_browser_agent function."""

from mcp_server_browser_use.run_agents import run_browser_agent
import inspect

sig = inspect.signature(run_browser_agent)
print("run_browser_agent parameters:")
print("-" * 80)
for name, param in sig.parameters.items():
    annotation = param.annotation if param.annotation != inspect.Parameter.empty else "Any"
    default = f" = {param.default}" if param.default != inspect.Parameter.empty else ""
    print(f"  {name}: {annotation}{default}")

print("\n" + "=" * 80)
print("Total parameters:", len(sig.parameters))
print("=" * 80)

# Check if storage_state is in the parameters
if 'storage_state' in sig.parameters:
    print("\n✅ storage_state parameter FOUND!")
else:
    print("\n❌ storage_state parameter NOT FOUND!")
    print("\nAvailable parameters:")
    for name in sig.parameters.keys():
        print(f"  - {name}")

