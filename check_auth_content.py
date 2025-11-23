#!/usr/bin/env python3
import json

data = json.load(open('auth.json'))
print(f'Cookies: {len(data.get("cookies", []))}')
print(f'Origins: {len(data.get("origins", []))}')
origins = data.get('origins', [])
print(f'localStorage items: {sum(len(o.get("localStorage", [])) for o in origins)}')

# Show first few cookies
cookies = data.get('cookies', [])
if cookies:
    print(f'\nFirst cookie: {cookies[0].get("name")} = {cookies[0].get("value")[:50]}...')
    
# Show origins
for origin in origins:
    print(f'\nOrigin: {origin.get("origin")}')
    ls = origin.get('localStorage', [])
    print(f'  localStorage items: {len(ls)}')
    for item in ls[:3]:
        print(f'    - {item.get("name")}')

