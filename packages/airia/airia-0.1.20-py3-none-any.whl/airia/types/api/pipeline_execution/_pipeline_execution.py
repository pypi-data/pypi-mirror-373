"""
Pydantic models for pipeline execution API responses.

This module defines the response models returned by pipeline execution endpoints,
including both synchronous and streaming response types.
"""

from typing import Any, AsyncIterator, Dict, Iterator

from pydantic import BaseModel, ConfigDict, Field

from ...sse import SSEMessage


class PipelineExecutionResponse(BaseModel):
    """Response model for standard pipeline execution requests.

    This model represents the response when executing a pipeline in normal mode
    (not debug mode and not streaming).

    Attributes:
        result: The execution result as a string
        report: Always None for standard executions
        is_backup_pipeline: Whether a backup pipeline was used for execution
    """

    result: str
    report: None
    is_backup_pipeline: bool = Field(alias="isBackupPipeline")


class PipelineExecutionDebugResponse(BaseModel):
    """Response model for pipeline execution requests in debug mode.

    This model includes additional debugging information in the report field
    that provides insights into the pipeline's execution process.

    Attributes:
        result: The execution result as a string
        report: Dictionary containing debugging information and execution details
        is_backup_pipeline: Whether a backup pipeline was used for execution
    """

    result: str
    report: Dict[str, Any]
    is_backup_pipeline: bool = Field(alias="isBackupPipeline")


class PipelineExecutionStreamedResponse(BaseModel):
    """Response model for streaming pipeline execution requests (synchronous client).

    This model contains an iterator that yields SSEMessage objects as they
    are received from the streaming response.

    Attributes:
        stream: Iterator that yields SSEMessage objects from the streaming response
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    stream: Iterator[SSEMessage]


class PipelineExecutionAsyncStreamedResponse(BaseModel):
    """Response model for streaming pipeline execution requests (asynchronous client).

    This model contains an async iterator that yields SSEMessage objects as they
    are received from the streaming response.

    Attributes:
        stream: Async iterator that yields SSEMessage objects from the streaming response
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    stream: AsyncIterator[SSEMessage]
