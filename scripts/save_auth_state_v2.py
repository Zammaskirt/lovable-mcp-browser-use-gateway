#!/usr/bin/env python3
"""
Generate Playwright storage_state for Lovable authentication.

This script opens Lovable.dev in a browser, waits for manual login,
and saves the authentication state to a file for reuse.

Usage:
    python scripts/save_auth_state_v2.py [output_path]
    python scripts/save_auth_state_v2.py ./auth.json
"""

import asyncio
import io
import json
import os
import sys
import threading
from pathlib import Path

from playwright.async_api import async_playwright

# Fix Unicode encoding on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


async def save_auth_state(output_path: str | None = None) -> None:
    """Generate and save Lovable authentication state."""
    if output_path is None:
        output_path = os.getenv("MCP_AUTH_STATE_PATH", "./auth.json")

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    print(f"🔐 Lovable Authentication State Generator")
    print(f"📁 Output: {output_file.absolute()}")
    print()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            print("🌐 Opening Lovable.dev...")
            try:
                await page.goto("https://lovable.dev", wait_until="load", timeout=60000)
            except Exception as e:
                print(f"⚠️  Navigation issue: {e}")
                print("   Continuing anyway - browser may still load...")

            print()
            print("=" * 70)
            print("⏳ WAITING FOR LOGIN")
            print("=" * 70)
            print()
            print("📋 Instructions:")
            print("   1. Look at the browser window that opened")
            print("   2. Log in to Lovable with your credentials")
            print("   3. After logging in, press ENTER in this terminal")
            print()
            print("=" * 70)
            print()

            # Wait for user to press Enter
            print("👉 Press ENTER when you've logged in to Lovable...")
            await asyncio.get_event_loop().run_in_executor(None, input)

            print()
            print("✅ Confirmed! Saving authentication state...")
            print()

            # Save storage state
            storage_state = await context.storage_state()

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

