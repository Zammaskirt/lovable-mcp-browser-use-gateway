#!/usr/bin/env python3
"""Test auth.json validity by loading it and checking Lovable authentication."""

import asyncio
import json
import time
from datetime import datetime

from playwright.async_api import async_playwright


async def test_auth_validity():
    """Test if auth.json session is still valid."""
    
    print("=" * 80)
    print("🔐 AUTH.JSON VALIDITY TEST")
    print("=" * 80)
    print()
    
    # Load auth.json
    print("📋 Step 1: Loading auth.json")
    print("-" * 80)
    try:
        with open("auth.json", "r") as f:
            auth_data = json.load(f)
        print(f"✅ Auth.json loaded successfully")
        print(f"   - Cookies: {len(auth_data.get('cookies', []))} found")
        print(f"   - Origins: {len(auth_data.get('origins', []))} found")
        
        # Check session cookies
        session_cookies = [c for c in auth_data.get('cookies', []) if 'lovable-session-id' in c.get('name', '')]
        print(f"   - Session cookies: {len(session_cookies)} found")
        for cookie in session_cookies:
            print(f"     • {cookie['name']}: expires {datetime.fromtimestamp(cookie['expires'])}")
        print()
    except Exception as e:
        print(f"❌ Failed to load auth.json: {e}")
        return
    
    # Launch browser with auth.json
    print("📋 Step 2: Launching browser with auth.json")
    print("-" * 80)
    start_time = time.time()
    
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=True)
            print(f"✅ Browser launched (headless mode)")
            
            # Create context with storage state
            print("📋 Step 3: Creating context with storage state")
            print("-" * 80)
            context = await browser.new_context(storage_state="auth.json")
            print(f"✅ Context created with auth.json")
            
            # Create page
            page = await context.new_page()
            print(f"✅ Page created")
            print()
            
            # Navigate to Lovable
            print("📋 Step 4: Navigating to lovable.dev")
            print("-" * 80)
            nav_start = time.time()
            try:
                await page.goto("https://lovable.dev", wait_until="load", timeout=30000)
                nav_time = time.time() - nav_start
                print(f"✅ Navigation successful ({nav_time:.2f}s)")
                print(f"   - URL: {page.url}")
                print()
            except Exception as e:
                print(f"❌ Navigation failed: {e}")
                print()
            
            # Check for authentication indicators
            print("📋 Step 5: Checking authentication status")
            print("-" * 80)
            
            # Check for login page
            if "login" in page.url.lower():
                print(f"❌ Still on login page - session may be invalid")
                print()
            else:
                print(f"✅ Not on login page")
            
            # Check for workspace/project indicators
            try:
                workspace = await page.query_selector('[data-testid="workspace"]')
                if workspace:
                    print(f"✅ Found workspace element")
                else:
                    print(f"⚠️  Workspace element not found")
            except Exception as e:
                print(f"⚠️  Error checking workspace: {e}")
            
            try:
                projects = await page.query_selector('[data-testid="projects-list"]')
                if projects:
                    print(f"✅ Found projects list element")
                else:
                    print(f"⚠️  Projects list element not found")
            except Exception as e:
                print(f"⚠️  Error checking projects: {e}")
            
            # Check for user profile/menu
            try:
                user_menu = await page.query_selector('[data-testid="user-menu"], .user-profile, [aria-label*="user"]')
                if user_menu:
                    print(f"✅ Found user menu element")
                else:
                    print(f"⚠️  User menu element not found")
            except Exception as e:
                print(f"⚠️  Error checking user menu: {e}")
            
            # Get page title and content
            title = await page.title()
            print(f"   - Page title: {title}")
            print()
            
            # Check for any error messages
            print("📋 Step 6: Checking for error messages")
            print("-" * 80)
            try:
                error_elements = await page.query_selector_all('[role="alert"], .error, .alert-error')
                if error_elements:
                    print(f"⚠️  Found {len(error_elements)} error elements")
                    for i, elem in enumerate(error_elements[:3]):
                        text = await elem.text_content()
                        print(f"   - Error {i+1}: {text[:100]}")
                else:
                    print(f"✅ No error messages found")
            except Exception as e:
                print(f"⚠️  Error checking for errors: {e}")
            print()
            
            # Wait a bit and check page state
            print("📋 Step 7: Waiting for page to stabilize")
            print("-" * 80)
            await page.wait_for_load_state("networkidle", timeout=10000)
            print(f"✅ Page stabilized")
            print()
            
            # Final verdict
            print("📋 FINAL VERDICT")
            print("-" * 80)
            if "login" not in page.url.lower():
                print(f"✅ AUTH.JSON IS VALID - Session is active")
                print(f"   - User is authenticated")
                print(f"   - Ready for browser agent execution")
            else:
                print(f"❌ AUTH.JSON IS INVALID - Session expired or invalid")
                print(f"   - User needs to log in again")
            
            elapsed = time.time() - start_time
            print(f"   - Total test time: {elapsed:.2f}s")
            print()
            
            await context.close()
            await browser.close()
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_auth_validity())

