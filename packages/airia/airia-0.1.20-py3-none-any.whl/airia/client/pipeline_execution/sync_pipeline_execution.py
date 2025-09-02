from typing import Any, Dict, List, Literal, Optional, Union, overload

from ...types._api_version import ApiVersion
from ...types.api.pipeline_execution import (
    PipelineExecutionDebugResponse,
    PipelineExecutionResponse,
    PipelineExecutionStreamedResponse,
)
from .._request_handler import RequestHandler
from .base_pipeline_execution import BasePipelineExecution


class PipelineExecution(BasePipelineExecution):
    def __init__(self, request_handler: RequestHandler):
        super().__init__(request_handler)

    @overload
    def execute_pipeline(
        self,
        pipeline_id: str,
        user_input: str,
        debug: Literal[False] = False,
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        async_output: Literal[False] = False,
        include_tools_response: bool = False,
        images: Optional[List[str]] = None,
        files: Optional[List[str]] = None,
        data_source_folders: Optional[Dict[str, Any]] = None,
        data_source_files: Optional[Dict[str, Any]] = None,
        in_memory_messages: Optional[List[Dict[str, str]]] = None,
        current_date_time: Optional[str] = None,
        save_history: bool = True,
        additional_info: Optional[List[Any]] = None,
        prompt_variables: Optional[Dict[str, Any]] = None,
        voice_enabled: bool = False,
        correlation_id: Optional[str] = None,
    ) -> PipelineExecutionResponse: ...

    @overload
    def execute_pipeline(
        self,
        pipeline_id: str,
        user_input: str,
        debug: Literal[True] = True,
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        async_output: Literal[False] = False,
        include_tools_response: bool = False,
        images: Optional[List[str]] = None,
        files: Optional[List[str]] = None,
        data_source_folders: Optional[Dict[str, Any]] = None,
        data_source_files: Optional[Dict[str, Any]] = None,
        in_memory_messages: Optional[List[Dict[str, str]]] = None,
        current_date_time: Optional[str] = None,
        save_history: bool = True,
        additional_info: Optional[List[Any]] = None,
        prompt_variables: Optional[Dict[str, Any]] = None,
        voice_enabled: bool = False,
        correlation_id: Optional[str] = None,
    ) -> PipelineExecutionDebugResponse: ...

    @overload
    def execute_pipeline(
        self,
        pipeline_id: str,
        user_input: str,
        debug: bool = False,
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        async_output: Literal[True] = True,
        include_tools_response: bool = False,
        images: Optional[List[str]] = None,
        files: Optional[List[str]] = None,
        data_source_folders: Optional[Dict[str, Any]] = None,
        data_source_files: Optional[Dict[str, Any]] = None,
        in_memory_messages: Optional[List[Dict[str, str]]] = None,
        current_date_time: Optional[str] = None,
        save_history: bool = True,
        additional_info: Optional[List[Any]] = None,
        prompt_variables: Optional[Dict[str, Any]] = None,
        voice_enabled: bool = False,
        correlation_id: Optional[str] = None,
    ) -> PipelineExecutionStreamedResponse: ...

    def execute_pipeline(
        self,
        pipeline_id: str,
        user_input: str,
        debug: bool = False,
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        async_output: bool = False,
        include_tools_response: bool = False,
        images: Optional[List[str]] = None,
        files: Optional[List[str]] = None,
        data_source_folders: Optional[Dict[str, Any]] = None,
        data_source_files: Optional[Dict[str, Any]] = None,
        in_memory_messages: Optional[List[Dict[str, str]]] = None,
        current_date_time: Optional[str] = None,
        save_history: bool = True,
        additional_info: Optional[List[Any]] = None,
        prompt_variables: Optional[Dict[str, Any]] = None,
        voice_enabled: bool = False,
        correlation_id: Optional[str] = None,
    ) -> Union[
        PipelineExecutionDebugResponse,
        PipelineExecutionResponse,
        PipelineExecutionStreamedResponse,
    ]:
        """
        Execute a pipeline with the provided input.

        Args:
            pipeline_id: The ID of the pipeline to execute.
            user_input: input text to process.
            debug: Whether debug mode execution is enabled. Default is False.
            user_id: Optional ID of the user making the request (guid).
            conversation_id: Optional conversation ID (guid).
            async_output: Whether to stream the response. Default is False.
            include_tools_response: Whether to return the initial LLM tool result. Default is False.
            images: Optional list of images formatted as base64 strings.
            files: Optional list of files formatted as base64 strings.
            data_source_folders: Optional data source folders information.
            data_source_files: Optional data source files information.
            in_memory_messages: Optional list of in-memory messages, each with a role and message.
            current_date_time: Optional current date and time in ISO format.
            save_history: Whether to save the userInput and output to conversation history. Default is True.
            additional_info: Optional additional information.
            prompt_variables: Optional variables to be used in the prompt.
            voice_enabled: Whether the request came through the airia-voice-proxy. Default is False.
            correlation_id: Optional correlation ID for request tracing. If not provided,
                        one will be generated automatically.

        Returns:
            Response containing the result of the execution.

        Raises:
            AiriaAPIError: If the API request fails with details about the error.
            requests.RequestException: For other request-related errors.

        Example:
            ```python
            client = AiriaClient(api_key="your_api_key")
            response = client.pipeline_execution.execute_pipeline(
                pipeline_id="pipeline_123",
                user_input="Tell me about quantum computing"
            )
            print(response.result)
            ```
        """
        request_data = self._pre_execute_pipeline(
            pipeline_id=pipeline_id,
            user_input=user_input,
            debug=debug,
            user_id=user_id,
            conversation_id=conversation_id,
            async_output=async_output,
            include_tools_response=include_tools_response,
            images=images,
            files=files,
            data_source_folders=data_source_folders,
            data_source_files=data_source_files,
            in_memory_messages=in_memory_messages,
            current_date_time=current_date_time,
            save_history=save_history,
            additional_info=additional_info,
            prompt_variables=prompt_variables,
            voice_enabled=voice_enabled,
            correlation_id=correlation_id,
            api_version=ApiVersion.V2.value,
        )
        resp = (
            self._request_handler.make_request_stream("POST", request_data)
            if async_output
            else self._request_handler.make_request("POST", request_data)
        )

        if not async_output:
            if not debug:
                return PipelineExecutionResponse(**resp)
            return PipelineExecutionDebugResponse(**resp)

        return PipelineExecutionStreamedResponse(stream=resp)
