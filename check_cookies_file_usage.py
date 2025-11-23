#!/usr/bin/env python
"""Check how cookies_file is used in BrowserContextConfig."""

import inspect
from browser_use.browser.context import BrowserContextConfig

# Get the source code
source = inspect.getsource(BrowserContextConfig)
print("BrowserContextConfig source code:")
print("=" * 80)
print(source[:2000])
print("\n... (truncated)")

