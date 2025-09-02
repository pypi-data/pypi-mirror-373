from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

from ...types._api_version import ApiVersion
from .._request_handler import AsyncRequestHandler, RequestHandler


class BasePipelineExecution:
    def __init__(self, request_handler: Union[RequestHandler, AsyncRequestHandler]):
        self._request_handler = request_handler

    def _pre_execute_pipeline(
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
        api_version: str = ApiVersion.V2.value,
    ):
        """
        Prepare request data for pipeline execution endpoint.

        This internal method constructs the URL and payload for pipeline execution
        requests, validating the API version and preparing all request components.

        Args:
            pipeline_id: ID of the pipeline to execute
            user_input: Input text to process
            debug: Whether to enable debug mode
            user_id: Optional user identifier
            conversation_id: Optional conversation identifier
            async_output: Whether to enable streaming output
            include_tools_response: Whether to include tool responses
            images: Optional list of base64-encoded images
            files: Optional list of base64-encoded files
            data_source_folders: Optional data source folder configuration
            data_source_files: Optional data source files configuration
            in_memory_messages: Optional list of in-memory messages
            current_date_time: Optional current date/time in ISO format
            save_history: Whether to save to conversation history
            additional_info: Optional additional information
            prompt_variables: Optional prompt variables
            voice_enabled: Whether the request came through the airia-voice-proxy
            correlation_id: Optional correlation ID for tracing
            api_version: API version to use for the request

        Returns:
            RequestData: Prepared request data for the pipeline execution endpoint

        Raises:
            ValueError: If an invalid API version is provided
        """
        if api_version not in ApiVersion.as_list():
            raise ValueError(
                f"Invalid API version: {api_version}. Valid versions are: {', '.join(ApiVersion.as_list())}"
            )
        url = urljoin(
            self._request_handler.base_url,
            f"{api_version}/PipelineExecution/{pipeline_id}",
        )

        payload = {
            "userInput": user_input,
            "debug": debug,
            "userId": user_id,
            "conversationId": conversation_id,
            "asyncOutput": async_output,
            "includeToolsResponse": include_tools_response,
            "images": images,
            "files": files,
            "dataSourceFolders": data_source_folders,
            "dataSourceFiles": data_source_files,
            "inMemoryMessages": in_memory_messages,
            "currentDateTime": current_date_time,
            "saveHistory": save_history,
            "additionalInfo": additional_info,
            "promptVariables": prompt_variables,
            "voiceEnabled": voice_enabled,
        }

        request_data = self._request_handler.prepare_request(
            url=url, payload=payload, correlation_id=correlation_id
        )

        return request_data
