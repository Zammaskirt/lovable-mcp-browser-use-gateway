#!/usr/bin/env python
"""Check if cookies are stored in the context."""

import asyncio
import json
from playwright.async_api import async_playwright

async def test_cookies():
    """Test if cookies are stored in the context."""
    
    # Prepare cookies
    auth_data = json.load(open('auth.json'))
    cookies = auth_data.get('cookies', [])
    
    print(f"Cookies to add: {len(cookies)}")
    for c in cookies:
        print(f"  - {c['name']} (domain: {c['domain']})")
    print()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        # Create context with cookies
        context = await browser.new_context()
        
        # Add cookies
        print("Adding cookies to context...")
        await context.add_cookies(cookies)
        print("✅ Cookies added")
        print()
        
        # Check cookies in context
        print("Cookies in context:")
        stored_cookies = await context.cookies()
        print(f"  Total: {len(stored_cookies)}")
        for c in stored_cookies:
            print(f"  - {c['name']} (domain: {c['domain']})")
        print()
        
        # Create page and navigate
        page = await context.new_page()
        await page.goto("https://lovable.dev", wait_until="load", timeout=30000)
        
        # Check cookies after navigation
        print("Cookies after navigation:")
        stored_cookies = await context.cookies()
        print(f"  Total: {len(stored_cookies)}")
        for c in stored_cookies:
            print(f"  - {c['name']} (domain: {c['domain']})")
        
        await browser.close()

asyncio.run(test_cookies())

