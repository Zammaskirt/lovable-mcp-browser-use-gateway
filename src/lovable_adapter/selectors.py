"""
Lovable UI selectors for deterministic automation.

These selectors are based on Lovable.dev UI structure and may need
updates if the UI changes. Prefer ARIA labels and text selectors
for robustness.
"""

# Authentication selectors
LOGIN_EMAIL_SELECTOR = 'input[type="email"]'
LOGIN_PASSWORD_SELECTOR = 'input[type="password"]'
LOGIN_SUBMIT_SELECTOR = 'button:has-text("Sign in"), button:has-text("Log in")'

# Project selectors
PROJECT_NAME_INPUT_SELECTOR = 'input[placeholder*="project"], input[placeholder*="name"]'
CREATE_PROJECT_BUTTON_SELECTOR = 'button:has-text("Create"), button:has-text("New Project")'

# Prompt/Build selectors
PROMPT_INPUT_SELECTOR = 'textarea[placeholder*="prompt"], textarea[placeholder*="describe"]'
BUILD_BUTTON_SELECTOR = 'button:has-text("Build"), button:has-text("Generate")'

# Status/Result selectors
BUILD_STATUS_SELECTOR = '[data-testid="build-status"], .build-status'
PREVIEW_URL_SELECTOR = 'a[href*="lovable.dev"], [data-testid="preview-url"]'
BUILD_COMPLETE_SELECTOR = ':has-text("Build complete"), :has-text("Ready")'

# Navigation selectors
WORKSPACE_SELECTOR = '[data-testid="workspace"], .workspace-menu'
PROJECTS_LIST_SELECTOR = '[data-testid="projects-list"], .projects-grid'

# Timeouts (in milliseconds)
DEFAULT_TIMEOUT = 30000  # 30 seconds
BUILD_TIMEOUT = 300000  # 5 minutes
LOGIN_TIMEOUT = 60000  # 1 minute
