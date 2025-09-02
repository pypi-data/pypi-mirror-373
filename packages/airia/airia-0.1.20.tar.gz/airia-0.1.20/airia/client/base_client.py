import os
from typing import Optional

import loguru

from ..constants import DEFAULT_BASE_URL, DEFAULT_TIMEOUT
from ..logs import configure_logging


class AiriaBaseClient:
    """Base client containing shared functionality for Airia API clients."""

    openai = None
    anthropic = None

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        api_key: Optional[str] = None,
        bearer_token: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
        log_requests: bool = False,
        custom_logger: Optional["loguru.Logger"] = None,
    ):
        """
        Initialize the Airia API client base class.

        Args:
            api_key: API key for authentication. If not provided, will attempt to use AIRIA_API_KEY environment variable.
            bearer_token: Bearer token for authentication. Must be provided explicitly (no environment variable fallback).
            timeout: Request timeout in seconds.
            log_requests: Whether to log API requests and responses. Default is False.
            custom_logger: Optional custom logger object to use for logging. If not provided, will use a default logger when `log_requests` is True.
        """
        # Resolve authentication credentials
        self.api_key, self.bearer_token = self.__class__._resolve_auth_credentials(
            api_key, bearer_token
        )

        # Store configuration
        self.base_url = base_url
        self.timeout = timeout
        self.log_requests = log_requests

        # Initialize logger
        self.logger = configure_logging() if custom_logger is None else custom_logger

    @staticmethod
    def _resolve_auth_credentials(
        api_key: Optional[str] = None, bearer_token: Optional[str] = None
    ):
        """
        Resolve authentication credentials from parameters and environment variables.

        Args:
            api_key (Optional[str]): The API key provided as a parameter. Defaults to None.
            bearer_token (Optional[str]): The bearer token provided as a parameter. Defaults to None.

        Returns:
            tuple: (api_key, bearer_token) - exactly one will be non-None

        Raises:
            ValueError: If no authentication method is provided or if both are provided.
        """
        # Check for explicit conflict first
        if api_key and bearer_token:
            raise ValueError(
                "Cannot provide both api_key and bearer_token. Please use only one authentication method."
            )

        # If bearer token is explicitly provided, use it exclusively
        if bearer_token:
            return None, bearer_token

        # If API key is explicitly provided, use it exclusively
        if api_key:
            return api_key, None

        # If neither is provided explicitly, fall back to environment variable
        resolved_api_key = os.environ.get("AIRIA_API_KEY")
        if resolved_api_key:
            return resolved_api_key, None

        # No authentication method found
        raise ValueError(
            "Authentication required. Provide either api_key (or set AIRIA_API_KEY environment variable) or bearer_token."
        )
