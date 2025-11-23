"""
Pytest configuration and fixtures for tests.
"""

import os
import sys

# Set test environment variables BEFORE importing server module
os.environ["MCP_BEARER_TOKEN"] = "test-token"

# Now we can import pytest and other modules
import pytest  # noqa: E402

