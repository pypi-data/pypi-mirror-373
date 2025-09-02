"""
Internal data structures for HTTP request preparation.

This module defines the data models used internally by the SDK clients
to organize and pass request information between methods.
"""

from io import BufferedIOBase
from typing import Any, Dict, Optional, Tuple

from pydantic import BaseModel, ConfigDict


class RequestData(BaseModel):
    """
    Structured container for HTTP request components.

    This internal data structure organizes all the components needed to make
    an HTTP request, including the URL, headers, payload, query parameters,
    and correlation ID for tracing.

    Attributes:
        url: The complete URL for the HTTP request
        payload: Optional JSON payload for the request body
        params: Optional query parameters to append to the URL
        files: Optional file data to be uploaded in the request body
        headers: HTTP headers including authentication and content-type
        correlation_id: Unique identifier for request tracing and logging
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    url: str
    payload: Optional[Dict[str, Any]]
    params: Optional[Dict[str, Any]]
    files: Optional[Dict[str, Tuple[str, BufferedIOBase, str]]]
    headers: Dict[str, Any]
    correlation_id: str
