from typing import Optional

import loguru

from ..constants import (
    DEFAULT_ANTHROPIC_GATEWAY_URL,
    DEFAULT_BASE_URL,
    DEFAULT_OPENAI_GATEWAY_URL,
    DEFAULT_TIMEOUT,
)
from ._request_handler import AsyncRequestHandler
from .base_client import AiriaBaseClient
from .conversations import AsyncConversations
from .data_vector_search import AsyncDataVectorSearch
from .deployments import AsyncDeployments
from .pipeline_execution import AsyncPipelineExecution
from .pipelines_config import AsyncPipelinesConfig
from .project import AsyncProject
from .store import AsyncStore


class AiriaAsyncClient(AiriaBaseClient):
    """Asynchronous client for interacting with the Airia API."""

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
        Initialize the asynchronous Airia API client.

        Args:
            base_url: Base URL of the Airia API.
            api_key: API key for authentication. If not provided, will attempt to use AIRIA_API_KEY environment variable.
            bearer_token: Bearer token for authentication. Must be provided explicitly (no environment variable fallback).
            timeout: Request timeout in seconds.
            log_requests: Whether to log API requests and responses. Default is False.
            custom_logger: Optional custom logger object to use for logging. If not provided, will use a default logger when `log_requests` is True.
        """
        super().__init__(
            base_url=base_url,
            api_key=api_key,
            bearer_token=bearer_token,
            timeout=timeout,
            log_requests=log_requests,
            custom_logger=custom_logger,
        )

        self._request_handler = AsyncRequestHandler(
            logger=self.logger,
            timeout=self.timeout,
            base_url=self.base_url,
            api_key=self.api_key,
            bearer_token=self.bearer_token,
            log_requests=self.log_requests,
        )
        self.pipeline_execution = AsyncPipelineExecution(self._request_handler)
        self.pipelines_config = AsyncPipelinesConfig(self._request_handler)
        self.project = AsyncProject(self._request_handler)
        self.conversations = AsyncConversations(self._request_handler)
        self.store = AsyncStore(self._request_handler)
        self.deployments = AsyncDeployments(self._request_handler)
        self.data_vector_search = AsyncDataVectorSearch(self._request_handler)

    @classmethod
    def with_openai_gateway(
        cls,
        base_url: str = DEFAULT_BASE_URL,
        gateway_url: str = DEFAULT_OPENAI_GATEWAY_URL,
        api_key: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
        log_requests: bool = False,
        custom_logger: Optional["loguru.Logger"] = None,
        **kwargs,
    ):
        """
        Initialize the asynchronous Airia API client with AsyncOpenAI gateway capabilities.

        Args:
            base_url: Base URL of the Airia API.
            gateway_url: Base URL of the Airia Gateway API.
            api_key: API key for authentication. If not provided, will attempt to use AIRIA_API_KEY environment variable.
            timeout: Request timeout in seconds.
            log_requests: Whether to log API requests and responses. Default is False.
            custom_logger: Optional custom logger object to use for logging. If not provided, will use a default logger when `log_requests` is True.
            **kwargs: Additional keyword arguments to pass to the AsyncOpenAI client initialization.
        """
        from openai import AsyncOpenAI

        client = cls(
            base_url=base_url,
            api_key=api_key,
            timeout=timeout,
            log_requests=log_requests,
            custom_logger=custom_logger,
        )
        cls.openai = AsyncOpenAI(
            api_key=client.api_key,
            base_url=gateway_url,
            **kwargs,
        )

        return client

    @classmethod
    def with_anthropic_gateway(
        cls,
        base_url: str = DEFAULT_BASE_URL,
        gateway_url: str = DEFAULT_ANTHROPIC_GATEWAY_URL,
        api_key: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
        log_requests: bool = False,
        custom_logger: Optional["loguru.Logger"] = None,
        **kwargs,
    ):
        """
        Initialize the asynchronous Airia API client with AsyncAnthropic gateway capabilities.

        Args:
            base_url: Base URL of the Airia API.
            gateway_url: Base URL of the Airia Gateway API.
            api_key: API key for authentication. If not provided, will attempt to use AIRIA_API_KEY environment variable.
            timeout: Request timeout in seconds.
            log_requests: Whether to log API requests and responses. Default is False.
            custom_logger: Optional custom logger object to use for logging. If not provided, will use a default logger when `log_requests` is True.
            **kwargs: Additional keyword arguments to pass to the AsyncAnthropic client initialization.
        """
        from anthropic import AsyncAnthropic

        client = cls(
            base_url=base_url,
            api_key=api_key,
            timeout=timeout,
            log_requests=log_requests,
            custom_logger=custom_logger,
        )
        cls.anthropic = AsyncAnthropic(
            api_key=client.api_key,
            base_url=gateway_url,
            **kwargs,
        )

        return client

    @classmethod
    def with_bearer_token(
        cls,
        bearer_token: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        log_requests: bool = False,
        custom_logger: Optional["loguru.Logger"] = None,
    ):
        """
        Initialize the asynchronous Airia API client with bearer token authentication.

        Args:
            bearer_token: Bearer token for authentication.
            base_url: Base URL of the Airia API.
            timeout: Request timeout in seconds.
            log_requests: Whether to log API requests and responses. Default is False.
            custom_logger: Optional custom logger object to use for logging. If not provided, will use a default logger when `log_requests` is True.
        """
        return cls(
            base_url=base_url,
            bearer_token=bearer_token,
            timeout=timeout,
            log_requests=log_requests,
            custom_logger=custom_logger,
        )

    async def close(self):
        """
        Closes the aiohttp session to free up system resources.

        This method should be called when the RequestHandler is no longer needed to ensure
        proper cleanup of the underlying session and its resources.
        """
        await self._request_handler.close()
