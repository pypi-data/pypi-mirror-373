"""
Pydantic models for deployment API responses.

This module defines the data structures returned by deployment-related endpoints,
including deployment listings with metadata, user prompts, and data sources.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class Project(BaseModel):
    """
    The base project model.

    Represents basic project information within deployment contexts.

    Attributes:
        id: Unique project identifier
        name: Human-readable project name
    """

    id: UUID = Field(description="Gets or sets the project identifier.")
    name: str = Field(description="Gets or sets the project name.")


class DataSource(BaseModel):
    """
    Condensed version of the datasource DTO.

    Represents basic data source information associated with deployments.

    Attributes:
        id: Optional unique identifier for the data source
        name: Optional human-readable name of the data source
    """

    id: Optional[UUID] = Field(
        None, description="Gets or Sets the datasource identifier."
    )
    name: Optional[str] = Field(None, description="Gets or Sets the datasource name.")


class UserPrompt(BaseModel):
    """
    Represents a user prompt entity in the system.

    User prompts are reusable text templates that can be associated with deployments
    to provide consistent interaction patterns.

    Attributes:
        user_prompt_id: Unique identifier for the user prompt
        name: Human-readable name of the user prompt
        message: The actual prompt message content
        description: Detailed description of what the prompt does
        updated_at: Timestamp of when the prompt was last modified
        active_deployments: Number of active deployments using this prompt
        project_id: Unique identifier of the project containing this prompt
        project_name: Name of the project containing this prompt
        project: Complete project information associated with this prompt
    """

    user_prompt_id: UUID = Field(
        alias="userPromptId",
        description="Gets or sets the unique identifier for the user prompt.",
    )
    name: str = Field(description="Gets or sets the name of the UserPrompt.")
    message: str = Field(description="Gets or sets the UserPrompt Message.")
    description: str = Field(description="Gets or sets the UserPrompt Description.")
    updated_at: datetime = Field(
        alias="updatedAt",
        description="Gets or sets the last modified date of the UserPrompt.",
    )
    active_deployments: int = Field(
        alias="activeDeployments",
        description="Gets or sets the number of active deployments for the UserPrompt.",
    )
    project_id: UUID = Field(
        alias="projectId",
        description="Gets or sets the unique identifier of the project that the prompt belongs to.",
    )
    project_name: Optional[str] = Field(
        None,
        alias="projectName",
        description="Gets or sets the name of the project that the prompt belongs to.",
    )
    project: Optional[Project] = Field(None, description="Gets or sets the project.")


class AboutDeploymentMetadata(BaseModel):
    """
    Represents metadata about a deployment for the About tab.

    Contains additional information displayed in the deployment's About section,
    including documentation and multimedia resources.

    Attributes:
        version: Version of the About Deployment metadata format
        video_url: URL to an explanatory video for the deployment
    """

    version: int = Field(
        description="Gets or sets the version of the About Deployment metadata."
    )
    video_url: str = Field(alias="videoUrl", description="Gets or sets the video url.")


class DeploymentItem(BaseModel):
    """
    Represents a deployment DTO.

    A deployment is a configured and published AI agent that can be used for conversations.
    It contains all the necessary information including the underlying pipeline,
    associated data sources, user prompts, and configuration settings.

    Attributes:
        deployment_id: Unique identifier for the deployment
        pipeline_id: Unique identifier of the pipeline powering this deployment
        deployment_name: Human-readable name of the deployment
        deployment_icon_url: Optional URL to the deployment's icon image
        description: Detailed description of what the deployment does
        project_id: Unique identifier of the project containing this deployment
        project_name: Name of the project containing this deployment
        user_prompts: List of user prompts associated with this deployment
        data_sources: List of data sources that the deployment can access
        is_recommended: Whether this deployment is marked as recommended
        tags: List of tags for categorizing and filtering deployments
        is_pinned: Whether this deployment is pinned for the current user
        deployment_type: Type of deployment (Chat, AddinChat, etc.)
        conversation_type: Type of conversation this deployment supports
        created_at: Timestamp when the deployment was created
        pipeline_user_id: ID of the user who created the underlying pipeline
        pipeline_name: Name of the underlying pipeline/agent
        deployment_prompt: Optional hardcoded prompt type for the deployment
        about_deployment_metadata: Optional metadata for the About tab
    """

    deployment_id: UUID = Field(
        alias="deploymentId", description="Gets the deployment ID."
    )
    pipeline_id: UUID = Field(
        alias="pipelineId",
        description="Gets the pipeline ID associated with this deployment.",
    )
    deployment_name: str = Field(
        alias="deploymentName", description="Gets the deployment name."
    )
    deployment_icon_url: Optional[str] = Field(
        None, alias="deploymentIconUrl", description="Gets the Deployment Icon URL."
    )
    description: str = Field(description="Gets the deployment description.")
    project_id: UUID = Field(
        alias="projectId",
        description="Gets the projectId associated with this deployment.",
    )
    project_name: Optional[str] = Field(
        None,
        alias="projectName",
        description="Gets the project name associated with this deployment.",
    )
    user_prompts: List[UserPrompt] = Field(
        alias="userPrompts",
        description="Gets the user prompts associated with this deployment.",
    )
    data_sources: List[DataSource] = Field(
        alias="dataSources",
        description="Gets the data sources associated with this deployment.",
    )
    is_recommended: bool = Field(
        alias="isRecommended",
        description="Gets a value indicating whether the deployment is recommended.",
    )
    tags: List[str] = Field(description="Gets the Tags.")
    is_pinned: bool = Field(
        alias="isPinned",
        description="Gets a value indicating whether the deployment is pinned for this user.",
    )
    deployment_type: str = Field(
        alias="deploymentType", description="Gets the deployment type."
    )
    conversation_type: str = Field(
        alias="conversationType",
        description="Gets or sets the conversation start type for this deployment.",
    )
    created_at: Optional[datetime] = Field(
        None, alias="createdAt", description="Gets when the deployment was created."
    )
    pipeline_user_id: Optional[UUID] = Field(
        None,
        alias="pipelineUserId",
        description="Gets the ID of the user who created deployed agent.",
    )
    pipeline_name: Optional[str] = Field(
        None, alias="pipelineName", description="Gets the name of the agent."
    )
    deployment_prompt: Optional[str] = Field(
        None, alias="deploymentPrompt", description="Gets the deployment prompt."
    )
    about_deployment_metadata: Optional[AboutDeploymentMetadata] = Field(
        None,
        alias="aboutDeploymentMetadata",
        description="Gets the metadata about the deployment, such as the video link.",
    )


class GetDeploymentsResponse(BaseModel):
    """
    Paged results for deployment entities.

    Contains a paginated list of deployments along with the total count,
    allowing for efficient retrieval of large deployment collections.

    Attributes:
        items: List of deployment items in the current page
        total_count: Total number of deployments matching the query
    """

    items: List[DeploymentItem] = Field(description="Gets or sets a list of items.")
    total_count: int = Field(
        alias="totalCount", description="Gets or sets the total count of items."
    )
