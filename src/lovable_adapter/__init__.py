"""
Lovable adapter for deterministic browser automation.

Provides helper functions for interacting with Lovable.dev UI.
These are optional helpers that can be used to optimize or fallback
from Saik0s CLI automation.
"""

from src.lovable_adapter.flows import (
    ensure_logged_in,
    extract_preview_url,
    open_or_create_project,
    paste_prompt,
    trigger_build,
    wait_for_build,
)
from src.lovable_adapter.selectors import (
    BUILD_BUTTON_SELECTOR,
    LOGIN_EMAIL_SELECTOR,
    LOGIN_PASSWORD_SELECTOR,
    LOGIN_SUBMIT_SELECTOR,
    PROJECT_NAME_INPUT_SELECTOR,
    PROMPT_INPUT_SELECTOR,
)

__all__ = [
    # Selectors
    "LOGIN_EMAIL_SELECTOR",
    "LOGIN_PASSWORD_SELECTOR",
    "LOGIN_SUBMIT_SELECTOR",
    "PROJECT_NAME_INPUT_SELECTOR",
    "PROMPT_INPUT_SELECTOR",
    "BUILD_BUTTON_SELECTOR",
    # Flows
    "ensure_logged_in",
    "open_or_create_project",
    "paste_prompt",
    "trigger_build",
    "wait_for_build",
    "extract_preview_url",
]
