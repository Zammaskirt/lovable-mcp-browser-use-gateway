#!/usr/bin/env python
"""Verify that cookies are being sent to the server."""

import asyncio
import json
import os
from playwright.async_api import async_playwright

async def test_cookies():
    """Test if cookies are being sent to lovable.dev."""
    
    # Prepare cookies file
    auth_data = json.load(open('auth.json'))
    cookies = auth_data.get('cookies', [])
    
    # Create a temporary cookies file
    import tempfile
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    json.dump(cookies, temp_file)
    temp_file.close()
    
    print(f"Cookies file: {temp_file.name}")
    print(f"Cookies count: {len(cookies)}")
    print()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        # Create context with cookies
        context = await browser.new_context()
        
        # Manually add cookies
        print("Adding cookies to context...")
        await context.add_cookies(cookies)
        print(f"✅ Added {len(cookies)} cookies")
        print()
        
        # Create page
        page = await context.new_page()
        
        # Track cookies sent in requests
        cookies_sent = []
        
        def on_request(request):
            headers = request.headers
            if 'cookie' in headers:
                cookies_sent.append({
                    'url': request.url,
                    'cookie_header': headers['cookie'][:100]  # First 100 chars
                })
        
        page.on("request", on_request)
        
        # Navigate to lovable.dev
        print("Navigating to https://lovable.dev...")
        try:
            await page.goto("https://lovable.dev", wait_until="load", timeout=30000)
            print("✅ Page loaded")
        except Exception as e:
            print(f"❌ Failed to load: {e}")
        
        print()
        print(f"Requests with cookies: {len(cookies_sent)}")
        if cookies_sent:
            print(f"First request: {cookies_sent[0]['url']}")
            print(f"Cookie header: {cookies_sent[0]['cookie_header']}")
        
        # Check page content
        print()
        print("Checking page content...")
        content = await page.content()
        if 'Log in' in content:
            print("❌ Found 'Log in' button - NOT logged in")
        elif 'alex' in content or 'account' in content.lower():
            print("✅ Found user info - LOGGED IN")
        else:
            print("⚠️  Could not determine login status")
        
        await browser.close()

asyncio.run(test_cookies())

