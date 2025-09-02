"""
Pydantic models for conversation management API responses.

This module defines data structures for conversation operations including
creation, retrieval, and message management within the Airia platform.
"""

from typing import Optional, List, Dict
from datetime import datetime

from pydantic import BaseModel, Field


class PolicyRedaction(BaseModel):
    """Information about content that was redacted due to policy violations.

    When content in a conversation violates platform policies, this model
    tracks what was redacted and where it occurred.

    Attributes:
        violating_text: The text content that violated platform policies
        violating_message_index: Index of the message containing the violation
    """

    violating_text: str = Field(alias="violatingText")
    violating_message_index: int = Field(alias="violatingMessageIndex")


class ConversationMessage(BaseModel):
    """Individual message within a conversation.

    Represents a single message exchange in a conversation, which can be
    from a user, assistant, or system. Messages may include text content
    and optional image attachments.

    Attributes:
        id: Unique identifier for the message
        conversation_id: ID of the conversation this message belongs to
        message: Optional text content of the message
        created_at: Timestamp when the message was created
        updated_at: Timestamp when the message was last updated
        role: Role of the message sender (user, assistant, system)
        images: Optional list of image URLs or identifiers
    """

    id: str
    conversation_id: str = Field(alias="conversationId")
    message: Optional[str] = None
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    role: str
    images: Optional[List[str]] = None


class GetConversationResponse(BaseModel):
    """Complete conversation data including messages and metadata.

    This response contains all information about a conversation including
    its message history, associated files, execution status, and any
    content moderation actions that have been applied.

    Attributes:
        user_id: ID of the user who owns the conversation
        conversation_id: Unique identifier for the conversation
        messages: List of messages in the conversation
        title: Optional title for the conversation
        websocket_url: Optional WebSocket URL for real-time updates
        deployment_id: Optional ID of the deployment handling the conversation
        data_source_files: Dictionary mapping data sources to their files
        is_bookmarked: Whether the conversation is bookmarked by the user
        policy_redactions: Optional dictionary of policy violations and redactions
        last_execution_status: Optional status of the last execution
        last_execution_id: Optional ID of the last execution
    """

    user_id: str = Field(alias="userId")
    conversation_id: str = Field(alias="conversationId")
    messages: List[ConversationMessage]
    title: Optional[str] = None
    websocket_url: Optional[str] = Field(None, alias="websocketUrl")
    deployment_id: Optional[str] = Field(None, alias="deploymentId")
    data_source_files: Dict[str, List[str]] = Field(alias="dataSourceFiles")
    is_bookmarked: bool = Field(alias="isBookmarked")
    policy_redactions: Optional[Dict[str, PolicyRedaction]] = Field(
        None, alias="policyRedactions"
    )
    last_execution_status: Optional[str] = Field(None, alias="lastExecutionStatus")
    last_execution_id: Optional[str] = Field(None, alias="lastExecutionId")


class CreateConversationResponse(BaseModel):
    """Response data for newly created conversations.

    Contains the essential information needed to begin interacting with
    a new conversation, including connection details and visual metadata.

    Attributes:
        user_id: ID of the user who created the conversation
        conversation_id: Unique identifier for the new conversation
        websocket_url: WebSocket URL for real-time conversation updates
        deployment_id: ID of the deployment handling the conversation
        icon_id: Optional ID of the conversation icon
        icon_url: Optional URL of the conversation icon
        description: Optional description of the conversation
        space_name: Optional name of the space containing the conversation
    """

    user_id: str = Field(alias="userId")
    conversation_id: str = Field(alias="conversationId")
    websocket_url: str = Field(alias="websocketUrl")
    deployment_id: str = Field(alias="deploymentId")
    icon_id: Optional[str] = Field(None, alias="iconId")
    icon_url: Optional[str] = Field(None, alias="iconUrl")
    description: Optional[str] = None
    space_name: Optional[str] = Field(None, alias="spaceName")
