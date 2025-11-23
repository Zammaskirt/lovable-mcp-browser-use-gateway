#!/usr/bin/env python
"""Check BrowserContextConfig parameters."""

from browser_use.browser.context import BrowserContextConfig
import inspect

sig = inspect.signature(BrowserContextConfig.__init__)
print("BrowserContextConfig parameters:")
print("-" * 80)
for name, param in sig.parameters.items():
    if name != 'self':
        annotation = param.annotation if param.annotation != inspect.Parameter.empty else "Any"
        default = f" = {param.default}" if param.default != inspect.Parameter.empty else ""
        print(f"  {name}: {annotation}{default}")

print("\n" + "=" * 80)
print("Checking if 'storage_state' is in parameters...")
if 'storage_state' in sig.parameters:
    print("✅ storage_state parameter FOUND!")
else:
    print("❌ storage_state parameter NOT FOUND!")

