import os
import sys
import uuid
from contextvars import ContextVar
from typing import BinaryIO, Optional, TextIO, Union

import loguru
from loguru import logger

# Create a context variable to store correlation ID
correlation_id_context: ContextVar[str] = ContextVar("correlation_id", default="")


def get_correlation_id() -> str:
    """
    Get the current correlation ID from context or return empty string if not set.

    Returns:
        str: The current correlation ID
    """
    return correlation_id_context.get()


def set_correlation_id(correlation_id: Optional[str] = None) -> str:
    """
    Set a correlation ID in the current context.

    Args:
        correlation_id (Optional[str]): The correlation ID to set. If None, a new UUID will be generated.

    Returns:
        str: The correlation ID that was set
    """
    if correlation_id is None:
        correlation_id = str(uuid.uuid4())
    correlation_id_context.set(correlation_id)
    return correlation_id


def clear_correlation_id() -> None:
    """Clear the correlation ID from the current context."""
    correlation_id_context.set("")


# Define a function to be used as a filter to inject correlation_id
def correlation_id_filter(record):
    record["extra"]["correlation_id"] = get_correlation_id() or "no-correlation-id"
    return record


def configure_logging(
    format_string: str = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level: str = "INFO",
    sink: Union[os.PathLike[str], TextIO, BinaryIO] = sys.stderr,
    rotation: Optional[str] = None,
    retention: Optional[str] = None,
    include_correlation_id: bool = True,
) -> "loguru.Logger":
    """
    Configure the loguru logger with custom settings.
    Check [Loguru Documentation](https://loguru.readthedocs.io/en/stable/api/logger.html) for more details.

    Args:
        format_string (str): The format string for log messages.
        level (str): The minimum logging level. Default: "INFO"
        sink: Where to send the log. Default: sys.stderr
        rotation (str, optional): When to rotate the log file.
                                  Example: "10 MB", "1 day"
                                  Only used when sink is a file path.
        retention (str, optional): How long to keep log files.
                                   Example: "1 week", "10 days"
                                   Only used when sink is a file path.
        include_correlation_id (bool): Whether to include correlation ID in log messages.
                                      Default: True

    Returns:
        The configured logger object
    """
    # Remove any existing handlers
    logger.remove()

    # Modify format string to include correlation ID if requested
    if include_correlation_id:
        format_string = "<magenta>[{extra[correlation_id]}]</magenta> " + format_string

    # Add rotation and retention only for file paths
    kwargs = {
        "format": format_string,
        "level": level,
        "filter": correlation_id_filter,  # Add the filter for each handler
    }

    if isinstance(sink, (str, os.PathLike)):
        if rotation is not None:
            kwargs["rotation"] = rotation
        if retention is not None:
            kwargs["retention"] = retention

    # Add the new handler
    logger.add(sink, **kwargs)

    return logger


# Example usage:
if __name__ == "__main__":
    # Basic configuration (uses sys.stderr)
    log = configure_logging()
    log.info("Basic logging configured successfully")

    # Set a correlation ID
    set_correlation_id("request-123")
    log.info("This log has a correlation ID")

    # Change correlation ID
    set_correlation_id("request-456")
    log.info("This log has a different correlation ID")

    # Use auto-generated correlation ID
    set_correlation_id()
    log.info("This log has an auto-generated correlation ID")

    # File-based logging with rotation and retention
    file_log = configure_logging(
        format_string="[{time:YYYY-MM-DD HH:mm:ss}] [{level}] {message}",
        level="DEBUG",
        sink="app.log",
        rotation="10 MB",
        retention="1 week",
    )
    file_log.debug("File logging configured successfully")

    # Stream-based logging
    stream_log = configure_logging(
        format_string="[{time:HH:mm:ss}] {message}", level="INFO", sink=sys.stdout
    )
    stream_log.info("Stream logging configured successfully")
