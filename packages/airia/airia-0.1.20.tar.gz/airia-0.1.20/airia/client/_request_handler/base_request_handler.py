import json
from typing import Any, Dict, Optional

import loguru

from ...logs import set_correlation_id
from ...types._request_data import RequestData


class BaseRequestHandler:
    def __init__(
        self,
        logger: "loguru.Logger",
        timeout: float,
        base_url: str,
        api_key: Optional[str] = None,
        bearer_token: Optional[str] = None,
        log_requests: bool = False,
    ):
        self.logger = logger
        self.timeout = timeout
        self.base_url = base_url
        self.api_key = api_key
        self.bearer_token = bearer_token
        self.log_requests = log_requests

    def close(self):
        raise NotImplementedError("Subclasses must implement this method")

    def prepare_request(
        self,
        url: str,
        payload: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
    ):
        """
        Prepare request data including headers, authentication, and logging.

        This method sets up all the necessary components for an API request including
        correlation ID, authentication headers, and sanitized logging.

        Args:
            url: The target URL for the request
            payload: Optional JSON payload for the request body
            params: Optional query parameters for the request
            files: Optional files to be uploaded in the request body
            correlation_id: Optional correlation ID for request tracing

        Returns:
            RequestData: A data structure containing all prepared request components
        """
        # Set correlation ID if provided or generate a new one
        correlation_id = set_correlation_id(correlation_id)

        # Set up base headers
        headers = {"X-Correlation-ID": correlation_id}

        # Add authentication header based on the method used
        if self.api_key:
            headers["X-API-KEY"] = self.api_key
        elif self.bearer_token:
            headers["Authorization"] = f"Bearer {self.bearer_token}"

        # Log the request if enabled
        if self.log_requests:
            # Create a sanitized copy of headers and params for logging
            log_headers = headers.copy()
            log_params = params.copy() if params is not None else {}
            log_files = (
                {k: (v[0], "[BINARY DATA]", v[2]) for k, v in files.items()}
                if files is not None
                else {}
            )

            # Filter out sensitive headers
            if "X-API-KEY" in log_headers:
                log_headers["X-API-KEY"] = "[REDACTED]"
            if "Authorization" in log_headers:
                log_headers["Authorization"] = "[REDACTED]"

            # Process payload for logging
            log_payload = payload.copy() if payload is not None else {}
            if "images" in log_payload and log_payload["images"] is not None:
                log_payload["images"] = f"{len(log_payload['images'])} images"
            if "files" in log_payload and log_payload["files"] is not None:
                log_payload["files"] = f"{len(log_payload['files'])} files"
            log_payload = json.dumps(log_payload)

            self.logger.info(
                f"URL: {url}\n"
                f"Headers: {json.dumps(log_headers)}\n"
                f"Payload: {log_payload}\n"
                f"Files: {log_files}\n"
                f"Params: {json.dumps(log_params)}\n"
            )

        return RequestData(
            **{
                "url": url,
                "payload": payload,
                "headers": headers,
                "params": params,
                "files": files,
                "correlation_id": correlation_id,
            }
        )
