import asyncio
import weakref
from typing import Any, AsyncIterator, Dict, Optional

import aiohttp
import loguru

from ...exceptions import AiriaAPIError
from ...types._request_data import RequestData
from ...utils.sse_parser import async_parse_sse_stream_chunked
from .base_request_handler import BaseRequestHandler


class AsyncRequestHandler(BaseRequestHandler):
    def __init__(
        self,
        logger: "loguru.Logger",
        timeout: float,
        base_url: str,
        api_key: Optional[str] = None,
        bearer_token: Optional[str] = None,
        log_requests: bool = False,
    ):
        self.session = aiohttp.ClientSession()

        self._finalizer = weakref.finalize(self, self._cleanup_session, self.session)

        super().__init__(
            logger=logger,
            timeout=timeout,
            api_key=api_key,
            base_url=base_url,
            bearer_token=bearer_token,
            log_requests=log_requests,
        )

    @staticmethod
    def _cleanup_session(session: aiohttp.ClientSession):
        """Static method to clean up session - called by finalizer"""
        if session and not session.closed:
            # Create a new event loop if none exists
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    raise RuntimeError("Event loop is closed")
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            # Close the session
            if not loop.is_running():
                loop.run_until_complete(session.close())
            else:
                # If loop is running, schedule the close operation
                asyncio.create_task(session.close())

    async def close(self):
        """
        Closes the aiohttp session to free up system resources.

        This method should be called when the RequestHandler is no longer needed to ensure
        proper cleanup of the underlying session and its resources.
        """
        if self.session and not self.session.closed:
            await self.session.close()

    def _handle_exception(
        self, e: aiohttp.ClientResponseError, url: str, correlation_id: str
    ):
        # Log the error response if enabled
        if self.log_requests:
            self.logger.error(
                f"API Error: {e.status} {e.message}\n"
                f"URL: {url}\n"
                f"Correlation ID: {correlation_id}"
            )

        # Extract error details from response
        error_message = e.message

        # Make sure sensitive auth information is not included in error messages
        sanitized_message = error_message
        if self.api_key and self.api_key in sanitized_message:
            sanitized_message = sanitized_message.replace(self.api_key, "[REDACTED]")
        if self.bearer_token and self.bearer_token in sanitized_message:
            sanitized_message = sanitized_message.replace(
                self.bearer_token, "[REDACTED]"
            )

        # Raise custom exception with status code and sanitized message
        raise AiriaAPIError(status_code=e.status, message=sanitized_message) from e

    async def make_request(
        self, method: str, request_data: RequestData, return_json: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Makes an asynchronous HTTP request to the Airia API.

        Args:
            method (str): The HTTP method (e.g., 'GET', 'POST')
            request_data: A dictionary containing the following request information:
                - url: The endpoint URL for the request
                - headers: HTTP headers to include in the request
                - payload: The JSON payload/body for the request
                - params: Optional query parameters to append to the URL
                - files: Optional file data to be uploaded in the request body
                - correlation_id: Unique identifier for request tracing
            return_json (bool): Whether to return the response as JSON. Default is True.

        Returns:
            resp ([Dict[str, Any]): The JSON response from the API as a dictionary.

        Raises:
            AiriaAPIError: If the API returns an error response, with details about the error
            aiohttp.ClientResponseError: For HTTP-related errors

        Note:
            This is an internal method used by other client methods to make API requests.
            It handles logging, error handling, and API key redaction in error messages.
        """
        try:
            # Make the request
            async with self.session.request(
                method=method,
                url=request_data.url,
                json=request_data.payload,
                params=request_data.params,
                headers=request_data.headers,
                timeout=self.timeout,
            ) as response:
                # Log the response if enabled
                if self.log_requests:
                    self.logger.info(
                        f"API Response: {response.status} {response.reason}\n"
                        f"URL: {request_data.url}\n"
                        f"Correlation ID: {request_data.correlation_id}"
                    )

                # Check for HTTP errors
                response.raise_for_status()

                # Return the response as a dictionary
                if return_json:
                    return await response.json()

        except aiohttp.ClientResponseError as e:
            self._handle_exception(e, request_data.url, request_data.correlation_id)

    async def make_request_stream(
        self, method: str, request_data: RequestData
    ) -> AsyncIterator[str]:
        """
        Makes an asynchronous HTTP request to the Airia API.

        Args:
            method (str): The HTTP method (e.g., 'GET', 'POST')
            request_data: A dictionary containing the following request information:
                - url: The endpoint URL for the request
                - headers: HTTP headers to include in the request
                - payload: The JSON payload/body for the request
                - params: Optional query parameters to append to the URL
                - files: Optional file data to be uploaded in the request body
                - correlation_id: Unique identifier for request tracing

        Yields:
            resp AsyncIterator[str]]: yields chunks of the response as they are received.

        Raises:
            AiriaAPIError: If the API returns an error response, with details about the error
            aiohttp.ClientResponseError: For HTTP-related errors

        Note:
            This is an internal method used by other client methods to make API requests.
            It handles logging, error handling, and API key redaction in error messages.
        """
        try:
            # Make the request
            async with self.session.request(
                method=method,
                url=request_data.url,
                json=request_data.payload,
                params=request_data.params,
                headers=request_data.headers,
                timeout=self.timeout,
                chunked=True,
            ) as response:
                # Log the response if enabled
                if self.log_requests:
                    self.logger.info(
                        f"API Response: {response.status} {response.reason}\n"
                        f"URL: {request_data.url}\n"
                        f"Correlation ID: {request_data.correlation_id}"
                    )

                # Check for HTTP errors
                response.raise_for_status()

                # Yields the response content as a stream if streaming
                async for message in async_parse_sse_stream_chunked(
                    response.content.iter_any()
                ):
                    yield message

        except aiohttp.ClientResponseError as e:
            self._handle_exception(e, request_data.url, request_data.correlation_id)

    async def make_request_multipart(
        self, method: str, request_data: RequestData, return_json: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Makes an asynchronous HTTP request with multipart form data to the Airia API.

        Args:
            method (str): The HTTP method (e.g., 'POST')
            request_data: A dictionary containing the following request information:
                - url: The endpoint URL for the request
                - headers: HTTP headers to include in the request
                - payload: The form data payload including file content
                - params: Optional query parameters to append to the URL
                - files: Optional file data to be uploaded in the request body
                - correlation_id: Unique identifier for request tracing
            return_json (bool): Whether to return the response as JSON. Default is True.

        Returns:
            resp (Optional[Dict[str, Any]]): The JSON response from the API as a dictionary.

        Raises:
            AiriaAPIError: If the API returns an error response, with details about the error
            aiohttp.ClientResponseError: For HTTP-related errors

        Note:
            This is an internal method used by file upload methods to make multipart requests.
            It handles multipart form data encoding, logging, and error handling.
        """
        try:
            # Prepare multipart form data
            data = aiohttp.FormData()

            # Add form fields
            for key, value in request_data.payload.items():
                data.add_field(key, str(value))

            # Add files
            for key, value in request_data.files.items():
                data.add_field(key, value[1], filename=value[0], content_type=value[2])

            # Make the request
            async with self.session.request(
                method=method,
                url=request_data.url,
                data=data,
                params=request_data.params,
                headers=request_data.headers,
                timeout=self.timeout,
            ) as response:
                # Log the response if enabled
                if self.log_requests:
                    self.logger.info(
                        f"API Response: {response.status} {response.reason}\n"
                        f"URL: {request_data.url}\n"
                        f"Correlation ID: {request_data.correlation_id}"
                    )

                # Check for HTTP errors
                response.raise_for_status()

                # Return the response as a dictionary
                if return_json:
                    return await response.json()

        except aiohttp.ClientResponseError as e:
            self._handle_exception(e, request_data.url, request_data.correlation_id)
