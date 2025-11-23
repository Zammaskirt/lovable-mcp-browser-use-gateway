#!/usr/bin/env python
"""Check cookies domain."""

import json

data = json.load(open('auth.json'))
cookies = data.get('cookies', [])

print("Cookies by domain:")
for c in cookies:
    print(f"  {c.get('domain')}: {c.get('name')} (expires: {c.get('expires')})")

print("\nAll cookies have lovable.dev domain:", all(c.get('domain') == 'lovable.dev' for c in cookies))

