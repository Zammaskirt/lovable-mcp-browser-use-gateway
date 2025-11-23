#!/usr/bin/env python3
"""
Generate Playwright storage_state for Lovable authentication.

This script opens Lovable.dev in a browser, waits for manual login,
and saves the authentication state to a file for reuse.

Usage:
    python scripts/save_auth_state.py [output_path]
    python scripts/save_auth_state.py ./auth.json
"""

import asyncio
import io
import json
import os
import sys
import threading
import time
from pathlib import Path

from playwright.async_api import async_playwright

# Fix Unicode encoding on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


def wait_for_user_input():
    """Wait for user to press Enter in a separate thread."""
    try:
        input()
        return True
    except (EOFError, KeyboardInterrupt):
        return False


async def save_auth_state(output_path: str | None = None) -> None:
    """
    Generate and save Lovable authentication state.

    Args:
        output_path: Path to save auth.json. Defaults to env var or ./auth.json
    """
    # Determine output path
    if output_path is None:
        output_path = os.getenv("MCP_AUTH_STATE_PATH", "./auth.json")

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    print(f"🔐 Lovable Authentication State Generator")
    print(f"📁 Output: {output_file.absolute()}")
    print()

    async with async_playwright() as p:
        # Launch browser in headed mode for manual login
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            # Navigate to Lovable
            print("🌐 Opening Lovable.dev...")
            try:
                await page.goto("https://lovable.dev", wait_until="domcontentloaded", timeout=60000)
            except Exception as e:
                print(f"⚠️  Navigation issue: {e}")
                print("   Continuing anyway - browser may still load...")

            # Wait for login to complete
            print()
            print("=" * 70)
            print("⏳ WAITING FOR LOGIN")
            print("=" * 70)
            print()
            print("📋 Instructions:")
            print("   1. Look at the browser window that opened")
            print("   2. Log in to Lovable with your credentials")
            print("   3. After logging in, you have TWO options:")
            print()
            print("   Option A (Automatic): Wait for detection")
            print("      - Script will detect login automatically")
            print("      - May take 10-30 seconds after login")
            print()
            print("   Option B (Manual): Press ENTER when ready")
            print("      - After you log in, press ENTER in this terminal")
            print("      - Script will save auth immediately")
            print()
            print("=" * 70)
            print()

            # Try automatic detection with multiple selectors
            login_detected = False
            selectors_to_try = [
                # Primary selectors - most reliable
                'button[data-testid="create-project-button"]',  # Create project button
                'a[href="/projects"]',  # Projects link
                'div[data-testid="projects-grid"]',  # Projects grid
                # Secondary selectors - fallback
                '[data-testid="workspace"]',
                '.workspace-menu',
                '[data-testid="projects-list"]',
                # Tertiary selectors - last resort
                'nav',  # Navigation element
                'button:has-text("Create")',  # Create button
            ]

            print("🔍 Attempting automatic login detection...")
            print("   Checking for login indicators...")
            print()

            # Try each selector with a short timeout
            for selector in selectors_to_try:
                try:
                    print(f"   Checking: {selector[:50]}...", end=" ", flush=True)
                    await page.wait_for_selector(selector, timeout=5000)
                    print("✅ Found!")
                    login_detected = True
                    break
                except Exception:
                    print("❌")
                    continue

            if login_detected:
                print()
                print("✅ Login detected automatically!")
                # Wait a bit longer to ensure localStorage is populated
                print("   Waiting for localStorage to populate...")
                await page.wait_for_timeout(3000)  # Wait 3 seconds
            else:
                print()
                print("⚠️  Could not auto-detect login")
                print("   Waiting for manual confirmation...")
                print()
                print("👉 Press ENTER in this terminal when you've logged in to Lovable")
                print()

                # Start thread to wait for user input
                input_thread = threading.Thread(target=wait_for_user_input, daemon=True)
                input_thread.start()

                # Wait for either user input or timeout
                input_thread.join(timeout=600)  # 10 minute timeout

                if input_thread.is_alive():
                    print("⏱️  Timeout reached. Proceeding with save...")
                else:
                    print("✅ Confirmed! Proceeding with save...")

            print()
            print("💾 Saving authentication state...")

            # Save storage state
            storage_state = await context.storage_state()

            # Debug: Check what we're saving
            print(f"   Storage state type: {type(storage_state).__name__}")
            if isinstance(storage_state, dict):
                print(f"   Cookies: {len(storage_state.get('cookies', []))}")
                print(f"   Origins: {len(storage_state.get('origins', []))}")
                origins = storage_state.get('origins', [])
                for origin in origins:
                    ls = origin.get('localStorage', [])
                    print(f"     - {origin.get('origin')}: {len(ls)} localStorage items")

            with open(output_file, "w") as f:
                json.dump(storage_state, f, indent=2)

            file_size = os.path.getsize(output_file)
            print(f"✅ Success! Auth state saved to: {output_file.absolute()}")
            print(f"   File size: {file_size} bytes")
            print()
            print("📝 Next steps:")
            print(f"   1. Store this file securely (contains session cookies)")
            print(f"   2. For Fly.io: fly secrets set MCP_AUTH_STATE_PATH=@{output_file}")
            print(f"   3. Or set env var: export MCP_AUTH_STATE_PATH={output_file}")
            print(f"   4. Run tests: python -m pytest tests/ -v")

        except Exception as e:
            print(f"❌ Error: {e}")
            print()
            print("Attempting to save auth state anyway...")
            try:
                storage_state = await context.storage_state()
                with open(output_file, "w") as f:
                    json.dump(storage_state, f, indent=2)
                print(f"✅ Auth state saved (may be incomplete)")
            except Exception as save_error:
                print(f"❌ Failed to save: {save_error}")
                raise

        finally:
            await browser.close()


def main() -> None:
    """CLI entry point."""
    output_path = sys.argv[1] if len(sys.argv) > 1 else None
    asyncio.run(save_auth_state(output_path))


if __name__ == "__main__":
    main()

