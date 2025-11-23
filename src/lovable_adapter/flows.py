"""
Lovable deterministic automation flows.

These flows provide robust, retry-enabled interactions with Lovable UI.
Use these as fallback or optimization when Saik0s CLI automation needs help.
"""

import re
from typing import Optional

from playwright.async_api import Page
from tenacity import retry, stop_after_attempt, wait_fixed

from src.lovable_adapter.selectors import (
    BUILD_BUTTON_SELECTOR,
    BUILD_COMPLETE_SELECTOR,
    BUILD_TIMEOUT,
    DEFAULT_TIMEOUT,
    PREVIEW_URL_SELECTOR,
    PROMPT_INPUT_SELECTOR,
)


@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
async def ensure_logged_in(page: Page) -> bool:
    """
    Verify user is logged in to Lovable.

    Returns True if logged in, False otherwise.
    """
    try:
        # Check if we're on login page
        if "login" in page.url.lower():
            return False
        # Check for workspace/project indicators
        await page.wait_for_selector('[data-testid="workspace"]', timeout=5000)
        return True
    except Exception:
        return False


async def open_or_create_project(page: Page, project_name: str) -> bool:
    """
    Open existing project or create new one.

    Returns True on success, False on failure.
    """
    try:
        # Try to find and click existing project
        project_link = page.locator(f'text="{project_name}"')
        if await project_link.count() > 0:
            await project_link.first.click()
            await page.wait_for_load_state("load", timeout=DEFAULT_TIMEOUT)
            return True

        # Create new project
        create_btn = page.locator('button:has-text("New Project"), button:has-text("Create")')
        if await create_btn.count() > 0:
            await create_btn.click()
            await page.fill('input[placeholder*="name"]', project_name)
            await page.click('button:has-text("Create")')
            await page.wait_for_load_state("load", timeout=DEFAULT_TIMEOUT)
            return True

        return False
    except Exception:
        return False


async def paste_prompt(page: Page, prompt_text: str) -> bool:
    """
    Paste prompt into Lovable prompt input.

    Returns True on success, False on failure.
    """
    try:
        prompt_input = page.locator(PROMPT_INPUT_SELECTOR)
        if await prompt_input.count() > 0:
            await prompt_input.first.fill(prompt_text)
            return True
        return False
    except Exception:
        return False


async def trigger_build(page: Page) -> bool:
    """
    Trigger build/generation in Lovable.

    Returns True on success, False on failure.
    """
    try:
        build_btn = page.locator(BUILD_BUTTON_SELECTOR)
        if await build_btn.count() > 0:
            await build_btn.click()
            return True
        return False
    except Exception:
        return False


async def wait_for_build(page: Page, timeout: int = BUILD_TIMEOUT) -> bool:
    """
    Wait for build to complete.

    Returns True if build completed, False on timeout.
    """
    try:
        await page.wait_for_selector(BUILD_COMPLETE_SELECTOR, timeout=timeout)
        return True
    except Exception:
        return False


async def extract_preview_url(page: Page) -> Optional[str]:
    """
    Extract preview URL from Lovable build result.

    Returns URL string or None if not found.
    """
    try:
        # Try to find preview link
        preview_link = page.locator(PREVIEW_URL_SELECTOR)
        if await preview_link.count() > 0:
            url = await preview_link.first.get_attribute("href")
            if url and "lovable.dev" in url:
                return url

        # Try to extract from page text
        content = await page.content()
        match = re.search(r"https://[a-z0-9-]+\.lovable\.dev", content)
        if match:
            return match.group(0)

        return None
    except Exception:
        return None
