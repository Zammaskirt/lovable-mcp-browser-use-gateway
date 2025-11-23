#!/usr/bin/env python
"""Check cookie expiration."""

import json
import time

data = json.load(open('auth.json'))
cookies = data.get('cookies', [])
now = time.time()

print("Cookie expiration status:")
for c in cookies:
    expires = c.get('expires', 0)
    days_left = (expires - now) / 86400
    print(f"  {c['name']}: expires in {days_left:.1f} days")

print()
print(f"Current time: {now}")
print(f"All cookies valid: {all((c.get('expires', 0) - now) > 0 for c in cookies)}")

