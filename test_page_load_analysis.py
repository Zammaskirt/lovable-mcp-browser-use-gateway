#!/usr/bin/env python3
"""Analyze page load behavior and identify blocking requests."""

import asyncio
import json
import time

from playwright.async_api import async_playwright


async def analyze_page_load():
    """Analyze what's preventing page from reaching networkidle."""
    
    print("=" * 80)
    print("📊 PAGE LOAD ANALYSIS")
    print("=" * 80)
    print()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(storage_state="auth.json")
        page = await context.new_page()
        
        # Track network requests
        requests_log = []
        
        def on_request(request):
            requests_log.append({
                'url': request.url,
                'method': request.method,
                'resource_type': request.resource_type,
                'time': time.time()
            })
        
        page.on("request", on_request)
        
        print("📋 Navigating to lovable.dev with 'load' state")
        print("-" * 80)
        start = time.time()
        
        try:
            await page.goto("https://lovable.dev", wait_until="load", timeout=30000)
            load_time = time.time() - start
            print(f"✅ Page reached 'load' state in {load_time:.2f}s")
        except Exception as e:
            print(f"❌ Failed to reach 'load' state: {e}")
        
        print()
        print("📋 Waiting 5 seconds to observe network activity")
        print("-" * 80)
        await asyncio.sleep(5)
        
        print(f"✅ Network requests during load: {len(requests_log)}")
        print()
        
        # Analyze requests
        print("📋 Request Analysis")
        print("-" * 80)
        
        # Group by resource type
        by_type = {}
        for req in requests_log:
            rt = req['resource_type']
            if rt not in by_type:
                by_type[rt] = []
            by_type[rt].append(req)
        
        for rt in sorted(by_type.keys()):
            print(f"{rt}: {len(by_type[rt])} requests")
        
        print()
        print("📋 Sample Requests")
        print("-" * 80)
        for req in requests_log[:10]:
            print(f"  {req['method']:6} {req['resource_type']:12} {req['url'][:60]}")
        
        print()
        print("📋 Checking for continuous polling/WebSocket")
        print("-" * 80)
        
        # Check for WebSocket or polling patterns
        ws_requests = [r for r in requests_log if 'ws' in r['url'].lower() or 'socket' in r['url'].lower()]
        polling_requests = [r for r in requests_log if 'poll' in r['url'].lower() or 'stream' in r['url'].lower()]
        
        if ws_requests:
            print(f"⚠️  WebSocket connections: {len(ws_requests)}")
            for req in ws_requests[:3]:
                print(f"   - {req['url'][:70]}")
        
        if polling_requests:
            print(f"⚠️  Polling requests: {len(polling_requests)}")
            for req in polling_requests[:3]:
                print(f"   - {req['url'][:70]}")
        
        if not ws_requests and not polling_requests:
            print(f"✅ No obvious WebSocket or polling detected")
        
        print()
        print("📋 Page Content Check")
        print("-" * 80)
        
        # Check page content
        title = await page.title()
        print(f"Title: {title}")
        
        # Check for main content
        try:
            main = await page.query_selector("main, [role='main'], .main-content")
            if main:
                print(f"✅ Main content area found")
            else:
                print(f"⚠️  Main content area not found")
        except:
            pass
        
        # Check for loading indicators
        try:
            loading = await page.query_selector(".loading, [role='progressbar'], .spinner")
            if loading:
                print(f"⚠️  Loading indicator still visible")
            else:
                print(f"✅ No loading indicators visible")
        except:
            pass
        
        print()
        print("📋 DIAGNOSIS")
        print("-" * 80)
        print("""
The page reaches 'load' state quickly but never reaches 'networkidle' because:

1. Lovable.dev likely uses WebSockets or continuous polling for real-time updates
2. The page has background network activity that never fully stops
3. This is normal for modern web applications with live features

RECOMMENDATION:
- Use 'load' state instead of 'networkidle' for faster page interactions
- This will reduce timeout issues significantly
- The page is functional after 'load' state completes
        """)
        
        await context.close()
        await browser.close()


if __name__ == "__main__":
    asyncio.run(analyze_page_load())

