"""
Server-Sent Events (SSE) stream parsing utilities.

This module provides functions for parsing SSE streams from both synchronous and
asynchronous HTTP responses. It handles the SSE protocol format and converts
raw stream data into typed message objects.
"""

import json
import re
from typing import AsyncIterable, AsyncIterator, Iterable, Iterator

from ..types.sse import SSEDict, SSEMessage


def _to_snake_case(name: str) -> str:
    """
    Convert camelCase or PascalCase string to snake_case.

    Args:
        name: The string to convert to snake_case

    Returns:
        The string converted to snake_case format
    """
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def parse_sse_stream_chunked(stream_chunks: Iterable[bytes]) -> Iterator[SSEMessage]:
    """
    Parse Server-Sent Events (SSE) stream from an iterable of byte chunks.

    This function processes streaming data from HTTP responses that follow the SSE protocol,
    parsing event blocks and converting them into typed SSE message objects. It handles
    incomplete chunks by buffering data until complete events are received.

    Args:
        stream_chunks: An iterable of byte chunks from an HTTP streaming response

    Yields:
        SSEMessage: Typed SSE message objects corresponding to the parsed events

    Note:
        Events are expected to follow the SSE format with 'event:' and 'data:' lines,
        terminated by double newlines (\n\n). The data portion should contain valid JSON.
    """
    buffer = ""

    for chunk in stream_chunks:
        buffer += chunk.decode("utf-8")

        # Look for complete events (ending with double newline)
        while "\n\n" in buffer:
            event_block, buffer = buffer.split("\n\n", 1)

            if not event_block.strip():
                continue

            event_name = None
            event_data = None

            # Parse each line in the event block
            for line in event_block.strip().split("\n"):
                line = line.strip()
                if line.startswith("event:"):
                    event_name = line[6:].strip()
                elif line.startswith("data:"):
                    data_json = line[5:].strip()
                    event_data = json.loads(data_json)

            if event_name and event_data:
                yield SSEDict[event_name](
                    **{_to_snake_case(k): v for k, v in event_data.items()}
                )


async def async_parse_sse_stream_chunked(
    stream_chunks: AsyncIterable[bytes],
) -> AsyncIterator[SSEMessage]:
    """
    Asynchronously parse Server-Sent Events (SSE) stream from an async iterable of byte chunks.

    This is the async version of parse_sse_stream_chunked, designed for use with
    asynchronous HTTP clients. It processes streaming data that follows the SSE protocol,
    parsing event blocks and converting them into typed SSE message objects.

    Args:
        stream_chunks: An async iterable of byte chunks from an HTTP streaming response

    Yields:
        SSEMessage: Typed SSE message objects corresponding to the parsed events

    Note:
        Events are expected to follow the SSE format with 'event:' and 'data:' lines,
        terminated by double newlines (\n\n). The data portion should contain valid JSON.
    """
    buffer = ""

    async for chunk in stream_chunks:
        buffer += chunk.decode("utf-8")

        # Look for complete events (ending with double newline)
        while "\n\n" in buffer:
            event_block, buffer = buffer.split("\n\n", 1)

            if not event_block.strip():
                continue

            event_name = None
            event_data = None

            # Parse each line in the event block
            for line in event_block.strip().split("\n"):
                line = line.strip()
                if line.startswith("event:"):
                    event_name = line[6:].strip()
                elif line.startswith("data:"):
                    data_json = line[5:].strip()
                    event_data = json.loads(data_json)

            if event_name and event_data:
                yield SSEDict[event_name](
                    **{_to_snake_case(k): v for k, v in event_data.items()}
                )
