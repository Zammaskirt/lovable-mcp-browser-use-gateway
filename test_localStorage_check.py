#!/usr/bin/env python
"""Check if localStorage is being used by the page."""

import asyncio
import json
from playwright.async_api import async_playwright

async def test_localStorage():
    """Test if localStorage is being used."""
    
    # Prepare storage state
    with open('auth.json') as f:
        auth_data = json.load(f)

    if isinstance(auth_data, list):
        cookies = auth_data
        origins = []
    else:
        cookies = auth_data.get('cookies', [])
        origins = auth_data.get('origins', [])
    
    print(f"Cookies: {len(cookies)}")
    print(f"Origins: {len(origins)}")
    print()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        
        # Add cookies
        await context.add_cookies(cookies)
        print("✅ Cookies added")
        
        # Add localStorage
        for origin in origins:
            origin_url = origin.get('origin')
            local_storage = origin.get('localStorage', [])
            if origin_url and local_storage:
                print(f"Setting localStorage for {origin_url}...")
                page = await context.new_page()
                await page.goto(origin_url, wait_until='domcontentloaded', timeout=10000)
                for item in local_storage:
                    try:
                        await page.evaluate(f"localStorage.setItem('{item['name']}', {json.dumps(item['value'])})")
                    except Exception as e:
                        print(f"  Failed to set {item['name']}: {e}")
                await page.close()
        
        print("✅ localStorage added")
        print()
        
        # Now navigate to lovable.dev and check if we're logged in
        page = await context.new_page()
        await page.goto("https://lovable.dev", wait_until="load", timeout=30000)
        
        # Check localStorage
        print("Checking localStorage on lovable.dev...")
        local_storage_data = await page.evaluate("() => JSON.stringify(localStorage)")
        local_storage_dict = json.loads(local_storage_data)
        print(f"localStorage items: {len(local_storage_dict)}")
        for key in list(local_storage_dict.keys())[:5]:
            print(f"  - {key}")
        
        # Check if we're logged in
        print()
        print("Checking login status...")
        content = await page.content()
        if 'Log in' in content:
            print("❌ Found 'Log in' button - NOT logged in")
        elif 'alex' in content or 'account' in content.lower():
            print("✅ Found user info - LOGGED IN")
        else:
            print("⚠️  Could not determine login status")
        
        await browser.close()

asyncio.run(test_localStorage())

