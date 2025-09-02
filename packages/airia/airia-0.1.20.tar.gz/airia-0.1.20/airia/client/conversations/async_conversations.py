from typing import Any, Dict, Optional

from ...types._api_version import ApiVersion
from ...types.api.conversations import (
    CreateConversationResponse,
    GetConversationResponse,
)
from .._request_handler import AsyncRequestHandler
from .base_conversations import BaseConversations


class AsyncConversations(BaseConversations):
    def __init__(self, request_handler: AsyncRequestHandler):
        super().__init__(request_handler)

    async def create_conversation(
        self,
        user_id: str,
        title: Optional[str] = None,
        deployment_id: Optional[str] = None,
        data_source_files: Dict[str, Any] = {},
        is_bookmarked: bool = False,
        correlation_id: Optional[str] = None,
    ) -> CreateConversationResponse:
        """
        Create a new conversation.

        Args:
            user_id (str): The unique identifier of the user creating the conversation.
            title (str, optional): The title for the conversation. If not provided,
                the conversation will be created without a title.
            deployment_id (str, optional): The unique identifier of the deployment
                to associate with the conversation. If not provided, the conversation
                will not be associated with any specific deployment.
            data_source_files (dict): Configuration for data source files
                to be associated with the conversation. If not provided, no data
                source files will be associated.
            is_bookmarked (bool): Whether the conversation should be bookmarked.
                Defaults to False.
            correlation_id (str, optional): A unique identifier for request tracing
                and logging. If not provided, one will be automatically generated.

        Returns:
            CreateConversationResponse: A response object containing the created
                conversation details including its ID, creation timestamp, and
                all provided parameters.

        Raises:
            AiriaAPIError: If the API request fails, including cases where:
                - The user_id doesn't exist (404)
                - The deployment_id is invalid (404)
                - Authentication fails (401)
                - Access is forbidden (403)
                - Server errors (5xx)

        Example:
            ```python
            from airia import AiriaAsyncClient

            client = AiriaAsyncClient(api_key="your_api_key")

            # Create a basic conversation
            conversation = await client.conversations.create_conversation(
                user_id="user_123"
            )
            print(f"Created conversation: {conversation.conversation_id}")

            # Create a conversation with all options
            conversation = await client.conversations.create_conversation(
                user_id="user_123",
                title="My Research Session",
                deployment_id="deployment_456",
                data_source_files={"documents": ["doc1.pdf", "doc2.txt"]},
                is_bookmarked=True
            )
            print(f"Created bookmarked conversation: {conversation.conversation_id}")
            ```

        Note:
            The user_id is required and must correspond to a valid user in the system.
            All other parameters are optional and can be set to None or their default values.
        """
        request_data = self._pre_create_conversation(
            user_id=user_id,
            title=title,
            deployment_id=deployment_id,
            data_source_files=data_source_files,
            is_bookmarked=is_bookmarked,
            correlation_id=correlation_id,
            api_version=ApiVersion.V1.value,
        )
        resp = await self._request_handler.make_request("POST", request_data)

        return CreateConversationResponse(**resp)

    async def get_conversation(
        self, conversation_id: str, correlation_id: Optional[str] = None
    ) -> GetConversationResponse:
        """
        Retrieve detailed information about a specific conversation by its ID.

        This method fetches comprehensive information about a conversation including
        all messages, metadata, policy redactions, and execution status.

        Args:
            conversation_id (str): The unique identifier of the conversation to retrieve.
            correlation_id (str, optional): A unique identifier for request tracing
                and logging. If not provided, one will be automatically generated.

        Returns:
            GetConversationResponse: A response object containing the conversation
                details including user ID, messages, title, deployment information,
                data source files, bookmark status, policy redactions, and execution status.

        Raises:
            AiriaAPIError: If the API request fails, including cases where:
                - The conversation_id doesn't exist (404)
                - Authentication fails (401)
                - Access is forbidden (403)
                - Server errors (5xx)

        Example:
            ```python
            from airia import AiriaAsyncClient

            async def main():
                client = AiriaAsyncClient(api_key="your_api_key")

                # Get conversation details
                conversation = await client.conversations.get_conversation(
                    conversation_id="conversation_123"
                )

                print(f"Conversation: {conversation.title}")
                print(f"User: {conversation.user_id}")
                print(f"Messages: {len(conversation.messages)}")
                print(f"Bookmarked: {conversation.is_bookmarked}")

                # Access individual messages
                for message in conversation.messages:
                    print(f"[{message.role}]: {message.message}")

            asyncio.run(main())
            ```

        Note:
            This method only retrieves conversation information and does not
            modify or execute any operations on the conversation.
        """
        request_data = self._pre_get_conversation(
            conversation_id=conversation_id,
            correlation_id=correlation_id,
            api_version=ApiVersion.V1.value,
        )
        resp = await self._request_handler.make_request("GET", request_data)

        return GetConversationResponse(**resp)

    async def delete_conversation(
        self,
        conversation_id: str,
        correlation_id: Optional[str] = None,
    ) -> None:
        """
        Delete a conversation by its ID.

        This method permanently removes a conversation and all associated data
        from the Airia platform. This action cannot be undone.

        Args:
            conversation_id: The unique identifier of the conversation to delete
            correlation_id: Optional correlation ID for request tracing

        Returns:
            None: This method returns nothing upon successful deletion

        Raises:
            AiriaAPIError: If the API request fails or the conversation doesn't exist
        """
        request_data = self._pre_delete_conversation(
            conversation_id=conversation_id,
            correlation_id=correlation_id,
            api_version=ApiVersion.V1.value,
        )
        await self._request_handler.make_request(
            "DELETE", request_data, return_json=False
        )
