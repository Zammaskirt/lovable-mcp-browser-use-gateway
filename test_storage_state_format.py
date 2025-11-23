#!/usr/bin/env python3
"""Test what context.storage_state() returns."""

import asyncio
import json
from playwright.async_api import async_playwright

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Navigate to a page
        await page.goto("https://example.com")
        
        # Set some localStorage
        await page.evaluate("() => localStorage.setItem('test_key', 'test_value')")
        
        # Get storage state
        storage_state = await context.storage_state()
        
        print(f"Type: {type(storage_state)}")
        print(f"Is dict: {isinstance(storage_state, dict)}")
        print(f"Is list: {isinstance(storage_state, list)}")
        
        if isinstance(storage_state, dict):
            print(f"Keys: {list(storage_state.keys())}")
            print(f"Has cookies: {'cookies' in storage_state}")
            print(f"Has origins: {'origins' in storage_state}")
        elif isinstance(storage_state, list):
            print(f"Length: {len(storage_state)}")
            if storage_state:
                print(f"First item keys: {list(storage_state[0].keys())}")
        
        print(f"\nFull content (first 500 chars):")
        print(json.dumps(storage_state, indent=2)[:500])
        
        await browser.close()

asyncio.run(test())

