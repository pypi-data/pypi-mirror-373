from typing import Any, Dict, Optional, Union
from urllib.parse import urljoin

from ...types._api_version import ApiVersion
from .._request_handler import AsyncRequestHandler, RequestHandler


class BaseConversations:
    def __init__(self, request_handler: Union[RequestHandler, AsyncRequestHandler]):
        self._request_handler = request_handler

    def _pre_create_conversation(
        self,
        user_id: str,
        title: Optional[str] = None,
        deployment_id: Optional[str] = None,
        data_source_files: Dict[str, Any] = {},
        is_bookmarked: bool = False,
        correlation_id: Optional[str] = None,
        api_version: str = ApiVersion.V1.value,
    ):
        """
        Prepare request data for creating a new conversation.

        This internal method constructs the URL and payload for conversation creation
        requests, including all conversation metadata and settings.

        Args:
            user_id: ID of the user creating the conversation
            title: Optional title for the conversation
            deployment_id: Optional deployment to associate with the conversation
            data_source_files: Optional data source files configuration
            is_bookmarked: Whether the conversation should be bookmarked
            correlation_id: Optional correlation ID for tracing
            api_version: API version to use for the request

        Returns:
            RequestData: Prepared request data for the conversation creation endpoint

        Raises:
            ValueError: If an invalid API version is provided
        """
        if api_version not in ApiVersion.as_list():
            raise ValueError(
                f"Invalid API version: {api_version}. Valid versions are: {', '.join(ApiVersion.as_list())}"
            )
        url = urljoin(self._request_handler.base_url, f"{api_version}/Conversations")

        payload = {
            "userId": user_id,
            "title": title,
            "deploymentId": deployment_id,
            "dataSourceFiles": data_source_files,
            "isBookmarked": is_bookmarked,
        }

        request_data = self._request_handler.prepare_request(
            url=url, payload=payload, correlation_id=correlation_id
        )

        return request_data

    def _pre_get_conversation(
        self,
        conversation_id: str,
        correlation_id: Optional[str] = None,
        api_version: str = ApiVersion.V1.value,
    ):
        """
        Prepare request data for retrieving a conversation by ID.

        This internal method constructs the URL for conversation retrieval
        requests using the provided conversation identifier.

        Args:
            conversation_id: ID of the conversation to retrieve
            correlation_id: Optional correlation ID for tracing
            api_version: API version to use for the request

        Returns:
            RequestData: Prepared request data for the conversation retrieval endpoint

        Raises:
            ValueError: If an invalid API version is provided
        """
        if api_version not in ApiVersion.as_list():
            raise ValueError(
                f"Invalid API version: {api_version}. Valid versions are: {', '.join(ApiVersion.as_list())}"
            )
        url = urljoin(
            self._request_handler.base_url,
            f"{api_version}/Conversations/{conversation_id}",
        )
        request_data = self._request_handler.prepare_request(
            url, correlation_id=correlation_id
        )

        return request_data

    def _pre_delete_conversation(
        self,
        conversation_id: str,
        correlation_id: Optional[str] = None,
        api_version: str = ApiVersion.V1.value,
    ):
        """
        Prepare request data for deleting a conversation by ID.

        This internal method constructs the URL for conversation deletion
        requests using the provided conversation identifier.

        Args:
            conversation_id: ID of the conversation to delete
            correlation_id: Optional correlation ID for tracing
            api_version: API version to use for the request

        Returns:
            RequestData: Prepared request data for the conversation deletion endpoint

        Raises:
            ValueError: If an invalid API version is provided
        """
        if api_version not in ApiVersion.as_list():
            raise ValueError(
                f"Invalid API version: {api_version}. Valid versions are: {', '.join(ApiVersion.as_list())}"
            )
        url = urljoin(
            self._request_handler.base_url,
            f"{api_version}/Conversations/{conversation_id}",
        )
        request_data = self._request_handler.prepare_request(
            url, correlation_id=correlation_id
        )

        return request_data
