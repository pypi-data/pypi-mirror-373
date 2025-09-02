"""
Constants used throughout the Airia SDK.

This module defines default values for API endpoints, timeouts, and other
configuration parameters used by the SDK clients.
"""

# Default API endpoints
DEFAULT_BASE_URL = "https://api.airia.ai/"
"""Default base URL for the main Airia API endpoints."""

DEFAULT_OPENAI_GATEWAY_URL = "https://gateway.airia.ai/openai/v1"
"""Default base URL for the Airia OpenAI Gateway API."""

DEFAULT_ANTHROPIC_GATEWAY_URL = "https://gateway.airia.ai/anthropic"
"""Default base URL for the Airia Anthropic Gateway API."""

# Default timeouts
DEFAULT_TIMEOUT = 30.0
"""Default timeout in seconds for API requests."""
