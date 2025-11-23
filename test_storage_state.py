#!/usr/bin/env python3
import asyncio
import json
from playwright.async_api import async_playwright

async def test_storage_state():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Navigate to a page
        await page.goto("https://example.com")
        
        # Get storage state
        storage_state = await context.storage_state()
        
        print(f"Type: {type(storage_state)}")
        print(f"Keys: {list(storage_state.keys()) if isinstance(storage_state, dict) else 'N/A'}")
        print(f"Content: {json.dumps(storage_state, indent=2)[:500]}")
        
        await browser.close()

asyncio.run(test_storage_state())

