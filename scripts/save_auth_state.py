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
from pathlib import Path

from playwright.async_api import async_playwright

# Fix Unicode encoding on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


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
            await page.goto("https://lovable.dev", wait_until="networkidle")

            # Wait for login to complete
            print("⏳ Waiting for manual login...")
            print("   Please log in to Lovable in the browser window.")
            print("   This script will continue once you're authenticated.")
            print()

            # Wait for workspace/project indicators (sign of successful login)
            try:
                await page.wait_for_selector(
                    '[data-testid="workspace"], .workspace-menu, [data-testid="projects-list"]',
                    timeout=600000,  # 10 minutes
                )
                print("✅ Login detected!")
            except Exception:
                print("⚠️  Timeout waiting for login. Proceeding anyway...")

            # Save storage state
            print("💾 Saving authentication state...")
            storage_state = await context.storage_state()

            with open(output_file, "w") as f:
                json.dump(storage_state, f, indent=2)

            print(f"✅ Success! Auth state saved to: {output_file.absolute()}")
            print()
            print("📝 Next steps:")
            print(f"   1. Store this file securely")
            print(f"   2. For Fly.io: fly secrets set MCP_AUTH_STATE_PATH=@{output_file}")
            print(f"   3. Or set env var: export MCP_AUTH_STATE_PATH={output_file}")

        finally:
            await browser.close()


def main() -> None:
    """CLI entry point."""
    output_path = sys.argv[1] if len(sys.argv) > 1 else None
    asyncio.run(save_auth_state(output_path))


if __name__ == "__main__":
    main()

