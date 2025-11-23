#!/usr/bin/env python3
"""Test if cookies are being loaded into the browser context."""

import asyncio
import json
import os
from playwright.async_api import async_playwright

async def test_cookies():
    auth_path = os.path.abspath('./auth.json')
    print(f"Auth path: {auth_path}")
    print(f"Auth exists: {os.path.exists(auth_path)}")
    
    # Load auth.json
    with open(auth_path, 'r') as f:
        data = json.load(f)
    
    print(f"Auth.json type: {type(data).__name__}")
    print(f"Cookies in file: {len(data.get('cookies', []))}")
    print(f"Origins in file: {len(data.get('origins', []))}")
    
    # Create browser context with cookies
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(storage_state=auth_path)
        page = await context.new_page()
        
        # Navigate to Lovable
        await page.goto("https://lovable.dev", wait_until="domcontentloaded", timeout=30000)
        
        # Get cookies from context
        cookies = await context.cookies()
        print(f"\nCookies loaded in context: {len(cookies)}")
        for cookie in cookies[:3]:
            print(f"  - {cookie['name']}: {cookie['value'][:50]}...")
        
        # Get localStorage
        ls_data = await page.evaluate("() => JSON.stringify(localStorage)")
        print(f"\nlocalStorage data: {ls_data[:200]}...")
        
        # Check if user is logged in
        user_id = await page.evaluate("() => localStorage.getItem('user_id')")
        print(f"\nUser ID from localStorage: {user_id}")
        
        # Check page content
        login_button = await page.query_selector('button:has-text("Log in")')
        print(f"Login button found: {login_button is not None}")
        
        await browser.close()

asyncio.run(test_cookies())

