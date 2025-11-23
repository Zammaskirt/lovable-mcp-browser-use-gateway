#!/usr/bin/env python3
"""Test loading storage state directly with Playwright."""

import asyncio
import json
import os
from playwright.async_api import async_playwright

async def test():
    auth_path = os.path.abspath('./auth.json')
    print(f"Auth path: {auth_path}")

    # Load auth.json to check format
    with open(auth_path, 'r') as f:
        data = json.load(f)

    print(f"Auth.json type: {type(data).__name__}")
    print(f"Cookies: {len(data.get('cookies', []))}")
    print(f"Origins: {len(data.get('origins', []))}")

    # Create browser context with storage_state parameter
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # Use storage_state parameter directly
        context = await browser.new_context(storage_state=auth_path)
        page = await context.new_page()

        # Navigate to Lovable
        print("\nNavigating to https://lovable.dev...")
        await page.goto("https://lovable.dev", wait_until="domcontentloaded", timeout=30000)

        # Get cookies from context
        cookies = await context.cookies()
        print(f"\nCookies in context: {len(cookies)}")
        for cookie in cookies:
            if 'lovable-session-id' in cookie.get('name', ''):
                print(f"  - {cookie['name']}: {cookie['value'][:50]}...")

        # Get localStorage
        ls_keys = await page.evaluate("() => Object.keys(localStorage)")
        print(f"\nlocalStorage keys: {ls_keys}")

        # Check for user info
        user_id = await page.evaluate("() => localStorage.getItem('user_id')")
        print(f"User ID from localStorage: {user_id}")

        # Check page content
        page_content = await page.content()
        has_login_button = "Log in" in page_content
        print(f"\nHas 'Log in' button: {has_login_button}")

        # Check for user avatar or profile
        has_avatar = "avatar" in page_content.lower() or "profile" in page_content.lower()
        print(f"Has avatar/profile: {has_avatar}")

        # Check for user name in page
        has_alex = "alex" in page_content.lower()
        print(f"Has 'alex' in page: {has_alex}")

        await browser.close()

asyncio.run(test())

