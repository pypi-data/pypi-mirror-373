import weakref
from typing import Any, Dict, Optional

import loguru
import requests

from ...exceptions import AiriaAPIError
from ...types._request_data import RequestData
from ...utils.sse_parser import parse_sse_stream_chunked
from .base_request_handler import BaseRequestHandler


class RequestHandler(BaseRequestHandler):
    def __init__(
        self,
        logger: "loguru.Logger",
        timeout: float,
        base_url: str,
        api_key: Optional[str] = None,
        bearer_token: Optional[str] = None,
        log_requests: bool = False,
    ):
        # Initialize session for synchronous requests
        self.session = requests.Session()
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
    def _cleanup_session(session: requests.Session):
        """Static method to clean up session - called by finalizer"""
        if session:
            session.close()

    def close(self):
        """
        Closes the requests session to free up system resources.

        This method should be called when the RequestHandler is no longer needed to ensure
        proper cleanup of the underlying session and its resources.
        """
        self.session.close()

    def _handle_exception(self, e: requests.HTTPError, url: str, correlation_id: str):
        # Log the error response if enabled
        if self.log_requests:
            self.logger.error(
                f"API Error: {e.response.status_code} {e.response.reason}\n"
                f"URL: {url}\n"
                f"Correlation ID: {correlation_id}"
            )

        # Extract error details from response if possible
        error_message = "API request failed"
        try:
            error_data = e.response.json()
            if isinstance(error_data, dict) and "message" in error_data:
                error_message = error_data["message"]
            elif isinstance(error_data, dict) and "error" in error_data:
                error_message = error_data["error"]
        except (ValueError, KeyError):
            # If JSON parsing fails or expected keys are missing
            error_message = f"API request failed: {str(e)}"

        # Make sure sensitive auth information is not included in error messages
        sanitized_message = error_message
        if self.api_key and self.api_key in sanitized_message:
            sanitized_message = sanitized_message.replace(self.api_key, "[REDACTED]")
        if self.bearer_token and self.bearer_token in sanitized_message:
            sanitized_message = sanitized_message.replace(
                self.bearer_token, "[REDACTED]"
            )

        # Raise custom exception with status code and sanitized message
        raise AiriaAPIError(
            status_code=e.response.status_code, message=sanitized_message
        ) from e

    def make_request(
        self, method: str, request_data: RequestData, return_json: bool = True
    ) -> Dict[str, Any]:
        """
        Makes a synchronous HTTP request to the Airia API.

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
            resp (Dict[str, Any]): The JSON response from the API as a dictionary.

        Raises:
            AiriaAPIError: If the API returns an error response, with details about the error
            requests.HTTPError: For HTTP-related errors

        Note:
            This is an internal method used by other client methods to make API requests.
            It handles logging, error handling, and API key redaction in error messages.
        """
        try:
            # Make the request
            response = self.session.request(
                method=method,
                url=request_data.url,
                json=request_data.payload,
                params=request_data.params,
                headers=request_data.headers,
                timeout=self.timeout,
            )

            # Log the response if enabled
            if self.log_requests:
                self.logger.info(
                    f"API Response: {response.status_code} {response.reason}\n"
                    f"URL: {request_data.url}\n"
                    f"Correlation ID: {request_data.correlation_id}\n"
                )

            # Check for HTTP errors
            response.raise_for_status()

            # Returns the JSON response
            if return_json:
                return response.json()

        except requests.HTTPError as e:
            self._handle_exception(e, request_data.url, request_data.correlation_id)

    def make_request_stream(self, method: str, request_data: RequestData):
        """
        Makes a synchronous HTTP request to the Airia API.

        Args:
            method (str): The HTTP method (e.g., 'GET', 'POST')
            request_data: A dictionary containing the following request information:
                - url: The endpoint URL for the request
                - headers: HTTP headers to include in the request
                - payload: The JSON payload/body for the request
                - params: Optional query parameters to append to the URL
                - files: Optional file data to be uploaded in the request body
                - correlation_id: Unique identifier for request tracing
            stream (bool): If True, the response will be streamed instead of downloaded all at once

        Yields:
            resp (Iterator[str]): Yields chunks of the response as they are received.

        Raises:
            AiriaAPIError: If the API returns an error response, with details about the error
            requests.HTTPError: For HTTP-related errors

        Note:
            This is an internal method used by other client methods to make API requests.
            It handles logging, error handling, and API key redaction in error messages.
        """
        try:
            # Make the request
            response = self.session.request(
                method=method,
                url=request_data.url,
                params=request_data.params,
                json=request_data.payload,
                headers=request_data.headers,
                timeout=self.timeout,
                stream=True,
            )

            # Log the response if enabled
            if self.log_requests:
                self.logger.info(
                    f"API Response: {response.status_code} {response.reason}\n"
                    f"URL: {request_data.url}\n"
                    f"Correlation ID: {request_data.correlation_id}\n"
                )

            # Check for HTTP errors
            response.raise_for_status()

            # Yields the response content as a stream
            for message in parse_sse_stream_chunked(response.iter_content()):
                yield message

        except requests.HTTPError as e:
            self._handle_exception(e, request_data.url, request_data.correlation_id)

    def make_request_multipart(
        self, method: str, request_data: RequestData, return_json: bool = True
    ):
        """
        Makes a synchronous HTTP request with multipart form data to the Airia API.

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
            resp (Dict[str, Any]): The JSON response from the API as a dictionary.

        Raises:
            AiriaAPIError: If the API returns an error response, with details about the error
            requests.HTTPError: For HTTP-related errors

        Note:
            This is an internal method used by file upload methods to make multipart requests.
            It handles multipart form data encoding, logging, and error handling.
        """
        try:
            # Make the request
            response = self.session.request(
                method=method,
                url=request_data.url,
                files=request_data.files,
                data=request_data.payload,
                params=request_data.params,
                headers=request_data.headers,
                timeout=self.timeout,
            )

            # Log the response if enabled
            if self.log_requests:
                self.logger.info(
                    f"API Response: {response.status_code} {response.reason}\n"
                    f"URL: {request_data.url}\n"
                    f"Correlation ID: {request_data.correlation_id}\n"
                )

            # Check for HTTP errors
            response.raise_for_status()

            # Returns the JSON response
            if return_json:
                return response.json()

        except requests.HTTPError as e:
            self._handle_exception(e, request_data.url, request_data.correlation_id)
