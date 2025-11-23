#!/usr/bin/env python3
"""Check cookie expiration dates."""

import json
from datetime import datetime

data = json.load(open('auth.json'))
cookies = data.get('cookies', [])

print("Session cookies:")
for cookie in cookies:
    if 'lovable-session-id' in cookie.get('name', ''):
        expires = cookie.get('expires', 0)
        exp_date = datetime.fromtimestamp(expires)
        now = datetime.now()
        days_left = (exp_date - now).days
        print(f"  {cookie['name']}: expires {exp_date} ({days_left} days left)")

print("\nAll cookies:")
for cookie in cookies:
    expires = cookie.get('expires', 0)
    exp_date = datetime.fromtimestamp(expires)
    now = datetime.now()
    days_left = (exp_date - now).days
    print(f"  {cookie['name']}: {days_left} days left")

